#!/bin/bash
echo "[STARTUP] Environment debug:"
echo "[STARTUP] PORT: $PORT"
echo "[STARTUP] FLASK_ENV: $FLASK_ENV"
echo "[STARTUP] PWD: $(pwd)"
echo "[STARTUP] Python version: $(python --version)"

# Avvia gunicorn con la porta corretta
echo "[STARTUP] Starting gunicorn on port $PORT"
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --access-logfile - --error-logfile - app:app