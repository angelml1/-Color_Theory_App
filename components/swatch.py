# singular color swatch on palette
import flet as ft


def swatch(hex_color: str, selected: bool = False, on_click=None, size: int = 56):
    return ft.Container(
        width=size, height=size, bgcolor=hex_color, border_radius=8,
        border=ft.Border.all(3 if selected else 1,
                             "#000000" if selected else "#888888"),
        tooltip=hex_color, on_click=on_click,
    )


def _badge(icon, tooltip: str, on_click, *, visible: bool = True, size: int = 18):
    return ft.Container(
        width=size, height=size, border_radius=size / 2,
        bgcolor=ft.Colors.WHITE, border=ft.Border.all(1, "#888888"),
        alignment=ft.Alignment(0, 0), tooltip=tooltip, on_click=on_click,
        visible=visible, content=ft.Icon(icon, size=size - 6, color="#222222"),
    )


def removable_swatch(hex_color: str, on_remove, on_click=None, selected: bool = False,
                     size: int = 48):
    """Swatch with an X in its corner that only shows while the mouse is over it."""
    x_button = _badge(ft.Icons.CLOSE, "Remove from palette", on_remove, visible=False)
    x_button.top, x_button.right = 0, 0

    def on_hover(e):
        x_button.visible = str(e.data).lower() == "true"
        x_button.update()

    return ft.Container(
        width=size, height=size, on_hover=on_hover,
        content=ft.Stack([swatch(hex_color, selected, on_click, size), x_button],
                         width=size, height=size),
    )


def addable_swatch(hex_color: str, palette, size: int = 56, on_click=None,
                   selected: bool = False):
    """Swatch with a + button in its corner; clicking the swatch also adds it by default."""
    def add(e):
        palette.add(hex_color)

    plus = _badge(ft.Icons.ADD, "Add to palette", add)
    plus.bottom, plus.right = 0, 0
    return ft.Stack([swatch(hex_color, selected, on_click or add, size), plus],
                    width=size, height=size)