# main.py — Enrutador y Orquestador de Boti
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import flet as ft
from config import NOMBRE, BG_DARK, BG_PANEL, TEXT_PRI, DATA_DIR
from modules import recipes, write_note
from views.chat_view import obtener_chat_view 

os.makedirs(DATA_DIR, exist_ok=True)
recipes.inicializar()
write_note.inicializar()

def main(page: ft.Page):
    page.title = NOMBRE
    page.bgcolor = BG_DARK
    page.padding = 0

    # Contenedor dinámico donde se renderiza la vista activa
    contenedor_principal = ft.Container(expand=True)

    # Lógica para alternar pantallas desde el Menú Lateral
    def _cambiar_seccion(e):
        indice = e.control.selected_index
        if indice == 0:
            contenedor_principal.content = obtener_chat_view(page)
        elif indice == 1:
            contenedor_principal.content = ft.Center(
                content=ft.Text("Aquí se mostrará tu Base de Datos de Recetas", color=TEXT_PRI, size=16)
            )
        
        page.drawer.open = False
        page.update()

    # --- Menú Lateral Deslizable ---
    page.drawer = ft.NavigationDrawer(
        on_change=_cambiar_seccion,
        controls=[
            ft.Container(height=20),
            ft.Container(
                content=ft.Text("Menú Principal", size=18, weight=ft.FontWeight.BOLD),
                padding=ft.Padding(left=16, right=16, top=0, bottom=10)
            ),
            ft.Divider(thickness=1),
            ft.NavigationDrawerDestination(icon="chat_bubble_outline", selected_icon="chat_bubble", label="Hablar con Boti"),
            ft.NavigationDrawerDestination(icon="storage", selected_icon="storage", label="Base de datos"),
        ]
    )

    # --- Cabecera Fija (AppBar) ---
    # Usamos ft.Icon en lugar de un IconButton para evitar el error de on_click obligado
    page.appbar = ft.AppBar(
        title=ft.Row(
            controls=[
                ft.CircleAvatar(
                    content=ft.Icon("smart_toy", color=TEXT_PRI, size=20), 
                    bgcolor=BG_DARK, 
                    radius=18
                ),
                ft.Text(NOMBRE, size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRI),
            ],
            spacing=10,
        ),
        bgcolor=BG_PANEL,
        center_title=False,
    )

    # Carga la pantalla del chat por defecto al abrir la app
    contenedor_principal.content = obtener_chat_view(page)

    # Ensamblaje en el Layout seguro
    page.add(
        ft.SafeArea(
            content=contenedor_principal,
            expand=True
        )
    )
    page.update()

if __name__ == "__main__":
    ft.run(main)