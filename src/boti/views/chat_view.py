# chat_view.py — Vista del Chat optimizada para Android y Mac
import flet as ft
from config import (
    BG_INPUT, BG_USER, BG_BOTI, TEXT_PRI, TEXT_MUT, TEXT_ACC, BORDER, BIENVENIDA
)

def obtener_chat_view(page: ft.Page) -> ft.Column:
    # Contenedor donde se irán mostrando los globos de texto
    chat_historial = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=10
    )

    # Caja de texto para escribir el mensaje (Quitamos autofocus para evitar errores en Android)
    txt_mensaje = ft.TextField(
        hint_text="Escribe un mensaje...",
        hint_style=ft.TextStyle(color=TEXT_MUT),
        color=TEXT_PRI,
        bgcolor=BG_INPUT,
        border_color=BORDER,
        border_radius=24,
        expand=True,
        text_size=14,
        content_padding=ft.Padding(left=16, right=16, top=10, bottom=10),
        on_submit=lambda e: _enviar_mensaje(e)
    )

    def _crear_bocadillo(texto: str, es_usuario: bool):
        """Genera los globos de texto limpios y 100% compatibles"""
        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(texto, color=TEXT_PRI, size=14),
                    bgcolor=BG_USER if es_usuario else BG_BOTI,
                    border_radius=ft.BorderRadius(
                        top_left=16, top_right=16,
                        bottom_left=4 if es_usuario else 16,
                        bottom_right=16 if es_usuario else 4
                    ),
                    padding=ft.Padding(left=14, right=14, top=10, bottom=10)
                    # 📌 Hemos eliminado por completo max_width y constraints. 
                    # Flet ajustará el globo al tamaño del texto automáticamente.
                )
            ],
            alignment=ft.MainAxisAlignment.END if es_usuario else ft.MainAxisAlignment.START
        )

    def _enviar_mensaje(e):
        texto = txt_mensaje.value.strip()
        if not texto:
            return

        # 1. Pintar mensaje del usuario
        chat_historial.controls.append(_crear_bocadillo(texto, es_usuario=True))
        txt_mensaje.value = ""
        page.update()

        # 2. Respuesta simulada para comprobar que la UI responde en Android
        # (Aquí irá tu lógica del modelo de IA, pero primero aseguramos la interfaz)
        respuesta_boti = f"Recibido en el móvil: '{texto}'. El motor de la interfaz funciona perfectamente. ✅"
        chat_historial.controls.append(_crear_bocadillo(respuesta_boti, es_usuario=False))
        page.update()

    # Insertamos el mensaje de bienvenida inicial de Boti
    chat_historial.controls.append(_crear_bocadillo(BIENVENIDA, es_usuario=False))

    # Construcción final de la vista en una sola columna limpia
    return ft.Column(
        controls=[
            # Área de mensajes
            ft.Container(
                content=chat_historial,
                expand=True,
                padding=ft.Padding(left=12, right=12, top=10, bottom=10)
            ),
            # Barra inferior de escritura
            ft.Container(
                content=ft.Row(
                    controls=[
                        txt_mensaje,
                        ft.IconButton(
                            icon=ft.Icons.SEND_ROUNDED,
                            icon_color=TEXT_ACC,
                            icon_size=24,
                            on_click=_enviar_mensaje
                        )
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=ft.Padding(left=8, right=8, top=8, bottom=16),
                border=ft.Border(top=ft.BorderSide(1, BORDER)),
                bgcolor=BG_INPUT
            )
        ],
        expand=True,
        spacing=0
    )