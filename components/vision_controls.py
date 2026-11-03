# widget for selecting color blindness and vision effects
import flet as ft

from color_math.conditions import (CVD_CONDITIONS, CVD_GROUPS, EFFECT_CONDITIONS,
                                   VisionState)

TYPICAL = "normal"


def _upd(control):
    try:
        control.update()
    except Exception:
        pass


class VisionControls:
    """Two controls for the two cards on the Vision tab:
    .cvd_control      single-select color blindness groups + one severity slider
    .effects_control  vision perception switches, each with its own slider
    Calls on_change(VisionState) after every change."""

    def __init__(self, on_change):
        self.on_change = on_change
        self.cvd_key: str | None = None
        self.effects: dict[str, float] = {}

        # --- color blindness --------
        tiles = [
            ft.ExpansionTile(
                title=ft.Text(group),
                controls=[ft.Radio(value=k, label=CVD_CONDITIONS[k].short) for k in keys],
            )
            for group, keys in CVD_GROUPS.items()
        ]
        self.cvd_group = ft.RadioGroup(
            value=TYPICAL, on_change=self._on_cvd,
            content=ft.Column(
                [ft.Radio(value=TYPICAL, label="Typical color vision"), *tiles],
                spacing=4),
        )
        self.cvd_name = ft.Text(weight=ft.FontWeight.BOLD)
        self.cvd_scale = ft.Text(size=12, italic=True)
        self.cvd_slider = ft.Slider(min=0, max=1, divisions=20, value=1.0,
                                    label="{value}", on_change_end=self._on_cvd_slider)
        self.cvd_box = ft.Column([self.cvd_name, self.cvd_scale, self.cvd_slider],
                                 visible=False, spacing=2)
        self.cvd_control = ft.Column([self.cvd_group, self.cvd_box], spacing=8)

        # --- vision perception ---------------------------------------------
        self.switches, self.sliders, self.boxes = {}, {}, {}
        rows = []
        for key, cond in EFFECT_CONDITIONS.items():
            switch = ft.Switch(label=cond.label, value=False,
                               on_change=lambda e, k=key: self._on_effect(k))
            slider = ft.Slider(min=0, max=1, divisions=20, value=cond.default,
                               label="{value}",
                               on_change_end=lambda e, k=key: self._on_effect_slider(k))
            box = ft.Column([ft.Text("Severity", size=12), slider], visible=False, spacing=0)
            self.switches[key], self.sliders[key], self.boxes[key] = switch, slider, box
            rows.append(ft.Column([switch, box], spacing=0))
        self.effects_control = ft.Column(rows, spacing=8)

        self.reset_button = ft.TextButton("Reset to typical vision",
                                          on_click=lambda e: self.reset())

    # --- state --------------------------------------------------------------------------
    def state(self) -> VisionState:
        cvd = (self.cvd_key, self.cvd_slider.value) if self.cvd_key else None
        return VisionState(cvd=cvd, effects=dict(self.effects))

    def _emit(self):
        self.on_change(self.state())

    # --- handlers -----------------------------------------------------------------------
    def _on_cvd(self, e):
        value = e.control.value
        self.cvd_key = None if value in (None, TYPICAL) else value
        if self.cvd_key:
            cond = CVD_CONDITIONS[self.cvd_key]
            self.cvd_slider.value = cond.default
            self.cvd_name.value = cond.label
            self.cvd_scale.value = cond.slider_label
        self.cvd_box.visible = self.cvd_key is not None
        _upd(self.cvd_box)
        self._emit()

    def _on_cvd_slider(self, e):
        if self.cvd_key:
            self._emit()

    def _on_effect(self, key: str):
        on = self.switches[key].value
        if on:
            self.effects[key] = self.sliders[key].value
        else:
            self.effects.pop(key, None)
        self.boxes[key].visible = on
        _upd(self.boxes[key])
        self._emit()

    def _on_effect_slider(self, key: str):
        if self.switches[key].value:
            self.effects[key] = self.sliders[key].value
            self._emit()

    def reset(self):
        self.cvd_key = None
        self.cvd_group.value = TYPICAL
        self.cvd_box.visible = False
        self.effects.clear()
        for key, cond in EFFECT_CONDITIONS.items():
            self.switches[key].value = False
            self.sliders[key].value = cond.default
            self.boxes[key].visible = False
        _upd(self.cvd_control)
        _upd(self.effects_control)
        self._emit()