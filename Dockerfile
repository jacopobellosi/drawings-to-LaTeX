FROM python:3.11-slim

# Prevents Python from writing .pyc files and enables faster logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

WORKDIR /app

# Install system dependencies required by Pillow (image handling) and some build tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libjpeg-dev \
       zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt ./

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . /app

EXPOSE 5000

# Simple entrypoint — change to gunicorn or uvicorn if you add production server
CMD ["python", "app.py"]
