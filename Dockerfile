FROM python:3.11-slim

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Crea directory di lavoro
WORKDIR /app

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'applicazione
COPY . .

# Crea un utente non-root
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Esponi la porta
EXPOSE 5000

# Comando per avviare l'applicazione
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
