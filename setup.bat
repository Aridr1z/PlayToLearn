@echo off
echo ============================================
echo Game Dialog Capturer - Setup
echo ============================================
echo.

echo Step 1: Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo Step 2: Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Step 3: Checking Tesseract installation...
where tesseract >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Tesseract not found in PATH
    echo Please download from: https://github.com/UB-Mannheim/tesseract/wiki
    echo After installation, add to PATH or update pytesseract_cmd in the script
) else (
    echo OK: Tesseract found!
)

echo.
echo ============================================
echo Setup complete!
echo ============================================
echo.
echo To start using:
echo   1. Run: venv\Scripts\activate
echo   2. Run: python game_dialog_capturer.py
echo   3. Press Ctrl+Shift+D to open menu
echo.
pause
