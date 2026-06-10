# views/notes_view.py
import flet as ft
from config import (
    BG_INPUT, BG_BOTI,
    TEXT_PRI, TEXT_MUT, TEXT_ACC, BORDER
)
from modules import write_note


def obtener_notes_view(page: ft.Page) -> ft.Column:

    estado = {"modo": "lista", "nota_abierta": {}}
    cuerpo = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)

    # ── Banner de sync ────────────────────────────────────
    banner_texto = ft.Text("", color=TEXT_MUT, size=11,
                           text_align=ft.TextAlign.CENTER)
    banner = ft.Container(
        content=ft.Row(
            controls=[
                ft.ProgressRing(width=12, height=12, stroke_width=2,
                                color=TEXT_ACC),
                banner_texto,
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=12, right=12, top=6, bottom=6),
        bgcolor=BG_INPUT,
        border_radius=8,
        visible=False,
        margin=ft.Margin(left=0, right=0, top=0, bottom=8),
    )

    def _ocultar_banner():
        banner.visible = False
        page.update()

    # ── Navegación interna ────────────────────────────────
    def _mostrar_lista():
        estado["modo"] = "lista"
        cuerpo.controls.clear()
        cuerpo.controls.append(_construir_lista())
        page.update()

    def _mostrar_formulario():
        estado["modo"] = "nueva"
        cuerpo.controls.clear()
        cuerpo.controls.append(_construir_formulario())
        page.update()

    def _mostrar_lectura(titulo, contenido, fecha):
        estado["modo"] = "lectura"
        estado["nota_abierta"] = {"titulo": titulo, "cuerpo": contenido, "fecha": fecha}
        cuerpo.controls.clear()
        cuerpo.controls.append(_construir_vista_lectura())
        page.update()

    # ── Sync al cargar ────────────────────────────────────
    def _arrancar_sync():
        from config import clave
        if not clave("NOTION_TOKEN") or not clave("NOTION_NOTES_DB"):
            return

        banner_texto.value = "Comprobando Notion..."
        banner.content.controls[0].visible = True
        banner.visible = True
        page.update()

        def _on_sync(ok: bool, msg: str):
            banner_texto.value = msg
            banner.content.controls[0].visible = False
            banner.visible = True
            cuerpo.controls.clear()
            cuerpo.controls.append(_construir_lista())
            page.update()
            import threading, time
            def _ocultar():
                time.sleep(3)
                _ocultar_banner()
            threading.Thread(target=_ocultar, daemon=True).start()

        from utils.notion_sync import sync_notas
        sync_notas(callback=_on_sync)

    # ── Lista ─────────────────────────────────────────────
    def _construir_lista():
        import sqlite3
        from config import DB_PATH
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute(
            "SELECT id, texto, fecha, sincronizada FROM notas ORDER BY fecha DESC LIMIT 50"
        )
        filas = cur.fetchall()
        con.close()

        tarjetas = []
        for nid, texto_raw, fecha_raw, sync in filas:
            fecha_corta = fecha_raw[:10] if fecha_raw else ""

            if texto_raw.startswith("📌 "):
                partes = texto_raw[2:].split("\n\n", 1)
                titulo_nota = partes[0].strip()
                cuerpo_nota = partes[1] if len(partes) > 1 else ""
            else:
                titulo_nota = texto_raw[:40] + ("..." if len(texto_raw) > 40 else "")
                cuerpo_nota = texto_raw

            icono_sync = ft.Icon(
                ft.Icons.CLOUD_DONE if sync else ft.Icons.PHONE_ANDROID,
                size=12,
                color=TEXT_ACC if sync else TEXT_MUT,
            )

            tarjetas.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.GestureDetector(
                                content=ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Text(titulo_nota, color=TEXT_PRI,
                                                        size=14,
                                                        weight=ft.FontWeight.W_500),
                                                icono_sync,
                                            ],
                                            spacing=6,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                        ft.Text(fecha_corta, color=TEXT_MUT, size=11),
                                    ],
                                    spacing=4,
                                ),
                                expand=True,
                                on_tap=lambda e, t=titulo_nota, c=cuerpo_nota, f=fecha_corta:
                                    _mostrar_lectura(t, c, f),
                            ),
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.REMOVE_RED_EYE_OUTLINED,
                                        icon_color=TEXT_ACC, icon_size=18,
                                        on_click=lambda e, t=titulo_nota, c=cuerpo_nota, f=fecha_corta:
                                            _mostrar_lectura(t, c, f),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_color="#ff4f4f", icon_size=18,
                                        on_click=lambda e, i=nid: _borrar_nota(i),
                                    ),
                                ],
                                spacing=4, tight=True,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=BG_BOTI, border_radius=12,
                    padding=ft.Padding(left=16, right=8, top=12, bottom=12),
                    margin=ft.Margin(left=0, right=0, top=0, bottom=8),
                )
            )

        if not tarjetas:
            tarjetas.append(
                ft.Container(
                    content=ft.Text("No hay notas aún. Añade una o conecta Notion.",
                                    color=TEXT_MUT, size=14,
                                    text_align=ft.TextAlign.CENTER),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.Padding(left=0, right=0, top=40, bottom=0),
                )
            )

        return ft.Column(controls=tarjetas, spacing=0,
                         scroll=ft.ScrollMode.AUTO, expand=True)

    def _borrar_nota(nid):
        write_note.borrar_nota(nid)
        _mostrar_lista()

    # ── Lectura ───────────────────────────────────────────
    def _construir_vista_lectura():
        nota = estado["nota_abierta"]
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.IconButton(icon=ft.Icons.ARROW_BACK,
                                          icon_color=TEXT_ACC, icon_size=20,
                                          on_click=lambda e: _mostrar_lista()),
                            ft.Text("Volver", color=TEXT_MUT, size=14),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=4, right=16, top=0, bottom=12),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(nota["titulo"], color=TEXT_PRI, size=18,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text(f"Creada el: {nota['fecha']}", color=TEXT_MUT, size=11),
                            ft.Divider(color=BORDER, height=20),
                            ft.Text(nota["cuerpo"], color=TEXT_PRI, size=14, selectable=True),
                        ],
                        spacing=8,
                    ),
                    bgcolor=BG_BOTI, border_radius=12,
                    padding=ft.Padding(left=18, right=18, top=16, bottom=18),
                ),
            ],
            spacing=0, scroll=ft.ScrollMode.AUTO, expand=True,
        )

    # ── Formulario ────────────────────────────────────────
    def _construir_formulario():
        f_titulo = ft.TextField(
            label="Título",
            label_style=ft.TextStyle(color=TEXT_ACC, size=12),
            hint_text="Ej: Ideas para el proyecto...",
            hint_style=ft.TextStyle(color=TEXT_MUT),
            color=TEXT_PRI, cursor_color=TEXT_ACC,
            bgcolor=BG_INPUT, border_color=BORDER, border_radius=10,
            text_size=14,
            content_padding=ft.Padding(left=14, right=14, top=12, bottom=12),
        )
        f_texto = ft.TextField(
            label="Contenido",
            label_style=ft.TextStyle(color=TEXT_ACC, size=12),
            hint_text="Escribe tu nota aquí...",
            hint_style=ft.TextStyle(color=TEXT_MUT),
            color=TEXT_PRI, cursor_color=TEXT_ACC,
            bgcolor=BG_INPUT, border_color=BORDER, border_radius=10,
            multiline=True, min_lines=5, max_lines=12, text_size=14,
            content_padding=ft.Padding(left=14, right=14, top=12, bottom=12),
        )
        msg_error = ft.Text("", color="#ff4f4f", size=12)

        def _guardar(e):
            if not (f_titulo.value or "").strip():
                msg_error.value = "Añade un título."
                page.update()
                return
            if not (f_texto.value or "").strip():
                msg_error.value = "La nota no puede estar vacía."
                page.update()
                return
            write_note.guardar_nota(f"{f_titulo.value.strip()}|{f_texto.value.strip()}")
            _mostrar_lista()

        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.IconButton(icon=ft.Icons.ARROW_BACK,
                                          icon_color=TEXT_ACC, icon_size=20,
                                          on_click=lambda e: _mostrar_lista()),
                            ft.Text("Nueva nota", color=TEXT_PRI, size=16,
                                    weight=ft.FontWeight.W_600),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=4, right=16, top=0, bottom=8),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[f_titulo, f_texto, msg_error,
                                  ft.Container(
                                      content=ft.Text("Guardar nota",
                                                      color=ft.Colors.WHITE, size=14,
                                                      weight=ft.FontWeight.W_500,
                                                      text_align=ft.TextAlign.CENTER),
                                      bgcolor="#2e5bff", border_radius=12,
                                      padding=ft.Padding(left=0, right=0, top=14, bottom=14),
                                      on_click=_guardar, ink=True,
                                  )],
                        spacing=12,
                    ),
                    bgcolor=BG_BOTI, border_radius=12,
                    padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                ),
            ],
            spacing=0, scroll=ft.ScrollMode.AUTO, expand=True,
        )

    # ── Arranque ──────────────────────────────────────────
    _mostrar_lista()
    _arrancar_sync()

    return ft.Column(
        controls=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("Notas", color=TEXT_PRI, size=18,
                                weight=ft.FontWeight.W_600, expand=True),
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=18),
                                    ft.Text("Nueva", color=ft.Colors.WHITE, size=13),
                                ],
                                spacing=4, tight=True,
                            ),
                            bgcolor="#2e5bff", border_radius=20,
                            padding=ft.Padding(left=12, right=14, top=7, bottom=7),
                            on_click=lambda e: _mostrar_formulario(), ink=True,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=16, right=16, top=16, bottom=12),
                border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
            ),
            ft.Container(
                content=ft.Column(
                    controls=[banner, cuerpo],
                    spacing=0, expand=True,
                ),
                expand=True,
                padding=ft.Padding(left=12, right=12, top=12, bottom=12),
            ),
        ],
        expand=True, spacing=0,
    )