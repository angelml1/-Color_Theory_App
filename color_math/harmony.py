# math for color harmonies (complimentary, triadic, etc)
from color_math.convert import hex_to_hsv, hsv_to_hex

HARMONIES = {
    "complementary":       [0, 180],
    "split-complementary": [0, 150, 210],
    "triadic":             [0, 120, 240],
    "tetradic":            [0, 60, 180, 240],
    "analogous":           [-30, 0, 30],
}
KINDS = list(HARMONIES) + ["monochromatic"]


def monochromatic(base_hex: str, count: int = 5,
                  s_min: float = 0.15, s_max: float = 1.0) -> list[str]:
    """Same hue and value, evenly spaced saturations. The step closest to the
    base's own saturation is snapped to it so the main color stays in the set."""
    if count <= 1:
        return [base_hex]
    h, s, v = hex_to_hsv(base_hex)
    step = (s_max - s_min) / (count - 1)
    sats = [s_min + i * step for i in range(count)]
    closest = min(range(count), key=lambda i: abs(sats[i] - s))
    sats[closest] = s
    return [hsv_to_hex(h, x, v) for x in sats]


def harmony(base_hex: str, kind: str | None, count: int = 5) -> list[str]:
    """kind=None -> just the base color. count only affects monochromatic."""
    if kind is None:
        return [base_hex]
    if kind == "monochromatic":
        return monochromatic(base_hex, count)
    h, s, v = hex_to_hsv(base_hex)
    return [hsv_to_hex(h + off, s, v) for off in HARMONIES[kind]]