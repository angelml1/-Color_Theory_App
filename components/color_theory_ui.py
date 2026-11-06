# small widgets shared by color theory sandbox page and its tabs
import flet as ft

# wrapper for flet updates in case widget is modified before it is rendered
def upd(control):
    try:
        control.update()
    except Exception:
        pass

# ui cards
def card(title: str, *controls, width: int | None = None) -> ft.Container:
    return ft.Container(
        content=ft.Column([ft.Text(title, size=18, weight=ft.FontWeight.BOLD), *controls],
                          spacing=10),
        padding=16, border=ft.Border.all(1, "#888888"), border_radius=12, width=width,
    )

# general real-time slider 
class Slider:
    """Label + live value + slider. Re-renders on release (like the vision controls)."""

    def __init__(self, label, lo, hi, value, on_release, *, divisions=None, fmt="{:.2f}",
                 hint: str | None = None):
        self.fmt = fmt
        self.name = ft.Text(label, size=12)
        self.readout = ft.Text(fmt.format(value), size=12, weight=ft.FontWeight.BOLD)
        self.slider = ft.Slider(min=lo, max=hi, value=value, divisions=divisions,
                                on_change=self._moved, on_change_end=lambda e: on_release())
        rows = [ft.Row([self.name, self.readout],
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN)]
        if hint:
            rows.append(ft.Text(hint, size=11, italic=True))
        self.control = ft.Column(rows + [self.slider], spacing=0)

    def _moved(self, e):
        self.readout.value = self.fmt.format(self.slider.value)
        upd(self.readout)

    @property
    def value(self) -> float:
        return float(self.slider.value)

# segmented toggle button
def segmented(options: dict, selected: str, on_change) -> ft.SegmentedButton:
    return ft.SegmentedButton(
        selected=[selected], on_change=lambda e: on_change(next(iter(e.control.selected))),
        segments=[ft.Segment(value=k, label=ft.Text(v)) for k, v in options.items()])

# color swatch used in ui
def result_swatch(palette, label: str, hex_color: str, width: int | None = None) -> ft.Control:
    """A result color with its hex and a label. Click to add it to the palette."""
    from components.swatch import swatch
    return ft.Column(
        [swatch(hex_color, size=40, on_click=lambda e, c=hex_color: palette.add(c)),
         ft.Text(hex_color, size=11), ft.Text(label, size=11, italic=True)],
        spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER, width=width)


# optional panel repurposing accessibility page vision effects
class VisionPanel:
    def __init__(self, on_change):
        from color_math.conditions import VisionState
        from components.vision_controls import VisionControls
        self._on_change = on_change
        self._state = VisionState()
        self.controls = VisionControls(self._changed)
        self.note = ft.Text("The preview shows simulated vision. Hex values below are "
                            "the real colors.", size=12, italic=True, visible=False)
        self.control = ft.ExpansionTile(
            title=ft.Text("Simulate a vision condition (optional)"),
            controls=[ft.Column([
                self.controls.reset_button,
                ft.Text("Color blindness", weight=ft.FontWeight.BOLD),
                self.controls.cvd_control,
                ft.Text("Vision perception", weight=ft.FontWeight.BOLD),
                self.controls.effects_control, self.note], spacing=8)])

    def _changed(self, state):
        self._state = state
        self.note.visible = self.active
        upd(self.note)
        self._on_change()

    @property
    def active(self) -> bool:
        return self._state.cvd is not None or bool(self._state.effects)

    def effect(self):
        from color_math.conditions import build_pipeline
        return build_pipeline(self._state)
