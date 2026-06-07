# views/notes_view.py
import flet as ft
from config import (
    BG_PANEL, BG_INPUT, BG_BOTI,
    TEXT_PRI, TEXT_MUT, TEXT_ACC, BORDER
)
from modules import write_note


def obtener_notes_view(page: ft.Page) -> ft.Column:

    # ── Estado de Navegación Interna ──────────────────────
    # Almacenamos el modo activo y los datos de la nota que se está leyendo
    estado = {
        "modo": "lista",
        "nota_abierta": {"titulo": "", "cuerpo": "", "fecha": ""}
    }

    cuerpo = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)

    # ── Enrutador de Vistas Internas ──────────────────────
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

    def _mostrar_lectura(titulo: str, contenido: str, fecha: str):
        estado["modo"] = "lectura"
        estado["nota_abierta"] = {"titulo": titulo, "cuerpo": contenido, "fecha": fecha}
        cuerpo.controls.clear()
        cuerpo.controls.append(_construir_vista_lectura())
        page.update()

    # ── 1. Vista: Lista de Notas (Solo Títulos) ───────────
    def _construir_lista() -> ft.Column:
        import sqlite3
        from config import DB_PATH
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute(
            "SELECT id, texto, fecha FROM notas ORDER BY fecha DESC LIMIT 50"
        )
        filas = cur.fetchall()
        con.close()

        tarjetas = []
        for nid, texto_raw, fecha_raw in filas:
            fecha_corta = fecha_raw[:10] if fecha_raw else ""
            
            # Procesamos el texto empaquetado para extraer el título limpio
            if texto_raw.startswith("📌 "):
                partes = texto_raw[2:].split("\n\n", 1)
                titulo_nota = partes[0]
                cuerpo_nota = partes[1] if len(partes) > 1 else ""
            else:
                titulo_nota = "Nota sin título"
                cuerpo_nota = texto_raw

            tarjetas.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            # Información de la nota (Hacer clic aquí también lee la nota)
                            ft.GestureDetector(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(titulo_nota, color=TEXT_PRI, size=14, weight=ft.FontWeight.W_500),
                                        ft.Text(fecha_corta, color=TEXT_MUT, size=11),
                                    ],
                                    spacing=4,
                                ),
                                expand=True,
                                on_tap=lambda e, t=titulo_nota, c=cuerpo_nota, f=fecha_corta: _mostrar_lectura(t, c, f)
                            ),
                            # Botonera de acciones
                            ft.Row(
                                controls=[
                                    # Botón Ver Nota completo (Igual que en recetas)
                                    ft.IconButton(
                                        icon=ft.Icons.REMOVE_RED_EYE_OUTLINED,
                                        icon_color=TEXT_ACC,
                                        icon_size=18,
                                        tooltip="Ver nota completa",
                                        on_click=lambda e, t=titulo_nota, c=cuerpo_nota, f=fecha_corta: _mostrar_lectura(t, c, f),
                                    ),
                                    # Botón Eliminar
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_color="#ff4f4f",
                                        icon_size=18,
                                        tooltip="Eliminar nota",
                                        on_click=lambda e, i=nid: _borrar_nota(i),
                                    ),
                                ],
                                spacing=4,
                                tight=True,
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
        write_note.borrar_nota(nid)
        _mostrar_lista()

    # ── 2. Vista: Detalle / Lectura Completa de Nota ──────
    def _construir_vista_lectura() -> ft.Column:
        nota = estado["nota_abierta"]
        return ft.Column(
            controls=[
                # Cabecera interna para volver atrás
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                icon_color=TEXT_ACC,
                                icon_size=20,
                                on_click=lambda e: _mostrar_lista(),
                            ),
                            ft.Text("Volver a la lista", color=TEXT_MUT, size=14),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=4, right=16, top=0, bottom=12),
                ),
                # Bloque de lectura estilizado
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(nota["titulo"], color=TEXT_PRI, size=18, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Creada el: {nota['fecha']}", color=TEXT_MUT, size=11),
                            ft.Divider(color=BORDER, height=20),
                            ft.Text(nota["cuerpo"], color=TEXT_PRI, size=14, selectable=True),
                        ],
                        spacing=8,
                    ),
                    bgcolor=BG_BOTI,
                    border_radius=12,
                    padding=ft.Padding(left=18, right=18, top=16, bottom=18),
                ),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    # ── 3. Vista: Formulario Nueva Nota ───────────────────
    def _construir_formulario() -> ft.Column:
        f_titulo = ft.TextField(
            label="Título de la nota",
            label_style=ft.TextStyle(color=TEXT_ACC, size=12),
            hint_text="Ej: Ideas para el proyecto...",
            hint_style=ft.TextStyle(color=TEXT_MUT),
            color=TEXT_PRI,
            cursor_color=TEXT_ACC,
            bgcolor=BG_INPUT,
            border_color=BORDER,
            border_radius=10,
            text_size=14,
            content_padding=ft.Padding(left=14, right=14, top=12, bottom=12),
        )

        f_texto = ft.TextField(
            label="Contenido",
            label_style=ft.TextStyle(color=TEXT_ACC, size=12),
            hint_text="Escribe tu nota aquí...",
            hint_style=ft.TextStyle(color=TEXT_MUT),
            color=TEXT_PRI,
            cursor_color=TEXT_ACC,
            bgcolor=BG_INPUT,
            border_color=BORDER,
            border_radius=10,
            multiline=True,
            min_lines=5,
            max_lines=12,
            text_size=14,
            content_padding=ft.Padding(left=14, right=14, top=12, bottom=12),
        )
        msg_error = ft.Text("", color="#ff4f4f", size=12)

        def _guardar(e):
            if not (f_titulo.value or "").strip():
                msg_error.value = "Por favor, añade un título a la nota."
                page.update()
                return
            if not (f_texto.value or "").strip():
                msg_error.value = "La nota no puede estar vacía."
                page.update()
                return
                
            datos_empaquetados = f"{f_titulo.value.strip()}|{f_texto.value.strip()}"
            write_note.guardar_nota(datos_empaquetados)
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
                            f_titulo,
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

    # ── Layout Principal ──────────────────────────────────
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