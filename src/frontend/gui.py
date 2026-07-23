"""
GUI - Interfaz gráfica principal
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import logging
import sys
from pathlib import Path

# Agregar padre al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from .region_selector import RegionSelector
from backend.ocr_engine import OCREngine
from backend.dialog_manager import DialogManager
from backend.screenshot import ScreenshotCapture

logger = logging.getLogger(__name__)

class GameDialogCapturer:
    """Aplicación principal con interfaz gráfica"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Game Dialog Capturer")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Inicializar backends
        self.ocr_engine = OCREngine()
        self.dialog_manager = DialogManager()
        self.screenshot_capture = ScreenshotCapture()
        
        # Estado de captura
        self.capturing = False
        self.current_region = None
        self.capture_thread = None
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Configura la interfaz"""
        self.root.configure(bg="#f5f5f5")
        
        # Frame superior - Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="Game Dialog Capturer",
            font=("Segoe UI", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Frame de controles principales
        control_frame = tk.Frame(self.root, bg="#ffffff", relief=tk.FLAT, bd=1)
        control_frame.pack(fill=tk.X, padx=12, pady=12)
        
        # Botones principales
        btn_frame = tk.Frame(control_frame, bg="#ffffff")
        btn_frame.pack(fill=tk.X, padx=12, pady=12)
        
        self.btn_region = tk.Button(
            btn_frame,
            text="Seleccionar Region",
            command=self._select_region,
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 10),
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.btn_region.pack(side=tk.LEFT, padx=5)
        
        self.btn_capture = tk.Button(
            btn_frame,
            text="Iniciar Captura",
            command=self._toggle_capture,
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 10),
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.btn_capture.pack(side=tk.LEFT, padx=5)
        
        self.btn_stop = tk.Button(
            btn_frame,
            text="Detener",
            command=self._stop_capture,
            bg="#e74c3c",
            fg="white",
            font=("Segoe UI", 10),
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(
            btn_frame,
            text="Inactivo",
            font=("Segoe UI", 9),
            fg="#95a5a6",
            bg="#ffffff"
        )
        self.status_label.pack(side=tk.LEFT, padx=25)
        
        # Frame de región seleccionada
        region_frame = tk.Frame(self.root, bg="#ecf0f1", relief=tk.FLAT)
        region_frame.pack(fill=tk.X, padx=12, pady=(0, 12))
        
        region_label = tk.Label(
            region_frame,
            text="Region Seleccionada",
            font=("Segoe UI", 9, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        region_label.pack(anchor=tk.W, padx=12, pady=(8, 0))
        
        self.region_info = tk.Label(
            region_frame,
            text="Ninguna region seleccionada",
            font=("Segoe UI", 9),
            fg="#e67e22",
            bg="#ecf0f1"
        )
        self.region_info.pack(anchor=tk.W, padx=12, pady=(0, 8))
        
        # Frame de diálogos
        dialogs_container = tk.Frame(self.root, bg="#ffffff", relief=tk.FLAT)
        dialogs_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        
        dialogs_label = tk.Label(
            dialogs_container,
            text="Dialogos Capturados",
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        )
        dialogs_label.pack(anchor=tk.W, padx=12, pady=(8, 8))
        
        # Scrollbar para lista de diálogos
        scrollbar = ttk.Scrollbar(dialogs_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 12), pady=(0, 12))
        
        self.dialogs_text = scrolledtext.ScrolledText(
            dialogs_container,
            height=12,
            width=80,
            yscrollcommand=scrollbar.set,
            state=tk.DISABLED,
            bg="#fafafa",
            fg="#2c3e50",
            font=("Consolas", 9),
            relief=tk.FLAT,
            borderwidth=0
        )
        self.dialogs_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        scrollbar.config(command=self.dialogs_text.yview)
        
        # Frame inferior - Botones de acción
        action_frame = tk.Frame(self.root, bg="#ffffff", relief=tk.FLAT)
        action_frame.pack(fill=tk.X, padx=12, pady=(0, 12))
        
        buttons_container = tk.Frame(action_frame, bg="#ffffff")
        buttons_container.pack(fill=tk.X, padx=12, pady=12)
        
        def create_action_button(parent, text, command, color="#95a5a6"):
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=("Segoe UI", 9),
                padx=12,
                pady=6,
                relief=tk.FLAT,
                cursor="hand2"
            )
            return btn
        
        create_action_button(
            buttons_container,
            "Refrescar",
            self._refresh_dialogs,
            "#34495e"
        ).pack(side=tk.LEFT, padx=3)
        
        create_action_button(
            buttons_container,
            "Exportar a Texto",
            self._export_dialogs,
            "#2980b9"
        ).pack(side=tk.LEFT, padx=3)
        
        create_action_button(
            buttons_container,
            "Limpiar Todos",
            self._clear_dialogs,
            "#c0392b"
        ).pack(side=tk.LEFT, padx=3)
        
        create_action_button(
            buttons_container,
            "Estadísticas",
            self._show_stats,
            "#8e44ad"
        ).pack(side=tk.LEFT, padx=3)
        
        # Captura status en la derecha
        self.capture_status = tk.Label(
            buttons_container,
            text="",
            font=("Segoe UI", 9),
            fg="#27ae60",
            bg="#ffffff"
        )
        self.capture_status.pack(side=tk.RIGHT, padx=20)
        
        # Refrescar diálogos inicialmente
        self._refresh_dialogs()
    
    def _apply_styles(self):
        """Aplica estilos a la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Personalizar scrollbar
        style.configure('TScrollbar', background='#ecf0f1', troughcolor='#f5f5f5')
    
    def _select_region(self):
        """Abre el selector de región"""
        if self.capturing:
            messagebox.showwarning("Advertencia", "Detiene la captura antes de cambiar region")
            return
        
        self.root.withdraw()
        time.sleep(0.5)
        
        selector = RegionSelector(self.root)
        region = selector.select_region()
        
        self.root.deiconify()
        
        if region:
            self.current_region = region
            self.region_info.config(
                text=f"Region: x1={region[0]} y1={region[1]} x2={region[2]} y2={region[3]}",
                foreground="green"
            )
            logger.info(f"Region seleccionada: {region}")
        else:
            messagebox.showinfo("Info", "Selección cancelada")
    
    def _toggle_capture(self):
        """Inicia la captura"""
        if not self.current_region:
            messagebox.showwarning("Advertencia", "Selecciona una region primero")
            return
        
        self.capturing = True
        self.status_label.config(text="Capturando...", fg="#27ae60")
        
        # Actualizar botones
        self.btn_capture.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_region.config(state=tk.DISABLED)
        
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
    
    def _stop_capture(self):
        """Detiene la captura"""
        self.capturing = False
        self.status_label.config(text="Detenido", fg="#e74c3c")
        
        # Actualizar botones
        self.btn_capture.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_region.config(state=tk.NORMAL)
        self.capture_status.config(text="")
    
    def _capture_loop(self):
        """
        Loop de captura automática con:
        - Estabilización: espera 2 capturas iguales antes de guardar
        - Rescate: si un diálogo pasa rápido (1 sola captura), lo guarda
          antes de que llegue el siguiente en vez de perderlo
        - Historial reciente: compara contra últimos 5 diálogos
        """
        self._capture_count = 0
        pending_text = ""      # Texto candidato esperando estabilizarse
        stable_count = 0       # Cuántas capturas seguidas lleva igual
        recent_texts = []      # Últimos diálogos guardados
        MAX_RECENT = 5
        STABLE_REQUIRED = 2
        
        def commit_dialog(text_to_save):
            """Guarda un diálogo si no es duplicado reciente"""
            if self.ocr_engine.is_duplicate_of_recent(text_to_save, recent_texts):
                return
            
            speaker, dialog_text = self.ocr_engine.split_speaker_and_text(text_to_save)
            if not speaker:
                speaker = "Unknown"
            
            self.dialog_manager.add_dialog(speaker, dialog_text)
            self.dialog_manager.save_dialogs()
            self._capture_count += 1
            
            recent_texts.append(text_to_save)
            if len(recent_texts) > MAX_RECENT:
                recent_texts.pop(0)
            
            self.capture_status.config(text=f"Capturados: {self._capture_count}")
            self._refresh_dialogs()
        
        while self.capturing:
            try:
                screenshot = self.screenshot_capture.capture_region(self.current_region)
                
                if screenshot:
                    text = self.ocr_engine.extract_text(screenshot)
                    
                    if text:
                        # Es el mismo texto si: son similares (fuzzy) O el nuevo
                        # contiene al anterior (texto animado creciendo)
                        same_as_pending = (
                            self.ocr_engine.is_similar(text, pending_text, threshold=0.80)
                            or (pending_text and pending_text in text)
                        )
                        
                        if same_as_pending:
                            stable_count += 1
                            # Quedarse con la versión más larga (más completa)
                            if len(text) > len(pending_text):
                                pending_text = text
                        else:
                            # Texto realmente nuevo. Si había uno pendiente que
                            # nunca se estabilizó (diálogo rápido), rescatarlo
                            if pending_text and stable_count >= 1:
                                commit_dialog(pending_text)
                            
                            pending_text = text
                            stable_count = 1
                        
                        # Guardar si el texto se mantuvo estable
                        if stable_count >= STABLE_REQUIRED:
                            commit_dialog(pending_text)
                            stable_count = 0
                
                time.sleep(1)
            
            except Exception as e:
                logger.error(f"Error en captura: {e}")
                time.sleep(1)
    
    def _refresh_dialogs(self):
        """Actualiza la lista de diálogos en pantalla"""
        dialogs = self.dialog_manager.get_dialogs()
        
        self.dialogs_text.config(state=tk.NORMAL)
        self.dialogs_text.delete(1.0, tk.END)
        
        if not dialogs:
            self.dialogs_text.insert(tk.END, "Sin dialogos capturados aun", "empty")
        else:
            for i, dialog in enumerate(dialogs, 1):
                # Línea separadora
                self.dialogs_text.insert(tk.END, "─" * 80 + "\n", "separator")
                
                # Header con número, timestamp y speaker
                header = f" {i}. [{dialog['timestamp']}] {dialog['speaker']}\n"
                self.dialogs_text.insert(tk.END, header, "header")
                
                # Contenido del diálogo
                content = f" {dialog['text']}\n\n"
                self.dialogs_text.insert(tk.END, content, "content")
        
        self.dialogs_text.config(state=tk.DISABLED)
        
        # Tags para colores y estilos mejorados
        self.dialogs_text.tag_configure("separator", foreground="#d0d0d0", font=("Consolas", 8))
        self.dialogs_text.tag_configure("header", foreground="#2980b9", font=("Segoe UI", 10, "bold"))
        self.dialogs_text.tag_configure("content", foreground="#2c3e50", font=("Segoe UI", 9), lmargin2=20, rmargin=10)
        self.dialogs_text.tag_configure("empty", foreground="#95a5a6", font=("Segoe UI", 10))
        
        # Auto-scroll al final
        self.dialogs_text.see(tk.END)
    
    def _export_dialogs(self):
        """Exporta diálogos a archivo de texto"""
        if not self.dialog_manager.get_dialogs():
            messagebox.showwarning("Advertencia", "No hay dialogos para exportar")
            return
        
        filepath = self.dialog_manager.export_to_text()
        if filepath:
            messagebox.showinfo("Exito", f"Dialogos exportados a:\n{filepath}")
        else:
            messagebox.showerror("Error", "Error al exportar dialogos")
    
    def _clear_dialogs(self):
        """Limpia todos los diálogos"""
        if messagebox.askyesno("Confirmar", "Eliminar todos los dialogos?"):
            self.dialog_manager.clear_dialogs()
            self._refresh_dialogs()
            messagebox.showinfo("Exito", "Dialogos eliminados")
    
    def _show_stats(self):
        """Muestra estadísticas de los diálogos"""
        stats = self.dialog_manager.get_stats()
        
        message = f"""
Estadisticas:

Total de dialogos: {stats['total']}
Personajes unicos: {stats['unique_speakers']}
Total de caracteres: {stats['total_characters']}

Personajes:
{', '.join(stats.get('speakers', []))}
        """.strip()
        
        messagebox.showinfo("Estadisticas", message)


def run_application():
    """Inicia la aplicación"""
    root = tk.Tk()
    app = GameDialogCapturer(root)
    root.mainloop()