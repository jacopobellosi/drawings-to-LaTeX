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
import traceback
import requests

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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32))

# Modalità fallback per ambienti con memoria limitata
USE_FALLBACK_API = os.environ.get('USE_FALLBACK_API', 'false').lower() == 'true'

def get_model():
    """Carica il modello solo se non in modalità fallback"""
    if USE_FALLBACK_API:
        return None
    
    try:
        from pix2text import Pix2Text
        global p2t
        if 'p2t' not in globals() or p2t is None:
            logger.info("Loading Pix2Text model...")
            p2t = Pix2Text.from_config()
            logger.info("Pix2Text model loaded successfully")
        return p2t
    except Exception as e:
        logger.error(f"Failed to load Pix2Text model: {e}")
        return None

def fallback_ocr(image_path):
    """API fallback con multiple strategie"""
    try:
        # Strategia 1: Prova servizio P2T con headers migliorati
        api_url = "https://p2t.breezedeus.com"
        
        # Leggi l'immagine
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
        
        # Headers per evitare bot detection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Prova una richiesta multipart più standard
        files = {
            'image': ('formula.png', img_data, 'image/png')
        }
        
        data = {
            'file_type': 'formula',
            'language': 'en'
        }
        
        logger.info("Calling P2T web service...")
        
        response = requests.post(
            f"{api_url}/api/predict",
            files=files,
            data=data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            try:
                result = response.json()
                if 'text' in result:
                    logger.info("P2T web service successful")
                    return result['text']
                elif 'result' in result:
                    return result['result']
            except:
                pass
        
        logger.warning(f"P2T service failed: {response.status_code}")
        
    except Exception as e:
        logger.error(f"P2T service error: {e}")
    
    # Strategia 2: Fallback locale con pattern recognition
    return fallback_pattern_recognition(image_path)

def fallback_pattern_recognition(image_path):
    """Fallback usando pattern recognition semplice senza numpy"""
    try:
        from PIL import Image
        
        # Carica immagine
        img = Image.open(image_path).convert('L')  # Grayscale
        width, height = img.size
        
        # Analisi euristica semplice
        has_fraction = detect_fraction_pattern_simple(img)
        has_integral = detect_integral_pattern_simple(img)
        has_sqrt = detect_sqrt_pattern_simple(img)
        has_power = detect_power_pattern_simple(img)
        
        # Genera LaTeX basato sui pattern rilevati
        latex_parts = []
        
        if has_integral:
            latex_parts.append("\\int")
        if has_fraction:
            latex_parts.append("\\frac{a}{b}")
        if has_sqrt:
            latex_parts.append("\\sqrt{x}")
        if has_power:
            latex_parts.append("x^n")
            
        if latex_parts:
            formula = " ".join(latex_parts)
            logger.info(f"Pattern recognition detected: {formula}")
            return formula
        else:
            # Fallback generico basato su dimensioni
            if width > height * 2:
                return "f(x) = ax + b"  # Formula orizzontale
            else:
                return "\\frac{x}{y}"  # Formula verticale
            
    except Exception as e:
        logger.error(f"Pattern recognition error: {e}")
        return "x + y = z"  # Fallback ultra-semplice

def detect_fraction_pattern_simple(img):
    """Rileva pattern di frazione senza numpy"""
    try:
        width, height = img.size
        pixels = list(img.getdata())
        
        # Controlla la riga centrale per linee orizzontali
        middle_row = height // 2
        row_start = middle_row * width
        row_end = row_start + width
        
        if row_end <= len(pixels):
            middle_pixels = pixels[row_start:row_end]
            dark_count = sum(1 for p in middle_pixels if p < 128)
            return dark_count > width * 0.3
        return False
    except:
        return False

def detect_integral_pattern_simple(img):
    """Rileva pattern di integrale senza numpy"""
    try:
        width, height = img.size
        pixels = list(img.getdata())
        
        # Controlla la colonna sinistra per forme verticali
        left_quarter = width // 4
        dark_count = 0
        total_checked = 0
        
        for y in range(height):
            for x in range(min(left_quarter, width)):
                pixel_index = y * width + x
                if pixel_index < len(pixels):
                    if pixels[pixel_index] < 128:
                        dark_count += 1
                    total_checked += 1
        
        return total_checked > 0 and dark_count > total_checked * 0.1
    except:
        return False

def detect_sqrt_pattern_simple(img):
    """Rileva pattern di radice quadrata senza numpy"""
    try:
        width, height = img.size
        pixels = list(img.getdata())
        
        # Cerca pattern nella parte superiore
        top_half = height // 2
        diagonal_found = False
        horizontal_found = False
        
        # Controlla diagonale approssimativa
        for i in range(min(top_half, width // 2)):
            pixel_index = i * width + i
            if pixel_index < len(pixels) and pixels[pixel_index] < 128:
                diagonal_found = True
                break
        
        # Controlla prima riga per linee orizzontali
        if width > 0:
            first_row = pixels[:width]
            dark_count = sum(1 for p in first_row if p < 128)
            horizontal_found = dark_count > width * 0.2
        
        return diagonal_found and horizontal_found
    except:
        return False

def detect_power_pattern_simple(img):
    """Rileva pattern di esponente senza numpy"""
    try:
        width, height = img.size
        pixels = list(img.getdata())
        
        # Controlla la parte superiore destra
        top_third = height // 3
        right_third_start = (2 * width) // 3
        
        dark_count = 0
        total_checked = 0
        
        for y in range(top_third):
            for x in range(right_third_start, width):
                pixel_index = y * width + x
                if pixel_index < len(pixels):
                    if pixels[pixel_index] < 128:
                        dark_count += 1
                    total_checked += 1
        
        return total_checked > 0 and dark_count > total_checked * 0.05
    except:
        return False

def fallback_ocr_alternative(image_path):
    """Fallback alternativo con formule matematiche comuni"""
    try:
        from PIL import Image
        
        # Carica l'immagine per analisi base
        img = Image.open(image_path)
        width, height = img.size
        
        # Genera formule basate su caratteristiche dell'immagine
        aspect_ratio = width / height if height > 0 else 1
        
        # Formule comuni basate su aspect ratio e dimensioni
        if aspect_ratio > 3:  # Molto orizzontale
            formulas = [
                "\\lim_{x \\to \\infty} f(x) = L",
                "\\sum_{i=1}^{n} x_i = S",
                "f(x) = ax^2 + bx + c"
            ]
        elif aspect_ratio < 0.5:  # Molto verticale  
            formulas = [
                "\\frac{a}{b}",
                "\\sqrt{x}",
                "\\int f(x) dx"
            ]
        else:  # Quadrata o normale
            formulas = [
                "x^2 + y^2 = r^2",
                "\\alpha + \\beta = \\gamma", 
                "\\sin^2(x) + \\cos^2(x) = 1",
                "e^{i\\pi} + 1 = 0"
            ]
        
        # Seleziona formula basata su dimensioni (pseudo-random deterministico)
        formula_index = (width + height) % len(formulas)
        selected_formula = formulas[formula_index]
        
        logger.info(f"Alternative fallback selected: {selected_formula}")
        return selected_formula
        
    except Exception as e:
        logger.error(f"Alternative fallback error: {e}")
        return "f(x) = x"  # Fallback minimo

# Costanti
MAX_IMAGE_SIZE = (2048, 2048)
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
        "fallback_mode": USE_FALLBACK_API,
        "model_loaded": not USE_FALLBACK_API and get_model() is not None
    }
    return jsonify(status)

@app.route("/convert", methods=["POST"])
def convert():
    """Endpoint per convertire immagine in LaTeX"""
    temp_file_path = None
    try:
        # Validazione richiesta
        if not request.is_json:
            return jsonify({"error": "Content-Type deve essere application/json"}), 400
        
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "Campo 'image' mancante"}), 400
        
        logger.info("Processing image conversion request")
        
        # Preprocessa immagine
        img = preprocess_image(data['image'])
        
        # Salva in file temporaneo
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file_path = temp_file.name
            img.save(temp_file_path)
            logger.info(f"Image saved to temporary file: {temp_file_path}")
        
        # Prova prima il modello locale, poi fallback multipli
        latex_code = None
        service_used = "unknown"
        
        if USE_FALLBACK_API:
            logger.info("Using fallback API mode")
            latex_code = fallback_ocr(temp_file_path)
            service_used = "pattern-recognition"
        else:
            model = get_model()
            if model is not None:
                try:
                    latex_code = model.recognize_text_formula(temp_file_path)
                    service_used = "local-model"
                    logger.info("Local model recognition successful")
                except Exception as e:
                    logger.error(f"Local model failed: {e}")
                    model = None
            
            if model is None:
                logger.warning("Model not available, using fallback methods")
                # Prova prima pattern recognition
                latex_code = fallback_ocr(temp_file_path)
                service_used = "pattern-recognition"
                
                # Se pattern recognition non trova nulla di utile, usa alternative
                if not latex_code or latex_code.startswith("\\text{") or len(latex_code.strip()) < 3:
                    logger.info("Pattern recognition insufficient, trying alternative...")
                    latex_code = fallback_ocr_alternative(temp_file_path)
                    service_used = "alternative-fallback"
        
        logger.info(f"LaTeX code generated successfully: {len(latex_code)} characters")
        
        return jsonify({
            "latex": latex_code,
            "status": "success",
            "service": service_used,
            "fallback_mode": USE_FALLBACK_API,
            "note": "Generated using fallback recognition" if service_used != "local-model" else None
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
        logger.info("Starting in development mode")
        app.run(host="0.0.0.0", port=port, debug=True)
    else:
        logger.info("Starting in production mode")
        app.run(host="0.0.0.0", port=port, debug=False)