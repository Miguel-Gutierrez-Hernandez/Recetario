# views/chat_view.py — Vista del Chat (100% Texto, optimizada y ultra-estable)
import flet as ft
import threading
from config import (
    BIENVENIDA, BG_INPUT, BG_USER, BG_BOTI, TEXT_PRI, TEXT_MUT, TEXT_ACC, BORDER, BG_PANEL
)
from modules.brain import responder
from modules import time_tools


# ── Componentes de la Interfaz ────────────────────────────
def _crear_bocadillo(texto: str, es_usuario: bool):
    """
    Genera globos de texto con salto de línea automático adaptativos
    utilizando la técnica de paddings y añade el avatar exterior para Boti.
    """
    # 1. El globo con el diseño exacto de tu Función 1 (Márgenes, paddings y adaptabilidad nativa)
    globo_layout = ft.Container(
        content=ft.Container(
            content=ft.Text(texto, color=TEXT_PRI, size=14, selectable=True),
            bgcolor=BG_USER if es_usuario else BG_BOTI,
            border_radius=ft.BorderRadius(
                top_left=16, top_right=16,
                bottom_left=4 if es_usuario else 16,
                bottom_right=16 if es_usuario else 4
            ),
            padding=ft.Padding(left=14, right=14, top=10, bottom=10),
        ),
        alignment=ft.alignment.Alignment(1, 0) if es_usuario else ft.alignment.Alignment(-1, 0),
        padding=ft.Padding(
            # 📌 Si es Boti, dejamos 52px a la izquierda (12px margen + 32px avatar + 8px separación)
            left=60 if es_usuario else 52,
            # 📌 Este padding derecho de 60px es el que frena el texto largo y lo obliga a cambiar de línea
            right=12 if es_usuario else 60,
            top=4,
            bottom=4
        )
    )

    # Si el mensaje es del usuario, devolvemos su globo limpio (va a la derecha y se encoge si es corto)
    if es_usuario:
        return globo_layout

    # 2. Si es BOTI, creamos el avatar flotante
    avatar = ft.Container(
        content=ft.Image(
            src="/icon.png",  # Tu ruta de los assets
            width=32,
            height=32,
            fit="contain",
        ),
        border_radius=16,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        left=12,  # Posicionado exactamente en los primeros píxeles del hueco izquierdo
        top=4,    # Alineado verticalmente con el inicio del globo
    )

    # 3. Metemos todo en un Stack EXTERNO. Al ser 'globo_layout' el hijo principal
    # sin posicionar, el Stack hereda el ancho completo de la pantalla y tu padding funciona de lujo.
    return ft.Stack(
        controls=[globo_layout, avatar]
    )

def typing_row() -> ft.Row:
    """Los tres puntitos de Boti pensando"""
    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(width=6, height=6, bgcolor=TEXT_MUT, border_radius=3),
                        ft.Container(width=6, height=6, bgcolor=TEXT_MUT, border_radius=3),
                        ft.Container(width=6, height=6, bgcolor=TEXT_MUT, border_radius=3),
                    ],
                    spacing=4,
                ),
                bgcolor=BG_BOTI, border_radius=16,
                padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            )
        ],
        alignment=ft.MainAxisAlignment.START,
    )


# ── Vista Principal ───────────────────────────────────────

def obtener_chat_view(page: ft.Page) -> ft.Column:
    chat_historial = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=10)
    chat_historial.controls.append(_crear_bocadillo(BIENVENIDA, es_usuario=False))

    # ── Configurar las Alarmas (Solo texto) ────────────────
    time_tools.on_alarma = lambda msg: (
        chat_historial.controls.append(_crear_bocadillo(msg, es_usuario=False)),
        page.update(),
    )

    # ── Componentes de la Barra Inferior ──────────────────
    btn_enviar = ft.IconButton(
        icon=ft.Icons.SEND_ROUNDED,
        icon_color=TEXT_ACC,
        icon_size=24,
        on_click=lambda e: _enviar_mensaje()
    )

    txt_mensaje = ft.TextField(
        hint_text="Escribe a Boti...",
        hint_style=ft.TextStyle(color=TEXT_MUT),
        border=ft.InputBorder.NONE,
        color=TEXT_PRI,
        bgcolor=ft.Colors.TRANSPARENT,
        expand=True,
        text_size=14,
        content_padding=ft.Padding(left=16, right=16, top=10, bottom=10),
        on_submit=lambda e: _enviar_mensaje()
    )

    # ── Lógica de envío ───────────────────────────────────
    def _enviar_mensaje():
        texto = txt_mensaje.value.strip()
        if not texto:
            return

        txt_mensaje.value = ""

        # 1. Añadimos el mensaje del usuario
        chat_historial.controls.append(_crear_bocadillo(texto, es_usuario=True))
        
        # 2. Añadimos los puntitos de "pensando"
        puntos_pensando = typing_row()
        chat_historial.controls.append(puntos_pensando)
        page.update()

        # 3. Procesamos en segundo plano
        def procesar():
            try:
                respuesta = responder(texto)
            except Exception as ex:
                respuesta = f"Error: {str(ex)}"
            
            chat_historial.controls.remove(puntos_pensando)
            chat_historial.controls.append(_crear_bocadillo(respuesta, es_usuario=False))
            page.update()

        threading.Thread(target=procesar, daemon=True).start()

    # ── Construcción de la Barra de Entrada ───────────────
    bottombar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=txt_mensaje,
                    bgcolor=BG_INPUT,
                    border_radius=24,
                    border=ft.Border(
                        left=ft.BorderSide(1, BORDER), right=ft.BorderSide(1, BORDER),
                        top=ft.BorderSide(1, BORDER), bottom=ft.BorderSide(1, BORDER)
                    ),
                    expand=True,
                ),
                btn_enviar,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=BG_PANEL,
        padding=ft.Padding(left=10, right=10, top=8, bottom=16),
        border=ft.Border(top=ft.BorderSide(1, BORDER)),
    )

    return ft.Column(
        controls=[
            ft.Container(content=chat_historial, expand=True, padding=ft.Padding(left=12, right=12, top=10, bottom=10)),
            bottombar,
        ],
        expand=True,
        spacing=0
    )