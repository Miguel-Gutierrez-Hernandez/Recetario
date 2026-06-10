# views/settings_view.py — Ajustes con diagnóstico Notion en pantalla

import flet as ft
from config import (
    IS_ANDROID, clave, guardar_claves,
    BG_INPUT, BG_BOTI,
    TEXT_PRI, TEXT_MUT, TEXT_ACC, BORDER, VERSION, NOMBRE,
    BG_PANEL
)


def obtener_settings_view(page: ft.Page) -> ft.Column:

    msg_ok    = ft.Text("", color="#4caf50", size=12)
    msg_error = ft.Text("", color="#ff4f4f", size=12)

    # ── Panel de diagnóstico ──────────────────────────────
    def _fila_estado(etiqueta: str, ok: bool, detalle: str) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.CHECK_CIRCLE if ok else ft.Icons.ERROR_OUTLINE,
                        color="#4caf50" if ok else "#ff4f4f",
                        size=16,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(etiqueta, color=TEXT_PRI, size=13,
                                    weight=ft.FontWeight.W_500),
                            ft.Text(detalle, color=TEXT_MUT, size=11),
                        ],
                        spacing=1, expand=True,
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=BG_INPUT,
            border_radius=8,
            padding=ft.Padding(left=12, right=12, top=10, bottom=10),
        )

    fila_notas   = ft.Container()
    fila_recetas = ft.Container()
    btn_comprobar_text = ft.Text("Comprobar conexión Notion",
                                  color=ft.Colors.WHITE, size=13,
                                  text_align=ft.TextAlign.CENTER)
    estado_general = ft.Text("", color=TEXT_MUT, size=11,
                              text_align=ft.TextAlign.CENTER)

    def _actualizar_diagnostico(resultado: dict):
        n = resultado["notas"]
        r = resultado["recetas"]
        fila_notas.content   = _fila_estado("Base de datos Notas",   n["ok"], n["msg"]).content
        fila_notas.bgcolor   = BG_INPUT
        fila_notas.border_radius = 8
        fila_notas.padding   = ft.Padding(left=12, right=12, top=10, bottom=10)
        fila_recetas.content = _fila_estado("Base de datos Recetas", r["ok"], r["msg"]).content
        fila_recetas.bgcolor = BG_INPUT
        fila_recetas.border_radius = 8
        fila_recetas.padding = ft.Padding(left=12, right=12, top=10, bottom=10)
        btn_comprobar_text.value = "Comprobar conexión Notion"
        estado_general.value = ""
        page.update()

    def _comprobar_notion(e):
        btn_comprobar_text.value = "Comprobando..."
        estado_general.value = ""
        fila_notas.content   = None
        fila_recetas.content = None
        page.update()

        from boti.utils.notion_debug import comprobar
        comprobar(_actualizar_diagnostico)

    # ── Campos de claves ──────────────────────────────────
    def _campo(etiqueta: str, clave_nombre: str, password: bool = False) -> ft.TextField:
        return ft.TextField(
            label=etiqueta,
            label_style=ft.TextStyle(color=TEXT_ACC, size=12),
            value=clave(clave_nombre),
            password=password,
            can_reveal_password=password,
            hint_text="No configurado" if not clave(clave_nombre) else "",
            hint_style=ft.TextStyle(color=TEXT_MUT),
            color=TEXT_PRI,
            cursor_color=TEXT_ACC,
            bgcolor=BG_INPUT,
            border_color=BORDER,
            focused_border_color=TEXT_ACC,
            border_radius=10,
            text_size=13,
            content_padding=ft.Padding(left=14, right=14, top=10, bottom=10),
        )

    f_notion_token      = _campo("Notion Token", "NOTION_TOKEN", password=True)
    f_notion_notes_db   = _campo("ID base de datos Notas", "NOTION_NOTES_DB")
    f_notion_recipes_db = _campo("ID base de datos Recetas", "NOTION_RECIPES_DB")
    f_spotify_id        = _campo("Spotify Client ID", "SPOTIFY_CLIENT_ID")
    f_spotify_secret    = _campo("Spotify Client Secret", "SPOTIFY_CLIENT_SECRET", password=True)

    def _guardar(e):
        msg_ok.value    = ""
        msg_error.value = ""

        nuevas = {
            "NOTION_TOKEN":          f_notion_token.value.strip(),
            "NOTION_NOTES_DB":       f_notion_notes_db.value.strip(),
            "NOTION_RECIPES_DB":     f_notion_recipes_db.value.strip(),
            "SPOTIFY_CLIENT_ID":     f_spotify_id.value.strip(),
            "SPOTIFY_CLIENT_SECRET": f_spotify_secret.value.strip(),
        }

        for nombre_clave, valor in nuevas.items():
            if "DB" in nombre_clave and valor and len(valor.replace("-", "")) != 32:
                msg_error.value = f"ID incorrecto en: {nombre_clave}"
                page.update()
                return

        try:
            guardar_claves(nuevas)
            import config
            config.CLAVES.update(nuevas)

            # ── Bug 2 fix: reinicializa los clientes Notion ──
            from boti.utils.notion_debug import reinicializar_modulos
            reinicializar_modulos()

            msg_ok.value = "Guardado. Comprueba la conexion con el boton de abajo."
        except Exception as ex:
            msg_error.value = f"Error al guardar: {ex}"

        page.update()

    # ── Helpers de sección ────────────────────────────────
    def _seccion(titulo: str, controles: list) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(titulo, color=TEXT_ACC, size=12,
                            weight=ft.FontWeight.W_600),
                    ft.Container(height=6),
                    *controles,
                ],
                spacing=10,
            ),
            bgcolor=BG_BOTI,
            border_radius=12,
            padding=ft.Padding(left=16, right=16, top=14, bottom=14),
        )

    nota_plataforma = ft.Container(
        content=ft.Text(
            "Android: las claves se guardan en el almacenamiento interno.\n"
            "Mac: se leen del archivo .env del proyecto."
            if IS_ANDROID else
            "Modo desarrollo: las claves se leen del .env.\n"
            "En Android se guardan aqui.",
            color=TEXT_MUT, size=12,
        ),
        bgcolor=BG_INPUT,
        border_radius=8,
        padding=ft.Padding(left=12, right=12, top=10, bottom=10),
    )

    return ft.Column(
        controls=[
            ft.Container(
                content=ft.Text("Ajustes", color=TEXT_PRI, size=18,
                                weight=ft.FontWeight.W_600),
                padding=ft.Padding(left=16, right=16, top=16, bottom=12),
                border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        nota_plataforma,
                        _seccion("Notion", [
                            f_notion_token,
                            f_notion_notes_db,
                            f_notion_recipes_db,
                        ]),
                        _seccion("Spotify (opcional)", [
                            f_spotify_id,
                            f_spotify_secret,
                        ]),
                        msg_ok,
                        msg_error,
                        ft.Container(
                            content=ft.Text(
                                "Guardar ajustes",
                                color=ft.Colors.WHITE, size=14,
                                weight=ft.FontWeight.W_500,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            bgcolor="#2e5bff",
                            border_radius=12,
                            padding=ft.Padding(left=0, right=0, top=14, bottom=14),
                            on_click=_guardar,
                            ink=True,
                        ),
                        ft.Divider(color=BORDER),
                        # ── Panel de diagnóstico Notion ───
                        _seccion("Diagnostico Notion", [
                            ft.Container(
                                content=btn_comprobar_text,
                                bgcolor="#1e3a5f",
                                border_radius=10,
                                padding=ft.Padding(left=0, right=0, top=12, bottom=12),
                                on_click=_comprobar_notion,
                                ink=True,
                            ),
                            estado_general,
                            fila_notas,
                            fila_recetas,
                        ]),
                        ft.Divider(color=BORDER),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(f"{NOMBRE} v{VERSION}",
                                            color=TEXT_MUT, size=12,
                                            text_align=ft.TextAlign.CENTER),
                                    ft.Text("Asistente personal offline",
                                            color=TEXT_MUT, size=11,
                                            text_align=ft.TextAlign.CENTER),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=2,
                            ),
                            alignment=ft.Alignment(0, 0),
                        ),
                    ],
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                ),
                expand=True,
                padding=ft.Padding(left=12, right=12, top=12, bottom=12),
            ),
        ],
        expand=True,
        spacing=0,
    )