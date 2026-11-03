# sample image to show vision effects
import base64
import io

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from color_math.contrast import readable_text_color
from color_math.convert import rgb_to_hex
from color_math.vision_effects import from_pil, to_pil


def _font(size: int):
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def _text(draw, xy, text, fill, font, anchor):
    try:
        draw.text(xy, text, fill=fill, font=font, anchor=anchor)
    except Exception: 
        draw.text(xy, text, fill=fill, font=font)


def make_scene(colors: list[str], fg: str, bg: str, width: int = 720,
               band_h: int = 70, panel_h: int = 170) -> np.ndarray:
    """Top: one band per palette color. Bottom: sample text in fg on bg."""
    height = (band_h if colors else 0) + panel_h
    im = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(im)

    y = 0
    if colors:
        band_w = width / len(colors)
        for i, c in enumerate(colors):
            x0, x1 = round(i * band_w), round((i + 1) * band_w)
            draw.rectangle([x0, 0, x1, band_h - 1], fill=c)
            _text(draw, ((x0 + x1) / 2, band_h / 2), "Aa",
                  readable_text_color(c), _font(28), "mm")
        y = band_h

    draw.rectangle([0, y, width, height], fill=bg)
    _text(draw, (24, y + 20), "Large text sample", fg, _font(34), "la")
    _text(draw, (24, y + 80), "Normal text: the quick brown fox jumps over the lazy dog.",
          fg, _font(16), "la")
    _text(draw, (24, y + 112), "Small text: 12 px detail, like a caption or label.",
          fg, _font(12), "la")
    return from_pil(im)


def image_to_b64(im: Image.Image) -> str:
    buf = io.BytesIO()
    im.convert("RGB").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def to_png_b64(arr: np.ndarray) -> str:
    return image_to_b64(to_pil(arr))


# --- eyedropper helpers --------------------------------------------------------
def grab_screen() -> Image.Image:
    """Screenshot of the whole desktop."""
    from PIL import ImageGrab
    try:
        return ImageGrab.grab(all_screens=True).convert("RGB")
    except TypeError:
        return ImageGrab.grab().convert("RGB")


def pixel_at(im: Image.Image, x: float, y: float) -> str:
    """'#rrggbb' of the pixel at (x, y), clamped to the image bounds."""
    x = min(max(int(x), 0), im.width - 1)
    y = min(max(int(y), 0), im.height - 1)
    r, g, b = im.convert("RGB").getpixel((x, y))
    return rgb_to_hex(r, g, b)