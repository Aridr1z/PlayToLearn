"""
Screenshot Module - Captura pantalla completa o región
"""

from PIL import ImageGrab
import logging

logger = logging.getLogger(__name__)

class ScreenshotCapture:
    """Captura screenshots de la pantalla o una región específica"""
    
    @staticmethod
    def capture_full_screen():
        """
        Captura toda la pantalla
        
        Returns:
            PIL.Image: Imagen capturada
        """
        try:
            screenshot = ImageGrab.grab()
            logger.info("Pantalla completa capturada")
            return screenshot
        except Exception as e:
            logger.error(f"Error capturando pantalla completa: {e}")
            return None
    
    @staticmethod
    def capture_region(bbox):
        """
        Captura una región específica de la pantalla
        
        Args:
            bbox: Tupla (x1, y1, x2, y2) con coordenadas
            
        Returns:
            PIL.Image: Imagen capturada
        """
        if not bbox or len(bbox) != 4:
            logger.error("Coordenadas inválidas")
            return None
        
        try:
            screenshot = ImageGrab.grab(bbox=bbox)
            logger.info(f"Región capturada: {bbox}")
            return screenshot
        except Exception as e:
            logger.error(f"Error capturando región: {e}")
            return None
    
    @staticmethod
    def normalize_bbox(x1, y1, x2, y2):
        """
        Normaliza las coordenadas del rectángulo
        
        Args:
            x1, y1, x2, y2: Coordenadas
            
        Returns:
            tuple: Coordenadas normalizadas (izq, arriba, der, abajo)
        """
        return (
            min(x1, x2),
            min(y1, y2),
            max(x1, x2),
            max(y1, y2)
        )
