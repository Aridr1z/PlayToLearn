# Estructura del Proyecto Game Dialog Capturer

```
game-dialog-capturer/
│
├── src/                               # Código principal
│   │
│   ├── backend/                       # Backend - Lógica de negocio
│   │   ├── __init__.py               # Inicializador
│   │   ├── ocr_engine.py             # Motor OCR (Tesseract)
│   │   ├── dialog_manager.py         # Gestión de diálogos (guardar/cargar)
│   │   └── screenshot.py             # Captura de pantalla
│   │
│   ├── frontend/                      # Frontend - Interfaz gráfica
│   │   ├── __init__.py               # Inicializador
│   │   ├── gui.py                    # Interfaz principal (Tkinter)
│   │   └── region_selector.py        # Snipping tool para seleccionar región
│   │
│   ├── __init__.py                   # Inicializador del paquete
│   └── main.py                       # Punto de entrada (python src/main.py)
│
├── dialogs/                          # Carpeta de datos (se crea automáticamente)
│   └── dialogs.json                  # Base de datos de diálogos
│
├── venv/                             # Virtual environment (no subir a GitHub)
│
├── requirements.txt                  # Dependencias Python
├── README.md                         # Documentación principal
├── ESTRUCTURA.md                     # Este archivo
├── .gitignore                        # Archivos a ignorar en Git
├── setup.bat                         # Instalación automática (Windows)
└── setup.sh                          # Instalación automática (Mac/Linux)
```

## Descripción de cada componente

### Backend (src/backend/)

#### ocr_engine.py
- Clase: `OCREngine`
- Responsable de: Leer texto de imágenes usando Tesseract
- Métodos principales:
  - `extract_text(image)` - Extrae texto simple
  - `extract_text_with_confidence(image)` - Extrae texto con nivel de confianza

#### dialog_manager.py
- Clase: `DialogManager`
- Responsable de: Guardar, cargar y exportar diálogos
- Métodos principales:
  - `add_dialog(speaker, text)` - Agrega nuevo diálogo
  - `save_dialogs()` - Guarda en JSON
  - `load_dialogs()` - Carga desde JSON
  - `export_to_text()` - Exporta a archivo .txt
  - `get_stats()` - Retorna estadísticas
  - `clear_dialogs()` - Limpia todos los diálogos

#### screenshot.py
- Clase: `ScreenshotCapture`
- Responsable de: Capturar pantalla (completa o región)
- Métodos principales:
  - `capture_full_screen()` - Captura toda la pantalla
  - `capture_region(bbox)` - Captura región específica

### Frontend (src/frontend/)

#### gui.py
- Clase: `GameDialogCapturer`
- Responsable de: Interfaz gráfica principal con Tkinter
- Funcionalidades:
  - Menú de controles (Seleccionar Region, Iniciar Captura)
  - Visualización de diálogos capturados
  - Panel de estadísticas
  - Botones de acción (Exportar, Limpiar, Estadísticas)
  - Thread para captura automática sin bloquear GUI

#### region_selector.py
- Clase: `RegionSelector`
- Responsable de: Herramienta visual tipo snipping tool
- Funcionalidades:
  - Abre ventana transparente
  - Usuario puede hacer click y drag para dibujar rectángulo
  - Retorna coordenadas (x1, y1, x2, y2)
  - ESC para cancelar

### Punto de entrada

#### main.py
- Función: `run_application()`
- Responsable de: Iniciar la app
- Uso: `python src/main.py`

## Flujo de datos

```
Seleccionar Region (GUI)
    ↓
RegionSelector (snipping tool)
    ↓
OCREngine (Tesseract)
    ↓
DialogManager (guardar JSON)
    ↓
GUI (mostrar en pantalla)
```

## Archivos de configuración

- `requirements.txt` - Dependencias Python (solo 2: pytesseract y Pillow)
- `.gitignore` - Archivos a ignorar en Git (venv, dialogs.json, etc)
- `setup.bat` - Instalación automática para Windows
- `setup.sh` - Instalación automática para Mac/Linux

## Cómo extender

### Agregar nueva funcionalidad al backend

1. Crea nuevo archivo en `src/backend/`
2. Define clase con lógica clara
3. Actualiza `src/backend/__init__.py`
4. Usa en `src/frontend/gui.py`

### Agregar nuevo botón a la interfaz

1. En `src/frontend/gui.py` método `_setup_ui()`
2. Agrega `ttk.Button(...)`
3. Define método `_on_button_click()`
4. Llama métodos del backend

### Cambiar estilos visuales

1. Edita colores en `src/frontend/gui.py` método `_apply_styles()`
2. O crea nuevo archivo `src/frontend/styles.py`

## Separación Frontend/Backend

- **Backend**: Contiene toda la lógica (OCR, guardado, etc)
- **Frontend**: Solo maneja interfaz y llamadas a backend
- **Ventaja**: Podrías cambiar frontend (Web, CLI, etc) sin tocar backend
