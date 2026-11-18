# slot for color chip, color code field, and eyedropper tool used on the contrast tab
import flet as ft

from color_math.convert import parse_color
from components.color_picker_dialog import open_color_editor


def _upd(control):
    try:
        control.update()
    except Exception:   
        pass


class ColorSlot:
    """Pick one color: click the chip for a mini color wheel, type hex/RGB, or use
    the eyedropper to take a color from the palette sidebar.
    Exposes .control, .value, .set(hex). Calls on_change() after a change."""

    def __init__(self, label: str, palette, initial: str, on_change):
        self.label = label
        self.palette = palette
        self.on_change = on_change
        self.value = initial

        self.chip = ft.Container(
            width=44, height=44, bgcolor=initial, border_radius=8,
            border=ft.Border.all(1, "#888888"),
            tooltip="Click to adjust on a color wheel", on_click=self._open_editor,
        )
        self.field = ft.TextField(
            value=initial, width=150, dense=True, hint_text="#RRGGBB or R, G, B",
            on_submit=self._apply, on_blur=self._apply,
        )
        self.dropper = ft.IconButton(
            ft.Icons.COLORIZE, tooltip="Eyedropper: pick a color from your palette",
            on_click=self._toggle_dropper,
        )
        self.control = ft.Column(
            [ft.Text(label, weight=ft.FontWeight.BOLD),
             ft.Row([self.chip, self.field, self.dropper])],
            spacing=6,
        )
        palette.pick.subscribe(self._on_pick_change)

    # --- mini color wheel ----------------------------------------------------------
    def _open_editor(self, e):
        self.palette.pick.cancel()
        open_color_editor(self.control.page, self.palette, self.value, self.set,
                          title=f"Adjust {self.label.lower()} color")

    # --- eyedropper (palette only) -------------------------------------------------
    def _mine(self) -> bool:
        pick = self.palette.pick
        return pick.active and pick.owner is self

    def _toggle_dropper(self, e):
        pick = self.palette.pick
        if self._mine():
            pick.cancel()
        else:
            # sidebar enters select mode
            pick.start(self, self.label, self.set)    

    def _on_pick_change(self):
        self.dropper.style = ft.ButtonStyle(
            bgcolor=ft.Colors.PRIMARY_CONTAINER if self._mine() else None)
        _upd(self.control)

    # --- typed input ---------------------------------------------------------------
    def _apply(self, e):
        parsed = parse_color(self.field.value)
        if parsed is None:
            self.field.error_text = "Use #RRGGBB or R, G, B (0 to 255)"
            _upd(self.field)
            return
        self.field.error_text = None
        if parsed == self.value:
            # normalizes '#abc' -> '#aabbcc'                      
            self.field.value = parsed                 
            _upd(self.field)
            return
        self.set(parsed)

    def set(self, hex_color: str, notify: bool = True):
        self.value = hex_color
        self.chip.bgcolor = hex_color
        self.field.value = hex_color
        self.field.error_text = None
        _upd(self.control)
        if notify:
            self.on_change()