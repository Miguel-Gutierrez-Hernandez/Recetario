# Boti — Asistente Personal

Asistente de voz y texto construido con Python y Flet.
Conectado a Notion, recetario propio, Wikipedia, YouTube y más.

---

## Requisitos

- Python 3.12
- Flet 0.80+ (con soporte para Flutter SDK)
- Cuenta Anthropic (API key)
- Notion (opcional)

---

## Instalación

git clone [https://github.com/tu-usuario/Recetario.git](https://github.com/tu-usuario/Recetario.git)
cd Recetario
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.ejemplo .env
Edita .env con tus claves

---

## Arrancar
Arrancar y CompilarUso local en Mac/PC:Bashsource .venv/bin/activate
python src/boti/main.py

## Compilar para Android (Generar APK)

flet build apk src/boti

---

## Estructura
Recetario/
├── requirements.txt
├── .env.ejemplo
├── src/boti/
│   ├── main.py                  # Enrutador y orquestador (Flet)
│   ├── config.py                # Detección de plataforma, rutas blindadas y variables globales
│   ├── flet.yaml                # Permisos de Android (Internet, Red) e info de la app
│   ├── data/
│   │   ├── boti.db              # Base de datos SQLite (Autogenerada)
│   │   ├── claves.json          # Claves seguras para móvil (Autogenerado)
│   │   └── alarma.mp3           # Sonido de alarma
│   ├── modules/
│   │   ├── brain.py             # Lógica central: Claude + intenciones
│   │   ├── recipes.py           # Recetario (SQLite local)
│   │   ├── write_note.py        # Guardar, borrar y sincronizar notas en Notion
│   │   ├── search_wikipedia.py  # Búsqueda en Wikipedia
│   │   ├── play_youtube.py      # Abrir vídeos en YouTube
│   │   ├── time_tools.py        # Hora actual y alarmas
│   │   └── open_apps.py         # Abrir apps y archivos
│   ├── views/                   # Vistas de la interfaz (Chat, Notas, Recetas, Ajustes)
│   └── utils/
│       ├── keywords.py          # Diccionario de comandos e intenciones
│       ├── listener.py          # Reconocimiento de voz (STT)
│       ├── talk.py              # Síntesis de voz (TTS)
│       └── write.py             # Utilidades de texto


Fase,Estado,Contenido
1,✅,Interfaz Flet + chat por texto + Claude
2,✅,Recetario SQLite + integración total con Notion (Sincronización y Archivo)
3,⏳,Voz: reconocimiento (STT) y síntesis (TTS)
4,⏳,"Wikipedia, YouTube, Spotify, WhatsApp"
5,✅,Build Android con persistencia local (flet build apk src/boti)

# Notion (Fase 2 completada)
NOTION_TOKEN=secret_...
NOTION_NOTES_DB=id-de-tu-base-de-datos
NOTION_RECIPES_DB=id-de-tu-base-de-datos

# Spotify (Fase 4)
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...

## Comandos de ejemplo

Escribes o dices,Boti hace
receta de tortilla,Busca en el recetario local
anota: comprar leche,Guarda la nota localmente y la envía a Notion con la hora exacta
qué es la fotosíntesis,Busca en Wikipedia
pon música de jazz,Abre YouTube
qué hora es,Dice la hora actual
Cualquier otra cosa,Responde Claude (Boti)