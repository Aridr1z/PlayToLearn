# Game Dialog Capturer

Aplicación para capturar automáticamente diálogos de videojuegos mediante reconocimiento óptico de caracteres (OCR). Diseñada para estudiantes de inglés que desean mejorar su vocabulario jugando videojuegos con subtítulos en inglés.

## Descripción General

Game Dialog Capturer permite seleccionar una región de la pantalla (como un snipping tool) y captura automáticamente cualquier texto que aparezca en esa área. El OCR reconoce el texto de las imágenes capturadas y lo almacena de manera organizada con timestamp y nombre del personaje. Los diálogos se guardan en JSON y pueden exportarse a texto plano para su revisión posterior.

## Características Principales

- Interfaz gráfica moderna y limpia
- Selección de región tipo snipping tool
- Captura automática cada 2 segundos
- Reconocimiento de texto mediante OCR (Tesseract)
- Almacenamiento de diálogos en JSON
- Exportación a archivos de texto
- Estadísticas de captura
- Botón de detención para controlar la captura
- Arquitectura modular con backend y frontend separados

## Requisitos del Sistema

- Python 3.7 o superior
- Tesseract OCR instalado en el sistema operativo
- 50 MB de espacio en disco
- Pantalla con resolución mínima 800x600

## Instalación

### Paso 1: Clonar o descargar el proyecto

```bash
git clone https://github.com/tuusuario/game-dialog-capturer.git
cd game-dialog-capturer
```

O descargar como ZIP desde GitHub.

### Paso 2: Crear entorno virtual

En Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

En Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Tesseract OCR

Este es el paso más importante. Sin Tesseract, la app no puede reconocer texto.

**Windows:**
1. Visita https://github.com/UB-Mannheim/tesseract/wiki
2. Descarga el instalador (tesseract-ocr-w64-setup-v5.x.x.exe)
3. Ejecuta el instalador
4. Cuando te pregunte dónde instalar, elige: C:\Program Files\Tesseract-OCR
5. Completa la instalación
6. Reinicia tu computadora para que el PATH se actualice

**Mac (con Homebrew):**
```bash
brew install tesseract
```

Si no tienes Homebrew, instálalo desde https://brew.sh

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Verificar instalación:**
En cualquier sistema, abre terminal y escribe:
```bash
tesseract --version
```

Si ves un número de versión, Tesseract está instalado correctamente.

### Paso 4: Instalar dependencias de Python

Con el entorno virtual activado:
```bash
pip install -r requirements.txt
```

Esto instala pytesseract y Pillow (solo 2 librerías).

## Uso de la Aplicación

### Iniciar

```bash
python src/main.py
```

Se abrirá una ventana con interfaz gráfica.

### Flujo de trabajo

**1. Seleccionar Región**
- Abre el juego con subtítulos en inglés en otra pantalla
- Posiciona la ventana de la app
- Click en botón "Seleccionar Region"
- Se oscurecerá la pantalla completamente
- Haz click en la esquina superior-izquierda del área de diálogos
- Arrastra hasta la esquina inferior-derecha para crear un rectángulo
- Suelta el mouse para confirmar
- Presiona ESC en cualquier momento para cancelar

**2. Iniciar Captura**
- Click en "Iniciar Captura"
- El estado cambiará a "Capturando..."
- La app capturará el texto cada 2 segundos automáticamente
- Los nuevos diálogos aparecerán en la lista

**3. Detener Captura**
- Click en "Detener" para pausar la captura
- Puedes volver a iniciar en cualquier momento

**4. Revisar Diálogos**
- Los diálogos aparecen con timestamp y número de speaker
- Scroll en el panel para ver toda la lista

**5. Exportar a Texto**
- Click en "Exportar a Texto"
- Se crea un archivo .txt en la carpeta dialogs/
- Puedes abrir con cualquier editor de texto

**6. Otras acciones**
- Refrescar: Recarga la lista de diálogos
- Limpiar Todos: Borra todos los diálogos guardados (pide confirmación)
- Estadísticas: Muestra cantidad total, personajes únicos, caracteres totales

## Estructura del Proyecto

