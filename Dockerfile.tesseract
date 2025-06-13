FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-jpn \
    tesseract-ocr-eng \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Download latest Japanese language data (optional, for better accuracy)
RUN wget -O /usr/share/tesseract-ocr/5/tessdata/jpn.traineddata \
    https://github.com/tesseract-ocr/tessdata_best/raw/main/jpn.traineddata

# Set TESSDATA_PREFIX environment variable
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 5000

# Set environment variables for production
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"] 