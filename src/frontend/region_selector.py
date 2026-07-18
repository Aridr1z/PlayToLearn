"""
Region Selector - Snipping tool para seleccionar área de la pantalla
"""

import tkinter as tk
from PIL import ImageGrab, ImageTk
import logging

logger = logging.getLogger(__name__)

class RegionSelector:
    """Herramienta visual para seleccionar una región de la pantalla"""
    
    def __init__(self, root=None):
        self.root = root or tk.Tk()
        self.selected_region = None
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.rect = None
        self.canvas = None
    
    def select_region(self):
        """
        Abre la ventana de selección
        
        Returns:
            tuple: Coordenadas (x1, y1, x2, y2) o None si se cancela
        """
        # Crear ventana transparent
        selector_window = tk.Toplevel(self.root)
        selector_window.attributes('-fullscreen', True)
        selector_window.attributes('-alpha', 0.3)
        selector_window.configure(bg='gray')
        
        self.canvas = tk.Canvas(selector_window, bg='gray', cursor='crosshair')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind('<Button-1>', self._on_press)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_release)
        self.canvas.bind('<Escape>', lambda e: self._cancel(selector_window))
        
        self.root.wait_window(selector_window)
        
        return self.selected_region
    
    def _on_press(self, event):
        """Registro del inicio del arrastre"""
        self.start_x = event.x
        self.start_y = event.y
    
    def _on_drag(self, event):
        """Dibuja el rectángulo mientras se arrastra"""
        self.end_x = event.x
        self.end_y = event.y
        
        # Elimina rectángulo anterior
        if self.rect:
            self.canvas.delete(self.rect)
        
        # Dibuja nuevo rectángulo
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y,
            self.end_x, self.end_y,
            outline='white', width=2
        )
    
    def _on_release(self, event):
        """Completa la selección"""
        self.end_x = event.x
        self.end_y = event.y
        
        # Valida que haya área seleccionada
        if abs(self.end_x - self.start_x) > 10 and abs(self.end_y - self.start_y) > 10:
            self.selected_region = (
                min(self.start_x, self.end_x),
                min(self.start_y, self.end_y),
                max(self.start_x, self.end_x),
                max(self.start_y, self.end_y)
            )
            logger.info(f"Region seleccionada: {self.selected_region}")
            self.canvas.master.destroy()
        else:
            logger.warning("Región demasiado pequeña")
    
    def _cancel(self, window):
        """Cancela la selección"""
        self.selected_region = None
        window.destroy()
        logger.info("Selección cancelada")
