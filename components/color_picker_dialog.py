# the mini color wheel popup used on the contrast tab
import flet as ft

from color_math.convert import parse_color
from components.color_wheel import ColorWheel
from components.dialogs import (PALETTE_FULL, SWATCH_ADDED, close_dialog,
                                show_dialog)
from palette_state import MAX_COLORS


def open_color_editor(page, palette, initial: str, on_apply, title: str = "Adjust color"):
    """Pop up a mini color wheel. 'Use this color' calls on_apply(hex);
    'Add to palette' adds the current color to the shared palette."""
    current = {"hex": initial}
    chip = ft.Container(width=44, height=44, bgcolor=initial, border_radius=8,
                        border=ft.Border.all(1, "#888888"))
    field = ft.TextField(value=initial, width=140, dense=True,
                         hint_text="#RRGGBB or R, G, B")
    status = ft.Text("", size=12, italic=True)

    def show(hex_color: str):        
        current["hex"] = hex_color
        chip.bgcolor = hex_color
        field.value = hex_color
        field.error_text = None
        chip.update()
        field.update()

    def on_typed(e):
        parsed = parse_color(field.value)
        if parsed is None:
            field.error_text = "Use #RRGGBB or R, G, B (0 to 255)"
            field.update()
            return
        if parsed != current["hex"]:
            wheel.set(parsed)       
        show(parsed)

    field.on_submit = on_typed
    field.on_blur = on_typed
    wheel = ColorWheel(show, initial=initial, size=200)

    def add(e):
        color = current["hex"]
        if color in palette.colors:
            status.value = "Already in your palette"
        elif len(palette.colors) >= MAX_COLORS:
            status.value = PALETTE_FULL
        else:
            palette.add(color)
            status.value = SWATCH_ADDED
        status.update()

    def use(e):
        close_dialog(page, dialog)
        on_apply(current["hex"])

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title),
        content=ft.Column(
            [wheel.control, ft.Row([chip, field], alignment=ft.MainAxisAlignment.CENTER), status],
            tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        actions=[ft.TextButton("Add to palette", on_click=add),
                 ft.FilledButton("Use this color", on_click=use),
                 ft.TextButton("Cancel", on_click=lambda e: close_dialog(page, dialog))],
    )
    show_dialog(page, dialog)