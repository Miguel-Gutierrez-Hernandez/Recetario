# modules/play_spotify.py — Buscar y abrir canciones/playlists en Spotify de forma nativa
from urllib.parse import quote_plus

_PALABRAS_IGNORAR = {
    "spotify", "pon", "poner", "busca", "buscar", "abre", "abrir",
    "reproduce", "reproducir", "cancion", "musica", "playlist",
    "lista", "quiero", "escuchar", "toca", "tocar"
}

_PALABRAS_PLAYLIST = {
    "playlist", "lista", "mis canciones", "mi lista",
    "lista de reproduccion", "mis listas"
}


def abrir(texto: str, page=None) -> str:
    t = texto.lower()
    es_playlist = any(p in t for p in _PALABRAS_PLAYLIST)

    if es_playlist:
        return _abrir_playlist(texto, page)
    else:
        return _buscar_cancion(texto, page)


def _buscar_cancion(texto: str, page=None) -> str:
    termino = _extraer_termino(texto)
    if not termino:
        return (
            "¿Qué quieres escuchar? Prueba:\n"
            "- pon en spotify flamenco\n"
            "- spotify Bad Bunny"
        )

    url_app = f"spotify:search:{quote_plus(termino)}"
    url_web = f"https://open.spotify.com/search/{quote_plus(termino)}"

    try:
        if page:
            page.launch_url(url_app)
        else:
            import webbrowser
            webbrowser.open(url_app)
        return f"Buscando en Spotify: {termino}"
    except Exception:
        try:
            if page:
                page.launch_url(url_web)
            else:
                import webbrowser
                webbrowser.open(url_web)
            return f"Abriendo Spotify: {termino}"
        except Exception as e:
            return f"No pude abrir Spotify: {e}"


def _abrir_playlist(texto: str, page=None) -> str:
    from config import clave
    client_id = clave("SPOTIFY_CLIENT_ID")

    if not client_id:
        url_app = "spotify:user:library"
        try:
            if page:
                page.launch_url(url_app)
            else:
                import webbrowser
                webbrowser.open(url_app)
            return "Abriendo tu biblioteca de Spotify."
        except Exception:
            return "No se pudo abrir la biblioteca de Spotify."

    termino = _extraer_termino(texto)
    return _buscar_playlist_api(termino, client_id, clave("SPOTIFY_CLIENT_SECRET"), page)


def _buscar_playlist_api(termino: str, client_id: str, client_secret: str, page=None) -> str:
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyOAuth

        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://localhost:8888/callback",
            scope="playlist-read-private playlist-read-collaborative",
        ))

        resultados = sp.search(q=termino, type="playlist", limit=5)
        items = resultados.get("playlists", {}).get("items", [])

        if not items:
            return f"No encontré ninguna playlist con: {termino}"

        playlist = items[0]
        url_app = f"spotify:playlist:{playlist['id']}"
        
        if page:
            page.launch_url(url_app)
        else:
            import webbrowser
            webbrowser.open(url_app)
        return f"Abriendo playlist: {playlist['name']}"

    except Exception:
        # Fallback seguro para que no se congele Android si la autenticación OAuth falla
        url_fallback = f"https://open.spotify.com/search/{quote_plus(termino)}/playlists"
        if page:
            page.launch_url(url_fallback)
        else:
            import webbrowser
            webbrowser.open(url_fallback)
        return f"Buscando playlist en Spotify: {termino}"


def _extraer_termino(texto: str) -> str:
    palabras = texto.lower().split()
    resultado = [p for p in palabras if p not in _PALABRAS_IGNORAR]
    return " ".join(resultado).strip()