# Use official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary files (exclude training data, tests, etc.)
COPY app_streamlit.py ./
COPY fake_news_detector/ ./fake_news_detector/
COPY fake_news_model/ ./fake_news_model/

# Create entrypoint script
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Create a non-root user
RUN useradd -m -u 1000 appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose ports for both Streamlit and API
EXPOSE 8501 8000

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8000/health || curl --fail http://localhost:8501/_stcore/health || exit 1

# Use entrypoint script
ENTRYPOINT ["./entrypoint.sh"] 