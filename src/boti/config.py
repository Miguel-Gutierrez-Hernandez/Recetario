# config.py — Configuracion global de Boti

import os
import sys

# ── Deteccion de plataforma ───────────────────────────────
# Flet moderno usa FLET_PLATFORM. También comprobamos propiedades de sys de Android.
_PLATFORM = os.getenv("FLET_PLATFORM", "").lower()
IS_ANDROID = _PLATFORM == "android" or hasattr(sys, "getandroidapilevel")
ES_MOVIL = IS_ANDROID  # Alias para compatibilidad con el enrutador de main.py

# ── Rutas ─────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if IS_ANDROID:
    # 📌 Ruta interna blindada para Android donde la app tiene permisos totales de escritura
    DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
else:
    # Tu ruta local de desarrollo en Mac
    RAIZ_PROYECTO = os.path.dirname(os.path.dirname(BASE_DIR))
    DATA_DIR = os.path.join(RAIZ_PROYECTO, "data")

DB_PATH     = os.path.join(DATA_DIR, "boti.db")
CLAVES_PATH = os.path.join(DATA_DIR, "claves.json")
ALARMA_MP3  = os.path.join(DATA_DIR, "alarma.mp3")

os.makedirs(DATA_DIR, exist_ok=True)

# ── Carga de claves ───────────────────────────────────────
def _cargar_claves() -> dict:
    """
    Mac/Windows: lee el .env de la raiz del proyecto.
    Android: lee claves.json del directorio de datos de la app.
    """
    claves = {}

    if not IS_ANDROID:
        # Entorno de desarrollo: usa python-dotenv
        try:
            from dotenv import load_dotenv
            carpeta = BASE_DIR
            # Sube hasta 5 niveles buscando el archivo .env
            for _ in range(5):
                env_path = os.path.join(carpeta, ".env")
                if os.path.exists(env_path):
                    # Forzamos override=True para que refresque la caché de la terminal
                    load_dotenv(env_path, override=True)
                    break
                carpeta = os.path.dirname(carpeta)
        except Exception:
            pass
            
        claves = {
            "ANTHROPIC_API_KEY":     os.getenv("ANTHROPIC_API_KEY", ""),
            "NOTION_TOKEN":          os.getenv("NOTION_TOKEN", ""),
            "NOTION_NOTES_DB":       os.getenv("NOTION_NOTES_DB", ""),
            "NOTION_RECIPES_DB":     os.getenv("NOTION_RECIPES_DB", ""),
            "SPOTIFY_CLIENT_ID":     os.getenv("SPOTIFY_CLIENT_ID", ""),
            "SPOTIFY_CLIENT_SECRET":  os.getenv("SPOTIFY_CLIENT_SECRET", ""),
        }
    else:
        # Android: lee del archivo JSON en almacenamiento interno
        import json
        if os.path.exists(CLAVES_PATH):
            try:
                with open(CLAVES_PATH, "r") as f:
                    claves = json.load(f)
            except Exception:
                claves = {}

    return claves


def guardar_claves(nuevas: dict):
    """Guarda las claves en Android (claves.json). No hace nada en Mac."""
    if not IS_ANDROID:
        return
    import json
    try:
        actuales = _cargar_claves()
        actuales.update(nuevas)
        with open(CLAVES_PATH, "w") as f:
            json.dump(actuales, f)
    except Exception:
        pass


# Claves disponibles globalmente
CLAVES = _cargar_claves()


def clave(nombre: str) -> str:
    """Devuelve el valor de una clave de configuracion."""
    return CLAVES.get(nombre, "")


# ── Identidad ─────────────────────────────────────────────
NOMBRE     = "Boti"
VERSION    = "1.0.0"
BIENVENIDA = (
    "Hola, soy Boti!\n"
    "Puedes escribir o decirme cosas como:\n"
    "- receta de tortilla\n"
    "- anota: comprar pan\n"
    "- que hora es\n"
    "Escribe ayuda para ver todos los comandos."
)

# ── UI: colores ───────────────────────────────────────────
BG_DARK  = "#0f1117"
BG_PANEL = "#1a1d27"
BG_INPUT = "#22253a"
BG_USER  = "#2e5bff"
BG_BOTI  = "#1e2235"
TEXT_PRI = "#e8eaf6"
TEXT_MUT = "#6b7280"
TEXT_ACC = "#7c8fff"
BORDER   = "#2a2d45"