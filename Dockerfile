FROM python:3.11-slim

# Prevents Python from writing .pyc files and enables faster logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    TIMEOUT=300

WORKDIR /app

# Install system dependencies required by Pillow and other packages
RUN apt-get update \
     && apt-get install -y --no-install-recommends \
         build-essential \
         libjpeg-dev \
         zlib1g-dev \
         libssl-dev \
         libffi-dev \
         pkg-config \
         curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . /app

# Create tmp directory with proper permissions
RUN mkdir -p /tmp && chmod 777 /tmp

EXPOSE 8080

# Use gunicorn with more appropriate settings for Cloud Run
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "1", "--threads", "2", "--timeout", "300", "--keep-alive", "2", "--max-requests", "1000", "--max-requests-jitter", "100", "app:app"]
