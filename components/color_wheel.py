# color wheel widget
import flet as ft
from flet_color_pickers import ColorPicker, PaletteType

from color_math.convert import hex_to_hsv, hsv_to_hex

SLIDER_LENGTH = 200
WHEEL_SIZE = 250


def _norm(value) -> str:
    """'#rrggbb' or '#AARRGGBB' -> '#rrggbb'."""
    return "#" + str(value).lstrip("#")[-6:].lower()


def _to_slider(s: float, v: float) -> float:
    """Where a color sits on the black -> hue -> white path (0 to 1)."""
    return 0.5 * v + 0.5 * (1 - s)


def _from_slider(h: float, t: float) -> str:
    if t <= 0.5:
        return hsv_to_hex(h, 1.0, 2 * t)          # black -> pure hue
    return hsv_to_hex(h, 2 * (1 - t), 1.0)        # pure hue -> white


class ColorWheel:
    """Hue wheel + one black -> hue -> white slider. The page only uses
    .control, .get(), .set(hex), and the on_pick(hex) callback."""

    def __init__(self, on_pick, initial: str = "#d62828"):
        self.on_pick = on_pick
        self._busy = False
        self._hex = initial
        self._h, s, v = hex_to_hsv(initial)

        self.picker = self._make_picker(initial)

        # Clip the picker to the wheel area so its built-in slider is hidden.
        self.wheel_view = ft.Container(
            content=self.picker,
            width=WHEEL_SIZE, height=WHEEL_SIZE,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

        self.track = ft.Container(
            width=15, height=SLIDER_LENGTH, border_radius=8,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.BOTTOM_CENTER,
                end=ft.Alignment.TOP_CENTER,
                colors=["#000000", "#ffffff", "#ffffff"],
            ),
        )
        self.slider = ft.Slider(
            min=0.0, max=1.0, value=_to_slider(s, v), width=SLIDER_LENGTH,
            active_color=ft.Colors.TRANSPARENT,
            inactive_color=ft.Colors.TRANSPARENT,
            on_change=self._on_slider,
            on_change_end=self._on_slider_end,
        )
        slider_stack = ft.Stack(
            [self.track,
             ft.Container(ft.RotatedBox(quarter_turns=3, content=self.slider),
                          alignment=ft.Alignment.CENTER)],
            width=30, height=SLIDER_LENGTH,
        )
        self.control = ft.Row(
            [slider_stack, self.wheel_view],
            alignment=ft.MainAxisAlignment.CENTER, spacing=15,
        )
        self._update_track()

    # --- internals ---------------------------------------------------------
    def _make_picker(self, color: str) -> ColorPicker:
        return ColorPicker(
            color=color,
            palette_type=PaletteType.HUE_WHEEL,
            color_picker_width=WHEEL_SIZE,
            picker_area_height_percent=1.0,
            hex_input_bar=False,
            enable_alpha=False,
            on_color_change=self._on_wheel,
        )

    def _set_picker(self, hex_color: str, rebuild: bool = True):
        """rebuild=True swaps in a new picker so the dot moves to the color."""
        self._busy = True
        try:
            if rebuild:
                self.picker = self._make_picker(hex_color)
                self.wheel_view.content = self.picker
            else:
                self.picker.color = hex_color
            self._safe_update()
        finally:
            self._busy = False

    def _update_track(self):
        pure = hsv_to_hex(self._h, 1, 1)
        self.track.gradient.colors = ["#000000", pure, "#ffffff"]
        self._safe_update()

    def _remember_hue(self, hex_color: str):
        h, s, v = hex_to_hsv(hex_color)
        if s > 0 and v > 0:
            self._h = h
        return s, v

    def _on_wheel(self, e):
        if self._busy:
            return
        hex_color = _norm(e.data)
        if hex_color == self._hex:
            return
        self._hex = hex_color
        s, v = self._remember_hue(hex_color)
        self.slider.value = _to_slider(s, v)
        self._update_track()
        self.on_pick(hex_color)

    def _on_slider(self, e):
        if self._busy:
            return
        self._hex = _from_slider(self._h, self.slider.value)
        self._set_picker(self._hex, rebuild=False)
        self.on_pick(self._hex)

    def _on_slider_end(self, e):
        self._set_picker(self._hex, rebuild=True)

    def _safe_update(self):
        try:
            self.control.update()
        except Exception:
            pass

    # --- public API --------------------------------------------------------
    def get(self) -> str:
        return self._hex

    def set(self, hex_color: str):
        self._hex = hex_color
        s, v = self._remember_hue(hex_color)
        self.slider.value = _to_slider(s, v)
        self._set_picker(hex_color, rebuild=True)
        self._update_track()