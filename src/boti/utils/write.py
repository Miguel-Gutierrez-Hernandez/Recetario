# modules/write_note.py — Notas locales (SQLite) con sync automatico a Notion

import sqlite3
import threading
import os
from config import DB_PATH

_notion_cliente = None
_notion_db_id   = None


def _inicializar_notion():
    global _notion_cliente, _notion_db_id
    try:
        from dotenv import load_dotenv
        load_dotenv()
        token = os.getenv("NOTION_TOKEN", "")
        db_id = os.getenv("NOTION_NOTES_DB", "")
        if not token or not db_id:
            return
        from notion_client import Client
        _notion_cliente = Client(auth=token)
        _notion_db_id   = db_id
    except Exception:
        pass


def _notion_disponible() -> bool:
    return _notion_cliente is not None and _notion_db_id is not None


def _sync_a_notion(texto: str, nid: int):
    def _enviar():
        try:
            _notion_cliente.pages.create(
                parent={"database_id": _notion_db_id},
                properties={
                    "Nombre": {
                        "title": [{"text": {"content": texto[:100]}}]
                    }
                },
                children=[{
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": texto}}]
                    }
                }],
            )
            _marcar_sincronizada(nid)
        except Exception:
            pass
    threading.Thread(target=_enviar, daemon=True).start()


def _conexion():
    return sqlite3.connect(DB_PATH)


def inicializar():
    con = _conexion()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            texto        TEXT NOT NULL,
            sincronizada INTEGER DEFAULT 0,
            creada       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.commit()
    con.close()
    _inicializar_notion()


def guardar(texto: str) -> str:
    PREFIJOS = [
        "anota:", "anota", "apunta:", "apunta",
        "guarda:", "guarda", "nota:", "recuerda que",
        "escribe que", "apuntate",
    ]
    contenido = texto.strip()
    t = contenido.lower()
    for p in PREFIJOS:
        if t.startswith(p):
            contenido = contenido[len(p):].strip(" :,-")
            break

    if not contenido:
        return "Que quieres que anote? No vi contenido despues del comando."

    con = _conexion()
    cur = con.cursor()
    cur.execute("INSERT INTO notas (texto, sincronizada) VALUES (?, 0)", (contenido,))
    nid = cur.lastrowid
    con.commit()
    con.close()

    if _notion_disponible():
        _sync_a_notion(contenido, nid)
        sufijo = " y enviada a Notion"
    else:
        sufijo = ""

    preview = contenido[:50] + ("..." if len(contenido) > 50 else "")
    return f"Nota guardada{sufijo}: {preview}"


def listar() -> str:
    con = _conexion()
    cur = con.cursor()
    cur.execute(
        "SELECT id, texto, sincronizada, creada FROM notas "
        "ORDER BY creada DESC LIMIT 10"
    )
    filas = cur.fetchall()
    con.close()

    if not filas:
        return "No tienes notas guardadas aun."

    lineas = ["Tus notas recientes:\n"]
    for nid, texto, sync, creada in filas:
        fecha   = creada[:10] if creada else ""
        icono   = "[N]" if sync else "[L]"
        preview = texto[:60] + ("..." if len(texto) > 60 else "")
        lineas.append(f"  #{nid} {fecha} {icono} {preview}")

    if _notion_disponible():
        lineas.append("\n[N] = en Notion   [L] = solo local")

    return "\n".join(lineas)


def borrar(texto: str) -> str:
    numeros = [s for s in texto.split() if s.isdigit()]
    if not numeros:
        return "Dime el numero de la nota. Ejemplo: borra nota 3"

    nid = int(numeros[0])
    con = _conexion()
    cur = con.cursor()
    cur.execute("SELECT texto FROM notas WHERE id = ?", (nid,))
    fila = cur.fetchone()

    if not fila:
        con.close()
        return f"No encontre la nota #{nid}."

    cur.execute("DELETE FROM notas WHERE id = ?", (nid,))
    con.commit()
    con.close()

    preview = fila[0][:50] + ("..." if len(fila[0]) > 50 else "")
    return f"Nota #{nid} borrada: {preview}"


def _marcar_sincronizada(nid: int):
    try:
        con = _conexion()
        cur = con.cursor()
        cur.execute("UPDATE notas SET sincronizada = 1 WHERE id = ?", (nid,))
        con.commit()
        con.close()
    except Exception:
        pass