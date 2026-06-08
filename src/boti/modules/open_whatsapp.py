# modules/open_whatsapp.py — Prepara mensaje y abre WhatsApp de forma nativa
from urllib.parse import quote

_PALABRAS_IGNORAR = {
    "whatsapp", "manda", "mandar", "envia", "enviar", "mensaje",
    "escribe", "escribir", "di", "dile", "a"
}

_PREFIJOS_DESTINATARIO = ["a ", "para "]


def abrir(texto: str, page=None) -> str:
    """Detecta destinatario y mensaje del texto y lo abre con Flet o webbrowser."""
    destinatario, mensaje = _parsear(texto)

    if not mensaje:
        return (
            "No entendí el mensaje. Prueba:\n"
            "- manda whatsapp a Juan que llego tarde\n"
            "- whatsapp a 612345678 hola que tal"
        )

    numero = _extraer_numero(destinatario)
    if numero:
        url = f"https://wa.me/{numero}?text={quote(mensaje)}"
    else:
        url = f"https://wa.me/?text={quote(mensaje)}"

    try:
        # 📌 Si tenemos la página de Flet, usamos el método nativo móvil, si no, fallback a PC
        if page:
            page.launch_url(url)
        else:
            import webbrowser
            webbrowser.open(url)

        if numero:
            return f"Abriendo WhatsApp con {destinatario}: {mensaje[:40]}..."
        else:
            return (
                f"Abriendo WhatsApp con el mensaje listo:\n{mensaje[:60]}...\n\n"
                f"Selecciona el contacto en WhatsApp y pulsa enviar."
            )
    except Exception as e:
        return f"No pude abrir WhatsApp: {e}"


def _parsear(texto: str) -> tuple[str, str]:
    t = texto.lower()
    for p in sorted(_PALABRAS_IGNORAR, key=len, reverse=True):
        t = t.replace(p, " ")
    t = " ".join(t.split())

    destinatario = ""
    mensaje = texto

    for prefijo in _PREFIJOS_DESTINATARIO:
        if prefijo in t:
            partes = t.split(prefijo, 1)
            if len(partes) == 2:
                resto = partes[1].strip()
                for sep in [" que ", ": ", ", "]:
                    if sep in resto:
                        sub = resto.split(sep, 1)
                        destinatario = sub[0].strip()
                        mensaje = sub[1].strip()
                        return destinatario, mensaje
                palabras = resto.split()
                if len(palabras) > 1:
                    destinatario = palabras[0]
                    mensaje = " ".join(palabras[1:])
                    return destinatario, mensaje

    return destinatario, mensaje


def _extraer_numero(texto: str) -> str:
    digitos = "".join(c for c in texto if c.isdigit())
    if len(digitos) >= 9:
        if not digitos.startswith("34") and len(digitos) == 9:
            digitos = "34" + digitos
        return digitos
    return ""