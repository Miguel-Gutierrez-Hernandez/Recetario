# modules/search_wikipedia.py — Búsqueda en Wikipedia (resumen corto)

# Palabras que se eliminan del texto para extraer el término de búsqueda
_PALABRAS_CLAVE = [
    "qué es", "que es", "quién es", "quien es",
    "cuéntame sobre", "cuentame sobre",
    "información sobre", "informacion sobre",
    "busca", "buscar", "wikipedia",
    "háblame de", "hablame de",
    "dime qué es", "dime que es",
]


def buscar(texto: str) -> str:
    """
    Extrae el término del texto, busca en Wikipedia en español
    y devuelve un resumen de 2-3 frases.
    """
    try:
        import wikipediaapi
        _wiki = wikipediaapi.Wikipedia(
            language="es",
            user_agent="Boti-AsistentePersonal/1.0"
        )
    except ImportError:
        return "⚠️ Error: La librería de Wikipedia no está instalada en este dispositivo."
    
    termino = _extraer_termino(texto)

    if not termino:
        return "No entendí sobre qué quieres que busque. Prueba: «qué es la fotosíntesis»"

    try:
        pagina = _wiki.page(termino)

        if not pagina.exists():
            # Intenta con la primera letra en mayúscula
            pagina = _wiki.page(termino.capitalize())

        if not pagina.exists():
            return f"No encontré nada en Wikipedia sobre «{termino}»."

        resumen = _primeras_frases(pagina.summary, n=3)
        return f"📖 {pagina.title}\n\n{resumen}"

    except Exception as e:
        return f"Error al buscar en Wikipedia: {e}"


# ── Helpers ───────────────────────────────────────────────

def _extraer_termino(texto: str) -> str:
    """Elimina las palabras clave de activación y devuelve el término limpio."""
    t = texto.lower().strip()
    for clave in sorted(_PALABRAS_CLAVE, key=len, reverse=True):
        if clave in t:
            t = t.replace(clave, "").strip(" :,-")
            break
    return t.strip()


def _primeras_frases(texto: str, n: int = 3) -> str:
    """Devuelve las primeras n frases de un texto."""
    if not texto:
        return "Sin descripción disponible."

    frases = []
    for frase in texto.replace("\n", " ").split(". "):
        frase = frase.strip()
        if frase:
            frases.append(frase if frase.endswith(".") else frase + ".")
        if len(frases) >= n:
            break

    return " ".join(frases)