"""
OCR Engine - Extrae texto de imágenes usando Tesseract con mejoras
"""

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import logging
import re
import nltk
from nltk.corpus import words
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

# Descargar corpus de palabras la primera vez
try:
    words.words()
except LookupError:
    logger.info("Descargando diccionario NLTK...")
    nltk.download('words', quiet=True)

class OCREngine:
    def __init__(self):
        self.language = 'eng+spa'
        self.initialized = self._check_tesseract()
        self.confidence_threshold = 70
        self.min_text_length = 8
        self.valid_words = set(words.words())  # Cargar diccionario
        self.min_valid_ratio = 0.60  # Bajado a 60% (era 70%)
        self.known_speakers = set()  # Speakers ya detectados en la sesion
    
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
        Extrae texto de una imagen PIL con pre y post-procesamiento
        
        Args:
            image: Imagen PIL o ruta a archivo
            
        Returns:
            str: Texto extraído y limpio
        """
        if not self.initialized:
            logger.error("Tesseract no está disponible")
            return ""
        
        try:
            if isinstance(image, str):
                image = Image.open(image)
            
            # Pre-procesamiento: mejorar imagen
            processed_image = self._preprocess_image(image)
            
            # Extraer texto con Tesseract
            text = pytesseract.image_to_string(processed_image, lang=self.language)
            
            # Post-procesamiento: limpiar texto
            text = self._clean_text(text)
            
            # Validar contexto
            if not self._is_valid_text(text):
                logger.warning(f"Texto rechazado por validación: {text[:50]}")
                return ""
            
            return text.strip()
        
        except Exception as e:
            logger.error(f"Error durante OCR: {e}")
            return ""
    
    def _preprocess_image(self, image):
        """
        Pre-procesa la imagen para mejorar OCR
        
        Args:
            image: Imagen PIL
            
        Returns:
            Image: Imagen mejorada
        """
        try:
            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Escalar imagen 1.5x (texto más grande = mejor OCR)
            width, height = image.size
            image = image.resize((int(width * 1.5), int(height * 1.5)), Image.Resampling.LANCZOS)
            
            # Convertir a escala de grises
            image = image.convert('L')
            
            # Aumentar contraste (mejora legibilidad)
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # Aumentar nitidez
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Reducir ruido (filtro suave)
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            logger.debug("Imagen pre-procesada correctamente")
            return image
        
        except Exception as e:
            logger.error(f"Error en pre-procesamiento: {e}")
            return image
    
    def _clean_text(self, text):
        """
        Limpia y normaliza el texto extraído por OCR
        
        Args:
            text: Texto crudo del OCR
            
        Returns:
            str: Texto limpio
        """
        # Remover saltos de línea múltiples
        text = re.sub(r'\n\s*\n', ' ', text)
        
        # Convertir saltos de línea simples a espacios
        text = text.replace('\n', ' ')
        
        # Remover espacios múltiples
        text = re.sub(r' +', ' ', text)
        
        # Remover caracteres especiales problemáticos
        # Mantener: letras, números, puntuación básica, guiones, apóstrofes
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\'\"\-\(\)]', '', text)
        
        # Limpiar espacios alrededor de puntuación
        text = re.sub(r'\s+([.,!?;:\)])', r'\1', text)
        text = re.sub(r'([\(\[])\s+', r'\1', text)
        
        # Remover números al inicio (típico error de OCR)
        text = re.sub(r'^[\d\s]+', '', text)
        
        # Remover espacios al inicio y final
        text = text.strip()
        
        return text
    
    def _is_valid_text(self, text):
        """
        Valida si el texto tiene sentido (contexto)
        
        Args:
            text: Texto a validar
            
        Returns:
            bool: True si texto es válido, False si es basura
        """
        if not text or len(text) < self.min_text_length:
            return False
        
        # Contar caracteres especiales/basura
        special_count = len(re.findall(r'[^a-zA-Z0-9\s\.\,\!\?\;\:\'\"\-\(\)]', text))
        special_ratio = special_count / len(text)
        
        # Si más del 20% son caracteres especiales = basura (más estricto)
        if special_ratio > 0.20:
            logger.warning(f"Texto rechazado: {special_ratio*100:.1f}% caracteres especiales")
            return False
        
        # Validar con diccionario
        if not self._validate_with_dictionary(text):
            return False
        
        # Contar palabras que parecen errores (números mezclados con letras)
        error_words = len(re.findall(r'\w*\d\w*[a-z]\w*|\w*[a-z]\w*\d\w*', text, re.IGNORECASE))
        total_words = len(text.split())
        
        if total_words > 0:
            error_ratio = error_words / total_words
            if error_ratio > 0.50:  # Si más del 50% de palabras tienen números raros
                logger.warning(f"Texto rechazado: {error_ratio*100:.1f}% palabras con formato raro")
                return False
        
        return True
    
    def _validate_with_dictionary(self, text):
        """
        Valida que el texto contenga palabras reales del diccionario
        Ignora nombres propios (mayúsculas) y palabras muy cortas
        
        Args:
            text: Texto a validar
            
        Returns:
            bool: True si mayoría de palabras son válidas
        """
        # Extraer palabras conservando mayusculas/minusculas
        raw_words = re.findall(r'[A-Za-z]+', text)
        
        if not raw_words:
            return False
        
        # Excluir palabras completamente en MAYUSCULAS (probables nombres propios
        # de personajes: EDWARD, KENWAY) para no penalizarlas injustamente
        words_in_text = [w.lower() for w in raw_words if not (w.isupper() and len(w) >= 2)]
        
        # Si todo eran nombres propios, aceptar (no hay nada que validar)
        if not words_in_text:
            return True
        
        # Filtrar palabras válidas
        # - Debe estar en diccionario
        # - O ser abreviatura común (2-3 caracteres)
        valid_words_list = []
        
        for word in words_in_text:
            # Palabras muy cortas (a, i, he) = pueden ser válidas aunque sean cortas
            if len(word) <= 2:
                if word in self.valid_words:
                    valid_words_list.append(word)
            # Palabras normales
            elif word in self.valid_words:
                valid_words_list.append(word)
        
        # Calcular ratio de palabras válidas
        if not words_in_text:
            return False
            
        valid_ratio = len(valid_words_list) / len(words_in_text)
        
        # Si menos del 60% de palabras son válidas = probablemente basura
        if valid_ratio < self.min_valid_ratio:
            logger.warning(f"Texto rechazado: solo {valid_ratio*100:.1f}% palabras válidas")
            return False
        
        logger.debug(f"Texto validado: {valid_ratio*100:.1f}% palabras válidas")
        return True
    
    def extract_text_with_confidence(self, image):
        """
        Extrae texto con nivel de confianza y filtra por umbral
        
        Args:
            image: Imagen PIL
            
        Returns:
            tuple: (texto_filtrado, confianza_promedio)
        """
        if not self.initialized:
            return "", 0
        
        try:
            if isinstance(image, str):
                image = Image.open(image)
            
            # Pre-procesar imagen
            processed_image = self._preprocess_image(image)
            
            # Obtener datos con confianza
            data = pytesseract.image_to_data(
                processed_image,
                lang=self.language,
                output_type=pytesseract.Output.DICT
            )
            
            text_parts = []
            confidences = []
            
            # Solo agregar palabras con confianza > threshold
            for i, word in enumerate(data['text']):
                confidence = int(data['conf'][i])
                
                if word.strip() and confidence > self.confidence_threshold:
                    text_parts.append(word)
                    confidences.append(confidence)
            
            # Limpiar texto combinado
            full_text = ' '.join(text_parts)
            full_text = self._clean_text(full_text)
            
            # Calcular confianza promedio
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            logger.info(f"OCR con confianza: {avg_confidence:.1f}%")
            
            return full_text, avg_confidence
        
        except Exception as e:
            logger.error(f"Error durante OCR con confianza: {e}")
            return "", 0
    
    def split_speaker_and_text(self, text):
        """
        Separa el nombre del personaje (en MAYUSCULAS) del dialogo.
        Tolera ruido OCR antes del nombre: 'J EDWARD KENWAY Most likely...'
        Recuerda speakers ya detectados para reconocerlos mas rapido.
        
        Args:
            text: Texto completo capturado
            
        Returns:
            tuple: (speaker, dialogo) - speaker es None si no se detecto
        """
        # 1) Buscar speakers ya conocidos dentro del texto
        # (maneja ruido raro alrededor del nombre)
        for known in sorted(self.known_speakers, key=len, reverse=True):
            idx = text.find(known)
            if idx != -1:
                rest = text[idx + len(known):].strip(' :.-')
                rest_letters = re.sub(r'[^A-Za-z]', '', rest)
                if rest_letters and not rest_letters.isupper():
                    logger.debug(f"Speaker conocido encontrado: {known}")
                    return known, rest
        
        # 2) Escanear tokens: saltar ruido corto, buscar secuencia en MAYUSCULAS
        tokens = text.split()
        i = 0
        examined = 0
        
        while i < len(tokens) and examined < 10:
            examined += 1
            letters = re.sub(r'[^A-Za-z]', '', tokens[i])
            
            is_caps = letters and letters.isupper() and len(letters) >= 2
            
            if is_caps:
                # Construir secuencia de palabras en MAYUSCULAS (max 4)
                j = i
                seq = []
                total_letters = 0
                while j < len(tokens) and len(seq) < 4:
                    l2 = re.sub(r'[^A-Za-z]', '', tokens[j])
                    if l2 and l2.isupper() and len(l2) >= 2:
                        seq.append(tokens[j])
                        total_letters += len(l2)
                        j += 1
                    else:
                        break
                
                # Secuencia valida: suma de letras >= 4 (evita basura como 'SA')
                # y debe quedar dialogo en minusculas/mixto despues
                if total_letters >= 4 and j < len(tokens):
                    rest = ' '.join(tokens[j:])
                    rest_letters = re.sub(r'[^A-Za-z]', '', rest)
                    if rest_letters and not rest_letters.isupper():
                        speaker = ' '.join(seq).strip(' :.-')
                        self.known_speakers.add(speaker)
                        logger.debug(f"Speaker detectado: {speaker}")
                        return speaker, rest
                
                # Secuencia invalida (ej. 'SA', 'SOK'): saltarla y seguir buscando
                i = j
            else:
                # Token de ruido: solo saltar si es corto (<= 3 letras)
                if len(letters) <= 3:
                    i += 1
                else:
                    # Palabra normal larga: aqui empieza el dialogo, no hay speaker
                    break
        
        return None, text
    
    def is_similar(self, text1, text2, threshold=0.80):
        """
        Compara dos textos con fuzzy matching (similitud de caracteres)
        Atrapa errores OCR tipo 'vvork' vs 'work'
        
        Args:
            text1: Primer texto
            text2: Segundo texto
            threshold: Similitud minima para considerarlos iguales (0.80 = 80%)
            
        Returns:
            bool: True si los textos son esencialmente el mismo
        """
        if not text1 or not text2:
            return False
        
        ratio = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        return ratio >= threshold
    
    def is_duplicate_of_recent(self, text, recent_texts, threshold=0.80):
        """
        Verifica si el texto es similar a alguno del historial reciente
        
        Args:
            text: Texto nuevo
            recent_texts: Lista de textos recientes
            threshold: Similitud minima
            
        Returns:
            bool: True si es duplicado de alguno reciente
        """
        for recent in recent_texts:
            if self.is_similar(text, recent, threshold):
                logger.debug(f"Duplicado detectado contra historial: {text[:40]}")
                return True
        return False
    
    def detect_real_change(self, text1, text2):
        """
        Detecta si hay cambio real entre dos textos (no solo ruido OCR)
        
        Args:
            text1: Texto anterior
            text2: Texto nuevo
            
        Returns:
            bool: True si es cambio significativo
        """
        if not text1 or not text2:
            return True
        
        # Fuzzy matching: si son 80%+ similares = mismo texto con ruido OCR
        if self.is_similar(text1, text2, threshold=0.80):
            logger.debug("Cambio ignorado: textos muy similares (ruido OCR)")
            return False
        
        return True