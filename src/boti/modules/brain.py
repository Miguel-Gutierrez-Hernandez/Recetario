# modules/brain.py — Cerebro de Boti (sin LLM, 100% local)

from utils.keywords import detectar_intencion, texto_ayuda
from modules import recipes, write_note, time_tools
from modules.search_wikipedia import buscar as wiki_buscar
from config import NOMBRE

SALUDOS = [
    f"Hola! Soy {NOMBRE}. En que te ayudo?",
    f"Buenas! Aqui {NOMBRE}, dime.",
    f"Hola! Dime que necesitas.",
]

_saludo_idx = 0


def responder(texto: str) -> str:
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

    return (
        f"No entendi eso.\n\n"
        + texto_ayuda()
    )