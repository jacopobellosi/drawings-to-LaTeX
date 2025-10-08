from flask import Flask,render_template,  request, jsonify
import base64
import re
import io
import os
from io import BytesIO
from PIL import Image
from pix2text import Pix2Text

# importa qui la tua libreria per immagine -> LaTeX
# esempio: from mylib import image_to_latex

app = Flask(__name__)
# lazy init of Pix2Text to avoid long startup during container start
p2t = None

def get_p2t():
    global p2t
    if p2t is None:
        p2t = Pix2Text.from_config()
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

@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json()
    img = preprocess_image(data['image'])
    # Save to a temp path (Cloud Run has writable /tmp)
    debug_path = os.path.join("/tmp", "debug_input.png")
    img.save(debug_path)
    print("Image received and decoded.")
    # Initialize Pix2Text on first use
    model = get_p2t()
    latex_code = model.recognize_text_formula(debug_path)
    print("LaTeX code generated:", latex_code)
    return jsonify({"latex": latex_code})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

from PIL import Image
import io, base64

