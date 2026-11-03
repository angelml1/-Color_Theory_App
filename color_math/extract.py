from PIL import Image


def extract_colors(image: Image.Image, count: int = 6) -> list[str]:
    """Return the most common quantized RGB colors in an image."""
    count = max(1, min(int(count), 256))
    sample = image.convert("RGB")
    sample.thumbnail((512, 512))
    quantized = sample.quantize(colors=count, method=Image.Quantize.FASTOCTREE)
    frequencies = quantized.getcolors(maxcolors=512 * 512) or []
    palette = quantized.getpalette()
    frequencies.sort(reverse=True)

    colors = []
    for _, index in frequencies:
        red, green, blue = palette[index * 3:index * 3 + 3]
        color = f"#{red:02x}{green:02x}{blue:02x}"
        if color not in colors:
            colors.append(color)
    return colors