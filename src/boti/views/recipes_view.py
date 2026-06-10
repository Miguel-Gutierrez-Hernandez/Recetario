# views/recipes_view.py
import flet as ft
from config import (
    BG_INPUT, BG_BOTI,
    TEXT_PRI, TEXT_MUT, TEXT_ACC, BORDER
)
from modules import recipes


def obtener_recipes_view(page: ft.Page) -> ft.Column:

    vista_actual = {"modo": "lista"}
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

    def _mostrar_banner(msg: str, cargando: bool = True):
        banner_texto.value = msg
        banner.content.controls[0].visible = cargando
        banner.visible = True
        page.update()

    def _ocultar_banner():
        banner.visible = False
        page.update()

    # ── Navegación interna ────────────────────────────────
    def _mostrar_lista(tras_sync: bool = False):
        vista_actual["modo"] = "lista"
        cuerpo.controls.clear()
        cuerpo.controls.append(_construir_lista())
        if tras_sync:
            _ocultar_banner()
        else:
            page.update()

    def _mostrar_detalle(nombre, ingredientes, pasos):
        vista_actual["modo"] = "detalle"
        cuerpo.controls.clear()
        cuerpo.controls.append(_construir_detalle(nombre, ingredientes, pasos))
        page.update()

    def _mostrar_formulario():
        vista_actual["modo"] = "nueva"
        cuerpo.controls.clear()
        cuerpo.controls.append(_construir_formulario())
        page.update()

    # ── Sync al cargar ────────────────────────────────────
    def _arrancar_sync():
        from config import clave
        if not clave("NOTION_TOKEN") or not clave("NOTION_RECIPES_DB"):
            return  # Sin Notion configurado, no hace nada

        _mostrar_banner("Comprobando Notion...")

        def _on_sync(ok: bool, msg: str):
            banner_texto.value = msg
            banner.content.controls[0].visible = False  # oculta el spinner
            banner.visible = True
            # Recarga la lista para mostrar las recetas nuevas
            cuerpo.controls.clear()
            cuerpo.controls.append(_construir_lista())
            page.update()
            # Oculta el banner tras 3 segundos
            import threading, time
            def _ocultar():
                time.sleep(3)
                _ocultar_banner()
            threading.Thread(target=_ocultar, daemon=True).start()

        from utils.notion_sync import sync_recetas
        sync_recetas(callback=_on_sync)

    # ── Lista ─────────────────────────────────────────────
    def _construir_lista() -> ft.Column:
        import sqlite3
        from config import DB_PATH
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT id, nombre, etiquetas, sincronizada FROM recetas ORDER BY nombre")
        filas = cur.fetchall()
        con.close()

        tarjetas = []
        for rid, nombre, etiquetas, sync in filas:
            icono_sync = ft.Container(
                content=ft.Icon(ft.Icons.CLOUD_DONE if sync else ft.Icons.PHONE_ANDROID,
                                size=12,
                                color=TEXT_ACC if sync else TEXT_MUT),
                tooltip="En Notion" if sync else "Solo local",
            )
            tarjetas.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Text(nombre, color=TEXT_PRI, size=15,
                                                    weight=ft.FontWeight.W_500),
                                            icono_sync,
                                        ],
                                        spacing=6,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    ft.Text(etiquetas or "sin etiquetas",
                                            color=TEXT_MUT, size=12),
                                ],
                                spacing=2, expand=True,
                            ),
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.ARROW_FORWARD_IOS,
                                        icon_color=TEXT_ACC, icon_size=16,
                                        on_click=lambda e, n=nombre: _abrir_receta(n),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_color="#ff4f4f", icon_size=18,
                                        on_click=lambda e, i=rid: _borrar_receta(i),
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
                    content=ft.Text("No hay recetas aún. Añade una o conecta Notion.",
                                    color=TEXT_MUT, size=14,
                                    text_align=ft.TextAlign.CENTER),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.Padding(left=0, right=0, top=40, bottom=0),
                )
            )

        return ft.Column(controls=tarjetas, spacing=0,
                         scroll=ft.ScrollMode.AUTO, expand=True)

    def _abrir_receta(nombre):
        import sqlite3
        from config import DB_PATH
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT nombre, ingredientes, pasos FROM recetas WHERE nombre=?", (nombre,))
        fila = cur.fetchone()
        con.close()
        if fila:
            _mostrar_detalle(*fila)

    def _borrar_receta(rid):
        recipes.borrar(rid)
        _mostrar_lista()

    # ── Detalle ───────────────────────────────────────────
    def _construir_detalle(nombre, ingredientes, pasos):
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.IconButton(icon=ft.Icons.ARROW_BACK,
                                          icon_color=TEXT_ACC, icon_size=20,
                                          on_click=lambda e: _mostrar_lista()),
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
                    bgcolor=BG_BOTI, border_radius=12,
                    padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                ),
            ],
            spacing=0, scroll=ft.ScrollMode.AUTO, expand=True,
        )

    # ── Formulario ────────────────────────────────────────
    def _construir_formulario():
        f_nombre       = _campo_form("Nombre del plato")
        f_ingredientes = _campo_form("Ingredientes", multiline=True)
        f_pasos        = _campo_form("Pasos de preparación", multiline=True, min_lines=4)
        f_etiquetas    = _campo_form("Etiquetas (ej: italiana, rápida)")
        msg_error      = ft.Text("", color="#ff4f4f", size=12)

        def _guardar(e):
            if not f_nombre.value or not f_pasos.value:
                msg_error.value = "El nombre y los pasos son obligatorios."
                page.update()
                return
            recipes.guardar_desde_texto(
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
                            ft.IconButton(icon=ft.Icons.ARROW_BACK,
                                          icon_color=TEXT_ACC, icon_size=20,
                                          on_click=lambda e: _mostrar_lista()),
                            ft.Text("Nueva receta", color=TEXT_PRI, size=16,
                                    weight=ft.FontWeight.W_600),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=4, right=16, top=0, bottom=8),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[f_nombre, f_ingredientes, f_pasos, f_etiquetas,
                                  msg_error,
                                  ft.Container(
                                      content=ft.Text("Guardar receta",
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
    _arrancar_sync()  # sync en segundo plano al abrir la vista

    return ft.Column(
        controls=[
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


def _campo_form(hint, multiline=False, min_lines=1):
    from config import TEXT_PRI, TEXT_MUT, TEXT_ACC, BG_INPUT, BORDER
    return ft.TextField(
        hint_text=hint,
        hint_style=ft.TextStyle(color=TEXT_MUT),
        color=TEXT_PRI, cursor_color=TEXT_ACC,
        bgcolor=BG_INPUT, border_color=BORDER, border_radius=10,
        multiline=multiline, min_lines=min_lines,
        max_lines=8 if multiline else 1,
        text_size=14,
        content_padding=ft.Padding(left=14, right=14, top=10, bottom=10),
    )