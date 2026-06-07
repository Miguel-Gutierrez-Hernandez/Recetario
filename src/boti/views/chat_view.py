# views/chat_view.py
import flet as ft
import threading
from config import (
    BIENVENIDA, BG_DARK, BG_PANEL, BG_INPUT, BG_USER, BG_BOTI,
    TEXT_PRI, TEXT_MUT, TEXT_ACC, BORDER
)
from modules.brain import responder
from modules import time_tools
from utils import listener, talk


# ── Componentes reutilizables ─────────────────────────────

def burbuja(texto: str, es_usuario: bool) -> ft.Container:
    return ft.Container(
        content=ft.Text(texto, color=TEXT_PRI, size=15, selectable=True),
        bgcolor=BG_USER if es_usuario else BG_BOTI,
        border_radius=ft.BorderRadius(
            top_left=16, top_right=16,
            bottom_left=2 if es_usuario else 16,
            bottom_right=16 if es_usuario else 2,
        ),
        padding=ft.Padding(left=14, right=14, top=10, bottom=10),
        margin=ft.Margin(
            left=40 if es_usuario else 0,
            right=0 if es_usuario else 40,
            top=0, bottom=6,
        ),
    )


def fila(texto: str, es_usuario: bool) -> ft.Row:
    return ft.Row(
        controls=[burbuja(texto, es_usuario)],
        alignment=(ft.MainAxisAlignment.END if es_usuario
                   else ft.MainAxisAlignment.START),
    )


def typing_row() -> ft.Row:
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
                margin=ft.Margin(left=0, right=40, top=0, bottom=6),
            )
        ],
        alignment=ft.MainAxisAlignment.START,
    )


# ── Vista del chat ────────────────────────────────────────

