# main.py 

import sys
import os
import threading

# Asegura que los imports relativos funcionen desde cualquier directorio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import flet as ft
from config import (
    NOMBRE, BIENVENIDA,
    BG_DARK, BG_PANEL, BG_INPUT, BG_USER, BG_BOTI,
    TEXT_PRI, TEXT_MUT, TEXT_ACC, BORDER, DATA_DIR,
)
from modules import recipes, write_note, time_tools
from modules.brain import responder

# ── Inicialización de módulos ─────────────────────────────────────────────────
os.makedirs(DATA_DIR, exist_ok=True)
recipes.inicializar()
write_note.inicializar()


# ── Componentes de UI ─────────────────────────────────────────────────────────

def burbuja(texto: str, es_usuario: bool) -> ft.Container:
    return ft.Container(
        content=ft.Text(texto, color=TEXT_PRI, size=14, selectable=True),
        bgcolor=BG_USER if es_usuario else BG_BOTI,
        border_radius=ft.BorderRadius(
            top_left=16, top_right=16,
            bottom_left=2 if es_usuario else 16,
            bottom_right=16 if es_usuario else 2,
        ),
        padding=ft.Padding(left=16, right=16, top=10, bottom=10),
        margin=ft.Margin(
            left=64 if es_usuario else 0,
            right=0 if es_usuario else 64,
            top=0,
            bottom=4,
        ),
    )


def fila(texto: str, es_usuario: bool) -> ft.Row:
    return ft.Row(
        controls=[burbuja(texto, es_usuario)],
        alignment=(ft.MainAxisAlignment.END if es_usuario
                   else ft.MainAxisAlignment.START),
    )


def chip(icono: str, etiqueta: str, comando: str, on_click_fn) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icono, size=13, color=TEXT_ACC),
                ft.Text(etiqueta, size=12, color=TEXT_ACC),
            ],
            spacing=4, tight=True,
        ),
        bgcolor=BG_PANEL,
        border=ft.Border.all(1, BORDER),
        border_radius=20,
        padding=ft.Padding(left=10, right=10, top=6, bottom=6),
        on_click=lambda e: on_click_fn(comando),
        ink=True,
    )


# ── App principal ─────────────────────────────────────────────────────────────

