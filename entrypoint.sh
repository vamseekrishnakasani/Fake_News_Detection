#!/bin/bash

# Fake News Detector Entrypoint Script
# Supports both Streamlit and FastAPI services

set -e

# Default values
SERVICE_TYPE=${SERVICE_TYPE:-"api"}
API_HOST=${API_HOST:-"0.0.0.0"}
API_PORT=${API_PORT:-"8000"}
STREAMLIT_HOST=${STREAMLIT_HOST:-"0.0.0.0"}
STREAMLIT_PORT=${STREAMLIT_PORT:-"8501"}

echo "Starting Fake News Detector service..."
echo "Service type: $SERVICE_TYPE"

# Function to run API
run_api() {
    echo "Starting FastAPI service on $API_HOST:$API_PORT"
    exec uvicorn fake_news_detector.api.app:app \
        --host "$API_HOST" \
        --port "$API_PORT" \
        --workers 1
}

# Function to run Streamlit
run_streamlit() {
    echo "Starting Streamlit service on $STREAMLIT_HOST:$STREAMLIT_PORT"
    exec streamlit run app_streamlit.py \
        --server.port="$STREAMLIT_PORT" \
        --server.address="$STREAMLIT_HOST" \
        --server.headless=true \
        --browser.gatherUsageStats=false
}

# Function to run both services
run_both() {
    echo "Starting both API and Streamlit services..."
    
    # Start API in background
    uvicorn fake_news_detector.api.app:app \
        --host "$API_HOST" \
        --port "$API_PORT" \
        --workers 1 &
    
    API_PID=$!
    
    # Start Streamlit in foreground
    streamlit run app_streamlit.py \
        --server.port="$STREAMLIT_PORT" \
        --server.address="$STREAMLIT_HOST" \
        --server.headless=true \
        --browser.gatherUsageStats=false &
    
    STREAMLIT_PID=$!
    
    # Wait for either process to exit
    wait -n
    
    # Kill both processes if one exits
    kill $API_PID $STREAMLIT_PID 2>/dev/null || true
    exit 1
}

# Main logic
case "$SERVICE_TYPE" in
    "api"|"API")
        run_api
        ;;
    "streamlit"|"STREAMLIT")
        run_streamlit
        ;;
    "both"|"BOTH")
        run_both
        ;;
    *)
        echo "Unknown service type: $SERVICE_TYPE"
        echo "Available options: api, streamlit, both"
        exit 1
        ;;
esac 