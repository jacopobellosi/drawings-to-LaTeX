# drawings-to-LaTeX

Small Flask app that converts a hand-drawn/math image to LaTeX using Pix2Text.

This repository contains a minimal web UI and a backend API implemented in `app.py`.

## What I added
- `Dockerfile` - builds a small image based on `python:3.11-slim` and installs requirements
- `.dockerignore` - keeps the image small by excluding common files
- `README.md` - this file

## Build and run with Docker (PowerShell)

Build the image (replace `jacopobellosi/drawings-to-latex` with your image name):

```powershell
docker build -t jacopobellosi/drawings-to-latex:latest .
```

Run the container locally and map port 5000:

```powershell
docker run --rm -p 5000:5000 jacopobellosi/drawings-to-latex:latest
```

Open http://localhost:5000 in your browser.

## Environment / Configuration
The app reads the `PORT` environment variable (defaults to `5000`). To change it when running with docker:

```powershell
docker run --rm -p 8080:8080 -e PORT=8080 jacopobellosi/drawings-to-latex:latest
```

## Notes & recommendations
- The repository uses `Pix2Text` (declared in `requirements.txt`). Make sure that package is available and installs cleanly (it may have extra native deps). If `Pix2Text` requires extra system libraries, add them to the `apt-get install` line in the `Dockerfile`.
- For production use, consider replacing the Flask development server with a WSGI server like `gunicorn` (e.g. `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`).
- The `Dockerfile` installs minimal build dependencies needed by Pillow. If you see build failures during pip install, add the required system packages shown in the error message.

- Important note — run locally

	This project is intended to be run locally. I tried running the same workflow through several external APIs and hosted services, but none produced the same quality or fidelity as executing the model and preprocessing pipeline locally. Approaches I tested include:

	- Hosted Pix2Text-like inference endpoints (remote containers or hosted model APIs). Outputs were inconsistent and often lower-quality compared with the local pipeline.
	- General cloud OCR / handwriting recognition APIs. These typically return plain text and struggle with mathematical notation, layout, and correct LaTeX formatting.
	- Commercial or third-party math OCR services that advertise LaTeX output. Some returned partial LaTeX but with missing symbols, incorrect formatting, or unstable results across similar inputs; others required paid access or different preprocessing steps.

	Common issues observed: mis-recognised math symbols, incorrect LaTeX markup, lost equation structure for multi-line inputs, and inconsistent handling of hand-drawn strokes. The differences are likely due to model/version mismatches, variations in preprocessing (resizing, binarization, deskewing), or the hosted services not being tuned on the same hand-drawn datasets.

	For consistent and reproducible results, run the app locally (see the Docker and local run instructions above). If you want, I can add a short reproducibility section showing the exact local commands I used and a small side-by-side example comparing local output with one or two remote services.



## What I didn't change
- I left `app.py` and `templates/index.html` unchanged. The server currently runs in debug mode — switch that off for production.

## License
See `LICENSE` in the repo root.
