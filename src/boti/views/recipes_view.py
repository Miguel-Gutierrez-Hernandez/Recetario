# views/recipes_view.py
import flet as ft
from config import (
    BG_DARK, BG_PANEL, BG_INPUT, BG_BOTI,
    TEXT_PRI, TEXT_MUT, TEXT_ACC, BORDER
)
from modules import recipes


def obtener_recipes_view(page: ft.Page) -> ft.Column:

    # ── Estado ────────────────────────────────────────────
    vista_actual = {"modo": "lista"}  # "lista" | "detalle" | "nueva"

    # ── Contenedor dinámico central ───────────────────────
    cuerpo = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)

    # ── Helpers de navegación interna ────────────────────
    def _mostrar_lista():
        vista_actual["modo"] = "lista"
        cuerpo.controls.clear()
        cuerpo.controls.append(_construir_lista())
        page.update()

    def _mostrar_detalle(nombre: str, ingredientes: str, pasos: str):
        vista_actual["modo"] = "detalle"
        cuerpo.controls.clear()
        cuerpo.controls.append(_construir_detalle(nombre, ingredientes, pasos))
        page.update()

    def _mostrar_formulario():
        vista_actual["modo"] = "nueva"
        cuerpo.controls.clear()
        cuerpo.controls.append(_construir_formulario())
        page.update()

    # ── Vista: lista de recetas ───────────────────────────
    def _construir_lista() -> ft.Column:
        import sqlite3
        from config import DB_PATH
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT id, nombre, etiquetas FROM recetas ORDER BY nombre")
        filas = cur.fetchall()
        con.close()

        tarjetas = []
        for rid, nombre, etiquetas in filas:
            tarjetas.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(nombre, color=TEXT_PRI, size=15,
                                            weight=ft.FontWeight.W_500),
                                    ft.Text(etiquetas or "sin etiquetas",
                                            color=TEXT_MUT, size=12),
                                ],
                                spacing=2, expand=True,
                            ),
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.ARROW_FORWARD_IOS,
                                        icon_color=TEXT_ACC,
                                        icon_size=16,
                                        on_click=lambda e, n=nombre: _abrir_receta(n),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_color="#ff4f4f",
                                        icon_size=18,
                                        on_click=lambda e, i=rid, n=nombre: _borrar_receta(i, n),
                                    ),
                                ],
                                spacing=0,
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
                    content=ft.Text("No hay recetas aún. ¡Añade una!",
                                    color=TEXT_MUT, size=14,
                                    text_align=ft.TextAlign.CENTER),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.Padding(left=0, right=0, top=40, bottom=0),
                )
            )

        return ft.Column(
            controls=tarjetas,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _abrir_receta(nombre: str):
        import sqlite3
        from config import DB_PATH
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT nombre, ingredientes, pasos FROM recetas WHERE nombre=?", (nombre,))
        fila = cur.fetchone()
        con.close()
        if fila:
            _mostrar_detalle(*fila)

    def _borrar_receta(rid: int, nombre: str):
        import sqlite3
        from config import DB_PATH
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("DELETE FROM recetas WHERE id=?", (rid,))
        con.commit()
        con.close()
        _mostrar_lista()

    # ── Vista: detalle de receta ──────────────────────────
    def _construir_detalle(nombre: str, ingredientes: str, pasos: str) -> ft.Column:
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
                            ft.Text(nombre, color=TEXT_PRI, size=16,
                                    weight=ft.FontWeight.W_600, expand=True),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=4, right=16, top=0, bottom=8),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Ingredientes", color=TEXT_ACC, size=13,
                                    weight=ft.FontWeight.W_600),
                            ft.Container(height=6),
                            ft.Text(ingredientes or "—", color=TEXT_PRI, size=14),
                            ft.Divider(color=BORDER, height=24),
                            ft.Text("Preparación", color=TEXT_ACC, size=13,
                                    weight=ft.FontWeight.W_600),
                            ft.Container(height=6),
                            ft.Text(pasos or "—", color=TEXT_PRI, size=14),
                        ],
                        spacing=4,
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

    # ── Vista: formulario nueva receta ────────────────────
    def _construir_formulario() -> ft.Column:
        f_nombre      = _campo_form("Nombre del plato")
        f_ingredientes = _campo_form("Ingredientes (separados por coma)", multiline=True)
        f_pasos       = _campo_form("Pasos de preparación", multiline=True, min_lines=4)
        f_etiquetas   = _campo_form("Etiquetas (ej: italiana, rápida)")
        msg_error     = ft.Text("", color="#ff4f4f", size=12)

        def _guardar(e):
            if not f_nombre.value or not f_pasos.value:
                msg_error.value = "El nombre y los pasos son obligatorios."
                page.update()
                return
            resultado = recipes.guardar_desde_texto(
                f"nombre: {f_nombre.value}\n"
                f"ingredientes: {f_ingredientes.value}\n"
                f"pasos: {f_pasos.value}\n"
                f"etiquetas: {f_etiquetas.value}"
            )
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
                            ft.Text("Nueva receta", color=TEXT_PRI, size=16,
                                    weight=ft.FontWeight.W_600),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=4, right=16, top=0, bottom=8),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            f_nombre, f_ingredientes, f_pasos, f_etiquetas,
                            msg_error,
                            ft.Container(
                                content=ft.Text("Guardar receta",
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

    # ── Layout principal de la vista ──────────────────────
    _mostrar_lista()

    return ft.Column(
        controls=[
            # Cabecera de la sección
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("Recetario", color=TEXT_PRI, size=18,
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


# ── Helpers ───────────────────────────────────────────────

def _campo_form(hint: str, multiline: bool = False, min_lines: int = 1) -> ft.TextField:
    from config import TEXT_PRI, TEXT_MUT, TEXT_ACC, BG_INPUT, BORDER
    return ft.TextField(
        hint_text=hint,
        hint_style=ft.TextStyle(color=TEXT_MUT),
        color=TEXT_PRI,
        cursor_color=TEXT_ACC,
        bgcolor=BG_INPUT,
        border_color=BORDER,
        border_radius=10,
        multiline=multiline,
        min_lines=min_lines,
        max_lines=8 if multiline else 1,
        text_size=14,
        content_padding=ft.Padding(left=14, right=14, top=10, bottom=10),
    )