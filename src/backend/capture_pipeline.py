"""
Capture Pipeline - Orquestador

Une el productor (CaptureWorker), la cola y el consumidor
(DialogProcessor) en una sola interfaz simple.

La capa de interfaz solo necesita: start(), stop() y get_stats().
"""

import logging
from queue import Queue

from .capture_worker import CaptureWorker
from .dialog_processor import DialogProcessor

logger = logging.getLogger(__name__)


class CapturePipeline:
    """Coordina la captura y el procesamiento de dialogos"""

    QUEUE_MAXSIZE = 10       # Frames en espera antes de descartar los viejos
    CAPTURE_INTERVAL = 0.4   # Segundos entre capturas de pantalla

    def __init__(self, screenshot_capture, ocr_engine):
        """
        Args:
            screenshot_capture: Instancia de ScreenshotCapture
            ocr_engine: Instancia de OCREngine
        """
        self.screenshot_capture = screenshot_capture
        self.ocr_engine = ocr_engine

        self._frame_queue = None
        self._producer = None
        self._consumer = None
        self._running = False

    @property
    def is_running(self):
        """Indica si el pipeline esta activo"""
        return self._running

    def start(self, region, on_dialog):
        """
        Inicia la captura sobre una region.

        Args:
            region: Tupla (x1, y1, x2, y2)
            on_dialog: Callback(speaker, texto) por cada dialogo detectado
        """
        if self._running:
            logger.warning("El pipeline ya esta corriendo")
            return

        self._frame_queue = Queue(maxsize=self.QUEUE_MAXSIZE)

        self._consumer = DialogProcessor(
            ocr_engine=self.ocr_engine,
            frame_queue=self._frame_queue,
            on_dialog=on_dialog,
        )

        self._producer = CaptureWorker(
            screenshot_capture=self.screenshot_capture,
            region=region,
            frame_queue=self._frame_queue,
            interval=self.CAPTURE_INTERVAL,
        )

        # El consumidor primero, para que no se pierdan los primeros frames
        self._consumer.start()
        self._producer.start()
        self._running = True

        logger.info("Pipeline de captura iniciado")

    def stop(self, timeout=3.0):
        """
        Detiene la captura de forma ordenada.
        Primero el productor (deja de entrar trabajo), luego el consumidor
        (termina lo que quedo en la cola).
        """
        if not self._running:
            return

        logger.info("Deteniendo pipeline...")

        if self._producer:
            self._producer.stop()
            self._producer.join(timeout=timeout)

        if self._consumer:
            self._consumer.stop()
            self._consumer.join(timeout=timeout)

        self._running = False
        logger.info("Pipeline detenido")

    def get_stats(self):
        """Retorna estadisticas combinadas del pipeline"""
        stats = {
            "captured": 0,
            "dropped": 0,
            "processed": 0,
            "emitted": 0,
            "queue_size": 0,
        }

        if self._producer:
            stats.update(self._producer.get_stats())
        if self._consumer:
            stats.update(self._consumer.get_stats())

        return stats