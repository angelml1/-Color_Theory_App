# popup when a swatch in the color palette is clicked on
import flet as ft

from color_math.convert import describe_color
from components.dialogs import close_dialog, show_dialog


def show_color_info(page, hex_color: str, on_remove=None):
    """Pop up a window with the color's HEX, RGB, HSL and HSV codes.
    If on_remove is given, the window also gets a 'Remove from palette' button,
    which is the only way to delete on screens without a mouse hover."""
    codes = describe_color(hex_color)
    status = ft.Text("", size=12, italic=True)

    def copy(text: str):
        try:
            page.set_clipboard(text)
            status.value = f"Copied {text}"
        except Exception:
            status.value = "Couldn't copy automatically. Select the text and copy it."
        status.update()

    rows = [
        ft.Row([
            ft.Text(label, width=44, weight=ft.FontWeight.BOLD),
            ft.Text(value, selectable=True, font_family="monospace", expand=True),
            ft.IconButton(ft.Icons.COPY, icon_size=18, tooltip=f"Copy {label}",
                          on_click=lambda e, v=value: copy(v)),
        ])
        for label, value in codes.items()
    ]

    chip = ft.Container(height=72, bgcolor=hex_color, border_radius=8,
                        border=ft.Border.all(1, "#888888"))

    def remove(e):
        close_dialog(page, dialog)
        on_remove()

    actions = []
    if on_remove is not None:
        actions.append(ft.TextButton("Remove from palette", on_click=remove))
    actions.append(ft.TextButton("Close", on_click=lambda e: close_dialog(page, dialog)))

    dialog = ft.AlertDialog(
        title=ft.Text("Color details"),
        content=ft.Column([chip, *rows, status], tight=True, width=320),
        actions=actions,
    )
    show_dialog(page, dialog)