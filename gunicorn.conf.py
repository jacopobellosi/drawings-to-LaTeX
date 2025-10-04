# Configurazione Gunicorn ottimizzata per cloud platforms
import os

# Forza il refresh delle variabili d'ambiente
port = os.environ.get("PORT", "5000")
print(f"[GUNICORN] Using PORT: {port}")  # Debug log

bind = f"0.0.0.0:{port}"
workers = 1
worker_class = "sync"
worker_connections = 100
timeout = 120
keepalive = 2
max_requests = 100
max_requests_jitter = 10
preload_app = False
accesslog = "-"
errorlog = "-"
loglevel = "info"
