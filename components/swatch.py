# singular color swatch on palette
import flet as ft

def swatch(hex_color: str, selected: bool = False, on_click=None,
           on_remove=None, size: int = 56):
    body = ft.Container(
        width=size, height=size, bgcolor=hex_color, border_radius=8,
        border=ft.Border.all(3 if selected else 1,
                             "#000000" if selected else "#888888"),
        tooltip=hex_color, on_click=on_click,
    )
    if on_remove is None:
        return body

    x_button = ft.Container(
        content=ft.Icon(ft.Icons.CLOSE, size=12, color="#ffffff"),
        width=18, height=18, border_radius=9,
        bgcolor="#333333", border=ft.Border.all(1, "#ffffff"),
        alignment=ft.Alignment.CENTER,
        right=2, top=2, visible=False,
        tooltip="Remove from palette",
        on_click=lambda e: on_remove(),
    )

    def on_hover(e):
        x_button.visible = str(e.data).lower() == "true"
        x_button.update()

    return ft.Container(
        content=ft.Stack([body, x_button], width=size, height=size),
        on_hover=on_hover,
    )