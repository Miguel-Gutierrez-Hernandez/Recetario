# modules/notion_debug.py — Diagnóstico de conexión Notion visible en la app

import threading
from config import clave, CLAVES_PATH, IS_ANDROID
import os

# Estado global del diagnóstico
estado = {
    "notas":   {"ok": False, "msg": "No comprobado"},
    "recetas": {"ok": False, "msg": "No comprobado"},
}


def comprobar(callback):
    """
    Comprueba la conexión con Notion en un hilo secundario.
    callback(resultado: dict) se llama al terminar con el estado actualizado.
    """
    def _proceso():
        token = clave("NOTION_TOKEN")
        notes_db  = clave("NOTION_NOTES_DB")
        recipes_db = clave("NOTION_RECIPES_DB")

        # ── 1. Comprueba que las claves existen ───────────
        if not token:
            estado["notas"]["msg"]   = "Sin NOTION_TOKEN"
            estado["recetas"]["msg"] = "Sin NOTION_TOKEN"
            callback(estado)
            return

        # ── 2. Intenta conectar ───────────────────────────
        try:
            from notion_client import Client
            cliente = Client(auth=token)

            # Verifica token haciendo una llamada mínima
            cliente.users.me()

        except Exception as e:
            msg = f"Token invalido: {e}"
            estado["notas"]["msg"]   = msg
            estado["recetas"]["msg"] = msg
            callback(estado)
            return

        # ── 3. Comprueba base de datos de notas ───────────
        if not notes_db:
            estado["notas"] = {"ok": False, "msg": "Sin NOTION_NOTES_DB"}
        else:
            try:
                cliente.databases.retrieve(database_id=notes_db.replace("-", ""))
                estado["notas"] = {"ok": True, "msg": "Conexion correcta"}
            except Exception as e:
                estado["notas"] = {"ok": False, "msg": f"Error: {e}"}

        # ── 4. Comprueba base de datos de recetas ─────────
        if not recipes_db:
            estado["recetas"] = {"ok": False, "msg": "Sin NOTION_RECIPES_DB"}
        else:
            try:
                cliente.databases.retrieve(database_id=recipes_db.replace("-", ""))
                estado["recetas"] = {"ok": True, "msg": "Conexion correcta"}
            except Exception as e:
                estado["recetas"] = {"ok": False, "msg": f"Error: {e}"}

        callback(estado)

    threading.Thread(target=_proceso, daemon=True).start()


def reinicializar_modulos():
    """
    Reinicializa los clientes de Notion en write_note y recipes
    con las claves actuales. Llamar tras guardar en Ajustes.
    """
    import modules.write_note as wn
    import modules.recipes as rec
    wn._inicializar_notion()
    rec._inicializar_notion()