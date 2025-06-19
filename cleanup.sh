#!/bin/bash

# Fake News Detector Production Cleanup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to safely remove files/directories
safe_remove() {
    if [ -e "$1" ]; then
        rm -rf "$1"
        print_status "Removed: $1"
    else
        print_warning "Not found: $1"
    fi
}

print_status "Starting production cleanup..."

# Check if model directory exists
if [ ! -d "fake_news_model" ]; then
    print_error "Model directory 'fake_news_model' not found. Cannot proceed with cleanup."
    exit 1
fi

# Training & Development Files
print_status "Removing training and development files..."
safe_remove "train.py"
safe_remove "prepare_dataset.py"
safe_remove "setup.py"
safe_remove "fake_news_detector.egg-info"

# Test Files
print_status "Removing test files..."
safe_remove "tests"
safe_remove ".pytest_cache"

# Large Data Files
print_status "Removing training data files..."
safe_remove "fake_news_detector/data"

# Training Model Files
print_status "Removing training model files..."
safe_remove "fake_news_detector/models/trainer.py"
safe_remove "fake_news_detector/models/dataset.py"

# System Files
print_status "Removing system files..."
safe_remove ".DS_Store"
safe_remove "fake_news_detector/.DS_Store"

# Python Cache
print_status "Removing Python cache files..."
safe_remove "fake_news_detector/__pycache__"
safe_remove "fake_news_detector/models/__pycache__"

# Virtual Environment
print_status "Removing virtual environment..."
safe_remove "news_venv"

# Clean up empty directories
print_status "Cleaning up empty directories..."
find . -type d -empty -delete 2>/dev/null || true

print_status "Cleanup completed successfully!"
print_status ""
print_status "Remaining files for production:"
echo "├── app_streamlit.py (Streamlit app)"
echo "├── fake_news_detector/"
echo "│   ├── api/ (FastAPI endpoints)"
echo "│   ├── utils/ (utilities)"
echo "│   └── models/ (model loading)"
echo "├── fake_news_model/ (trained model)"
echo "├── Dockerfile* (Docker configurations)"
echo "├── docker-compose.yml"
echo "├── requirements*.txt"
echo "├── deploy.sh"
echo "└── .dockerignore"
print_status ""
print_status "You can now deploy with: ./deploy.sh" 