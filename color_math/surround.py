# math for sandbox surround tab: how a color looks on different backgrounds

import numpy as np

from color_math.convert import (hex_to_rgb, oklab_to_srgb, rgb_to_hex, srgb_to_oklab)

LIGHTNESS_PUSH = 0.18      # how far L moves away from surround's L
CHROMA_PUSH = 0.18         # how far (a, b) moves away from surround's (a, b)
MATCH_TOLERANCE = 0.015    # about the smallest difference most people can see
BORDER_DAMPING = 0.45      # neutral gap between the two weakens effect

# approximated Oklab hue angles, used to describe shift in color words
_HUE_NAMES = [(29, "red"), (55, "orange"), (110, "yellow"), (142, "green"),
              (195, "cyan"), (264, "blue"), (305, "purple"), (350, "pink")]

# helper to convert hex to Oklab
def hex_to_oklab(hex_color: str) -> np.ndarray:
    return srgb_to_oklab(np.array(hex_to_rgb(hex_color), dtype=float) / 255)

# helper to convert Oklab to hex
def oklab_to_hex(lab) -> str:
    rgb = np.clip(oklab_to_srgb(np.asarray(lab, dtype=float)), 0.0, 1.0) * 255
    return rgb_to_hex(*rgb)

# helper to convert hex to Oklch (lightness, chroma, hue)
def oklch(hex_color: str) -> tuple[float, float, float]:
    """(lightness 0-1, chroma, hue in degrees 0-360)."""
    L, a, b = hex_to_oklab(hex_color)
    return float(L), float(np.hypot(a, b)), float(np.degrees(np.arctan2(b, a)) % 360)

# returns closest color name from Oklab hue angle
def hue_name(degrees: float) -> str:
    """Nearest color name for an Oklab hue angle."""
    def gap(h):
        return abs((degrees - h + 180) % 360 - 180)
    return min(_HUE_NAMES, key=lambda item: gap(item[0]))[1]

# determines how strong the perceptual illusion is
# weaker when a neutral colored border seperates the two
def effect_strength(center_fraction: float, border: bool) -> float:
    base = float(np.clip(1.2 - center_fraction, 0.4, 1.0))
    return base * (BORDER_DAMPING if border else 1.0)

# calculates the percieved color in Oklab space
def _perceived_lab(center: str, surround: str, strength: float) -> np.ndarray:
    c, s = hex_to_oklab(center), hex_to_oklab(surround)
    out = c.copy()
    out[0] = np.clip(c[0] + strength * LIGHTNESS_PUSH * (c[0] - s[0]), 0.0, 1.0)
    out[1:] = c[1:] - strength * CHROMA_PUSH * s[1:]
    return out

# wrapper for previous function to return hex instead
def perceived_color(center: str, surround: str, strength: float = 1.0) -> str:
    return oklab_to_hex(_perceived_lab(center, surround, strength))

# 
def matching_color(target: str, on_surround: str, to_surround: str, strength: float = 1.0) -> dict:
    goal = _perceived_lab(target, on_surround, strength)
    s = hex_to_oklab(to_surround)
    a, c = strength * LIGHTNESS_PUSH, strength * CHROMA_PUSH
    x = np.empty(3)
    x[0] = (goal[0] + a * s[0]) / (1 + a)
    x[1:] = goal[1:] + c * s[1:]
    color = oklab_to_hex(x)
    got = _perceived_lab(color, to_surround, strength)
    error = float(np.linalg.norm(got - goal))
    return {"color": color, "looks_like": oklab_to_hex(goal), "error": error,
            "exact": error < MATCH_TOLERANCE}

#
def describe_shift(actual: str, perceived: str) -> dict:
    a, p = hex_to_oklab(actual), hex_to_oklab(perceived)
    d_l = float(p[0] - a[0])
    d_ab = p[1:] - a[1:]
    size = float(np.hypot(*d_ab))
    toward = hue_name(float(np.degrees(np.arctan2(d_ab[1], d_ab[0])) % 360)) \
        if size > 0.004 else None
    return {"d_lightness": d_l, "d_color": size, "toward": toward}

# generates the preview
def render_surround(center: str | list[str], surrounds: list[str], *, center_fraction: float = 0.3,
                    border: str | None = None, width: int = 640, height: int = 280) -> np.ndarray:
    centers = [center] * len(surrounds) if isinstance(center, str) else list(center)
    n = max(len(surrounds), 1)
    img = np.ones((height, width, 3), dtype=float)
    edges = [round(i * width / n) for i in range(n + 1)]
    for i, bg in enumerate(surrounds):
        x0, x1 = edges[i], edges[i + 1]
        img[:, x0:x1] = np.array(hex_to_rgb(bg), dtype=float) / 255
        side = max(2, int(min(x1 - x0, height) * center_fraction))
        cx, cy = (x0 + x1) // 2, height // 2
        left, top = cx - side // 2, cy - side // 2
        if border:
            gap = 6
            img[top - gap:top + side + gap, left - gap:left + side + gap] = \
                np.array(hex_to_rgb(border), dtype=float) / 255
        img[top:top + side, left:left + side] = np.array(hex_to_rgb(centers[i]), dtype=float) / 255
    return img
