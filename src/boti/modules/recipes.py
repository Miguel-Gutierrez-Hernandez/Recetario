# modules/recipes.py — Recetario SQLite con sync y borrado en Notion

import sqlite3
import threading
import os
from config import DB_PATH

_notion_cliente = None
_notion_db_id   = None


def _inicializar_notion():
    global _notion_cliente, _notion_db_id
    try:
        from config import clave
        token = clave("NOTION_TOKEN")
        db_id = clave("NOTION_RECIPES_DB")
        if not token or not db_id:
            return
        from notion_client import Client
        _notion_cliente = Client(auth=token)
        _notion_db_id   = db_id
    except Exception:
        pass


def _notion_disponible() -> bool:
    return _notion_cliente is not None and _notion_db_id is not None


def _sync_a_notion(nombre: str, ingredientes: str, pasos: str, etiquetas: str, rid: int):
    def _enviar():
        try:
            resultado = _notion_cliente.pages.create(
                parent={"database_id": _notion_db_id},
                properties={
                    "Nombre": {
                        "title": [{"text": {"content": nombre[:100]}}]
                    },
                    "Ingredientes": {
                        "rich_text": [{"text": {"content": ingredientes[:2000]}}]
                    },
                    "Etiquetas": {
                        "rich_text": [{"text": {"content": etiquetas[:200]}}]
                    },
                },
                children=[
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [{"type": "text", "text": {"content": "Preparacion"}}]
                        }
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": pasos[:2000]}}]
                        }
                    },
                ],
            )
            notion_page_id = resultado["id"]
            con = sqlite3.connect(DB_PATH)
            cur = con.cursor()
            cur.execute(
                "UPDATE recetas SET sincronizada = 1, notion_page_id = ? WHERE id = ?",
                (notion_page_id, rid),
            )
            con.commit()
            con.close()
        except Exception:
            pass
    threading.Thread(target=_enviar, daemon=True).start()


def _borrar_de_notion(notion_page_id: str):
    def _eliminar():
        try:
            _notion_cliente.pages.update(
                page_id=notion_page_id,
                archived=True,
            )
        except Exception:
            pass
    threading.Thread(target=_eliminar, daemon=True).start()


def _conexion():
    return sqlite3.connect(DB_PATH)


RECETAS_INICIALES = [
    (
        "Tortilla espanola",
        "4 huevos, 3 patatas medianas, 1 cebolla, aceite de oliva, sal",
        "1. Pela y corta las patatas en laminas finas.\n"
        "2. Frie las patatas con la cebolla a fuego medio 15 min.\n"
        "3. Escurre el aceite. Bate los huevos con sal y mezcla.\n"
        "4. Cuaja en sarten tapada 4 min. Da la vuelta y cuaja 3 min mas.",
        "huevo, patata, espanola, tradicional",
    ),
    (
        "Pasta al pesto",
        "200g pasta, albahaca, 2 ajos, 30g pinones, 50g parmesano, aceite, sal",
        "1. Cuece la pasta en agua salada.\n"
        "2. Tritura albahaca, ajo, pinones y parmesano.\n"
        "3. Anade aceite hasta obtener salsa homogenea.\n"
        "4. Mezcla con la pasta escurrida y sirve.",
        "pasta, italiana, rapida",
    ),
    (
        "Gazpacho",
        "1kg tomates, 1 pepino, 1 pimiento rojo, 1 ajo, aceite, vinagre, sal",
        "1. Trocea todos los vegetales.\n"
        "2. Bate hasta obtener crema fina.\n"
        "3. Anade aceite, vinagre y sal.\n"
        "4. Refrigera minimo 1 hora.",
        "tomate, fria, verano, vegetariana",
    ),
    (
        "Arroz con leche",
        "200g arroz, 1L leche, 150g azucar, canela, piel de limon",
        "1. Calienta la leche con canela y limon.\n"
        "2. Anade el arroz y baja el fuego.\n"
        "3. Cocina 30-35 min removiendo.\n"
        "4. Anade azucar los ultimos 5 min. Sirve frio.",
        "postre, dulce, tradicional",
    ),
    (
        "Lentejas con verduras",
        "300g lentejas, zanahoria, puerro, patata, ajo, laurel, pimenton, aceite, sal",
        "1. Pica las verduras en trozos medianos.\n"
        "2. Sofrie ajo, puerro y zanahoria 5 min.\n"
        "3. Anade lentejas, patata, laurel y pimenton.\n"
        "4. Cubre con agua y cocina 35-40 min.",
        "legumbre, cuchara, invierno, economica",
    ),
]


