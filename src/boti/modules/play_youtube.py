# modules/play_youtube.py — Abre YouTube de forma nativa
from urllib.parse import quote_plus

_PALABRAS_IGNORAR = {
    "pon", "poner", "busca", "buscar", "abre", "abrir",
    "youtube", "video", "musica", "cancion", "reproduce",
    "quiero", "escuchar", "ver", "busca"
}


def abrir(texto: str, page=None) -> str:
    termino = _extraer_termino(texto)
    if not termino:
        return "¿Qué quieres buscar en YouTube? Ejemplo: pon en youtube flamenco"

    url = f"https://www.youtube.com/results?search_query={quote_plus(termino)}"
    try:
        if page:
            page.launch_url(url)
        else:
            import webbrowser
            webbrowser.open(url)
        return f"Abriendo YouTube con: {termino}"
    except Exception as e:
        return f"No pude abrir YouTube: {e}"


def _extraer_termino(texto: str) -> str:
    palabras = texto.lower().split()
    resultado = [p for p in palabras if p not in _PALABRAS_IGNORAR]
    return " ".join(resultado).strip()