```
game-dialog-capturer/
│
├── src/
│   ├── backend/                    Lógica de la aplicación
│   │   ├── ocr_engine.py          Motor OCR (Tesseract)
│   │   ├── dialog_manager.py      Gestión de datos
│   │   ├── screenshot.py          Captura de pantalla
│   │   └── __init__.py
│   │
│   ├── frontend/                   Interfaz gráfica
│   │   ├── gui.py                 Ventana principal (Tkinter)
│   │   ├── region_selector.py     Snipping tool
│   │   └── __init__.py
│   │
│   ├── main.py                    Punto de entrada
│   └── __init__.py
│
├── dialogs/                        Carpeta de datos (se crea automático)
│   └── dialogs.json              Base de datos de diálogos
│
├── venv/                           Entorno virtual (no subir a GitHub)
│
├── requirements.txt                Dependencias Python
├── README.md                       Este archivo
├── ESTRUCTURA.md                   Documentación técnica
├── .gitignore                      Archivos ignorados por Git
├── setup.bat                       Instalación automática (Windows)
└── setup.sh                        Instalación automática (Mac/Linux)
```

## Cómo Funcionan los Componentes

### Backend (Lógica de negocio)

**ocr_engine.py**
- Utiliza Tesseract para leer texto de imágenes
- Método principal: extract_text(imagen) devuelve el texto detectado
- Soporta inglés y español

**dialog_manager.py**
- Guarda y carga diálogos desde archivo JSON
- Métodos: add_dialog, save_dialogs, load_dialogs, export_to_text
- Mantiene automáticamente los datos entre sesiones

**screenshot.py**
- Captura la pantalla completa o una región específica
- Utiliza PIL para manejo de imágenes
- Recibe coordenadas (x1, y1, x2, y2) para región específica

### Frontend (Interfaz gráfica)

**gui.py**
- Construye la interfaz con Tkinter
- Gestiona eventos de botones
- Ejecuta captura en thread separado para no congelar la interfaz
- Actualiza lista de diálogos en tiempo real

**region_selector.py**
- Ventana transparente para seleccionar región
- Usuario dibuja rectángulo con mouse
- Devuelve coordenadas del área seleccionada
- ESC para cancelar

## Almacenamiento de Datos

Los diálogos se guardan en archivo JSON ubicado en dialogs/dialogs.json

Formato:
```json
{
  "dialogs": [
    {
      "timestamp": "14:32:45",
      "speaker": "Speaker 1",
      "text": "Hello, how are you doing?"
    },
    {
      "timestamp": "14:35:12",
      "speaker": "Speaker 2",
      "text": "I am doing well, thank you"
    }
  ]
}
```

Cada diálogo contiene:
- timestamp: Hora en formato HH:MM:SS
- speaker: Identificador del personaje
- text: Contenido del diálogo

## Solución de Problemas

### Error: "Tesseract is not installed or not in PATH"

Solución:
1. Verifica que Tesseract está instalado: tesseract --version
2. Si falta, instálalo según tu sistema (ver sección Instalación)
3. Reinicia tu computadora
4. Si persiste, verifica que instalaste en la ruta correcta:
   - Windows: C:\Program Files\Tesseract-OCR

### La captura no detecta texto

Causas comunes:
- El juego está en otro idioma (revisa que esté en inglés)
- La región seleccionada es muy pequeña o no incluye los diálogos
- El texto es muy pequeño (aumenta tamaño de fuente en el juego)
- Tesseract no tiene suficiente confianza para reconocer

Soluciones:
- Aumenta el tamaño de fuente del juego a 120% o más
- Selecciona una región más grande que incluya espacio extra
- Asegúrate de que hay contraste entre texto y fondo
- Toma una screenshot manualmente para verificar qué ve

### La región seleccionada tiene error

Error: "Región demasiado pequeña"

Solución:
- La región debe tener mínimo 10x10 píxeles
- Arrastra más distancia para crear rectángulo más grande

### Los diálogos no aparecen en la lista

Solución:
- Click en "Refrescar" para actualizar la lista
- Verifica que el archivo dialogs/dialogs.json existe
- Si está vacío, significa que OCR no reconoce el texto en esa región

## Consejos para Mejorar Resultados

1. Selecciona una región solo con los diálogos (sin otros elementos)
2. El contraste debe ser alto (texto oscuro sobre fondo claro o viceversa)
3. El texto debe ser claramente legible para un humano
4. Aumenta el tamaño de fuente en el juego si es posible
5. Ajusta el brillo/contraste del monitor para mejor OCR


## Licencia

MIT License - Este proyecto es código abierto y libre de usar, modificar y distribuir.



