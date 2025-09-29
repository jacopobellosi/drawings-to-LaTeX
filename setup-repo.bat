@echo off
echo ========================================
echo   LaTeX OCR - Repository Setup
echo ========================================
echo.

echo [1/5] Inizializzando repository Git...
git init
if %errorlevel% neq 0 (
    echo ERRORE: Git non trovato. Installa Git prima di continuare.
    pause
    exit /b 1
)

echo [2/5] Aggiungendo file al repository...
git add .

echo [3/5] Creando commit iniziale...
git commit -m "Initial commit: LaTeX OCR production ready app"

echo [4/5] Setup completato!
echo.
echo PROSSIMI PASSI:
echo.
echo 1. Crea repository su GitHub:
echo    https://github.com/new
echo.
echo 2. Collega repository remota:
echo    git remote add origin https://github.com/TUO-USERNAME/NOME-REPO.git
echo.
echo 3. Push del codice:
echo    git push -u origin main
echo.
echo 4. Deploy su Railway:
echo    https://railway.app
echo    - "Deploy from GitHub repo"
echo    - Seleziona la tua repository
echo    - Aggiungi SECRET_KEY nelle variabili d'ambiente
echo.
echo [5/5] Per maggiori dettagli, leggi DEPLOYMENT.md
echo.

pause
