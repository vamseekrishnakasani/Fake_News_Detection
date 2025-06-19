import streamlit as st
import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification
from fake_news_detector.models.trainer import ModelTrainer
from fake_news_detector.utils.preprocessor import TextPreprocessor
import logging

# Set up logging for the app
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set Streamlit page configuration
st.set_page_config(
    page_title="Fake News Detector",
    page_icon="📰",
    layout="wide"
)

# Custom CSS for styling the app
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTextArea textarea {
        font-size: 16px;
    }
    .prediction-box {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .fake {
        background-color: #d32f2f !important;  /* Strong red */
        color: #fff !important;                /* White text */
        border: 1px solid #b71c1c;
    }
    .real {
        background-color: #388e3c !important;  /* Strong green */
        color: #fff !important;                /* White text */
        border: 1px solid #1b5e20;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_model():
    """
    Load the trained model and tokenizer for inference.
    Returns:
        ModelTrainer: An instance of ModelTrainer for predictions.
    """
    try:
        model_path = './fake_news_model'
        tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
        model = RobertaForSequenceClassification.from_pretrained(model_path)
        return ModelTrainer(model, tokenizer)
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        st.error("Error loading the model. Please ensure the model is trained and available.")
        return None

def main():
    """
    Streamlit app main function for fake news detection.
    Allows users to input news text and get predictions from the model.
    """
    # Title and description
    st.title("📰 Fake News Detector")
    st.markdown("""
    This application uses a RoBERTa-based model to detect whether a news article is likely to be real or fake.
    Enter the text of a news article below to analyze it.
    """)

    # Load model and tokenizer
    trainer = load_model()
    if trainer is None:
        st.stop()

    # Input method selection
    input_method = st.selectbox(
        "Choose input method:",
        ["Plain Text", "JSON Format", "Multiple Fields"]
    )

    if input_method == "Plain Text":
        # Simple text input
        text_input = st.text_area(
            "Enter the news article text:",
            height=200,
            placeholder="Paste the news article text here..."
        )
        input_data = text_input if text_input else None
        
    elif input_method == "JSON Format":
        # JSON input
        json_input = st.text_area(
            "Enter JSON data:",
            height=200,
            placeholder='{"title": "Article Title", "body": "Article content...", "author": "Author Name"}'
        )
        input_data = json_input if json_input else None
        
    else:  # Multiple Fields
        # Multiple field input
        st.markdown("### Enter article details:")
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Title/Headline:", placeholder="Article title...")
            author = st.text_input("Author:", placeholder="Author name...")
            
        with col2:
            source = st.text_input("Source:", placeholder="News source...")
            date = st.text_input("Date:", placeholder="Publication date...")
            
        body = st.text_area("Article Body:", height=150, placeholder="Main article content...")
        
        # Create a dictionary from the fields
        input_data = {
            "title": title,
            "author": author,
            "source": source,
            "date": date,
            "body": body
        }
        
        # Remove empty fields
        input_data = {k: v for k, v in input_data.items() if v}

    # Add a submit button
    if st.button("Analyze", type="primary"):
        if input_data:
            with st.spinner("Analyzing the text..."):
                try:
                    # Use the flexible preprocessor to handle different input formats
                    processed_text = TextPreprocessor.preprocess_input(input_data)
                    
                    if not processed_text or len(processed_text.strip()) < 10:
                        st.error("No meaningful text content found. Please provide more text.")
                        return
                    
                    # Make prediction using the model
                    prediction = trainer.predict(processed_text)
                    
                    # Display results
                    st.markdown("### Results")
                    
                    # Show processed text (first 300 characters)
                    with st.expander("Processed Text (first 300 characters)"):
                        st.text(processed_text[:300] + "..." if len(processed_text) > 300 else processed_text)
                    
                    # Create a colored box for the prediction
                    prediction_class = "fake" if prediction["prediction"] == "Fake" else "real"
                    confidence = prediction["confidence"] * 100
                    
                    st.markdown(f"""
                    <div class="prediction-box {prediction_class}">
                        <h3>Prediction: {prediction["prediction"]}</h3>
                        <p>Confidence: {confidence:.2f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add explanation based on prediction
                    if prediction["prediction"] == "Fake":
                        st.warning("""
                        ⚠️ This article shows characteristics of potentially fake news. 
                        Please verify the information from reliable sources.
                        """)
                    else:
                        st.success("""
                        ✅ This article shows characteristics of potentially real news. 
                        However, always verify information from multiple reliable sources.
                        """)
                        
                except Exception as e:
                    logger.error(f"Prediction error: {str(e)}")
                    st.error("An error occurred while analyzing the text. Please try again.")
        else:
            st.warning("Please enter some text to analyze.")

    # Add information about the model and supported formats
    with st.expander("About the Model & Supported Formats"):
        st.markdown("""
        ### Model Information
        - **Model Type**: RoBERTa (Robustly Optimized BERT Pretraining Approach)
        - **Task**: Binary Classification (Real vs Fake News)
        - **Training**: Fine-tuned on a dataset of real and fake news articles
        
        ### Supported Input Formats
        1. **Plain Text**: Direct text input
        2. **JSON Format**: Structured data with fields like title, body, content, etc.
        3. **Multiple Fields**: Separate inputs for title, author, body, etc.
        
        ### How to Use
        1. Choose your preferred input method
        2. Enter the news article content
        3. Click the "Analyze" button
        4. View the prediction and confidence score
        
        ### Important Note
        This tool is meant to assist in identifying potentially fake news but should not be the sole basis for determining the veracity of news articles. Always verify information from multiple reliable sources.
        """)

if __name__ == "__main__":
    main() 