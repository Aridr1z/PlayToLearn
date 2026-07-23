"""
Dialog Processor - Hilo consumidor

Saca frames de la cola, les aplica OCR y decide cuales textos son
dialogos reales que vale la pena guardar.

Reglas de decision:
  - Estabilizacion: un texto se guarda cuando aparece en 2 lecturas
    seguidas (ya termino de escribirse en pantalla).
  - Rescate: si un dialogo aparece una sola vez y llega uno nuevo,
    se guarda igual para no perderlo (dialogos rapidos).
  - Deduplicacion: se compara contra los ultimos N dialogos guardados
    para evitar repeticiones y rebotes del OCR.
"""

import threading
import logging
from queue import Empty

logger = logging.getLogger(__name__)


class DialogProcessor(threading.Thread):
    """Hilo que consume frames, hace OCR y emite dialogos validos"""

    STABLE_REQUIRED = 2      # Lecturas iguales para considerar texto estable
    MAX_RECENT = 8           # Cuantos dialogos recientes recordar
    SIMILARITY_THRESHOLD = 0.72

    def __init__(self, ocr_engine, frame_queue, on_dialog=None):
        """
        Args:
            ocr_engine: Instancia de OCREngine
            frame_queue: Cola de donde leer los frames
            on_dialog: Callback(speaker, texto) al detectar un dialogo valido
        """
        super().__init__(daemon=True, name="DialogProcessor")
        self.ocr_engine = ocr_engine
        self.frame_queue = frame_queue
        self.on_dialog = on_dialog

        self._stop_event = threading.Event()

        # Estado de decision
        self._pending_text = ""
        self._stable_count = 0
        self._pending_saved = False   # El pendiente actual ya se guardo
        self._recent_texts = []

        # Estadisticas
        self.frames_processed = 0
        self.dialogs_emitted = 0

    def stop(self):
        """Solicita la detencion del hilo"""
        self._stop_event.set()

    def run(self):
        """Bucle principal del consumidor"""
        logger.info("DialogProcessor iniciado")

        while not self._stop_event.is_set():
            try:
                # Timeout corto para poder revisar el stop_event periodicamente
                frame = self.frame_queue.get(timeout=0.5)
            except Empty:
                continue

            try:
                self._process_frame(frame)
                self.frames_processed += 1
            except Exception as e:
                logger.error(f"Error procesando frame: {e}")
            finally:
                self.frame_queue.task_done()

        # Al detener, rescatar lo que haya quedado pendiente
        self._flush_pending()
        logger.info(
            f"DialogProcessor detenido "
            f"(procesados: {self.frames_processed}, dialogos: {self.dialogs_emitted})"
        )

    def _process_frame(self, frame):
        """Aplica OCR a un frame y actualiza el estado de decision"""
        text = self.ocr_engine.extract_text(frame)

        if not text:
            return

        if self._is_same_as_pending(text):
            # El mismo dialogo sigue en pantalla
            self._stable_count += 1
            # Conservar la version mas larga (mas completa)
            if len(text) > len(self._pending_text):
                self._pending_text = text
        else:
            # Dialogo distinto: guardar el anterior antes de reemplazarlo
            self._flush_pending()
            self._pending_text = text
            self._stable_count = 1
            self._pending_saved = False

        # Guardar una sola vez por dialogo, aunque siga en pantalla
        if not self._pending_saved and self._stable_count >= self.STABLE_REQUIRED:
            self._commit(self._pending_text)
            self._pending_saved = True

    def _is_same_as_pending(self, text):
        """
        Determina si el texto es el mismo dialogo que el pendiente.
        Contempla ruido del OCR y texto animado que va creciendo.
        """
        if not self._pending_text:
            return False

        if self.ocr_engine.is_similar(text, self._pending_text, self.SIMILARITY_THRESHOLD):
            return True

        # Texto animado: el nuevo contiene al anterior
        return self._pending_text in text

    def _flush_pending(self):
        """
        Guarda el texto pendiente si nunca se guardo.
        Cubre los dialogos rapidos que aparecieron una sola vez.
        """
        if self._pending_text and not self._pending_saved and self._stable_count >= 1:
            self._commit(self._pending_text)
        self._pending_text = ""
        self._stable_count = 0
        self._pending_saved = False

    def _commit(self, text):
        """Valida contra el historial reciente y emite el dialogo"""
        if self.ocr_engine.is_duplicate_of_recent(
            text, self._recent_texts, self.SIMILARITY_THRESHOLD
        ):
            logger.debug("Dialogo descartado: duplicado reciente")
            return

        speaker, dialog_text = self.ocr_engine.split_speaker_and_text(text)
        if not speaker:
            speaker = "Unknown"

        self._recent_texts.append(text)
        if len(self._recent_texts) > self.MAX_RECENT:
            self._recent_texts.pop(0)

        self.dialogs_emitted += 1

        if self.on_dialog:
            self.on_dialog(speaker, dialog_text)

    def get_stats(self):
        """Retorna estadisticas del consumidor"""
        return {
            "processed": self.frames_processed,
            "emitted": self.dialogs_emitted,
        }