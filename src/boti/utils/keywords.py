# keywords.py — Diccionario de intenciones y palabras clave

# Cada intención tiene:
#   "claves"   → palabras que la activan (cualquiera es suficiente)
#   "desc"     → descripción corta para el menú de ayuda
#   "ejemplo"  → ejemplo de uso

INTENCIONES = {

    # ── Recetas ───────────────────────────────────────────
    "receta_buscar": {
        "claves": ["receta", "ingredientes", "cómo hago", "cómo se hace",
                   "cómo preparo", "preparar", "cocinar", "plato", "hacer"],
        "desc":   "Buscar una receta",
        "ejemplo": "receta de tortilla",
    },
    "receta_listar": {
        "claves": ["mis recetas", "todas las recetas", "lista de recetas",
                   "qué recetas", "recetas disponibles", "recetario"],
        "desc":   "Ver todas las recetas",
        "ejemplo": "mis recetas",
    },
    "receta_añadir": {
        "claves": ["añade receta", "nueva receta", "guarda receta",
                   "agrega receta", "crear receta"],
        "desc":   "Añadir una receta nueva",
        "ejemplo": "nueva receta",
    },

    # ── Notas ─────────────────────────────────────────────
    "nota_guardar": {
        "claves": ["anota", "apunta", "guarda", "nota:", "recuerda que",
                   "escribe que", "apúntate"],
        "desc":   "Guardar una nota",
        "ejemplo": "anota: comprar leche",
    },
    "nota_listar": {
        "claves": ["mis notas", "ver notas", "lista de notas",
                   "qué notas", "notas guardadas", "muéstrame las notas"],
        "desc":   "Ver las notas guardadas",
        "ejemplo": "mis notas",
    },
    "nota_borrar": {
        "claves": ["borra nota", "elimina nota", "borrar nota", "eliminar nota"],
        "desc":   "Borrar una nota",
        "ejemplo": "borra nota 2",
    },

    # ── Tiempo ────────────────────────────────────────────
    "hora_actual": {
        "claves": ["qué hora es", "hora actual", "dime la hora",
                   "qué hora", "hora es"],
        "desc":   "Ver la hora actual",
        "ejemplo": "qué hora es",
    },
    "fecha_actual": {
        "claves": ["qué día es", "fecha de hoy", "qué fecha", "día de hoy",
                   "fecha actual", "qué día"],
        "desc":   "Ver la fecha de hoy",
        "ejemplo": "qué día es hoy",
    },
    "alarma_poner": {
        "claves": ["pon una alarma", "poner alarma", "alarma a las",
                   "alarma para las", "ponme una alarma", "temporizador",
                   "pon un temporizador", "avísame en"],
        "desc":   "Poner una alarma o temporizador",
        "ejemplo": "alarma a las 8:30 / avísame en 5 minutos",
    },

    # ── Meta ──────────────────────────────────────────────
    "ayuda": {
        "claves": ["ayuda", "help", "qué puedes hacer", "comandos",
                   "qué sabes hacer", "para qué sirves", "qué haces"],
        "desc":   "Ver lista de comandos",
        "ejemplo": "ayuda",
    },
    "saludo": {
        "claves": ["hola", "buenos días", "buenas tardes", "buenas noches",
                   "hey", "ey boti", "boti"],
        "desc":   "Saludar a Boti",
        "ejemplo": "hola boti",
    },
}

# Prefijos de activación por nombre (se eliminan antes de procesar el comando)
PREFIJOS_NOMBRE = ["boti,", "boti:", "boti"]


def detectar_intencion(texto: str) -> tuple[str | None, str]:
    """
    Analiza el texto y devuelve (intencion, texto_limpio).
    texto_limpio es el texto sin el prefijo de activación ni la palabra clave.
    Devuelve (None, texto) si no se detecta ninguna intención.
    """
    t = texto.lower().strip()

    # Elimina prefijo de nombre si existe
    for prefijo in PREFIJOS_NOMBRE:
        if t.startswith(prefijo):
            t = t[len(prefijo):].strip()
            break

    # Busca la intención con la clave más larga que coincida (evita falsos positivos)
    mejor_intencion = None
    mejor_clave = ""

    for intencion, datos in INTENCIONES.items():
        for clave in datos["claves"]:
            if clave in t and len(clave) > len(mejor_clave):
                mejor_intencion = intencion
                mejor_clave = clave

    # Texto limpio: elimina la clave detectada para extraer el argumento
    texto_limpio = t.replace(mejor_clave, "").strip(" :,-") if mejor_clave else t

    return mejor_intencion, texto_limpio


def texto_ayuda() -> str:
    """Genera el texto de ayuda con todos los comandos disponibles."""
    lineas = ["📋 Esto es lo que sé hacer:\n"]
    for datos in INTENCIONES.values():
        if datos["desc"] == "Saludar a Boti":
            continue  # No hace falta listar el saludo
        lineas.append(f"• {datos['desc']}\n  Ejemplo: «{datos['ejemplo']}»")
    return "\n".join(lineas)