def obtener_chat_view(page: ft.Page) -> ft.Column:

    mensajes = ft.ListView(
        expand=True,
        spacing=0,
        padding=ft.Padding(left=12, right=12, top=12, bottom=12),
        auto_scroll=True,
    )
    mensajes.controls.append(fila(BIENVENIDA, es_usuario=False))

    # ── Botón silencio en el AppBar ───────────────────────
    _voz_activa = {"valor": True}

    def _toggle_voz(e):
        _voz_activa["valor"] = not _voz_activa["valor"]
        talk.silenciar(_voz_activa["valor"])
        btn_silencio.icon = (ft.Icons.VOLUME_UP if _voz_activa["valor"]
                             else ft.Icons.VOLUME_OFF)
        btn_silencio.icon_color = TEXT_ACC if _voz_activa["valor"] else "#ff4f4f"
        page.update()

    btn_silencio = ft.IconButton(
        icon=ft.Icons.VOLUME_UP,
        icon_color=TEXT_ACC,
        icon_size=20,
        tooltip="Silenciar voz de Boti",
        on_click=_toggle_voz,
    )
    if page.appbar:
        page.appbar.actions = [btn_silencio]

    # Alarmas: las muestra y las lee en voz alta
    time_tools.on_alarma = lambda msg: (
        mensajes.controls.append(fila(msg, es_usuario=False)),
        talk.hablar(msg),
        page.update(),
    )

    # ── Botones de la barra de entrada ────────────────────
    btn_voz = ft.IconButton(
        icon=ft.Icons.MIC,
        icon_color=TEXT_ACC,
        icon_size=24,
        tooltip="Hablar",
        visible=True,
        on_click=lambda e: None,
    )
    btn_enviar = ft.Container(
        content=ft.Icon(ft.Icons.SEND, color=ft.Colors.WHITE, size=18),
        bgcolor="#2e5bff",
        border_radius=20,
        width=40, height=40,
        alignment=ft.Alignment(0, 0),
        visible=False,
        ink=True,
        on_click=lambda e: None,
    )
    btn_escuchando = ft.IconButton(
        icon=ft.Icons.GRAPHIC_EQ,
        icon_color="#ff4f4f",
        icon_size=24,
        tooltip="Escuchando...",
        disabled=True,
        visible=False,
        on_click=lambda e: None,
    )

    # ── Campo de texto ────────────────────────────────────
    campo = ft.TextField(
        hint_text="Escribe a Boti...",
        hint_style=ft.TextStyle(color=TEXT_MUT),
        border=ft.InputBorder.NONE,
        color=TEXT_PRI,
        cursor_color=TEXT_ACC,
        bgcolor=ft.Colors.TRANSPARENT,
        expand=True,
        multiline=True,
        min_lines=1,
        max_lines=4,
        text_size=15,
        shift_enter=True,
        content_padding=ft.Padding(left=16, right=16, top=12, bottom=12),
    )

    # ── Helpers de estado de botones ─────────────────────
    def _mostrar_boton_voz():
        btn_voz.visible        = True
        btn_enviar.visible     = False
        btn_escuchando.visible = False
        page.update()

    def _mostrar_boton_enviar():
        btn_voz.visible        = False
        btn_enviar.visible     = True
        btn_escuchando.visible = False
        page.update()

    def _mostrar_escuchando():
        btn_voz.visible        = False
        btn_enviar.visible     = False
        btn_escuchando.visible = True
        page.update()

    # ── Envio de mensaje ──────────────────────────────────
    def _enviar(texto: str | None = None):
        texto = (texto or campo.value or "").strip()
        if not texto:
            return

        campo.value = ""
        _mostrar_boton_voz()

        mensajes.controls.append(fila(texto, es_usuario=True))
        t = typing_row()
        mensajes.controls.append(t)
        page.update()

        def procesar():
            respuesta = responder(texto)
            if t in mensajes.controls:
                mensajes.controls.remove(t)
            mensajes.controls.append(fila(respuesta, es_usuario=False))
            page.update()
            talk.hablar(respuesta)   # lee la respuesta en voz alta

        threading.Thread(target=procesar, daemon=True).start()

    # ── Control dinamico del boton ────────────────────────
    def _on_campo_cambio(e):
        if len((campo.value or "").strip()) > 0:
            _mostrar_boton_enviar()
        else:
            _mostrar_boton_voz()

    campo.on_change  = _on_campo_cambio
    campo.on_submit  = lambda e: _enviar()
    btn_enviar.on_click = lambda e: _enviar()

    # ── Callbacks del listener de voz ────────────────────
    async def _al_iniciar_escucha():
        mensajes.controls.append(fila("Escuchando...", es_usuario=True))
        _mostrar_escuchando()

    async def _al_reconocer(texto: str):
        _quitar_ultimo_si(mensajes, "Escuchando...")
        _enviar(texto)

    async def _al_error_voz(msg: str):
        _quitar_ultimo_si(mensajes, "Escuchando...")
        mensajes.controls.append(fila(f"{msg}", es_usuario=False))
        _mostrar_boton_voz()

    async def _al_fin_escucha():
        if btn_escuchando.visible:
            _mostrar_boton_voz()

    listener.on_inicio = _al_iniciar_escucha
    listener.on_texto  = _al_reconocer
    listener.on_error  = _al_error_voz
    listener.on_fin    = _al_fin_escucha

    def _hablar_voz():
        if listener.esta_escuchando():
            return
        listener.escuchar(page)

    btn_voz.on_click = lambda e: _hablar_voz()

    # ── Barra inferior ────────────────────────────────────
    bottombar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=campo,
                    bgcolor=BG_INPUT,
                    border_radius=22,
                    border=ft.Border(
                        left=ft.BorderSide(1, BORDER),
                        right=ft.BorderSide(1, BORDER),
                        top=ft.BorderSide(1, BORDER),
                        bottom=ft.BorderSide(1, BORDER),
                    ),
                    expand=3,
                ),
                ft.Container(
                    content=ft.Row(
                        controls=[btn_voz, btn_escuchando, btn_enviar],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    expand=1,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.END,
            spacing=4,
        ),
        bgcolor=BG_PANEL,
        padding=ft.Padding(left=10, right=6, top=10, bottom=10),
        border=ft.Border(top=ft.BorderSide(1, BORDER)),
    )

    return ft.Column(
        controls=[
            ft.Container(content=mensajes, expand=True),
            bottombar,
        ],
        expand=True,
        spacing=0,
    )


# ── Utilidad ──────────────────────────────────────────────

def _quitar_ultimo_si(lista: ft.ListView, texto: str):
    if not lista.controls:
        return
    ultimo = lista.controls[-1]
    try:
        valor = ultimo.controls[0].content.value
        if texto in valor:
            lista.controls.pop()
    except AttributeError:
        pass