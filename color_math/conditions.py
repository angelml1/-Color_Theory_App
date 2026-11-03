# presets that combine math for different conditions
# pipeline for stacking effects from color blindness and vision effects
from dataclasses import dataclass, field
from functools import partial
from typing import Callable

from color_math import color_blindness as cb
from color_math.vision_effects import (Effect, blur, grayscale, haze, pipeline,
                                       reduce_contrast, yellow_tint)


@dataclass(frozen=True)
class Condition:
    label: str                          # full name
    short: str                          # radio / switch text
    build: Callable[[float], Effect]    # severity (0-1) -> effect
    default: float = 1.0
    slider_label: str = "Severity"
    order: int = 0                      


SEVERITY_LABEL = "Severity: 1 = complete (-opia), lower = partial (-anomaly)"

# single select
CVD_CONDITIONS = {
    "protan": Condition("Protanopia / protanomaly", "Protan (red-sensitive cones)",
        lambda s: partial(cb.simulate, kind="protan", severity=s),
        slider_label=SEVERITY_LABEL),
    "deutan": Condition("Deuteranopia / deuteranomaly", "Deutan (green-sensitive cones)",
        lambda s: partial(cb.simulate, kind="deutan", severity=s),
        slider_label=SEVERITY_LABEL),
    "tritan": Condition("Tritanopia / tritanomaly", "Tritan (blue-sensitive cones)",
        lambda s: partial(cb.simulate, kind="tritan", severity=s),
        slider_label=SEVERITY_LABEL),
    "achromatopsia": Condition("Achromatopsia", "Achromatopsia (no color)",
        lambda s: partial(grayscale, amount=s),
        slider_label="Color loss: 1 = complete"),
}

# color blindness dropdown groups
CVD_GROUPS = {
    "Red-Green": ["protan", "deutan"],
    "Blue-Yellow": ["tritan"],
    "Monochromacy": ["achromatopsia"],
}

# muti-select - stacks on top of the CVD choice.
EFFECT_CONDITIONS = {
    "cataracts": Condition("Cataracts", "Cataracts",
        lambda s: pipeline(partial(yellow_tint, amount=0.7 * s),
                           partial(haze, amount=0.3 * s)),
        default=0.7, order=10),
    "low_contrast": Condition("Reduced contrast sensitivity", "Low contrast",
        lambda s: partial(reduce_contrast, amount=0.85 * s),
        order=20),
    "low_acuity": Condition("Low acuity (blur)", "Low acuity",
        lambda s: partial(blur, amount=s),
        order=30),                                            
}


@dataclass(frozen=True)
class VisionState:
    cvd: tuple[str, float] | None = None                
    effects: dict[str, float] = field(default_factory=dict)


def build_pipeline(state: VisionState) -> Effect:
    """Color changes first, then effects in fixed order (blur last)."""
    steps = []
    if state.cvd:
        key, severity = state.cvd
        steps.append(CVD_CONDITIONS[key].build(severity))
    for key in sorted(state.effects, key=lambda k: EFFECT_CONDITIONS[k].order):
        steps.append(EFFECT_CONDITIONS[key].build(state.effects[key]))
    return pipeline(*steps)