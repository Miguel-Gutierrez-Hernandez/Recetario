# config.py — Configuración global de Boti

import os

# ── Identidad ─────────────────────────────────────────────
NOMBRE      = "Boti"
VERSION     = "1.0.0"
BIENVENIDA  = (
    "Hola, soy Boti 👋\n"
    "Puedes escribir o decirme cosas como:\n"
    "• «receta de tortilla»\n"
    "• «anota: comprar pan»\n"
    "• «qué hora es»\n"
    "Escribe «ayuda» para ver todos los comandos."
)

# ── Rutas ─────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, "data")
DB_PATH     = os.path.join(DATA_DIR, "boti.db")
ALARMA_MP3  = os.path.join(DATA_DIR, "alarma.mp3")

# ── UI: colores ───────────────────────────────────────────
BG_DARK     = "#0f1117"
BG_PANEL    = "#1a1d27"
BG_INPUT    = "#22253a"
BG_USER     = "#2e5bff"
BG_BOTI     = "#1e2235"
TEXT_PRI    = "#e8eaf6"
TEXT_MUT    = "#6b7280"
TEXT_ACC    = "#7c8fff"
BORDER      = "#2a2d45"

# -------- Buscador ------------------------------------------------------------
SEARCH_ENGINES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "wikipedia": "https://es.wikipedia.org",
    "wolframalpha": "https://www.wolframalpha.com",
    "whatsapp": "https://web.whatsapp.com"
}

# -------- ARCHIVO ------------------------------------------------------------
FILE_PATH = {
    "ejemplo": "data/ejemplo.txt",
    "receta": "data/Receta_Paella.pdf",
    "nota": "data/nota.txt"
}

# -------- PROGRAMS ------------------------------------------------------------
PROGRAMS = {
    "discord":     "/Applications/Discord.app",
    "calculadora": "/System/Applications/Calculator.app",
    "notas":       "/System/Applications/Notes.app",
    "word":        "/Applications/Microsoft Word.app",
    "excel":       "/Applications/Microsoft Excel.app",
    "powerpoint":  "/Applications/Microsoft PowerPoint.app",
}