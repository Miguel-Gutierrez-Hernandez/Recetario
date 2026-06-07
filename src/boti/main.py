# main.py — Enrutador y orquestador de Boti
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import flet as ft
from config import (
    NOMBRE, BG_DARK, BG_PANEL, BG_BOTI,
    TEXT_PRI, TEXT_ACC, TEXT_MUT, BORDER, DATA_DIR, IS_ANDROID
)
from modules import recipes, write_note

os.makedirs(DATA_DIR, exist_ok=True)
recipes.inicializar()
write_note.inicializar()


def main(page: ft.Page):
    page.title = NOMBRE
    page.bgcolor = BG_DARK
    page.padding = 0

    contenedor_principal = ft.Container(expand=True)

    titulos = {0: "Chat", 1: "Recetario", 2: "Notas", 3: "Ajustes"}

    def _cargar_seccion(indice: int):
        # Importaciones aqui para evitar circulos
        from views.chat_view     import obtener_chat_view
        from views.recipes_view  import obtener_recipes_view
        from views.notes_view    import obtener_notes_view
        from views.settings_view import obtener_settings_view

        page.appbar.title.controls[1].value = titulos.get(indice, NOMBRE)

        if indice == 0:
            contenedor_principal.content = obtener_chat_view(page)
        elif indice == 1:
            contenedor_principal.content = obtener_recipes_view(page)
        elif indice == 2:
            contenedor_principal.content = obtener_notes_view(page)
        elif indice == 3:
            contenedor_principal.content = obtener_settings_view(page)

        page.drawer.open = False
        page.update()

    def _cambiar_seccion(e):
        _cargar_seccion(e.control.selected_index)

    # ── Menu lateral ──────────────────────────────────────
    page.drawer = ft.NavigationDrawer(
        on_change=_cambiar_seccion,
        controls=[
            ft.Container(height=20),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text("B", size=20,
                                            color=TEXT_ACC,
                                            weight=ft.FontWeight.BOLD),
                            width=36, height=36,
                            bgcolor=BG_BOTI,
                            border_radius=10,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(NOMBRE, size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_PRI),
                                ft.Text("Asistente personal", size=11,
                                        color=TEXT_MUT),
                            ],
                            spacing=0, tight=True,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=16, right=16, top=0, bottom=16),
            ),
            ft.Divider(thickness=1, color=BORDER),
            ft.Container(height=8),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.CHAT_BUBBLE_OUTLINE,
                selected_icon=ft.Icons.CHAT_BUBBLE,
                label="Chat",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.RESTAURANT_MENU_OUTLINED,
                selected_icon=ft.Icons.RESTAURANT_MENU,
                label="Recetario",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.NOTE_OUTLINED,
                selected_icon=ft.Icons.NOTE,
                label="Notas",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Ajustes",
            ),
        ],
    )

    # ── AppBar ────────────────────────────────────────────
    page.appbar = ft.AppBar(
        title=ft.Row(
            controls=[
                ft.CircleAvatar(
                    content=ft.Icon(ft.Icons.SMART_TOY, color=TEXT_PRI),
                    bgcolor=BG_BOTI,
                    radius=18,
                ),
                ft.Text("Chat", size=18,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_PRI),
            ],
            spacing=10,
        ),
        bgcolor=BG_PANEL,
        center_title=False,
    )

    _cargar_seccion(0)

    page.add(
        ft.SafeArea(
            content=contenedor_principal,
            expand=True,
        )
    )
    page.update()


if __name__ == "__main__":
    if IS_ANDROID:
        # Android usa ft.app(target=...)
        ft.app(target=main)
    else:
        # Tu Mac usa ft.run(...) sin el texto 'target='
        ft.run(main)