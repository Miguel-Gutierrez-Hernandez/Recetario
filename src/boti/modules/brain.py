# modules/brain.py — Cerebro de Boti (sin LLM, 100% local)

from utils.keywords import detectar_intencion, texto_ayuda
from modules import recipes, write_note, time_tools
from config import NOMBRE

SALUDOS = [
    f"¡Hola! Soy {NOMBRE}. ¿En qué te ayudo?",
    f"¡Buenas! Aquí {NOMBRE}, dime.",
    f"¡Hola! Dime qué necesitas.",
]

_saludo_idx = 0


def responder(texto: str) -> str:
    """
    Punto de entrada principal.
    Detecta la intención y delega en el módulo correspondiente.
    """
    intencion, argumento = detectar_intencion(texto)

    # ── Saludo ────────────────────────────────────────────
    if intencion == "saludo":
        global _saludo_idx
        respuesta = SALUDOS[_saludo_idx % len(SALUDOS)]
        _saludo_idx += 1
        return respuesta

    # ── Ayuda ─────────────────────────────────────────────
    if intencion == "ayuda":
        return texto_ayuda()

    # ── Recetas ───────────────────────────────────────────
    if intencion == "receta_buscar":
        return recipes.buscar(argumento)

    if intencion == "receta_listar":
        return recipes.listar()

    if intencion == "receta_añadir":
        return recipes.añadir_interactivo()

    # ── Notas ─────────────────────────────────────────────
    if intencion == "nota_guardar":
        return write_note.guardar(texto)   # texto completo para extraer el contenido

    if intencion == "nota_listar":
        return write_note.listar()

    if intencion == "nota_borrar":
        return write_note.borrar(argumento)

    # ── Tiempo ────────────────────────────────────────────
    if intencion == "hora_actual":
        return time_tools.hora_actual()

    if intencion == "fecha_actual":
        return time_tools.fecha_actual()

    if intencion == "alarma_poner":
        return time_tools.procesar_alarma(argumento)

    # ── No entendido ──────────────────────────────────────
    return (
        f"No entendí «{texto[:40]}».\n\n"
        + texto_ayuda()
    )