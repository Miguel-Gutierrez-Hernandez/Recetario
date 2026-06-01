# 🤖 Boti — Asistente de Voz en Python

Asistente de voz en español desarrollado en Python con interfaz Kivy para Android. Reconoce comandos por voz y ejecuta acciones como buscar en Wikipedia, reproducir YouTube, poner alarmas y más.

---

## Estructura del proyecto

```
Recetario/
├── buildozer.spec          # Configuración de compilación Android
├── src/boti/
│   ├── main.py             # Punto de entrada — interfaz Kivy
│   ├── config.py           # Configuración: nombre, rutas, motores de búsqueda
│   ├── data/
│   │   └── alarma.mp3      # Sonido de alarma
│   ├── modules/
│   │   ├── play_youtube.py      # Reproducir en YouTube
│   │   ├── search_wikipedia.py  # Buscar en Wikipedia
│   │   ├── time_tools.py        # Hora actual y alarma
│   │   ├── open_apps.py         # Abrir apps y archivos
│   │   └── write_note.py        # Escribir notas por voz
│   └── utils/
│       ├── keywords.py     # Diccionario de comandos
│       ├── listener.py     # Escucha y reconocimiento de voz
│       ├── talk.py         # Síntesis de voz (TTS)
│       └── write.py        # Escritura de texto
```

---

## 🗣️ Comandos disponibles

| Comando | Ejemplo | Acción |
|---|---|---|
| `reproduce` | *reproduce Coldplay* | Busca y reproduce en YouTube |
| `busca` | *busca inteligencia artificial* | Busca en Wikipedia |
| `hora` | *hora* | Dice la hora actual |
| `alarma` | *alarma a las 8:30* | Configura una alarma |
| `abre` | *abre chrome* | Abre una app o navegador |
| `archivo` | *archivo notas* | Abre un archivo local |
| `escribe` | *escribe* | Dicta y guarda una nota |

---

## Requisitos

### Para desarrollo (Mac)
- Python 3.9+
- Buildozer
- JDK 17
- Android SDK / NDK (descargados automáticamente por Buildozer)

### Para el móvil
- Android 7.0+ (API 24)
- Permisos: Internet, Micrófono

---

## Instalación y desarrollo

### 1. Clonar el repositorio
```bash
git clone <url-del-repo>
cd Recetario
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
source venv/bin/activate
pip install kivy plyer wikipedia requests
```

### 3. Configurar `config.py`
```python
NAME = "boti"           # Nombre del asistente

SEARCH_ENGINES = {
    "youtube": "https://www.youtube.com/results?search_query={}",
    "google":  "https://www.google.com/search?q={}",
}

FILE_PATH = {
    "notas": "data/nota.txt",
}

PROGRAMS = {
    "discord": "/Applications/Discord.app",
    "notas":   "/System/Applications/Notes.app",
}
```

---

## Compilar el APK

### Primera vez
```bash
# Asegurarse de usar JDK 17
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-17.jdk/Contents/Home

buildozer android debug 2>&1 | tee buildozer_output.txt
```

### Compilaciones siguientes (más rápido)
```bash
buildozer android debug
```

El APK se genera en:
```
bin/asistente-0.1-arm64-v8a_armeabi-v7a-debug.apk
```

---

## Instalar en el móvil

### Por cable USB (requiere depuración USB activada)
```bash
adb install bin/asistente-0.1-arm64-v8a_armeabi-v7a-debug.apk
```

### Sin cable
Comparte el APK por Google Drive, WhatsApp, etc. y ábrelo desde el móvil.

> En el Honor: **Ajustes → Seguridad → Instalar apps de fuentes desconocidas**

---

## Depuración

Para ver logs de error en tiempo real con el móvil conectado por USB:

```bash
# Añadir adb al PATH si hace falta
export PATH=$PATH:/Users/administrador/.buildozer/android/platform/android-sdk/platform-tools

# Ver logs filtrando errores de Python/Kivy
adb logcat | grep -E "python|kivy|asistente|ERROR|FATAL" 2>&1 | tee crash_log.txt
```

---

## Dependencias principales

| Librería | Uso |
|---|---|
| `kivy` | Interfaz gráfica Android |
| `plyer` | TTS, micrófono, audio nativos de Android |
| `wikipedia` | Búsquedas en Wikipedia |
| `requests` | Peticiones HTTP |

---