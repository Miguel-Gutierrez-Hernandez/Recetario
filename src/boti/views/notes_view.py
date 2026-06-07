# views/notes_view.py
import flet as ft
from config import (
    BG_PANEL, BG_INPUT, BG_BOTI,
    TEXT_PRI, TEXT_MUT, TEXT_ACC, BORDER
)
from modules import write_note


def obtener_notes_view(page: ft.Page) -> ft.Column:

    # ── Estado ────────────────────────────────────────────
    vista_actual = {"modo": "lista"}

    cuerpo = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)

    # ── Navegación interna ────────────────────────────────
    def _mostrar_lista():
        vista_actual["modo"] = "lista"
        cuerpo.controls.clear()
        cuerpo.controls.append(_construir_lista())
        page.update()

    def _mostrar_formulario():
        vista_actual["modo"] = "nueva"
        cuerpo.controls.clear()
        cuerpo.controls.append(_construir_formulario())
        page.update()

    # ── Vista: lista de notas ─────────────────────────────
    def _construir_lista() -> ft.Column:
        import sqlite3
        from config import DB_PATH
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute(
            "SELECT id, texto, creada FROM notas ORDER BY creada DESC LIMIT 50"
        )
        filas = cur.fetchall()
        con.close()

        tarjetas = []
        for nid, texto, creada in filas:
            fecha = creada[:10] if creada else ""
            preview = texto[:80] + ("…" if len(texto) > 80 else "")
            tarjetas.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(preview, color=TEXT_PRI, size=14),
                                    ft.Text(fecha, color=TEXT_MUT, size=11),
                                ],
                                spacing=4, expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color="#ff4f4f",
                                icon_size=18,
                                on_click=lambda e, i=nid: _borrar_nota(i),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=BG_BOTI,
                    border_radius=12,
                    padding=ft.Padding(left=16, right=8, top=12, bottom=12),
                    margin=ft.Margin(left=0, right=0, top=0, bottom=8),
                )
            )

        if not tarjetas:
            tarjetas.append(
                ft.Container(
                    content=ft.Text("No hay notas aún. ¡Añade una!",
                                    color=TEXT_MUT, size=14,
                                    text_align=ft.TextAlign.CENTER),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.Padding(left=0, right=0, top=40, bottom=0),
                )
            )

        return ft.Column(controls=tarjetas, spacing=0,
                         scroll=ft.ScrollMode.AUTO, expand=True)

    def _borrar_nota(nid: int):
        import sqlite3
        from config import DB_PATH
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("DELETE FROM notas WHERE id=?", (nid,))
        con.commit()
        con.close()
        _mostrar_lista()

    # ── Vista: formulario nueva nota ──────────────────────
    def _construir_formulario() -> ft.Column:
        f_texto = ft.TextField(
            hint_text="Escribe tu nota aquí...",
            hint_style=ft.TextStyle(color=TEXT_MUT),
            color=TEXT_PRI,
            cursor_color=TEXT_ACC,
            bgcolor=BG_INPUT,
            border_color=BORDER,
            border_radius=10,
            multiline=True,
            min_lines=5,
            max_lines=15,
            text_size=14,
            content_padding=ft.Padding(left=14, right=14, top=12, bottom=12),
        )
        msg_error = ft.Text("", color="#ff4f4f", size=12)

        def _guardar(e):
            if not (f_texto.value or "").strip():
                msg_error.value = "La nota no puede estar vacía."
                page.update()
                return
            write_note.guardar(f_texto.value.strip())
            _mostrar_lista()

        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                icon_color=TEXT_ACC,
                                icon_size=20,
                                on_click=lambda e: _mostrar_lista(),
                            ),
                            ft.Text("Nueva nota", color=TEXT_PRI, size=16,
                                    weight=ft.FontWeight.W_600),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=4, right=16, top=0, bottom=8),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            f_texto,
                            msg_error,
                            ft.Container(
                                content=ft.Text("Guardar nota",
                                                color=ft.Colors.WHITE,
                                                size=14,
                                                weight=ft.FontWeight.W_500,
                                                text_align=ft.TextAlign.CENTER),
                                bgcolor="#2e5bff",
                                border_radius=12,
                                padding=ft.Padding(left=0, right=0, top=14, bottom=14),
                                on_click=_guardar,
                                ink=True,
                            ),
                        ],
                        spacing=12,
                    ),
                    bgcolor=BG_BOTI,
                    border_radius=12,
                    padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                ),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    # ── Layout principal ──────────────────────────────────
    _mostrar_lista()

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
                            bgcolor="#2e5bff",
                            border_radius=20,
                            padding=ft.Padding(left=12, right=14, top=7, bottom=7),
                            on_click=lambda e: _mostrar_formulario(),
                            ink=True,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=16, right=16, top=16, bottom=12),
                border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
            ),
            ft.Container(content=cuerpo, expand=True,
                         padding=ft.Padding(left=12, right=12, top=12, bottom=12)),
        ],
        expand=True,
        spacing=0,
    )