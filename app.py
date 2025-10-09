from flask import Flask, render_template, request, jsonify
import base64
import re
import io
import os
from io import BytesIO
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variable for lazy loading
p2t = None

def get_p2t():
    global p2t
    if p2t is None:
        try:
            logger.info("Loading Pix2Text model...")
            from pix2text import Pix2Text
            p2t = Pix2Text.from_config()
            logger.info("Pix2Text model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Pix2Text model: {e}")
            raise
    return p2t

def preprocess_image(data_url):
    # Rimuove il prefisso "data:image/png;base64,"
    header, encoded = data_url.split(",", 1)
    img = Image.open(io.BytesIO(base64.b64decode(encoded))).convert("RGBA")
    
    # Crea un'immagine con sfondo bianco
    white_bg = Image.new("RGB", img.size, (255, 255, 255))
    
    # Incolla l'immagine originale sullo sfondo bianco
    white_bg.paste(img, mask=img.split()[-1])  # Usa il canale alpha come maschera
    
    # Trova dimensioni multiple di 32
    new_w = (white_bg.width  + 31) // 32 * 32
    new_h = (white_bg.height + 31) // 32 * 32

    # Ridimensiona
    white_bg = white_bg.resize((new_w, new_h), Image.LANCZOS)

    return white_bg


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    """Health check endpoint for Cloud Run"""
    return jsonify({"status": "healthy"}), 200

@app.route("/convert", methods=["POST"])
def convert():
    try:
        logger.info("Received conversion request")
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({"error": "No image data provided"}), 400
            
        img = preprocess_image(data['image'])
        
        # Save to a temp path (Cloud Run has writable /tmp)
        debug_path = os.path.join("/tmp", "debug_input.png")
        img.save(debug_path)
        logger.info("Image preprocessed and saved")
        
        # Initialize Pix2Text on first use
        model = get_p2t()
        latex_code = model.recognize_text_formula(debug_path)
        logger.info(f"LaTeX code generated: {latex_code}")
        
        # Clean up temp file
        try:
            os.remove(debug_path)
        except:
            pass
            
        return jsonify({"latex": latex_code})
        
    except Exception as e:
        logger.error(f"Error in conversion: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)  # Disable debug in production

