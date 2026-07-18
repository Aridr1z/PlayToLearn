"""
Dialog Manager - Gestiona el almacenamiento y recuperación de diálogos
"""

import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DialogManager:
    def __init__(self, dialogs_dir="dialogs"):
        self.dialogs_dir = dialogs_dir
        self.dialogs_file = os.path.join(dialogs_dir, "dialogs.json")
        self.dialogs = []
        self._ensure_dir()
        self.load_dialogs()
    
    def _ensure_dir(self):
        """Crea la carpeta de diálogos si no existe"""
        if not os.path.exists(self.dialogs_dir):
            os.makedirs(self.dialogs_dir)
            logger.info(f"Carpeta creada: {self.dialogs_dir}")
    
    def load_dialogs(self):
        """Carga diálogos del archivo JSON"""
        try:
            if os.path.exists(self.dialogs_file):
                with open(self.dialogs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.dialogs = data.get('dialogs', [])
                logger.info(f"Cargados {len(self.dialogs)} diálogos")
            else:
                self.dialogs = []
                logger.info("Archivo de diálogos no encontrado. Iniciando nuevo.")
        except Exception as e:
            logger.error(f"Error cargando diálogos: {e}")
            self.dialogs = []
    
    def save_dialogs(self):
        """Guarda todos los diálogos en JSON"""
        try:
            data = {"dialogs": self.dialogs}
            with open(self.dialogs_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Guardados {len(self.dialogs)} diálogos")
            return True
        except Exception as e:
            logger.error(f"Error guardando diálogos: {e}")
            return False
    
    def add_dialog(self, speaker, text):
        """
        Añade un nuevo diálogo
        
        Args:
            speaker: Nombre del personaje
            text: Texto del diálogo
        """
        if not text or not text.strip():
            logger.warning("Intento de agregar diálogo vacío")
            return None
        
        dialog = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "speaker": speaker or "Unknown",
            "text": text.strip()
        }
        
        self.dialogs.append(dialog)
        logger.info(f"Diálogo agregado: {speaker}")
        return dialog
    
    def clear_dialogs(self):
        """Elimina todos los diálogos"""
        self.dialogs = []
        self.save_dialogs()
        logger.info("Todos los diálogos eliminados")
    
    def export_to_text(self, filename=None):
        """
        Exporta diálogos a archivo de texto
        
        Args:
            filename: Nombre del archivo (optional)
            
        Returns:
            str: Ruta del archivo exportado
        """
        if not self.dialogs:
            logger.warning("No hay diálogos para exportar")
            return None
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(self.dialogs_dir, f"dialogs_{timestamp}.txt")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for dialog in self.dialogs:
                    f.write(f"[{dialog['timestamp']}] {dialog['speaker']}\n")
                    f.write(f"{dialog['text']}\n\n")
            
            logger.info(f"Diálogos exportados a {filename}")
            return filename
        
        except Exception as e:
            logger.error(f"Error exportando a texto: {e}")
            return None
    
    def get_dialogs(self):
        """Retorna lista de todos los diálogos"""
        return self.dialogs
    
    def get_stats(self):
        """Retorna estadísticas de los diálogos"""
        if not self.dialogs:
            return {
                "total": 0,
                "unique_speakers": 0,
                "total_characters": 0
            }
        
        speakers = set(d['speaker'] for d in self.dialogs)
        total_chars = sum(len(d['text']) for d in self.dialogs)
        
        return {
            "total": len(self.dialogs),
            "unique_speakers": len(speakers),
            "total_characters": total_chars,
            "speakers": list(speakers)
        }
