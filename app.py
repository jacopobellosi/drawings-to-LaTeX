from flask import Flask, render_template, request, jsonify
import base64
import io
import os
import sys
import tempfile
import logging
from datetime import datetime
from io import BytesIO
from PIL import Image
import traceback
import requests
import json

# Carica variabili d'ambiente se il file .env esiste
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurazione per production
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Genera SECRET_KEY automaticamente se non presente
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    import secrets
    secret_key = secrets.token_hex(32)
    logger.warning("SECRET_KEY not found in environment, generated automatically")
    logger.info("For production, set SECRET_KEY environment variable")

app.config['SECRET_KEY'] = secret_key

# Log della configurazione all'avvio
logger.info(f"Flask app starting with SECRET_KEY configured: {bool(app.config['SECRET_KEY'])}")
logger.info(f"Max content length: {app.config['MAX_CONTENT_LENGTH']}")
logger.info(f"Environment PORT: {os.environ.get('PORT', 'Not set')}")

# Costanti
MAX_IMAGE_SIZE = (1024, 1024)
ALLOWED_FORMATS = {'PNG', 'JPEG', 'JPG'}


def p2t_api_ocr(image_path):
    """Usa solo P2T (Pix2Text) Web API - 10.000 caratteri gratis al giorno"""
    try:
        api_url = "https://p2t.breezedeus.com/api/v1/pix2text"
        
        with open(image_path, 'rb') as img_file:
            files = {'image': img_file}
            data = {
                'recognize_formula': 'true',
                'recognize_text': 'false'  # Solo formule LaTeX
            }
            
            logger.info("Calling P2T (Pix2Text) API...")
            response = requests.post(api_url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    # Estrai le formule LaTeX dal risultato
                    data = result.get('data', {})
                    latex_results = data.get('latex_results', [])
                    if latex_results:
                        latex_code = latex_results[0].get('latex', '')
                        if latex_code:
                            logger.info("P2T API successful")
                            return latex_code
                            
    except Exception as e:
        logger.error(f"P2T API error: {e}")
    
    return None

def validate_image_data(data_url):
    """Valida il formato e le dimensioni dell'immagine"""
    try:
        if not data_url or not data_url.startswith('data:image/'):
            return False, "Formato immagine non valido"
        
        header, encoded = data_url.split(",", 1)
        if len(encoded) > 8 * 1024 * 1024:  # 8MB in base64 per API
            return False, "Immagine troppo grande per API"
            
        return True, None
    except Exception as e:
        return False, f"Errore nella validazione: {str(e)}"

def preprocess_image(data_url):
    """Preprocessa l'immagine ottimizzata per API"""
    try:
        # Valida input
        is_valid, error_msg = validate_image_data(data_url)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Decodifica immagine
        header, encoded = data_url.split(",", 1)
        img_data = base64.b64decode(encoded)
        img = Image.open(io.BytesIO(img_data)).convert("RGBA")
        
        # Ridimensiona per API (più piccola = più veloce)
        if img.size[0] > MAX_IMAGE_SIZE[0] or img.size[1] > MAX_IMAGE_SIZE[1]:
            img.thumbnail(MAX_IMAGE_SIZE, Image.LANCZOS)
            logger.info(f"Image resized to {img.size} for API")
        
        # Crea sfondo bianco
        white_bg = Image.new("RGB", img.size, (255, 255, 255))
        white_bg.paste(img, mask=img.split()[-1])
        
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
        "mode": "p2t-only",
        "available_apis": {
            "p2t": True  # 10.000 caratteri/giorno
        },
        "environment": {
            "port": os.environ.get('PORT', 'Not set'),
            "flask_env": os.environ.get('FLASK_ENV', 'Not set'),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        }
    }
    return jsonify(status)

@app.route("/debug")
def debug_info():
    """Debug endpoint per Railway"""
    import sys
    debug_data = {
        "python_version": sys.version,
        "flask_version": "3.0.0",
        "working_directory": os.getcwd(),
        "environment_vars": {
            "PORT": os.environ.get('PORT'),
            "FLASK_ENV": os.environ.get('FLASK_ENV'),
            "SECRET_KEY_SET": bool(os.environ.get('SECRET_KEY'))
        },
        "app_config": {
            "SECRET_KEY_SET": bool(app.config.get('SECRET_KEY')),
            "MAX_CONTENT_LENGTH": app.config.get('MAX_CONTENT_LENGTH')
        }
    }
    return jsonify(debug_data)

@app.route("/convert", methods=["POST"])
def convert():
    """Endpoint per convertire immagine in LaTeX usando solo API"""
    temp_file_path = None
    try:
        # Validazione richiesta
        if not request.is_json:
            return jsonify({"error": "Content-Type deve essere application/json"}), 400
        
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "Campo 'image' mancante"}), 400
        
        logger.info("Processing image conversion request (P2T-only mode)")
        
        # Preprocessa immagine
        img = preprocess_image(data['image'])
        
        # Salva in file temporaneo
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file_path = temp_file.name
            img.save(temp_file_path, optimize=True, quality=95)
            logger.info(f"Image saved to temporary file: {temp_file_path}")
        
        # Usa solo P2T API
        latex_code = p2t_api_ocr(temp_file_path)
        
        if not latex_code:
            logger.warning("P2T API failed")
            return jsonify({"error": "Impossibile elaborare l'immagine con P2T API"}), 500
        
        logger.info(f"LaTeX code generated successfully: {len(latex_code)} characters")
        
        return jsonify({
            "latex": latex_code,
            "status": "success",
            "service": "p2t",
            "mode": "p2t-only",
            "note": "Generated using P2T (Pix2Text) API"
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
        if temp_file_path and os.path.exists(temp_file_path):
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
        logger.info("Starting in development mode (P2T-only)")
        app.run(host="0.0.0.0", port=port, debug=True)
    else:
        logger.info("Starting in production mode (P2T-only)")
        app.run(host="0.0.0.0", port=port, debug=False)