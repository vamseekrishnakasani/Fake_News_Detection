#!/bin/bash

# Fake News Detector Docker Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if model directory exists
if [ ! -d "fake_news_model" ]; then
    print_error "Model directory 'fake_news_model' not found. Please train the model first."
    exit 1
fi

# Function to build and run containers
deploy_all() {
    print_status "Building and deploying all services..."
    
    # Build and start services
    docker-compose up --build -d
    
    print_status "Services deployed successfully!"
    print_status "Streamlit app: http://localhost:8501"
    print_status "API: http://localhost:8000"
    print_status "API docs: http://localhost:8000/docs"
}

# Function to deploy only Streamlit
deploy_streamlit() {
    print_status "Building and deploying Streamlit app..."
    
    docker build -t fake-news-app .
    docker run -d --name fake-news-streamlit -p 8501:8501 \
        -e SERVICE_TYPE=streamlit \
        -e STREAMLIT_HOST=0.0.0.0 \
        -e STREAMLIT_PORT=8501 \
        -v $(pwd)/fake_news_model:/app/fake_news_model:ro fake-news-app
    
    print_status "Streamlit app deployed successfully!"
    print_status "Access at: http://localhost:8501"
}

# Function to deploy only API
deploy_api() {
    print_status "Building and deploying API..."
    
    docker build -t fake-news-app .
    docker run -d --name fake-news-api -p 8000:8000 \
        -e SERVICE_TYPE=api \
        -e API_HOST=0.0.0.0 \
        -e API_PORT=8000 \
        -v $(pwd)/fake_news_model:/app/fake_news_model:ro fake-news-app
    
    print_status "API deployed successfully!"
    print_status "API: http://localhost:8000"
    print_status "API docs: http://localhost:8000/docs"
}

# Function to deploy both services in one container
deploy_both() {
    print_status "Building and deploying both services in one container..."
    
    docker build -t fake-news-app .
    docker run -d --name fake-news-both -p 8501:8501 -p 8000:8000 \
        -e SERVICE_TYPE=both \
        -e API_HOST=0.0.0.0 \
        -e API_PORT=8000 \
        -e STREAMLIT_HOST=0.0.0.0 \
        -e STREAMLIT_PORT=8501 \
        -v $(pwd)/fake_news_model:/app/fake_news_model:ro fake-news-app
    
    print_status "Both services deployed successfully!"
    print_status "Streamlit app: http://localhost:8501"
    print_status "API: http://localhost:8000"
    print_status "API docs: http://localhost:8000/docs"
}

# Function to stop all services
stop_all() {
    print_status "Stopping all services..."
    docker-compose down
    docker stop fake-news-streamlit fake-news-api fake-news-both 2>/dev/null || true
    docker rm fake-news-streamlit fake-news-api fake-news-both 2>/dev/null || true
    print_status "All services stopped."
}

# Function to show logs
show_logs() {
    if [ "$1" = "streamlit" ]; then
        docker-compose logs -f streamlit-app
    elif [ "$1" = "api" ]; then
        docker-compose logs -f api
    elif [ "$1" = "both" ]; then
        docker-compose logs -f both-services
    else
        docker-compose logs -f
    fi
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker-compose down --rmi all --volumes --remove-orphans
    docker stop fake-news-streamlit fake-news-api fake-news-both 2>/dev/null || true
    docker rm fake-news-streamlit fake-news-api fake-news-both 2>/dev/null || true
    docker system prune -f
    print_status "Cleanup completed."
}

# Main script logic
case "${1:-all}" in
    "all")
        deploy_all
        ;;
    "streamlit")
        deploy_streamlit
        ;;
    "api")
        deploy_api
        ;;
    "both")
        deploy_both
        ;;
    "stop")
        stop_all
        ;;
    "logs")
        show_logs "$2"
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  all       - Deploy both Streamlit and API services (default)"
        echo "  streamlit - Deploy only Streamlit app"
        echo "  api       - Deploy only API"
        echo "  both      - Deploy both services in one container"
        echo "  stop      - Stop all services"
        echo "  logs      - Show logs (use: logs streamlit, logs api, or logs both)"
        echo "  cleanup   - Clean up all Docker resources"
        echo "  help      - Show this help message"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information."
        exit 1
        ;;
esac 