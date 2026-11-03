# pick foreground and background colors for contrast checker widget
import flet as ft

from color_math.convert import parse_color
from components.screen_picker import pick_from_screen


def _upd(control):
    try:
        control.update()
    except Exception: 
        pass


class ContrastPicker:
    """Pick one color by typing hex/RGB, or with the eyedropper (palette or screen).
    Exposes .control, .value, .set(hex). Calls on_change() after a change."""

    def __init__(self, label: str, palette, initial: str, on_change):
        self.label = label
        self.palette = palette
        self.on_change = on_change
        self.value = initial

        self.chip = ft.Container(width=44, height=44, bgcolor=initial, border_radius=8,
                                 border=ft.Border.all(1, "#888888"))
        self.field = ft.TextField(
            value=initial, width=150, dense=True, hint_text="#RRGGBB or R, G, B",
            on_submit=self._apply, on_blur=self._apply,
        )
        self.dropper = ft.IconButton(
            ft.Icons.COLORIZE, tooltip="Eyedropper: pick from your palette or the screen",
            on_click=self._toggle_dropper,
        )
        self.screen_btn = ft.TextButton("Pick from screen", visible=False,
                                        on_click=self._pick_screen)

        self.control = ft.Column(
            [ft.Text(label, weight=ft.FontWeight.BOLD),
             ft.Row([self.chip, self.field, self.dropper]),
             self.screen_btn],
            spacing=6,
        )
        palette.pick.subscribe(self._on_pick_change)

    # --- eyedropper --------------------------------------------------------------
    def _mine(self) -> bool:
        pick = self.palette.pick
        return pick.active and pick.owner is self

    def _toggle_dropper(self, e):
        pick = self.palette.pick
        if self._mine():
            pick.cancel()
        else:
            pick.start(self, self.label, self.set)    # sidebar enters select mode

    def _on_pick_change(self):
        mine = self._mine()
        self.dropper.style = ft.ButtonStyle(
            bgcolor=ft.Colors.PRIMARY_CONTAINER if mine else None)
        self.screen_btn.visible = mine
        _upd(self.control)

    def _pick_screen(self, e):
        self.palette.pick.cancel()
        pick_from_screen(self.control.page, self.set)

    # --- typed input ---------------------------------------------------------------
    def _apply(self, e):
        parsed = parse_color(self.field.value)
        if parsed is None:
            self.field.error_text = "Use #RRGGBB or R, G, B (0 to 255)"
            _upd(self.field)
            return
        self.field.error_text = None
        if parsed == self.value:  
            self.field.value = parsed                 # normalizes '#abc' -> '#aabbcc'
            _upd(self.field)
            return
        self.set(parsed)

    def set(self, hex_color: str):
        self.value = hex_color
        self.chip.bgcolor = hex_color
        self.field.value = hex_color
        self.field.error_text = None
        _upd(self.control)
        self.on_change()