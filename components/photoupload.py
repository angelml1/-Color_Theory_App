#the logic for uploading images
import io

import numpy as np
from PIL import Image, UnidentifiedImageError

ALLOWED_TYPES = {"PNG", "JPEG", "WEBP", "BMP", "GIF"}
MAX_UPLOAD_MB = 10


def _stream_size(source):
    """Best-effort size of a file-like object, or None if unmeasurable."""
    try:
        pos = source.tell()
        source.seek(0, io.SEEK_END)
        size = source.tell()
        source.seek(pos)
        return size
    except (AttributeError, OSError):
        return None


def load_image(source, max_size=None):
    #Turn an upload into an RGB PIL image.

    #source can be a file path, raw bytes, or a file-like object
    #if max size is set, we shrink so the longest side is at most this many pixels.
    #shows a  message if the file isn't usable.
    #note: GIFs are read as their first frame only.

    if isinstance(source, (bytes, bytearray)):
        source = io.BytesIO(source)
    elif hasattr(source, "seek"):
        source.seek(0)  # uploads may already have been read once

    size = _stream_size(source)
    if size is not None and size > MAX_UPLOAD_MB * 1024 * 1024:
        raise ValueError(f"Image is larger than {MAX_UPLOAD_MB} MB.")

    try:
        image = Image.open(source)
        image.load()  # forces a full read so corrupt files fail here
    except (UnidentifiedImageError, OSError):
        raise ValueError("That file isn't a readable image.")

    if image.format not in ALLOWED_TYPES:
        raise ValueError(f"Unsupported image type: {image.format}")

    # Composite any transparency over white so hidden RGB doesn't pollute colors
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        image = image.convert("RGBA")
        bg = Image.new("RGB", image.size, (255, 255, 255))
        bg.paste(image, mask=image.split()[-1])
        image = bg
    else:
        image = image.convert("RGB")

    if max_size:
        image.thumbnail((max_size, max_size))  # keeps aspect ratio
    return image


def to_array(image):
    """PIL image -> numpy array of shape (H, W, 3)."""
    return np.array(image)