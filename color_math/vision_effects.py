# math for simulation of different levels of vision (low vision, low contrast, etc)
"""Primitive image effects. Each takes a float array (H, W, 3), sRGB 0-1,
plus an `amount` (0 = off, 1 = max), and returns the same shape."""
from functools import reduce
from typing import Callable

import numpy as np
from scipy.ndimage import gaussian_filter

from color_math.convert import hex_to_rgb, linear_to_srgb, srgb_to_linear, rgb_to_hex

Effect = Callable[[np.ndarray], np.ndarray]

LUMA = np.array([0.2126, 0.7152, 0.0722])


def grayscale(img: np.ndarray, amount: float = 1.0) -> np.ndarray:
    """Keep luminance, drop hue (a value study). amount=1 is fully gray."""
    y = srgb_to_linear(img) @ LUMA
    gray = linear_to_srgb(np.repeat(y[..., None], 3, axis=-1))
    return (1 - amount) * img + amount * gray


def blur(img: np.ndarray, amount: float = 0.0, max_frac: float = 0.012) -> np.ndarray:
    """Low acuity. Blur radius scales with image width, so it looks the same
    on a small preview and a large photo."""
    sigma = amount * max_frac * img.shape[1]
    if sigma <= 0:
        return img
    return gaussian_filter(img, sigma=(sigma, sigma, 0), mode="nearest")


def reduce_contrast(img: np.ndarray, amount: float = 0.0) -> np.ndarray:
    """Compress toward mid-gray (amount=1 is a flat gray image)."""
    return 0.5 + (img - 0.5) * (1 - amount)


def haze(img: np.ndarray, amount: float = 0.0) -> np.ndarray:
    """Veiling glare: stray light added on top, done in linear light."""
    lin = srgb_to_linear(img)
    return linear_to_srgb((1 - amount) * lin + amount * 1.0)


def yellow_tint(img: np.ndarray, amount: float = 0.0) -> np.ndarray:
    """Yellowed lens: attenuate blue strongly and green slightly."""
    scale = np.array([1.0, 1 - 0.15 * amount, 1 - 0.6 * amount])
    return linear_to_srgb(srgb_to_linear(img) * scale)


def pipeline(*effects: Effect) -> Effect:
    """Chain effects left to right. An empty pipeline is typical vision."""
    return lambda img: reduce(lambda x, f: f(x), effects, img)


def apply_to_hex(hex_color: str, effect: Effect) -> str:
    """Run an effect on one color (a 1x1 image)."""
    rgb = np.array([[[v / 255 for v in hex_to_rgb(hex_color)]]], dtype=float)
    out = np.clip(effect(rgb), 0.0, 1.0)[0, 0]
    return rgb_to_hex(*(v * 255 for v in out))


def from_pil(im) -> np.ndarray:
    return np.asarray(im.convert("RGB"), dtype=float) / 255


def to_pil(arr: np.ndarray):
    from PIL import Image
    return Image.fromarray((np.clip(arr, 0, 1) * 255).round().astype("uint8"))