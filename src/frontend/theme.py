"""
Theme - Paletas de color de la interfaz

Centraliza todos los colores en un solo lugar. La interfaz nunca
escribe un color a mano: pide un token (por ejemplo "panel_bg") y
el tema decide el valor segun el modo activo.

Las paletas estan pensadas para cumplir un contraste minimo de
4.5:1 entre texto y su fondo (recomendacion WCAG AA).
"""

import logging

logger = logging.getLogger(__name__)


LIGHT = {
    "name": "light",
    # Superficies
    "app_bg": "#f5f5f5",
    "panel_bg": "#ffffff",
    "panel_alt_bg": "#ecf0f1",
    "header_bg": "#2c3e50",
    "textarea_bg": "#fafafa",
    # Texto
    "header_fg": "#ffffff",
    "text_primary": "#2c3e50",
    "text_muted": "#5f6d78",
    "text_on_accent": "#ffffff",
    # Estados
    "success": "#1e8449",
    "danger": "#c0392b",
    "warning": "#9c5b00",
    # Botones principales
    "btn_region": "#256f9e",
    "btn_start": "#1e8449",
    "btn_stop": "#c0392b",
    # Botones de accion
    "btn_refresh": "#34495e",
    "btn_export": "#2471a3",
    "btn_clear": "#a93226",
    "btn_stats": "#7d3c98",
    "btn_theme": "#5d6d7e",
    "btn_disabled": "#b6bec5",
    # Area de dialogos
    "dialog_speaker": "#1f618d",
    "dialog_text": "#2c3e50",
    "separator": "#d5dbdb",
    # Scrollbar
    "scroll_bg": "#ecf0f1",
    "scroll_trough": "#f5f5f5",
}


DARK = {
    "name": "dark",
    # Superficies
    "app_bg": "#15181d",
    "panel_bg": "#22262e",
    "panel_alt_bg": "#2a2f38",
    "header_bg": "#0f1216",
    "textarea_bg": "#1b1f25",
    # Texto
    "header_fg": "#f0f3f7",
    "text_primary": "#e4e8ee",
    "text_muted": "#a4aebb",
    "text_on_accent": "#ffffff",
    # Estados
    "success": "#5dd68a",
    "danger": "#ff7b72",
    "warning": "#e3a047",
    # Botones principales
    "btn_region": "#2f6fa8",
    "btn_start": "#20794a",
    "btn_stop": "#b23a30",
    # Botones de accion
    "btn_refresh": "#3d4753",
    "btn_export": "#2b6795",
    "btn_clear": "#9c342c",
    "btn_stats": "#6b4292",
    "btn_theme": "#4a5462",
    "btn_disabled": "#3a4049",
    # Area de dialogos
    "dialog_speaker": "#79b8ff",
    "dialog_text": "#dbe1e8",
    "separator": "#39404a",
    # Scrollbar
    "scroll_bg": "#39404a",
    "scroll_trough": "#22262e",
}


class ThemeManager:
    """Guarda el tema activo y permite alternarlo"""

    def __init__(self, initial="light"):
        self._palette = DARK if initial == "dark" else LIGHT
        self._listeners = []

    @property
    def palette(self):
        """Diccionario de colores del tema activo"""
        return self._palette

    @property
    def is_dark(self):
        """True si el tema activo es el oscuro"""
        return self._palette["name"] == "dark"

    def get(self, token):
        """Devuelve el color asociado a un token"""
        return self._palette.get(token, "#ff00ff")  # magenta = token faltante

    def toggle(self):
        """Alterna entre claro y oscuro y notifica a los suscriptores"""
        self._palette = LIGHT if self.is_dark else DARK
        logger.info(f"Tema cambiado a: {self._palette['name']}")
        self._notify()
        return self._palette

    def subscribe(self, callback):
        """Registra una funcion a ejecutar cuando cambie el tema"""
        self._listeners.append(callback)

    def _notify(self):
        for callback in self._listeners:
            try:
                callback(self._palette)
            except Exception as e:
                logger.error(f"Error aplicando tema: {e}")