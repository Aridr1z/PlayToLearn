"""
GUI - Interfaz gráfica principal

No define colores propios: los pide al ThemeManager mediante tokens.
Cada widget se registra con el rol que cumple ("panel", "titulo", etc.)
y al cambiar de tema se repintan todos de una pasada.
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
from .theme import ThemeManager
from backend.ocr_engine import OCREngine
from backend.dialog_manager import DialogManager
from backend.screenshot import ScreenshotCapture
from backend.capture_pipeline import CapturePipeline

logger = logging.getLogger(__name__)


class GameDialogCapturer:
    """Aplicación principal con interfaz gráfica"""

    def __init__(self, root):
        self.root = root
        self.root.title("Game Dialog Capturer")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Tema visual
        self.theme = ThemeManager(initial="light")

        # Inicializar backends
        self.ocr_engine = OCREngine()
        self.dialog_manager = DialogManager()
        self.screenshot_capture = ScreenshotCapture()

        # Pipeline de captura (productor + cola + consumidor)
        self.pipeline = CapturePipeline(self.screenshot_capture, self.ocr_engine)

        # Estado de captura
        self.capturing = False
        self.current_region = None
        self._capture_count = 0

        # Widgets agrupados por rol, para repintarlos al cambiar de tema
        self._themed = {
            "surface": [],      # (widget, token_de_fondo)
            "text": [],         # (widget, token_fondo, token_texto)
            "button": [],       # (widget, token_color)
        }

        self._setup_ui()
        self._apply_theme()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # Registro de widgets para el tema
    # ------------------------------------------------------------------

    def _surface(self, widget, bg_token):
        """Registra un contenedor (frame)"""
        self._themed["surface"].append((widget, bg_token))
        return widget

    def _text(self, widget, bg_token, fg_token):
        """Registra un widget con texto (label)"""
        self._themed["text"].append((widget, bg_token, fg_token))
        return widget

    def _button(self, widget, color_token):
        """Registra un boton"""
        self._themed["button"].append((widget, color_token))
        return widget

    # ------------------------------------------------------------------
    # Construccion de la interfaz
    # ------------------------------------------------------------------

    def _setup_ui(self):
        """Configura la interfaz"""
        self._build_header()
        self._build_controls()
        self._build_region_panel()
        self._build_dialogs_panel()
        self._build_actions()
        self._refresh_dialogs()

    def _build_header(self):
        """Barra superior con titulo y boton de tema"""
        header = self._surface(
            tk.Frame(self.root, height=70), "header_bg"
        )
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        self._text(
            tk.Label(header, text="Game Dialog Capturer",
                     font=("Segoe UI", 18, "bold")),
            "header_bg", "header_fg"
        ).pack(side=tk.LEFT, padx=20, pady=15)

        self.btn_theme = self._button(
            tk.Button(header, text="Modo Oscuro", command=self._toggle_theme,
                      fg="white", font=("Segoe UI", 9), padx=14, pady=6,
                      relief=tk.FLAT, cursor="hand2"),
            "btn_theme"
        )
        self.btn_theme.pack(side=tk.RIGHT, padx=20, pady=18)

    def _build_controls(self):
        """Panel con los botones de captura"""
        control_frame = self._surface(
            tk.Frame(self.root, relief=tk.FLAT, bd=1), "panel_bg"
        )
        control_frame.pack(fill=tk.X, padx=12, pady=12)

        btn_frame = self._surface(tk.Frame(control_frame), "panel_bg")
        btn_frame.pack(fill=tk.X, padx=12, pady=12)

        def main_button(text, command, token, state=tk.NORMAL):
            btn = tk.Button(btn_frame, text=text, command=command, fg="white",
                            font=("Segoe UI", 10), padx=15, pady=8,
                            relief=tk.FLAT, cursor="hand2", state=state)
            btn.pack(side=tk.LEFT, padx=5)
            return self._button(btn, token)

        self.btn_region = main_button(
            "Seleccionar Region", self._select_region, "btn_region")
        self.btn_capture = main_button(
            "Iniciar Captura", self._toggle_capture, "btn_start")
        self.btn_stop = main_button(
            "Detener", self._stop_capture, "btn_stop", state=tk.DISABLED)

        self.status_label = self._text(
            tk.Label(btn_frame, text="Inactivo", font=("Segoe UI", 9)),
            "panel_bg", "text_muted"
        )
        self.status_label.pack(side=tk.LEFT, padx=25)

    def _build_region_panel(self):
        """Panel que muestra la region seleccionada"""
        region_frame = self._surface(
            tk.Frame(self.root, relief=tk.FLAT), "panel_alt_bg"
        )
        region_frame.pack(fill=tk.X, padx=12, pady=(0, 12))

        self._text(
            tk.Label(region_frame, text="Region Seleccionada",
                     font=("Segoe UI", 9, "bold")),
            "panel_alt_bg", "text_primary"
        ).pack(anchor=tk.W, padx=12, pady=(8, 0))

        self.region_info = self._text(
            tk.Label(region_frame, text="Ninguna region seleccionada",
                     font=("Segoe UI", 9)),
            "panel_alt_bg", "warning"
        )
        self.region_info.pack(anchor=tk.W, padx=12, pady=(0, 8))

    def _build_dialogs_panel(self):
        """Panel con la lista de dialogos capturados"""
        container = self._surface(
            tk.Frame(self.root, relief=tk.FLAT), "panel_bg"
        )
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        self._text(
            tk.Label(container, text="Dialogos Capturados",
                     font=("Segoe UI", 9, "bold")),
            "panel_bg", "text_primary"
        ).pack(anchor=tk.W, padx=12, pady=(8, 8))

        self.dialogs_text = scrolledtext.ScrolledText(
            container, height=12, width=80, state=tk.DISABLED,
            font=("Segoe UI", 9), relief=tk.FLAT, borderwidth=0,
            insertbackground="#888888"
        )
        self.dialogs_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

    def _build_actions(self):
        """Barra inferior con acciones secundarias"""
        action_frame = self._surface(
            tk.Frame(self.root, relief=tk.FLAT), "panel_bg"
        )
        action_frame.pack(fill=tk.X, padx=12, pady=(0, 12))

        container = self._surface(tk.Frame(action_frame), "panel_bg")
        container.pack(fill=tk.X, padx=12, pady=12)

        def action_button(text, command, token):
            btn = tk.Button(container, text=text, command=command, fg="white",
                            font=("Segoe UI", 9), padx=12, pady=6,
                            relief=tk.FLAT, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=3)
            return self._button(btn, token)

        action_button("Refrescar", self._refresh_dialogs, "btn_refresh")
        action_button("Exportar a Texto", self._export_dialogs, "btn_export")
        action_button("Limpiar Todos", self._clear_dialogs, "btn_clear")
        action_button("Estadisticas", self._show_stats, "btn_stats")

        self.capture_status = self._text(
            tk.Label(container, text="", font=("Segoe UI", 9)),
            "panel_bg", "success"
        )
        self.capture_status.pack(side=tk.RIGHT, padx=20)

    # ------------------------------------------------------------------
    # Aplicacion del tema
    # ------------------------------------------------------------------

    def _toggle_theme(self):
        """Alterna entre modo claro y oscuro"""
        self.theme.toggle()
        self._apply_theme()

    def _apply_theme(self):
        """Repinta toda la interfaz con la paleta activa"""
        t = self.theme.get

        self.root.configure(bg=t("app_bg"))

        for widget, bg_token in self._themed["surface"]:
            widget.configure(bg=t(bg_token))

        for widget, bg_token, fg_token in self._themed["text"]:
            widget.configure(bg=t(bg_token), fg=t(fg_token))

        for widget, color_token in self._themed["button"]:
            widget.configure(
                bg=t(color_token),
                fg=t("text_on_accent"),
                activebackground=t(color_token),
                activeforeground=t("text_on_accent"),
                disabledforeground=t("btn_disabled"),
            )

        self.dialogs_text.configure(
            bg=t("textarea_bg"), fg=t("dialog_text")
        )

        # Scrollbar interna del ScrolledText
        if hasattr(self.dialogs_text, "vbar"):
            self.dialogs_text.vbar.configure(
                bg=t("scroll_bg"),
                troughcolor=t("scroll_trough"),
                activebackground=t("scroll_bg"),
                highlightbackground=t("panel_bg"),
                borderwidth=0,
                relief=tk.FLAT,
            )

        self.btn_theme.configure(
            text="Modo Claro" if self.theme.is_dark else "Modo Oscuro"
        )

        self._apply_ttk_styles()
        self._refresh_dialogs()

    def _apply_ttk_styles(self):
        """Ajusta los widgets ttk (scrollbar) al tema activo"""
        t = self.theme.get
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Vertical.TScrollbar",
            background=t("scroll_bg"),
            troughcolor=t("scroll_trough"),
            bordercolor=t("scroll_trough"),
            arrowcolor=t("text_muted"),
        )

    # ------------------------------------------------------------------
    # Ciclo de captura
    # ------------------------------------------------------------------

    def _select_region(self):
        """Abre el selector de región"""
        if self.capturing:
            messagebox.showwarning(
                "Advertencia", "Detiene la captura antes de cambiar region")
            return

        self.root.withdraw()
        time.sleep(0.5)

        selector = RegionSelector(self.root)
        region = selector.select_region()

        self.root.deiconify()

        if region:
            self.current_region = region
            self.region_info.config(
                text=f"Region: x1={region[0]} y1={region[1]} "
                     f"x2={region[2]} y2={region[3]}",
                fg=self.theme.get("success")
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
        self._capture_count = 0
        self.status_label.config(
            text="Capturando...", fg=self.theme.get("success"))

        self.btn_capture.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_region.config(state=tk.DISABLED)

        self.pipeline.start(self.current_region, self._on_dialog_detected)

    def _stop_capture(self):
        """Detiene la captura"""
        self.capturing = False
        self.status_label.config(
            text="Deteniendo...", fg=self.theme.get("warning"))
        self.btn_stop.config(state=tk.DISABLED)

        threading.Thread(target=self._shutdown_pipeline, daemon=True).start()

    def _shutdown_pipeline(self):
        """Detiene el pipeline y reactiva los controles"""
        self.pipeline.stop()
        self.root.after(0, self._on_capture_stopped)

    def _on_capture_stopped(self):
        """Restaura la interfaz una vez detenida la captura"""
        self.status_label.config(
            text="Detenido", fg=self.theme.get("danger"))
        self.btn_capture.config(state=tk.NORMAL)
        self.btn_region.config(state=tk.NORMAL)
        self.capture_status.config(text="")
        self._refresh_dialogs()

    def _on_dialog_detected(self, speaker, text):
        """
        Callback invocado por el pipeline cuando detecta un dialogo.
        Corre en el hilo del procesador, por eso reprograma la
        actualizacion de la interfaz en el hilo principal de Tkinter.
        """
        self.dialog_manager.add_dialog(speaker, text)
        self.dialog_manager.save_dialogs()
        self._capture_count += 1
        self.root.after(0, self._on_dialog_ui_update)

    def _on_dialog_ui_update(self):
        """Actualiza la interfaz tras un nuevo dialogo (hilo principal)"""
        self.capture_status.config(text=f"Capturados: {self._capture_count}")
        self._refresh_dialogs()

    # ------------------------------------------------------------------
    # Lista de dialogos y acciones
    # ------------------------------------------------------------------

    def _refresh_dialogs(self):
        """Actualiza la lista de diálogos en pantalla"""
        dialogs = self.dialog_manager.get_dialogs()

        self.dialogs_text.config(state=tk.NORMAL)
        self.dialogs_text.delete(1.0, tk.END)

        if not dialogs:
            self.dialogs_text.insert(tk.END, "Sin dialogos capturados aun", "empty")
        else:
            for i, dialog in enumerate(dialogs, 1):
                self.dialogs_text.insert(tk.END, "─" * 80 + "\n", "separator")
                header = f" {i}. [{dialog['timestamp']}] {dialog['speaker']}\n"
                self.dialogs_text.insert(tk.END, header, "header")
                self.dialogs_text.insert(tk.END, f" {dialog['text']}\n\n", "content")

        self.dialogs_text.config(state=tk.DISABLED)

        # Colores del contenido segun el tema activo
        t = self.theme.get
        self.dialogs_text.tag_configure(
            "separator", foreground=t("separator"), font=("Consolas", 8))
        self.dialogs_text.tag_configure(
            "header", foreground=t("dialog_speaker"), font=("Segoe UI", 10, "bold"))
        self.dialogs_text.tag_configure(
            "content", foreground=t("dialog_text"), font=("Segoe UI", 9),
            lmargin2=20, rmargin=10)
        self.dialogs_text.tag_configure(
            "empty", foreground=t("text_muted"), font=("Segoe UI", 10))

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
        pipeline_stats = self.pipeline.get_stats()

        message = f"""
Dialogos:

Total de dialogos: {stats['total']}
Personajes unicos: {stats['unique_speakers']}
Total de caracteres: {stats['total_characters']}

Personajes:
{', '.join(stats.get('speakers', []))}

Pipeline de captura:

Frames capturados: {pipeline_stats['captured']}
Frames procesados: {pipeline_stats['processed']}
Frames descartados: {pipeline_stats['dropped']}
En cola: {pipeline_stats['queue_size']}
        """.strip()

        messagebox.showinfo("Estadisticas", message)

    def _on_close(self):
        """Detiene el pipeline antes de cerrar la ventana"""
        if self.pipeline.is_running:
            self.pipeline.stop(timeout=2.0)
        self.root.destroy()


def run_application():
    """Inicia la aplicación"""
    root = tk.Tk()
    app = GameDialogCapturer(root)
    root.mainloop()