"""Backend module"""

from .ocr_engine import OCREngine
from .dialog_manager import DialogManager
from .screenshot import ScreenshotCapture

__all__ = ['OCREngine', 'DialogManager', 'ScreenshotCapture']
