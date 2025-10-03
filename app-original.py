from flask import Flask, render_template, request, jsonify
import base64
import re
import io
import os
import uuid
import tempfile
import logging
from datetime import datetime
from io import BytesIO
from PIL import Image
from pix2text import Pix2Text
import traceback

# Carica variabili d'ambiente se il file .env esiste
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv non installato, va bene

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurazione per production
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32))

# Inizializza il modello
p2t = None  # Caricamento lazy

def get_model():
    """Carica il modello solo quando necessario per risparmiare memoria"""
    global p2t
    if p2t is None:
        try:
            logger.info("Loading Pix2Text model (ultra-light config)...")
            # Configurazione ultra-minimale per ridurre drasticamente la memoria
            p2t = Pix2Text.from_config(
                total_configs={
                    'layout': None,  # Disabilita layout detection
                    'formula': {
                        'model_name': 'latex-ocr',  # Solo formula OCR
                        'device': 'cpu',  # Forza CPU invece di GPU
                    },
                    'text': None,  # Disabilita text recognition
                }
            )
            logger.info("Pix2Text model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Pix2Text model: {e}")
            logger.info("Trying fallback minimal config...")
            try:
                # Fallback: configurazione ancora più minimale
                p2t = Pix2Text.from_config()
                logger.info("Fallback model loaded")
            except Exception as e2:
                logger.error(f"Fallback also failed: {e2}")
                p2t = None
    return p2t

# Costanti
MAX_IMAGE_SIZE = (2048, 2048)  # Dimensione massima immagine
ALLOWED_FORMATS = {'PNG', 'JPEG', 'JPG'}

def validate_image_data(data_url):
    """Valida il formato e le dimensioni dell'immagine"""
    try:
        if not data_url or not data_url.startswith('data:image/'):
            return False, "Formato immagine non valido"
        
        header, encoded = data_url.split(",", 1)
        if len(encoded) > 10 * 1024 * 1024:  # 10MB in base64
            return False, "Immagine troppo grande"
            
        return True, None
    except Exception as e:
        return False, f"Errore nella validazione: {str(e)}"

def preprocess_image(data_url):
    """Preprocessa l'immagine con gestione degli errori"""
    try:
        # Valida input
        is_valid, error_msg = validate_image_data(data_url)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Decodifica immagine
        header, encoded = data_url.split(",", 1)
        img_data = base64.b64decode(encoded)
        img = Image.open(io.BytesIO(img_data)).convert("RGBA")
        
        # Limita dimensioni
        if img.size[0] > MAX_IMAGE_SIZE[0] or img.size[1] > MAX_IMAGE_SIZE[1]:
            img.thumbnail(MAX_IMAGE_SIZE, Image.LANCZOS)
            logger.info(f"Image resized to {img.size}")
        
        # Crea sfondo bianco
        white_bg = Image.new("RGB", img.size, (255, 255, 255))
        white_bg.paste(img, mask=img.split()[-1])
        
        # Trova dimensioni multiple di 32
        new_w = (white_bg.width + 31) // 32 * 32
        new_h = (white_bg.height + 31) // 32 * 32
        
        # Ridimensiona
        if new_w != white_bg.width or new_h != white_bg.height:
            white_bg = white_bg.resize((new_w, new_h), Image.LANCZOS)
        
        return white_bg
        
    except Exception as e:
        logger.error(f"Error in preprocess_image: {e}")
        raise


@app.route("/")
def index():
    """Pagina principale"""
    return render_template("index.html")

@app.route("/health")
def health_check():
    """Health check per monitoring"""
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "model_loaded": p2t is not None
    }
    return jsonify(status)

@app.route("/convert", methods=["POST"])
def convert():
    """Endpoint per convertire immagine in LaTeX"""
    temp_file = None
    try:
        # Validazione richiesta
        if not request.is_json:
            return jsonify({"error": "Content-Type deve essere application/json"}), 400
        
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "Campo 'image' mancante"}), 400
        
        # Controlla se il modello è caricato
        model = get_model()
        if model is None:
            return jsonify({"error": "Servizio temporaneamente non disponibile"}), 503
        
        logger.info("Processing image conversion request")
        
        # Preprocessa immagine
        img = preprocess_image(data['image'])
        
        # Salva in file temporaneo
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file_path = temp_file.name
            img.save(temp_file_path)
            logger.info(f"Image saved to temporary file: {temp_file_path}")
        
        # Riconosci il testo/formula
        latex_code = model.recognize_text_formula(temp_file_path)
        logger.info(f"LaTeX code generated successfully: {len(latex_code)} characters")
        
        return jsonify({
            "latex": latex_code,
            "status": "success"
        })
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
        
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Errore interno del server"}), 500
        
    finally:
        # Pulisci file temporaneo
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.info(f"Temporary file cleaned up: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file: {e}")

@app.errorhandler(413)
def handle_file_too_large(error):
    """Gestisce file troppo grandi"""
    return jsonify({"error": "File troppo grande (max 16MB)"}), 413

@app.errorhandler(404)
def handle_not_found(error):
    """Gestisce pagine non trovate"""
    return jsonify({"error": "Endpoint non trovato"}), 404

@app.errorhandler(500)
def handle_internal_error(error):
    """Gestisce errori interni"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Errore interno del server"}), 500

if __name__ == "__main__":
    # Configurazione per development vs production
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    
    if debug:
        logger.info("Starting in development mode")
        app.run(host="0.0.0.0", port=port, debug=True)
    else:
        logger.info("Starting in production mode")
        # Per production, usa un server WSGI come Gunicorn
        app.run(host="0.0.0.0", port=port, debug=False)

# Per deployment con Gunicorn
# gunicorn -w 4 -b 0.0.0.0:5000 app:app

