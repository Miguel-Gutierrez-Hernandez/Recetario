# modules/time_tools.py — Hora, fecha y alarmas

import threading
import time
import re
from datetime import datetime

# Callback que la UI asignará para recibir la notificación de alarma
# Uso: time_tools.on_alarma = lambda msg: mostrar_mensaje(msg)
on_alarma = None


# ── Hora y fecha ──────────────────────────────────────────────────────────────

def hora_actual() -> str:
    ahora = datetime.now()
    return f"🕐 Son las {ahora.strftime('%H:%M')}"


def fecha_actual() -> str:
    ahora = datetime.now()
    dias   = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
    meses  = ["enero","febrero","marzo","abril","mayo","junio",
               "julio","agosto","septiembre","octubre","noviembre","diciembre"]
    dia_semana = dias[ahora.weekday()]
    return (f"📅 Hoy es {dia_semana} "
            f"{ahora.day} de {meses[ahora.month-1]} de {ahora.year}")


# ── Alarmas ───────────────────────────────────────────────────────────────────

def procesar_alarma(texto: str) -> str:
    """
    Detecta si es alarma a una hora fija («a las 8:30»)
    o temporizador («en 5 minutos / en 30 segundos»).
    """
    t = texto.lower()

    # Temporizador: «avísame en X minutos/segundos»
    match_min = re.search(r"en\s+(\d+)\s+minuto", t)
    match_seg = re.search(r"en\s+(\d+)\s+segundo", t)
    match_hor = re.search(r"en\s+(\d+)\s+hora", t)

    if match_min:
        segundos = int(match_min.group(1)) * 60
        return _poner_temporizador(segundos, f"{match_min.group(1)} minutos")
    if match_seg:
        segundos = int(match_seg.group(1))
        return _poner_temporizador(segundos, f"{match_seg.group(1)} segundos")
    if match_hor:
        segundos = int(match_hor.group(1)) * 3600
        return _poner_temporizador(segundos, f"{match_hor.group(1)} horas")

    # Alarma a hora fija: «a las 8:30» o «para las 20:00»
    match_hora = re.search(r"(\d{1,2})[:\.](\d{2})", t)
    if match_hora:
        h, m = int(match_hora.group(1)), int(match_hora.group(2))
        return _poner_alarma_hora(h, m)

    return ("No entendí la hora. Prueba:\n"
            "• «avísame en 10 minutos»\n"
            "• «alarma a las 8:30»")


def _poner_temporizador(segundos: int, etiqueta: str) -> str:
    def disparar():
        time.sleep(segundos)
        _notificar(f"⏰ ¡Temporizador de {etiqueta} completado!")

    threading.Thread(target=disparar, daemon=True).start()
    return f"⏱️ Temporizador puesto para {etiqueta}. Te aviso cuando acabe."


def _poner_alarma_hora(hora: int, minuto: int) -> str:
    def disparar():
        while True:
            ahora = datetime.now()
            if ahora.hour == hora and ahora.minute == minuto:
                _notificar(f"⏰ ¡Alarma! Son las {hora:02d}:{minuto:02d}")
                break
            time.sleep(20)  # Comprueba cada 20 segundos

    threading.Thread(target=disparar, daemon=True).start()
    return f"⏰ Alarma puesta para las {hora:02d}:{minuto:02d}."


def _notificar(mensaje: str):
    """Llama al callback de la UI si está asignado."""
    if callable(on_alarma):
        on_alarma(mensaje)