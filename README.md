# Boti — Asistente Personal

Asistente de voz y texto construido con Python y Flet.
Conectado a Notion, recetario propio, Wikipedia, YouTube y más.

---

## Requisitos

- Python 3.12
- Flet 0.85+
- Cuenta Anthropic (API key)
- Notion (opcional)

---

## Instalación

```bash
git clone https://github.com/tu-usuario/Recetario.git
cd Recetario
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.ejemplo .env
# Edita .env con tus claves
```

---

## Arrancar

```bash
source .venv/bin/activate
python src/boti/main.py
```

---

## Estructura

```
Recetario/
├── requirements.txt
├── .env.ejemplo
├── src/boti/
│   ├── main.py                  # Interfaz de chat (Flet)
│   ├── config.py                # Nombre, rutas, ajustes globales
│   ├── data/
│   │   └── alarma.mp3           # Sonido de alarma
│   ├── modules/
│   │   ├── brain.py             # Lógica central: Claude + intenciones
│   │   ├── recipes.py           # Recetario (SQLite local)
│   │   ├── write_note.py        # Guardar notas en Notion
│   │   ├── search_wikipedia.py  # Búsqueda en Wikipedia
│   │   ├── play_youtube.py      # Abrir vídeos en YouTube
│   │   ├── time_tools.py        # Hora actual y alarmas
│   │   └── open_apps.py         # Abrir apps y archivos
│   └── utils/
│       ├── keywords.py          # Diccionario de comandos e intenciones
│       ├── listener.py          # Reconocimiento de voz (STT)
│       ├── talk.py              # Síntesis de voz (TTS)
│       └── write.py             # Utilidades de texto
```

---

## Hoja de ruta

| Fase | Estado | Contenido |
|------|--------|-----------|
| 1 | ✅ | Interfaz Flet + chat por texto + Claude |
| 2 | 🔜 | Recetario SQLite + integración Notion |
| 3 | ⏳ | Voz: reconocimiento (STT) y síntesis (TTS) |
| 4 | ⏳ | Wikipedia, YouTube, Spotify, WhatsApp |
| 5 | ⏳ | Build Android (`flet build android`) |

---

## Variables de entorno

Copia `.env.ejemplo` como `.env` y rellena:

```env
ANTHROPIC_API_KEY=sk-ant-...

# Notion (opcional, Fase 2)
NOTION_TOKEN=secret_...
NOTION_NOTES_DB=id-de-tu-base-de-datos
NOTION_RECIPES_DB=id-de-tu-base-de-datos

# Spotify (Fase 4)
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
```

---

## Comandos de ejemplo

| Escribes o dices | Boti hace |
|-----------------|-----------|
| `receta de tortilla` | Busca en el recetario local |
| `anota: comprar leche` | Guarda en Notion |
| `qué es la fotosíntesis` | Busca en Wikipedia |
| `pon música de jazz` | Abre YouTube |
| `qué hora es` | Dice la hora actual |
| Cualquier otra cosa | Responde Claude (Boti) |

---

## Contribuir

Proyecto personal en desarrollo activo.
Cada fase se desarrolla en su propia rama de git.