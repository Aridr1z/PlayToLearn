#!/bin/bash

echo "============================================"
echo "Game Dialog Capturer - Setup"
echo "============================================"
echo ""

echo "Step 1: Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo ""
echo "Step 2: Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Step 3: Checking Tesseract installation..."
if ! command -v tesseract &> /dev/null; then
    echo ""
    echo "WARNING: Tesseract not found!"
    echo ""
    echo "Mac users, install with:"
    echo "  brew install tesseract"
    echo ""
    echo "Linux users (Ubuntu/Debian), install with:"
    echo "  sudo apt-get install tesseract-ocr"
else
    echo "OK: Tesseract found at $(which tesseract)"
fi

echo ""
echo "============================================"
echo "Setup complete!"
echo "============================================"
echo ""
echo "To start using:"
echo "  1. Run: source venv/bin/activate"
echo "  2. Run: python game_dialog_capturer.py"
echo "  3. Press Ctrl+Shift+D to open menu"
echo ""
