# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app
# Create the non root user

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .

# Expose port 8080
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV FLASK_APP=app.py


# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/', timeout=5)"

# Run the Flask application
CMD ["python", "app.py"]
