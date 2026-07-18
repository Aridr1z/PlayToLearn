"""
Main entry point - Inicia la aplicación
"""

import sys
from pathlib import Path

# Agregar la carpeta src al path
sys.path.insert(0, str(Path(__file__).parent))

from frontend.gui import run_application

if __name__ == "__main__":
    run_application()