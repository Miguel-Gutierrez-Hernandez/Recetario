# utils/talk.py — Síntesis de voz (TTS)
# Estrategia:
#   1. Intenta gTTS si hay internet (mejor calidad, funciona en Android)
#   2. Si falla o no hay conexión, usa pyttsx3 (offline, solo Mac/Windows)

import threading
import os
import tempfile

# ── Estado global ─────────────────────────────────────────
_hablando   = False
_habilitado = True   # el usuario puede silenciar a Boti


def esta_hablando() -> bool:
    return _hablando


def silenciar(valor: bool):
    """Activa o desactiva la voz de Boti."""
    global _habilitado
    _habilitado = valor


def hablar(texto: str):
    """
    Lanza la síntesis en un hilo secundario para no bloquear la UI.
    Prueba gTTS primero; si falla, usa pyttsx3.
    """
    if not _habilitado or not texto.strip():
        return
    threading.Thread(target=_sintetizar, args=(texto,), daemon=True).start()


# ── Lógica interna ────────────────────────────────────────

def _sintetizar(texto: str):
    global _hablando
    _hablando = True
    try:
        if _hay_internet():
            _hablar_gtts(texto)
        else:
            _hablar_pyttsx3(texto)
    except Exception:
        # Último recurso: si gTTS falló por cualquier razón, prueba pyttsx3
        try:
            _hablar_pyttsx3(texto)
        except Exception:
            pass  # Silencio — no interrumpir la app por un error de voz
    finally:
        _hablando = False


def _hablar_gtts(texto: str):
    """gTTS: genera MP3 en un archivo temporal y lo reproduce."""
    from gtts import gTTS
    import playsound

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        ruta = f.name

    try:
        tts = gTTS(text=texto, lang="es", slow=False)
        tts.save(ruta)
        playsound.playsound(ruta, block=True)
    finally:
        try:
            os.remove(ruta)
        except OSError:
            pass


def _hablar_pyttsx3(texto: str):
    """pyttsx3: motor offline del sistema (Mac/Windows)."""
    import pyttsx3
    motor = pyttsx3.init()
    motor.setProperty("rate", 175)    # velocidad (palabras/min)
    motor.setProperty("volume", 0.9)
    # Intenta seleccionar una voz en español si está disponible
    voces = motor.getProperty("voices")
    for voz in voces:
        if "es" in (voz.languages[0] if voz.languages else "").lower() \
                or "spanish" in voz.name.lower() \
                or "jorge" in voz.name.lower() \
                or "paulina" in voz.name.lower():
            motor.setProperty("voice", voz.id)
            break
    motor.say(texto)
    motor.runAndWait()


def _hay_internet() -> bool:
    """Comprobación rápida de conectividad (timeout 1.5s)."""
    import socket
    try:
        socket.setdefaulttimeout(1.5)
        socket.create_connection(("8.8.8.8", 53))
        return True
    except OSError:
        return False