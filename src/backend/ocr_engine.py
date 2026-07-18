"""
OCR Engine - Extrae texto de imágenes usando Tesseract
"""

import pytesseract
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class OCREngine:
    def __init__(self):
        self.language = 'eng+spa'
        self.initialized = self._check_tesseract()
    
    def _check_tesseract(self):
        """Verifica si Tesseract está disponible"""
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR inicializado correctamente")
            return True
        except Exception as e:
            logger.error(f"Error al inicializar Tesseract: {e}")
            return False
    
    def extract_text(self, image):
        """
        Extrae texto de una imagen PIL
        
        Args:
            image: Imagen PIL o ruta a archivo
            
        Returns:
            str: Texto extraído
        """
        if not self.initialized:
            logger.error("Tesseract no está disponible")
            return ""
        
        try:
            if isinstance(image, str):
                image = Image.open(image)
            
            text = pytesseract.image_to_string(image, lang=self.language)
            return text.strip()
        
        except Exception as e:
            logger.error(f"Error durante OCR: {e}")
            return ""
    
    def extract_text_with_confidence(self, image):
        """
        Extrae texto con nivel de confianza
        
        Args:
            image: Imagen PIL
            
        Returns:
            tuple: (texto, confianza)
        """
        if not self.initialized:
            return "", 0
        
        try:
            if isinstance(image, str):
                image = Image.open(image)
            
            data = pytesseract.image_to_data(image, lang=self.language, output_type=pytesseract.Output.DICT)
            
            text_parts = []
            confidences = []
            
            for i, text in enumerate(data['text']):
                if text.strip():
                    text_parts.append(text)
                    confidences.append(int(data['conf'][i]))
            
            full_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return full_text, avg_confidence
        
        except Exception as e:
            logger.error(f"Error durante OCR con confianza: {e}")
            return "", 0