def main(page: ft.Page):
    page.title = NOMBRE
    page.bgcolor = BG_DARK
    page.padding = 0
    page.window.width  = 420
    page.window.height = 780
    page.window.min_width  = 340
    page.window.min_height = 500

    # ── Lista de mensajes ─────────────────────────────────
    mensajes = ft.ListView(
        expand=True,
        spacing=2,
        padding=ft.Padding(left=14, right=14, top=12, bottom=12),
        auto_scroll=True,
    )
    mensajes.controls.append(fila(BIENVENIDA, es_usuario=False))

    # ── Conector de alarma → UI ───────────────────────────
    def notificacion_alarma(msg: str):
        mensajes.controls.append(fila(msg, es_usuario=False))
        page.update()

    time_tools.on_alarma = notificacion_alarma

    # ── Campo de texto ────────────────────────────────────
    campo = ft.TextField(
        hint_text="Escribe un mensaje…",
        hint_style=ft.TextStyle(color=TEXT_MUT),
        border=ft.InputBorder.NONE,
        color=TEXT_PRI,
        cursor_color=TEXT_ACC,
        bgcolor=ft.Colors.TRANSPARENT, 
        expand=True,
        multiline=True,
        min_lines=1,
        max_lines=4,
        text_size=14,
        shift_enter=True,
        on_submit=lambda e: _enviar(),
    )

    # ── Indicador de escritura ────────────────────────────
    def typing_row() -> ft.Row:
        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(width=7, height=7,
                                         bgcolor=TEXT_MUT, border_radius=4),
                            ft.Container(width=7, height=7,
                                         bgcolor=TEXT_MUT, border_radius=4),
                            ft.Container(width=7, height=7,
                                         bgcolor=TEXT_MUT, border_radius=4),
                        ],
                        spacing=4,
                    ),
                    bgcolor=BG_BOTI,
                    border_radius=16,
                    padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                    margin=ft.Margin(left=0, right=64, top=0, bottom=4),
                )
            ],
            alignment=ft.MainAxisAlignment.START,
        )

    # ── Lógica de envío ───────────────────────────────────
    def _enviar_comando(texto: str):
        campo.value = texto
        _enviar()

    def _enviar():
        texto = (campo.value or "").strip()
        if not texto:
            return
        campo.value = ""
        mensajes.controls.append(fila(texto, es_usuario=True))

        typing = typing_row()
        mensajes.controls.append(typing)
        page.update()

        def procesar():
            respuesta = responder(texto)
            if typing in mensajes.controls:
                mensajes.controls.remove(typing)
            mensajes.controls.append(fila(respuesta, es_usuario=False))
            page.update()

        threading.Thread(target=procesar, daemon=True).start()

    def _limpiar():
        mensajes.controls.clear()
        mensajes.controls.append(fila("Conversación limpiada. ¿En qué te ayudo?",
                                      es_usuario=False))
        page.update()

    # ── Chips de acción rápida ────────────────────────────
    # Solución definitiva: Pasamos los iconos como cadenas de texto seguras
    chips_row = ft.Row(
        controls=[
            chip("restaurant",    "Recetas",  "mis recetas",    _enviar_comando),
            chip("note_add",      "Anotar",   "anota: ",        _enviar_comando),
            chip("access_time",   "Hora",     "qué hora es",    _enviar_comando),
            chip("help_outline",  "Ayuda",    "ayuda",          _enviar_comando),
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=8,
    )

    # ── Barra superior ────────────────────────────────────
    topbar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text("✦", size=18, color=TEXT_ACC),
                    width=34, height=34,
                    bgcolor=BG_PANEL,
                    border_radius=9,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column(
                    controls=[
                        ft.Text(NOMBRE, size=15,
                                weight=ft.FontWeight.W_600, color=TEXT_PRI),
                        ft.Text("listo", size=11, color=TEXT_ACC),
                    ],
                    spacing=0, tight=True,
                ),
                ft.Container(expand=True),
                ft.IconButton(
                    icon="delete_outline", # Icono como texto seguro
                    icon_color=TEXT_MUT,
                    icon_size=18,
                    tooltip="Limpiar chat",
                    on_click=lambda e: _limpiar(),
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=BG_PANEL,
        padding=ft.Padding(left=14, right=14, top=11, bottom=11),
        border=ft.Border(bottom=ft.BorderSide(1, BORDER)),    )

    # ── Barra inferior ────────────────────────────────────
    btn_enviar = ft.IconButton(
        icon="arrow_upward_rounded", # Icono como texto seguro
        icon_color=ft.Colors.WHITE,
        bgcolor="#2e5bff",
        icon_size=18,
        width=36, height=36,
        on_click=lambda e: _enviar(),
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
    )

    bottombar = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(content=chips_row, padding=ft.Padding(left=0, right=0, top=0, bottom=8)),
                ft.Container(
                    content=ft.Row(
                        controls=[campo, btn_enviar],
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        spacing=8,
                    ),
                    bgcolor=BG_INPUT,
                    border_radius=16,
                    border=ft.Border.all(1, BORDER),
                    padding=ft.Padding(left=14, right=8, top=8, bottom=8),
                ),
            ],
            spacing=0,
        ),
        bgcolor=BG_DARK,
        padding=ft.Padding(left=14, right=14, top=11, bottom=11),
        border=ft.Border(top=ft.BorderSide(1, BORDER)),    )

    # ── Layout ────────────────────────────────────────────
    page.add(
        ft.Column(
            controls=[
                topbar,
                ft.Container(content=mensajes, expand=True),
                bottombar,
            ],
            expand=True,
            spacing=0,
        )
    )

    campo.focus()
    page.update()


if __name__ == "__main__":
    ft.run(main)