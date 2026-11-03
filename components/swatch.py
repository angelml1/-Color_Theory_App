# singular color swatch on palette
import flet as ft


def swatch(hex_color: str, selected: bool = False, on_click=None, size: int = 56):
    return ft.Container(
        width=size, height=size, bgcolor=hex_color, border_radius=8,
        border=ft.Border.all(3 if selected else 1,
                             "#000000" if selected else "#888888"),
        tooltip=hex_color, on_click=on_click,
    )