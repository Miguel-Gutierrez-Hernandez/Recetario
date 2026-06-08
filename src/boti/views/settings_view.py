# views/settings_view.py — Ajustes: gestion de claves API en Android

import flet as ft
from config import (
    IS_ANDROID, clave, guardar_claves,
    BG_DARK, BG_PANEL, BG_INPUT, BG_BOTI,
    TEXT_PRI, TEXT_MUT, TEXT_ACC, BORDER, VERSION, NOMBRE
)


def obtener_settings_view(page: ft.Page) -> ft.Column:

    msg_ok    = ft.Text("", color="#4caf50", size=12)
    msg_error = ft.Text("", color="#ff4f4f", size=12)

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

    # ── Campos de claves ──────────────────────────────────
    f_notion_token      = _campo("Notion Token", "NOTION_TOKEN", password=True)
    f_notion_notes_db   = _campo("Notion - ID base de datos Notas", "NOTION_NOTES_DB")
    f_notion_recipes_db = _campo("Notion - ID base de datos Recetas", "NOTION_RECIPES_DB")

    f_spotify_id     = _campo("Spotify Client ID", "SPOTIFY_CLIENT_ID")
    f_spotify_secret = _campo("Spotify Client Secret", "SPOTIFY_CLIENT_SECRET", password=True)

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

        # Valida que los IDs de Notion tengan formato correcto (32 chars hex)
        for nombre_clave, valor in nuevas.items():
            if "DB" in nombre_clave and valor and len(valor.replace("-", "")) != 32:
                msg_error.value = f"El ID de base de datos no parece correcto: {nombre_clave}"
                page.update()
                return

        try:
            guardar_claves(nuevas)
            # Recarga las claves en memoria
            import config
            config.CLAVES.update(nuevas)
            msg_ok.value = "Ajustes guardados correctamente."
        except Exception as ex:
            msg_error.value = f"Error al guardar: {ex}"

        page.update()

    # ── Seccion de info ───────────────────────────────────
    def _seccion(titulo: str, controles: list) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(titulo, color=TEXT_ACC, size=12,
                            weight=ft.FontWeight.W_600),
                    ft.Container(height=8),
                    *controles,
                ],
                spacing=10,
            ),
            bgcolor=BG_BOTI,
            border_radius=12,
            padding=ft.Padding(left=16, right=16, top=14, bottom=14),
        )

    # ── Nota informativa segun plataforma ─────────────────
    if IS_ANDROID:
        nota_plataforma = ft.Container(
            content=ft.Text(
                "Las claves se guardan de forma segura en el "
                "almacenamiento interno de tu dispositivo.",
                color=TEXT_MUT, size=12,
            ),
            bgcolor=BG_INPUT,
            border_radius=8,
            padding=ft.Padding(left=12, right=12, top=10, bottom=10),
        )
    else:
        nota_plataforma = ft.Container(
            content=ft.Text(
                "En modo desarrollo las claves se leen del archivo .env "
                "en la raiz del proyecto. Esta pantalla solo guarda en Android.",
                color=TEXT_MUT, size=12,
            ),
            bgcolor=BG_INPUT,
            border_radius=8,
            padding=ft.Padding(left=12, right=12, top=10, bottom=10),
        )

    return ft.Column(
        controls=[
            # Cabecera
            ft.Container(
                content=ft.Text("Ajustes", color=TEXT_PRI, size=18,
                                weight=ft.FontWeight.W_600),
                padding=ft.Padding(left=16, right=16, top=16, bottom=12),
                border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
            ),
            # Contenido con scroll
            ft.Container(
                content=ft.Column(
                    controls=[
                        nota_plataforma,
                        ft.Container(height=4),
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
                                color=ft.Colors.WHITE,
                                size=14,
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