# 🚀 DEPLOYMENT GUIDE - LaTeX OCR

## 📁 File da includere nella Repository

### ✅ **File ESSENZIALI per la repository:**
```
├── app.py                 # Applicazione principale
├── requirements.txt       # Dipendenze Python
├── Procfile              # Per Heroku/Railway
├── Dockerfile            # Per deployment Docker
├── docker-compose.yml    # Per deployment locale Docker
├── gunicorn.conf.py      # Configurazione server produzione
├── .env.example          # Template variabili d'ambiente
├── .gitignore           # File da ignorare in Git
├── .dockerignore        # File da ignorare in Docker
├── README.md            # Documentazione
└── templates/
    └── index.html       # Frontend
```

### ❌ **File da NON includere:**
- `venv/` (ambiente virtuale)
- `.env` (variabili d'ambiente reali)
- `debug_input.png` (file temporanei)
- `*.png`, `*.jpg` (immagini di test)
- `provaOCR.py`, `provaOCR2.py` (file di prova)
- `archive.zip` (archivi)
- `git/` (cartelle git annidate)

## 🔧 Setup Repository GitHub

### 1. Inizializza Repository
```bash
cd "c:\Users\Utente\OneDrive\test\latexocr"
git init
git add .
git commit -m "Initial commit - LaTeX OCR app"
```

### 2. Crea Repository su GitHub
1. Vai su https://github.com/new
2. Nome: `latex-ocr-app` (o come preferisci)
3. Descrizione: "Web app to convert handwritten math formulas to LaTeX"
4. Public/Private: a tua scelta
5. NON aggiungere README (già presente)

### 3. Collega e Push
```bash
git remote add origin https://github.com/TUO-USERNAME/latex-ocr-app.git
git branch -M main
git push -u origin main
```

## 🌐 Opzioni di Deployment Online

### 🥇 **RAILWAY (Raccomandato - Più Semplice)**

**Perché Railway:**
- ✅ Deploy automatico da GitHub
- ✅ 500 ore gratuite/mese
- ✅ SSL automatico
- ✅ Facile configurazione

**Steps:**
1. Vai su https://railway.app
2. "Deploy from GitHub repo"
3. Seleziona la tua repository
4. Railway rileva automaticamente Python
5. Aggiungi variabile: `SECRET_KEY` = `your-secret-key-here`
6. Deploy automatico!

**URL finale:** `https://your-app-name.up.railway.app`

---

### 🥈 **RENDER (Alternativa Ottima)**

**Steps:**
1. Vai su https://render.com
2. "New Web Service"
3. Connetti GitHub repository
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn --config gunicorn.conf.py app:app`
6. Aggiungi Environment Variable: `SECRET_KEY`

---

### 🥉 **HEROKU (Più Popolare ma a Pagamento)**

**Steps:**
```bash
# Installa Heroku CLI
heroku login
heroku create your-app-name
heroku config:set SECRET_KEY="your-secret-key-here"
git push heroku main
```

---

### 🐳 **DIGITALOCEAN APP PLATFORM**

**Steps:**
1. Vai su DigitalOcean App Platform
2. "Create App"
3. Connetti GitHub
4. Seleziona "Dockerfile"
5. Configura environment variables

---

### 🔧 **VPS PERSONALIZZATO (Avanzato)**

**Se hai un VPS:**
```bash
# Sul server
git clone https://github.com/TUO-USERNAME/latex-ocr-app.git
cd latex-ocr-app
docker-compose up -d
```

## ⚡ Quick Start (Railway - Raccomandato)

### 1. Prepara Repository
```bash
cd "c:\Users\Utente\OneDrive\test\latexocr"
git init
git add .
git commit -m "LaTeX OCR production ready"
# Push su GitHub
```

### 2. Deploy su Railway
1. https://railway.app → Login with GitHub
2. "Deploy from GitHub repo"
3. Seleziona repository
4. Aggiungi variabile: `SECRET_KEY` = `mysecretkey123`
5. Deploy!

### 3. Test
- URL: `https://your-app.up.railway.app`
- Health check: `https://your-app.up.railway.app/health`

## 🔐 Sicurezza Pre-Deploy

### ✅ Checklist Sicurezza:
- [ ] Cambia `SECRET_KEY` (non usare quella di esempio!)
- [ ] Verifica che `.env` sia in `.gitignore`
- [ ] Testa localmente con `FLASK_ENV=production`
- [ ] Controlla che non ci siano file sensibili nel repo

### 🔑 Genera SECRET_KEY sicura:
```python
import secrets
print(secrets.token_urlsafe(32))
```

## 📊 Monitoraggio Post-Deploy

### Health Check:
```bash
curl https://your-app.com/health
```

### Logs (Railway):
- Dashboard Railway → Deployments → View Logs

## 💰 Costi Stimati

| Piattaforma | Piano Gratuito | Limiti |
|-------------|----------------|---------|
| **Railway** | 500h/mese | $0 |
| **Render** | 750h/mese | $0 |
| **Heroku** | 0h/mese | $7/mese |
| **DigitalOcean** | $0 trial | $5/mese |

## 🆘 Troubleshooting

### Errore "Application failed to start":
- Controlla logs
- Verifica `requirements.txt`
- Assicurati che `SECRET_KEY` sia impostata

### Errore "Module not found":
- Aggiungi modulo mancante a `requirements.txt`
- Fai nuovo deploy

### App lenta al primo avvio:
- È normale (cold start)
- Considera keep-alive con cron job
