# Configurazione Gunicorn ottimizzata per memoria limitata
bind = "0.0.0.0:5000"
workers = 1  # Ridotto da 4 a 1 per risparmiare memoria
worker_class = "sync"
worker_connections = 100  # Ridotto da 1000
timeout = 120  # Aumentato per il caricamento del modello
keepalive = 2
max_requests = 100  # Ridotto per liberare memoria periodicamente
max_requests_jitter = 10
preload_app = False  # Disabilitato per ridurre memory footprint iniziale
accesslog = "-"
errorlog = "-"
loglevel = "info"
worker_tmp_dir = "/dev/shm"  # Usa RAM invece di disco per tmp
