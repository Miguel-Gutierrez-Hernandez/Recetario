# modules/brain.py — Cerebro de Boti

from utils.keywords import detectar_intencion, texto_ayuda
from modules import recipes, write_note, time_tools
from modules.search_wikipedia import buscar as wiki_buscar
from modules.play_youtube import abrir as youtube_abrir
from modules.play_spotify import abrir as spotify_abrir
from modules.open_whatsapp import abrir as whatsapp_abrir
from config import NOMBRE

SALUDOS = [
    f"¡Hola! Soy {NOMBRE}. ¿En qué te ayudo?",
    f"¡Buenas! Aquí {NOMBRE}, dime.",
    f"¡Hola! Dime qué necesitas.",
]

_saludo_idx = 0


# 📌 CAMBIO CLAVE: Añadir ', page=None' para que acepte el parámetro de Flet
def responder(texto: str, page=None) -> str:
    intencion, argumento = detectar_intencion(texto)

    if intencion == "saludo":
        global _saludo_idx
        respuesta = SALUDOS[_saludo_idx % len(SALUDOS)]
        _saludo_idx += 1
        return respuesta

    if intencion == "ayuda":
        return texto_ayuda()

    if intencion == "receta_buscar":
        return recipes.buscar(argumento)

    if intencion == "receta_listar":
        return recipes.listar()

    if intencion == "receta_aniadir":
        return recipes.aniadir_interactivo()

    if intencion == "nota_guardar":
        return write_note.guardar(texto)

    if intencion == "nota_listar":
        return write_note.listar()

    if intencion == "nota_borrar":
        return write_note.borrar(argumento)

    if intencion == "hora_actual":
        return time_tools.hora_actual()

    if intencion == "fecha_actual":
        return time_tools.fecha_actual()

    if intencion == "alarma_poner":
        return time_tools.procesar_alarma(argumento)

    if intencion == "wikipedia":
        return wiki_buscar(texto)

    # 📌 CAMBIO CLAVE: Pasar el objeto 'page' a tus tres nuevos módulos móviles
    if intencion == "youtube":
        return youtube_abrir(texto, page)

    if intencion == "spotify":
        return spotify_abrir(texto, page)

    if intencion == "whatsapp":
        return whatsapp_abrir(texto, page)

    return f"No entendí eso.\n\n" + texto_ayuda()