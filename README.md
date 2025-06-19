# Fake News Detection with RoBERTa

A modular implementation of a fake news detection system using RoBERTa, with a FastAPI-based deployment and Streamlit user interface.

## Project Structure

```
fake_news_detector/
├── api/
│   └── app.py           # FastAPI application
├── models/
│   ├── dataset.py       # Dataset handling
│   └── trainer.py       # Model training and evaluation
├── utils/
│   └── config.py        # Configuration management
└── __init__.py          # Package initialization
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/vamseekrishnakasani/Fake_News_Detection.git
cd fake-news-detector
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Training the Model

1. Prepare your dataset in CSV format with columns:
   - `text`: The news article text
   - `label`: 0 for real news, 1 for fake news

2. Train the model:
```bash
python train.py
```

### Running the API

1. Start the API server:
```bash
python -m fake_news_detector.api.app
```

2. The API will be available at `http://localhost:8000`

#### Example: Using the API with Python
```python
import requests
response = requests.post(
    "http://localhost:8000/predict",
    json={"text": "NASA launches new rocket."}
)
print(response.json())
```

### Running the Streamlit App

1. Start the Streamlit app:
```bash
streamlit run app_streamlit.py
```
2. The app will open in your browser at `http://localhost:8501`

## Docker Deployment

1. Build the Docker image:
```bash
docker build -t fake-news-detector .
```
2. Run the container:
```bash
docker run -p 8000:8000 fake-news-detector
```
3. The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /`: Welcome message
- `POST /predict`: Make predictions
  ```json
  {
    "text": "Your news article text here"
  }
  ```

## Configuration

The system can be configured using environment variables:

```bash
# Model Configuration
MODEL_NAME=roberta-base
MAX_LENGTH=512
NUM_LABELS=2
BATCH_SIZE=8
NUM_EPOCHS=3
LEARNING_RATE=2e-5
WARMUP_STEPS=500
WEIGHT_DECAY=0.01

# Training Configuration
OUTPUT_DIR=./fake_news_model
LOGGING_DIR=./logs
LOGGING_STEPS=100
EVAL_STEPS=500
SAVE_STEPS=500

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
MODEL_PATH=./fake_news_model
```

## Development

### Adding New Features

1. Create new modules in appropriate directories
2. Update `__init__.py` to expose new functionality
3. Add tests in the `tests` directory
4. Update documentation

### Running Tests

```bash
pytest tests/
```

## License

MIT License 
