# convert between color formats (hex, rgb, etc)
import colorsys
import re

_HEX = re.compile(r"#?([0-9a-f]{3}|[0-9a-f]{6})")
_RGB = re.compile(r"(?:rgb\()?\s*(\d{1,3})\s*[,\s]\s*(\d{1,3})\s*[,\s]\s*(\d{1,3})\s*\)?")


def hex_to_hsv(hex_color: str) -> tuple[float, float, float]:
    """'#rrggbb' -> (hue 0-360, saturation 0-1, value 0-1)"""
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h * 360, s, v


def hsv_to_hex(h: float, s: float, v: float) -> str:
    """(hue in degrees, saturation 0-1, value 0-1) -> '#rrggbb'"""
    s = min(max(s, 0.0), 1.0)
    v = min(max(v, 0.0), 1.0)
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360, s, v)
    return "#{:02x}{:02x}{:02x}".format(round(r * 255), round(g * 255), round(b * 255))


def parse_color(text: str) -> str | None:
    """Accepts '#3a7bd5', '3a7bd5', '#abc', '58, 123, 213', '58 123 213',
    or 'rgb(58, 123, 213)'. Returns '#rrggbb', or None if it can't be read."""
    t = (text or "").strip().lower()

    m = _HEX.fullmatch(t)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return "#" + h

    m = _RGB.fullmatch(t)
    if m:
        r, g, b = (int(x) for x in m.groups())
        if max(r, g, b) <= 255:
            return "#{:02x}{:02x}{:02x}".format(r, g, b)
    return None