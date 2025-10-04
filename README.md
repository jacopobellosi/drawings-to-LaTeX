# drawings-to-LaTeX

Small Flask app that converts a hand-drawn/math image to LaTeX using Pix2Text.

This repository contains a minimal web UI and a backend API implemented in `app.py`.

## What I added
- `Dockerfile` - builds a small image based on `python:3.11-slim` and installs requirements
- `.dockerignore` - keeps the image small by excluding common files
- `README.md` - this file

## Build and run with Docker (PowerShell)

Build the image (replace `yourname/drawings-to-latex` with your image name):

```powershell
docker build -t yourname/drawings-to-latex:latest .
```

Run the container locally and map port 5000:

```powershell
docker run --rm -p 5000:5000 yourname/drawings-to-latex:latest
```

Open http://localhost:5000 in your browser.

## Environment / Configuration
The app reads the `PORT` environment variable (defaults to `5000`). To change it when running with docker:

```powershell
docker run --rm -p 8080:8080 -e PORT=8080 yourname/drawings-to-latex:latest
```

## Notes & recommendations
- The repository uses `Pix2Text` (declared in `requirements.txt`). Make sure that package is available and installs cleanly (it may have extra native deps). If `Pix2Text` requires extra system libraries, add them to the `apt-get install` line in the `Dockerfile`.
- For production use, consider replacing the Flask development server with a WSGI server like `gunicorn` (e.g. `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`).
- The `Dockerfile` installs minimal build dependencies needed by Pillow. If you see build failures during pip install, add the required system packages shown in the error message.

## Publish to Docker Hub

```powershell
docker tag yourname/drawings-to-latex:latest yourdockerhubusername/drawings-to-latex:latest; docker push yourdockerhubusername/drawings-to-latex:latest
```

## What I didn't change
- I left `app.py` and `templates/index.html` unchanged. The server currently runs in debug mode — switch that off for production.

## License
See `LICENSE` in the repo root.
