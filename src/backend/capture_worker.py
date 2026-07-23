"""
Capture Worker - Hilo productor

Captura screenshots a ritmo constante y los deposita en una cola.
No hace OCR ni procesamiento: su unico trabajo es no perder frames.
Si la cola se llena (el consumidor va lento), descarta el frame mas
viejo para conservar siempre los mas recientes.
"""

import threading
import time
import logging
from queue import Full, Empty

logger = logging.getLogger(__name__)


class CaptureWorker(threading.Thread):
    """Hilo que captura la pantalla periodicamente y la encola"""

    def __init__(self, screenshot_capture, region, frame_queue, interval=0.4):
        """
        Args:
            screenshot_capture: Instancia de ScreenshotCapture
            region: Tupla (x1, y1, x2, y2) de la region a capturar
            frame_queue: Cola donde depositar los frames
            interval: Segundos entre capturas
        """
        super().__init__(daemon=True, name="CaptureWorker")
        self.screenshot_capture = screenshot_capture
        self.region = region
        self.frame_queue = frame_queue
        self.interval = interval

        self._stop_event = threading.Event()
        self.frames_captured = 0
        self.frames_dropped = 0

    def stop(self):
        """Solicita la detencion del hilo"""
        self._stop_event.set()

    def run(self):
        """Bucle principal del productor"""
        logger.info(f"CaptureWorker iniciado (intervalo: {self.interval}s)")

        while not self._stop_event.is_set():
            cycle_start = time.time()

            try:
                frame = self.screenshot_capture.capture_region(self.region)

                if frame is not None:
                    self._enqueue(frame)
                    self.frames_captured += 1

            except Exception as e:
                logger.error(f"Error capturando frame: {e}")

            # Dormir el resto del intervalo (descontando lo que tardo la captura)
            elapsed = time.time() - cycle_start
            remaining = self.interval - elapsed
            if remaining > 0:
                self._stop_event.wait(remaining)

        logger.info(
            f"CaptureWorker detenido "
            f"(capturados: {self.frames_captured}, descartados: {self.frames_dropped})"
        )

    def _enqueue(self, frame):
        """
        Deposita un frame en la cola.
        Si esta llena, descarta el mas viejo para dar espacio al nuevo.
        """
        try:
            self.frame_queue.put_nowait(frame)
        except Full:
            try:
                self.frame_queue.get_nowait()  # Descartar el mas viejo
                self.frames_dropped += 1
                self.frame_queue.put_nowait(frame)
                logger.debug("Cola llena: frame antiguo descartado")
            except (Empty, Full):
                self.frames_dropped += 1

    def get_stats(self):
        """Retorna estadisticas del productor"""
        return {
            "captured": self.frames_captured,
            "dropped": self.frames_dropped,
            "queue_size": self.frame_queue.qsize(),
        }
    
    