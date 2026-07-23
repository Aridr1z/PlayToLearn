"""
Frame Filter - Descarta frames repetidos antes del OCR

El OCR cuesta alrededor de medio segundo por frame, mientras que
comparar dos miniaturas cuesta unos 2 milisegundos.

Este filtro compara cada frame con el anterior y avisa si la pantalla
cambio. Si no cambio, no hace falta volver a leerla: el texto es el
mismo. Asi el procesador no se atrasa ni acumula frames viejos.

Como se compara
---------------
Se reduce el frame a una miniatura en escala de grises y se cuentan
los pixeles que cambiaron de forma apreciable. Se cuentan pixeles en
lugar de promediar porque el texto ocupa una parte pequena de la
imagen: un promedio diluye la diferencia y confundiria dos dialogos
distintos con el mismo.

Valores medidos sobre una region tipica de subtitulos (759x273),
contando pixeles sobre una miniatura de 128x48:

    imagen identica ................   0 pixeles
    ruido de compresion o video ....   0 pixeles
    una sola letra distinta ........ 0-1 pixeles
    una palabra mas (typewriter) ...  16 pixeles
    dialogo completamente distinto .  52 pixeles

El umbral de 3 pixeles ignora el ruido y las diferencias de una sola
letra (que casi siempre son errores del OCR sobre el mismo texto) y
detecta cualquier cambio real de palabra en adelante. Ante la duda el
filtro responde "cambio", porque gastar un OCR de mas es preferible a
perderse un dialogo.
"""

import logging
from PIL import Image

logger = logging.getLogger(__name__)


class FrameFilter:
    """Detecta si la imagen cambio respecto a la anterior"""

    THUMB_SIZE = (128, 48)      # Miniatura para comparar
    PIXEL_DELTA = 20            # Cuanto debe variar un pixel para contar
    MIN_CHANGED_PIXELS = 3      # Pixeles distintos para considerar que cambio

    def __init__(self, min_changed_pixels=None):
        self._last_thumb = None
        self.min_changed_pixels = (
            min_changed_pixels
            if min_changed_pixels is not None
            else self.MIN_CHANGED_PIXELS
        )
        self.skipped = 0
        self.analyzed = 0

    def has_changed(self, frame):
        """
        Indica si el frame es distinto al anterior.

        Args:
            frame: Imagen PIL

        Returns:
            bool: True si cambio (hay que hacer OCR), False si es igual
        """
        try:
            thumb = self._thumbnail(frame)
        except Exception as e:
            logger.debug(f"No se pudo comparar el frame: {e}")
            return True  # Ante la duda, procesarlo

        if self._last_thumb is None:
            self._last_thumb = thumb
            self.analyzed += 1
            return True

        changed_pixels = self._count_changed(self._last_thumb, thumb)
        self._last_thumb = thumb

        if changed_pixels < self.min_changed_pixels:
            self.skipped += 1
            return False

        self.analyzed += 1
        return True

    def reset(self):
        """Olvida el frame anterior"""
        self._last_thumb = None

    def _thumbnail(self, frame):
        """Convierte el frame en una miniatura en escala de grises"""
        small = frame.convert('L').resize(
            self.THUMB_SIZE, Image.Resampling.BILINEAR
        )
        return small.tobytes()

    def _count_changed(self, a, b):
        """Cuenta cuantos pixeles cambiaron de forma apreciable"""
        if len(a) != len(b):
            return self.min_changed_pixels  # Tamano distinto: tratar como cambio

        delta = self.PIXEL_DELTA
        changed = 0
        for x, y in zip(a, b):
            if abs(x - y) >= delta:
                changed += 1
                if changed >= self.min_changed_pixels:
                    return changed  # Ya alcanza, no hace falta seguir
        return changed

    def get_stats(self):
        """Retorna cuantos frames se ahorraron"""
        total = self.skipped + self.analyzed
        return {
            "frames_skipped": self.skipped,
            "frames_analyzed": self.analyzed,
            "skip_ratio": (self.skipped / total) if total else 0.0,
        }