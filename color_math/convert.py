# convert between color formats (hex, rgb, etc)
import colorsys
import re
import numpy as np

_HEX = re.compile(r"#?([0-9a-f]{3}|[0-9a-f]{6})")
_RGB = re.compile(r"(?:rgb\()?\s*(\d{1,3})\s*[,\s]\s*(\d{1,3})\s*[,\s]\s*(\d{1,3})\s*\)?")


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """'#rrggbb' -> (0-255, 0-255, 0-255)"""
    return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))


def rgb_to_hex(r: float, g: float, b: float) -> str:
    return "#{:02x}{:02x}{:02x}".format(*(int(round(min(max(v, 0), 255))) for v in (r, g, b)))


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


def srgb_to_linear(a) -> np.ndarray:
    """sRGB (0-1) -> linear light (0-1). Works on scalars and arrays."""
    a = np.clip(np.asarray(a, dtype=float), 0.0, 1.0)
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(a) -> np.ndarray:
    a = np.clip(np.asarray(a, dtype=float), 0.0, 1.0)
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - 0.055)

# Oklab conversion added by Cori

def srgb_to_oklab(a) -> np.ndarray:
    lin_rgb = srgb_to_linear(a)

    # matrix via Bruce Lindboom
    # url: http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    m = np.array([
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ])
    # matricies m1 and m2 via Björn Ottoson
    # url: https://bottosson.github.io/posts/oklab/
    m1 = np.array([
        [0.8189330101, 0.3618667424, -0.1288597137],
        [0.0329845436, 0.9293118715,  0.0361456387],
        [0.0482003018, 0.2643662691,  0.6338517070],
    ])
    m2 = np.array([
        [0.2104542553,  0.7936177850, -0.0040720468],
        [1.9779984951, -2.4285922050,  0.4505937099],
        [0.0259040371,  0.7827717662, -0.8086757660],
    ])

    # calculate xyz from linear rbg
    xyz = lin_rgb @ m.T

    # xyz to L, M, S cones
    lms = xyz @ m1.T

    # fix floating point errors
    lms = np.where(np.abs(lms) < 1e-14, 0.0, lms)

    lms_p = np.cbrt(lms)
        
    return lms_p @ m2.T

def oklab_to_srgb(a) -> np.ndarray:

    # mathematical inverses of m, m2, and m3 from srgb_to_oklab()
    inv_m = np.array([
        [ 3.24045484, -1.53713885, -0.49853155],
        [-0.96926639,  1.87601093,  0.04155608],
        [ 0.05564342, -0.20402585,  1.05722516]
    ])
    inv_m1 = np.array([
        [ 1.22701385, -0.55779998,  0.28125615],
        [-0.04058018,  1.11225687, -0.07167668],
        [-0.07638128, -0.42148198,  1.58616322]
    ])
    inv_m2 = np.array([
        [ 1.00000000, 0.39633779, 0.21580376],
        [ 1.00000001, -0.10556134, -0.06385417],
        [ 1.00000005, -0.08948418, -1.29148554] 
    ])

    lms_p = a @ inv_m2.T     # undo m2 transform -> lms'
    
    lms = np.power(lms_p, 3) # undo cube root ----> L, M, S cones
    
    xyz = lms @ inv_m1.T     # undo m1 transform -> xyz color space
    
    lin_rgb = xyz @ inv_m.T  # undo m transform --> linear rgb

    return linear_to_srgb(lin_rgb)

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

def main():
    print(srgb_to_linear(hex_to_rgb("#ffffff")))


if __name__ == "__main__":
    main()