def inicializar():
    con = _conexion()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recetas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre          TEXT NOT NULL,
            ingredientes    TEXT,
            pasos           TEXT,
            etiquetas       TEXT,
            sincronizada    INTEGER DEFAULT 0,
            notion_page_id  TEXT DEFAULT NULL,
            creada          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    for col, defn in [
        ("sincronizada",   "INTEGER DEFAULT 0"),
        ("notion_page_id", "TEXT DEFAULT NULL"),
    ]:
        try:
            cur.execute(f"ALTER TABLE recetas ADD COLUMN {col} {defn}")
        except Exception:
            pass

    cur.execute("SELECT COUNT(*) FROM recetas")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO recetas (nombre, ingredientes, pasos, etiquetas) VALUES (?,?,?,?)",
            RECETAS_INICIALES,
        )
    con.commit()
    con.close()
    _inicializar_notion()


# ── Comandos ──────────────────────────────────────────────

def buscar(texto: str) -> str:
    IGNORAR = {"receta", "de", "la", "el", "un", "una", "para", "con",
               "como", "hacer", "hago", "preparo", "cocinar", "plato", "se", "hace"}
    palabras = [p for p in texto.lower().split()
                if p not in IGNORAR and len(p) > 2]

    con = _conexion()
    cur = con.cursor()

    if not palabras:
        cur.execute("SELECT nombre, ingredientes, pasos FROM recetas LIMIT 3")
    else:
        cond = " OR ".join(
            ["nombre LIKE ? OR ingredientes LIKE ? OR etiquetas LIKE ?"] * len(palabras)
        )
        vals = [v for p in palabras for v in (f"%{p}%", f"%{p}%", f"%{p}%")]
        cur.execute(
            f"SELECT nombre, ingredientes, pasos FROM recetas WHERE {cond} LIMIT 3",
            vals,
        )

    filas = cur.fetchall()
    con.close()

    if not filas:
        return "No encontre ninguna receta. Prueba mis recetas para ver todas."

    if len(filas) == 1:
        return _formato_receta(*filas[0])

    opciones = "\n".join(f"  {i+1}. {f[0]}" for i, f in enumerate(filas))
    return f"Encontre varias recetas:\n{opciones}\n\nEscribe el nombre exacto para verla completa."


def listar() -> str:
    con = _conexion()
    cur = con.cursor()
    cur.execute("SELECT id, nombre, etiquetas, sincronizada FROM recetas ORDER BY nombre")
    filas = cur.fetchall()
    con.close()

    if not filas:
        return "No hay recetas guardadas aun."

    lineas = ["Recetario completo:\n"]
    for rid, nombre, etiquetas, sync in filas:
        icono = "[N]" if sync else "[L]"
        tag   = f" - {etiquetas}" if etiquetas else ""
        lineas.append(f"  {rid}. {nombre}{tag} {icono}")

    if _notion_disponible():
        lineas.append("\n[N] = en Notion   [L] = solo local")

    return "\n".join(lineas)


def guardar_desde_texto(texto: str) -> str:
    lineas = {}
    for l in texto.splitlines():
        if ":" in l:
            clave, _, valor = l.partition(":")
            lineas[clave.strip().lower()] = valor.strip()

    nombre       = lineas.get("nombre", "")
    ingredientes = lineas.get("ingredientes", "")
    pasos        = lineas.get("pasos", "")
    etiquetas    = lineas.get("etiquetas", "")

    if not nombre or not pasos:
        return "Faltan datos. Necesito al menos nombre y pasos."

    con = _conexion()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO recetas (nombre, ingredientes, pasos, etiquetas, sincronizada) "
        "VALUES (?,?,?,?,0)",
        (nombre, ingredientes, pasos, etiquetas),
    )
    rid = cur.lastrowid
    con.commit()
    con.close()

    if _notion_disponible():
        _sync_a_notion(nombre, ingredientes, pasos, etiquetas, rid)
        sufijo = " y enviada a Notion"
    else:
        sufijo = ""

    return f"Receta {nombre} guardada{sufijo}."


def borrar(rid: int) -> str:
    con = _conexion()
    cur = con.cursor()
    cur.execute("SELECT nombre, notion_page_id FROM recetas WHERE id = ?", (rid,))
    fila = cur.fetchone()

    if not fila:
        con.close()
        return f"No encontre la receta #{rid}."

    nombre, notion_page_id = fila
    cur.execute("DELETE FROM recetas WHERE id = ?", (rid,))
    con.commit()
    con.close()

    if notion_page_id and _notion_disponible():
        _borrar_de_notion(notion_page_id)
        sufijo = " y archivada en Notion"
    else:
        sufijo = ""

    return f"Receta {nombre} borrada{sufijo}."


def aniadir_interactivo() -> str:
    return (
        "Para anadir una receta escribe en este formato:\n\n"
        "nueva receta\n"
        "nombre: Nombre del plato\n"
        "ingredientes: ingrediente1, ingrediente2...\n"
        "pasos: 1. Paso uno. 2. Paso dos...\n"
        "etiquetas: pasta, italiana, rapida"
    )


def _formato_receta(nombre: str, ingredientes: str, pasos: str) -> str:
    return (
        f"Receta: {nombre}\n\n"
        f"Ingredientes:\n{ingredientes}\n\n"
        f"Preparacion:\n{pasos}"
    )