from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import uvicorn
import logging
from ..models.trainer import ModelTrainer
from ..utils.preprocessor import TextPreprocessor

logger = logging.getLogger(__name__)

class NewsText(BaseModel):
    """
    Pydantic model for request body. Expects a single field: text (str).
    """
    text: str

class NewsData(BaseModel):
    """
    Flexible Pydantic model for different input formats.
    """
    text: str = None
    title: str = None
    body: str = None
    content: str = None
    article: str = None
    headline: str = None
    description: str = None
    # Allow additional fields
    class Config:
        extra = "allow"

class FakeNewsAPI:
    """
    Encapsulates the FastAPI app and model loading for fake news detection.
    """
    def __init__(self, model_path='./fake_news_model'):
        """
        Loads the model and tokenizer for inference.
        Args:
            model_path (str): Path to the trained model directory.
        """
        self.model_path = model_path
        self.tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
        self.model = RobertaForSequenceClassification.from_pretrained(model_path)
        self.trainer = ModelTrainer(self.model, self.tokenizer)

    def create_app(self):
        """
        Creates and returns a FastAPI app with prediction endpoints.
        Returns:
            app (FastAPI): The FastAPI application.
        """
        app = FastAPI(title="Fake News Detection API")
        
        @app.post("/predict")
        async def predict_fake_news(news: NewsData):
            """
            Predict if the input news text is real or fake.
            Supports multiple input formats including plain text, JSON objects, etc.
            Args:
                news (NewsData): Request body with various possible text fields.
            Returns:
                dict: Prediction result and confidence.
            """
            try:
                # Convert Pydantic model to dict for preprocessing
                input_data = news.dict()
                
                # Use the flexible preprocessor to extract and clean text
                processed_text = TextPreprocessor.preprocess_input(input_data)
                
                if not processed_text or len(processed_text.strip()) < 10:
                    raise HTTPException(
                        status_code=400, 
                        detail="No meaningful text content found in the input"
                    )
                
                # Make prediction
                prediction = self.trainer.predict(processed_text)
                
                return {
                    "prediction": prediction["prediction"],
                    "confidence": prediction["confidence"],
                    "processed_text": processed_text[:200] + "..." if len(processed_text) > 200 else processed_text,
                    "original_input": input_data
                }
            except ValueError as e:
                logger.error(f"Input validation error: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"Prediction error: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/predict/text")
        async def predict_text(news: NewsText):
            """
            Simple endpoint for plain text input.
            Args:
                news (NewsText): Request body with 'text' field.
            Returns:
                dict: Prediction result and confidence.
            """
            try:
                processed_text = TextPreprocessor.preprocess_input(news.text)
                
                if not processed_text or len(processed_text.strip()) < 10:
                    raise HTTPException(
                        status_code=400, 
                        detail="No meaningful text content found"
                    )
                
                prediction = self.trainer.predict(processed_text)
                
                return {
                    "prediction": prediction["prediction"],
                    "confidence": prediction["confidence"],
                    "processed_text": processed_text[:200] + "..." if len(processed_text) > 200 else processed_text
                }
            except Exception as e:
                logger.error(f"Prediction error: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/")
        async def root():
            """
            Root endpoint for health check or welcome message.
            """
            return {
                "message": "Welcome to Fake News Detection API",
                "endpoints": {
                    "/predict": "Flexible endpoint accepting various input formats",
                    "/predict/text": "Simple endpoint for plain text input"
                },
                "supported_formats": [
                    "Plain text",
                    "JSON with text/body/content fields",
                    "Dictionary with various field names",
                    "HTML content (will be cleaned)"
                ]
            }
        
        return app

def run_api(host="0.0.0.0", port=8000):
    """
    Run the FastAPI app using Uvicorn.
    """
    api = FakeNewsAPI()
    app = api.create_app()
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_api() 