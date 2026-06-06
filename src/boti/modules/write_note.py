# modules/write_note.py — Notas locales en SQLite

import sqlite3
from config import DB_PATH


def _conexion():
    return sqlite3.connect(DB_PATH)


def inicializar():
    """Crea la tabla de notas si no existe."""
    con = _conexion()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            texto   TEXT NOT NULL,
            creada  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.commit()
    con.close()


# ── Comandos ──────────────────────────────────────────────────────────────────

def guardar(texto: str) -> str:
    """Guarda una nota. Elimina prefijos de comando del texto."""
    PREFIJOS = ["anota:", "anota", "apunta:", "apunta", "guarda:", "guarda",
                "nota:", "recuerda que", "escribe que", "apúntate"]

    contenido = texto.strip()
    t = contenido.lower()
    for p in PREFIJOS:
        if t.startswith(p):
            contenido = contenido[len(p):].strip(" :,-")
            break

    if not contenido:
        return "¿Qué quieres que anote? No vi ningún contenido después del comando."

    con = _conexion()
    cur = con.cursor()
    cur.execute("INSERT INTO notas (texto) VALUES (?)", (contenido,))
    nid = cur.lastrowid
    con.commit()
    con.close()

    preview = contenido[:50] + ("…" if len(contenido) > 50 else "")
    return f"📝 Nota #{nid} guardada: «{preview}»"


def listar() -> str:
    """Devuelve las últimas 10 notas."""
    con = _conexion()
    cur = con.cursor()
    cur.execute(
        "SELECT id, texto, creada FROM notas ORDER BY creada DESC LIMIT 10"
    )
    filas = cur.fetchall()
    con.close()

    if not filas:
        return "No tienes notas guardadas aún."

    lineas = ["📋 Tus notas recientes:\n"]
    for nid, texto, creada in filas:
        fecha = creada[:10] if creada else ""
        preview = texto[:60] + ("…" if len(texto) > 60 else "")
        lineas.append(f"  #{nid} [{fecha}] {preview}")
    return "\n".join(lineas)


def borrar(texto: str) -> str:
    """Borra una nota por su número. Extrae el número del texto."""
    numeros = [s for s in texto.split() if s.isdigit()]
    if not numeros:
        return ("Dime el número de la nota que quieres borrar.\n"
                "Ejemplo: «borra nota 3»\n"
                "Escribe «mis notas» para ver los números.")

    nid = int(numeros[0])
    con = _conexion()
    cur = con.cursor()
    cur.execute("SELECT texto FROM notas WHERE id = ?", (nid,))
    fila = cur.fetchone()

    if not fila:
        con.close()
        return f"No encontré la nota #{nid}. Escribe «mis notas» para ver las disponibles."

    cur.execute("DELETE FROM notas WHERE id = ?", (nid,))
    con.commit()
    con.close()

    preview = fila[0][:50] + ("…" if len(fila[0]) > 50 else "")
    return f"🗑️ Nota #{nid} borrada: «{preview}»"