# persistent palette widget
import flet as ft

from components.swatch import swatch


def palette_sidebar(palette) -> ft.Control:
    swatch_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=360)
    empty = ft.Text("No colors yet", italic=True)
    undo = ft.TextButton("Undo", icon=ft.Icons.UNDO,
                         on_click=lambda e: palette.undo())

    body = ft.Column(
        [ft.Text("Palette", weight=ft.FontWeight.BOLD), swatch_col, empty, undo],
        width=150, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    toggle_btn = ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT)
    root = ft.Row([toggle_btn, body], vertical_alignment=ft.CrossAxisAlignment.START)

    def refresh():
        swatch_col.controls = [
            swatch(c, size=48, on_click=lambda e, c=c: palette.remove(c))
            for c in palette.colors
        ]
        empty.visible = not palette.colors
        try:
            root.update()
        except Exception:
            pass

    def toggle(e):
        body.visible = not body.visible
        toggle_btn.icon = (ft.Icons.CHEVRON_RIGHT if body.visible
                           else ft.Icons.CHEVRON_LEFT)
        root.update()

    toggle_btn.on_click = toggle
    palette.subscribe(refresh)
    refresh()
    return root