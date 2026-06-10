# modules/notion_sync.py — Sincronización bidireccional Notion <-> SQLite utilizando requests puro

import sqlite3
import threading
import requests
from config import DB_PATH

# Versión de la API de Notion estable y recomendada
NOTION_API_VERSION = "2022-06-28"


def _obtener_config_notas():
    """Devuelve (headers, db_id) para notas o (None, None) si no está configurado."""
    try:
        from config import clave
        token = clave("NOTION_TOKEN")
        db_id = clave("NOTION_NOTES_DB")
        if not token or not db_id:
            return None, None
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json"
        }
        return headers, db_id.replace("-", "").strip()
    except Exception:
        return None, None


def _obtener_config_recetas():
    """Devuelve (headers, db_id) para recetas o (None, None) si no está configurado."""
    try:
        from config import clave
        token = clave("NOTION_TOKEN")
        db_id = clave("NOTION_RECIPES_DB")
        if not token or not db_id:
            return None, None
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json"
        }
        return headers, db_id.replace("-", "").strip()
    except Exception:
        return None, None


# ── Sync de Notas ─────────────────────────────────────────

def sync_notas(callback=None):
    """
    Descarga de Notion las notas que no existen en SQLite local utilizando requests.
    """
    def _proceso():
        headers, db_id = _obtener_config_notas()
        if not headers:
            if callback:
                callback(False, "Notion no configurado")
            return

        try:
            # Obtiene IDs de páginas Notion ya conocidas en SQLite
            con = sqlite3.connect(DB_PATH)
            cur = con.cursor()
            cur.execute("SELECT notion_page_id FROM notas WHERE notion_page_id IS NOT NULL")
            ids_locales = {r[0] for r in cur.fetchall()}
            con.close()

            nuevas = 0
            cursor_notion = None
            url_query = f"https://api.notion.com/v1/databases/{db_id}/query"

            while True:
                payload = {"page_size": 100}
                if cursor_notion:
                    payload["start_cursor"] = cursor_notion

                # 📌 Petición POST pura inspirada en tu código
                response = requests.post(url_query, json=payload, headers=headers)
                response.raise_for_status()
                resultado = response.json()
                
                paginas = resultado.get("results", [])

                for pagina in paginas:
                    pid = pagina["id"]
                    if pid in ids_locales:
                        continue  # Ya la tenemos

                    # Extrae título
                    props = pagina.get("properties", {})
                    titulo = ""
                    for key in ["Name", "Nombre", "name", "nombre", "Title", "title"]:
                        t = props.get(key, {}).get("title", [])
                        if t:
                            titulo = t[0].get("text", {}).get("content", "")
                            break

                    # Extrae fecha
                    fecha = pagina.get("created_time", "")[:19].replace("T", " ")

                    # Extrae contenido de los bloques utilizando GET puro
                    try:
                        url_bloques = f"https://api.notion.com/v1/blocks/{pid}/children"
                        res_bloques = requests.get(url_bloques, headers=headers)
                        res_bloques.raise_for_status()
                        bloques = res_bloques.json()

                        contenido = "\n".join(
                            b.get("paragraph", {})
                             .get("rich_text", [{}])[0]
                             .get("text", {})
                             .get("content", "")
                            for b in bloques.get("results", [])
                            if b.get("type") == "paragraph"
                               and b.get("paragraph", {}).get("rich_text")
                        )
                    except Exception:
                        contenido = ""

                    texto_guardar = f"📌 {titulo}\n\n{contenido}" if titulo else contenido

                    # Inserta en SQLite
                    con = sqlite3.connect(DB_PATH)
                    cur = con.cursor()
                    cur.execute(
                        "INSERT INTO notas (texto, fecha, sincronizada, notion_page_id) "
                        "VALUES (?, ?, 1, ?)",
                        (texto_guardar, fecha, pid),
                    )
                    con.commit()
                    con.close()
                    nuevas += 1

                if not resultado.get("has_more"):
                    break
                cursor_notion = resultado.get("next_cursor")

            msg = f"Sync completado: {nuevas} nota(s) nueva(s) de Notion." if nuevas else "Todo sincronizado."
            if callback:
                callback(True, msg)

        except Exception as e:
            if callback:
                callback(False, f"Error al sincronizar notas: {e}")

    threading.Thread(target=_proceso, daemon=True).start()


# ── Sync de Recetas ───────────────────────────────────────

def sync_recetas(callback=None):
    """
    Descarga de Notion las recetas que no existen en SQLite local utilizando requests.
    """
    def _proceso():
        headers, db_id = _obtener_config_recetas()
        if not headers:
            if callback:
                callback(False, "Notion no configurado")
            return

        try:
            con = sqlite3.connect(DB_PATH)
            cur = con.cursor()
            cur.execute("SELECT notion_page_id FROM recetas WHERE notion_page_id IS NOT NULL")
            ids_locales = {r[0] for r in cur.fetchall()}
            con.close()

            nuevas = 0
            cursor_notion = None
            url_query = f"https://api.notion.com/v1/databases/{db_id}/query"

            while True:
                payload = {"page_size": 100}
                if cursor_notion:
                    payload["start_cursor"] = cursor_notion

                # 📌 Petición POST pura inspirada en tu código
                response = requests.post(url_query, json=payload, headers=headers)
                response.raise_for_status()
                resultado = response.json()

                paginas = resultado.get("results", [])

                for pagina in paginas:
                    pid = pagina["id"]
                    if pid in ids_locales:
                        continue

                    props = pagina.get("properties", {})

                    # Nombre (título)
                    nombre = ""
                    for key in ["Nombre", "Name", "nombre", "name"]:
                        t = props.get(key, {}).get("title", [])
                        if t:
                            nombre = t[0].get("text", {}).get("content", "")
                            break
                    if not nombre:
                        continue  # Sin nombre no la importamos

                    # Ingredientes y etiquetas (columnas rich_text)
                    def _rich(key):
                        rt = props.get(key, {}).get("rich_text", [])
                        return rt[0].get("text", {}).get("content", "") if rt else ""

                    ingredientes = _rich("Ingredientes")
                    etiquetas    = _rich("Etiquetas")

                    # Pasos (bloques de texto de la página con GET puro)
                    try:
                        url_bloques = f"https://api.notion.com/v1/blocks/{pid}/children"
                        res_bloques = requests.get(url_bloques, headers=headers)
                        res_bloques.raise_for_status()
                        bloques = res_bloques.json()

                        pasos = "\n".join(
                            b.get("paragraph", {})
                             .get("rich_text", [{}])[0]
                             .get("text", {})
                             .get("content", "")
                            for b in bloques.get("results", [])
                            if b.get("type") == "paragraph"
                               and b.get("paragraph", {}).get("rich_text")
                        )
                    except Exception:
                        pasos = ""

                    con = sqlite3.connect(DB_PATH)
                    cur = con.cursor()
                    cur.execute(
                        "INSERT INTO recetas "
                        "(nombre, ingredientes, pasos, etiquetas, sincronizada, notion_page_id) "
                        "VALUES (?, ?, ?, ?, 1, ?)",
                        (nombre, ingredientes, pasos, etiquetas, pid),
                    )
                    con.commit()
                    con.close()
                    nuevas += 1

                if not resultado.get("has_more"):
                    break
                cursor_notion = resultado.get("next_cursor")

            msg = f"Sync completado: {nuevas} receta(s) nueva(s) de Notion." if nuevas else "Todo sincronizado."
            if callback:
                callback(True, msg)

        except Exception as e:
            if callback:
                callback(False, f"Error al sincronizar recetas: {e}")

    threading.Thread(target=_proceso, daemon=True).start()