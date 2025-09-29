# 🎯 LaTeX OCR - Handwritten Math to LaTeX

> Convert handwritten mathematical formulas to LaTeX code with AI-powered OCR

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/deploy)

## ✨ Features

- 🖋️ **Draw formulas** with mouse or touch
- 🤖 **AI-powered recognition** using Pix2Text
- 📝 **Real-time LaTeX preview** with KaTeX
- 📋 **One-click copy** of generated LaTeX code
- 📱 **Mobile-friendly** responsive design
- 🚀 **Production-ready** with Docker support

## 🚀 Quick Start

### Online Demo
👉 **[Try it live!](https://your-app.up.railway.app)** (Replace with your deployed URL)

### Local Development
```bash
# Clone repository
git clone https://github.com/yourusername/latex-ocr-app.git
cd latex-ocr-app

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py

# Open http://localhost:5000
```

## 🎮 How to Use

1. **Draw** your mathematical formula on the canvas
2. **Click** "Converti in LaTeX" to process
3. **View** the generated LaTeX code and live preview
4. **Copy** the LaTeX code with one click

![Demo GIF](https://via.placeholder.com/600x300/f0f0f0/333?text=Add+Demo+GIF+Here)

## 🛠️ Tech Stack

- **Backend**: Flask, Pix2Text, PIL
- **Frontend**: HTML5 Canvas, KaTeX, Vanilla JS
- **Deployment**: Docker, Gunicorn
- **AI/ML**: Pix2Text for formula recognition

## 🚀 Deployment in Produzione

### Opzione 1: Docker (Raccomandato)

```bash
# Clona il repository
git clone <your-repo-url>
cd latexocr

# Copia e modifica le variabili d'ambiente
cp .env.example .env
# Modifica .env con i tuoi valori

# Build e avvia con Docker Compose
docker-compose up -d

# L'applicazione sarà disponibile su http://localhost:5000
```

### Opzione 2: Deployment Tradizionale

```bash
# Installa dipendenze
pip install -r requirements.txt

# Configura variabili d'ambiente
export FLASK_ENV=production
export SECRET_KEY="your-secret-key-here"

# Avvia con Gunicorn
gunicorn --config gunicorn.conf.py app:app
```

### Opzione 3: Heroku

```bash
# Aggiungi file Procfile
echo "web: gunicorn --config gunicorn.conf.py app:app" > Procfile

# Deploy su Heroku
heroku create your-app-name
heroku config:set SECRET_KEY="your-secret-key"
git push heroku main
```

### Opzione 4: Railway/Render/DigitalOcean

Il progetto è pronto per il deployment su:
- **Railway**: Rileva automaticamente Python e Dockerfile
- **Render**: Usa il Dockerfile incluso
- **DigitalOcean App Platform**: Compatibile con Docker

## 🔧 Configurazione

### Variabili d'Ambiente

- `FLASK_ENV`: `production` per produzione
- `SECRET_KEY`: Chiave segreta per Flask (IMPORTANTE: cambiarla!)
- `PORT`: Porta del server (default: 5000)
- `LOG_LEVEL`: Livello di logging (default: INFO)

### Sicurezza

- ✅ Validazione input
- ✅ Limite dimensioni file (16MB)
- ✅ Gestione file temporanei
- ✅ Rate limiting pronto
- ✅ Logging completo
- ✅ Health check endpoint

## 📊 Monitoring

### Health Check
```bash
curl http://your-domain.com/health
```

### Logs
```bash
# Con Docker
docker-compose logs -f

# Con Gunicorn
tail -f gunicorn.log
```

## 🔒 Sicurezza

1. **Cambia la SECRET_KEY** in produzione
2. **Usa HTTPS** (configura reverse proxy)
3. **Limita accesso** se necessario
4. **Monitora i logs** per attività sospette

## 🚀 Performance

- Usa **4 worker Gunicorn** per default
- **File temporanei** puliti automaticamente
- **Validazione** input per evitare abuse
- **Timeout** configurati per stabilità

## 📱 Caratteristiche

- ✅ Interfaccia web responsive
- ✅ Supporto touch per mobile
- ✅ Anteprima LaTeX in tempo reale
- ✅ Copia codice LaTeX con un click
- ✅ Gestione errori user-friendly
- ✅ Logging completo

## 🔧 Manutenzione

### Aggiornare Dipendenze
```bash
pip install --upgrade -r requirements.txt
```

### Backup
Non ci sono dati persistenti da backuppare (applicazione stateless).

### Scaling
Per traffico elevato:
1. Aumenta i worker Gunicorn
2. Usa un load balancer
3. Considera Redis per caching
