# src/boti/modules/write_note.py
import sqlite3, datetime, threading
from config import DB_PATH

_notion_cliente = None
_notion_db_id   = None

def _inicializar_notion():
    global _notion_cliente, _notion_db_id
    try:
        from config import clave
        token = clave("NOTION_TOKEN")
        db_id = clave("NOTION_NOTES_DB")
        
        # 📌 SI NO HAY CLAVES (Como pasa en Android al principio), ABORTAMOS AL INSTANTE
        if not token or not db_id:
            _notion_cliente = None
            _notion_db_id = None
            print("⚠️ Notion no configurado. Trabajando en modo local.")
            return
            
        db_id = db_id.replace("-", "").strip()
        from notion_client import Client
        _notion_cliente = Client(auth=token)
        _notion_db_id   = db_id
        print("✅ Cliente de Notion inicializado correctamente.")
    except Exception as e:
        _notion_cliente = None
        _notion_db_id = None
        print(f"❌ Error al inicializar Notion: {e}")

def _notion_disponible() -> bool:
    return _notion_cliente is not None and _notion_db_id is not None

def _sync_a_notion(titulo: str, texto: str, fecha: str, nid: int):
    def _enviar():
        try:
            # Enviamos a Notion el Título (Name) Y la Fecha (Fecha)
            resultado = _notion_cliente.pages.create(
                parent={"database_id": _notion_db_id},
                properties={
                    "Name": {
                        "title": [{"text": {"content": titulo[:100]}}]
                    },
                    # ⏰ Añadimos de nuevo la columna Fecha como tipo texto (rich_text)
                    # IMPORTANTE: Asegúrate de que en tu Notion la columna se llame exactamente "Fecha"
                    "Fecha": {
                        "rich_text": [{"text": {"content": fecha}}]
                    },
                },
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": texto[:2000]}}]
                        }
                    },
                ],
            )
            # Guardamos el ID de Notion en nuestra fila local
            notion_page_id = resultado["id"]
            con = sqlite3.connect(DB_PATH)
            cur = con.cursor()
            cur.execute(
                "UPDATE notas SET sincronizada = 1, notion_page_id = ? WHERE id = ?",
                (notion_page_id, nid),
            )
            con.commit()
            con.close()
        except Exception as e:
            print(f"❌ Error al subir nota a Notion: {e}")
    threading.Thread(target=_enviar, daemon=True).start()

def _conexion():
    return sqlite3.connect(DB_PATH)

def inicializar():
    con = _conexion()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            texto           TEXT NOT NULL,
            fecha           TEXT NOT NULL,  -- 👈 Cambiado a TEXT para guardar la hora exacta real
            sincronizada    INTEGER DEFAULT 0,
            notion_page_id  TEXT DEFAULT NULL
        )
    """)
    for col, defn in [("sincronizada", "INTEGER DEFAULT 0"), ("notion_page_id", "TEXT DEFAULT NULL")]:
        try:
            cur.execute(f"ALTER TABLE notas ADD COLUMN {col} {defn}")
        except Exception:
            pass
    con.commit()
    con.close()
    _inicializar_notion()


def guardar_nota(texto_completo: str) -> str:
    if "|" in texto_completo:
        titulo, texto = texto_completo.split("|", 1)
    else:
        titulo = "Nota sin título"
        texto = texto_completo

    ahora_local = datetime.datetime.now()
    fecha_legible = ahora_local.strftime("%d-%m-%Y %H:%M:%S")

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    texto_guardar = f"📌 {titulo}\n\n{texto}"
    
    cur.execute(
        "INSERT INTO notas (texto, fecha, sincronizada) VALUES (?, ?, 0)", 
        (texto_guardar, fecha_legible)
    )
    nid = cur.lastrowid # 👈 Obtenemos el id local de la nota
    con.commit()
    con.close()

    if _notion_disponible():
        # Pasamos EXACTAMENTE los 4 argumentos que espera la función de abajo:
        _sync_a_notion(titulo, texto, fecha_legible, nid)
        sufijo = " y enviada a Notion"
    else:
        sufijo = ""

    return f"Nota guardada localmente{sufijo}."

def listar_notas():
    con = _conexion()
    cur = con.cursor()
    cur.execute("SELECT id, texto, fecha, sincronizada FROM notas ORDER BY fecha DESC")
    filas = cur.fetchall()
    con.close()
    return filas

# Asegúrate de que este bloque esté hacia el final de src/boti/modules/write_note.py

def _borrar_de_notion(notion_page_id: str):
    """Archiva de forma asíncrona la página en Notion para que no dé lag en la app."""
    def _eliminar():
        try:
            _notion_cliente.pages.update(
                page_id=notion_page_id,
                archived=True,
            )
            print(f"🗑️ Nota archivada con éxito en Notion (Page ID: {notion_page_id})")
        except Exception as e:
            print(f"❌ Error al archivar en Notion: {e}")
            
    threading.Thread(target=_eliminar, daemon=True).start()


def borrar_nota(nid: int) -> str:
    """Borra la nota de la base de datos SQLite local y de Notion si está sincronizada."""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT notion_page_id FROM notas WHERE id = ?", (nid,))
    fila = cur.fetchone()
    
    if not fila:
        con.close()
        return f"No encontré la nota #{nid}."
        
    notion_page_id = fila[0]
    cur.execute("DELETE FROM notas WHERE id = ?", (nid,))
    con.commit()
    con.close()
    
    # Ahora sí encontrará la función perfectamente ✅
    if notion_page_id and _notion_disponible():
        _borrar_de_notion(notion_page_id)
        sufijo = " y archivada en Notion"
    else:
        sufijo = ""
        
    return f"Nota #{nid} eliminada{sufijo}."