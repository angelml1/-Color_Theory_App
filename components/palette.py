# persistent palette widget
import flet as ft

from components.swatch import swatch


def palette_sidebar(palette) -> ft.Control:
    pick = palette.pick

    swatch_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=320)
    empty = ft.Text("No colors yet", italic=True)
    hint = ft.Text("Click a color to remove it", size=11, italic=True)
    banner_text = ft.Text(size=12)
    banner = ft.Container(
        content=ft.Column(
            [banner_text, ft.TextButton("Cancel", on_click=lambda e: pick.cancel())],
            spacing=2),
        padding=8, border_radius=8, bgcolor=ft.Colors.PRIMARY_CONTAINER, visible=False,
    )
    undo = ft.TextButton("Undo", icon=ft.Icons.UNDO, on_click=lambda e: palette.undo())

    body = ft.Column(
        [ft.Text("Palette", weight=ft.FontWeight.BOLD), banner, swatch_col,
         empty, hint, undo],
        width=150, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    toggle_btn = ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT)
    root = ft.Row([toggle_btn, body], vertical_alignment=ft.CrossAxisAlignment.START)

    def refresh():
        picking = pick.active
        banner.visible = picking
        if picking:
            banner_text.value = (f"Eyedropper: click a color to use it as {pick.label}."
                                 if palette.colors else
                                 "Your palette is empty. Add colors on the Color Wheel "
                                 "page or Upload page.")
            body.visible = True
            toggle_btn.icon = ft.Icons.CHEVRON_RIGHT

        swatch_col.controls = [
            swatch(c, size=48, selected=picking,
                   on_click=(lambda e, c=c: pick.choose(c)) if picking
                   else (lambda e, c=c: palette.remove(c)))
            for c in palette.colors
        ]
        empty.visible = not palette.colors
        hint.visible = bool(palette.colors) and not picking
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
    pick.subscribe(refresh)
    refresh()
    return root