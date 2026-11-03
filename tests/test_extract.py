from PIL import Image

from color_math.extract import extract_colors


def test_extract_colors_orders_by_frequency():
    image = Image.new("RGB", (10, 10), (255, 0, 0))
    for x in range(5):
        for y in range(5):
            image.putpixel((x, y), (0, 0, 255))

    assert extract_colors(image, 2) == ["#ff0000", "#0000ff"]


def test_extract_colors_returns_only_colors_present():
    image = Image.new("RGB", (8, 8), (12, 34, 56))

    assert extract_colors(image, 6) == ["#0c2238"]


def test_extract_colors_clamps_requested_count():
    image = Image.new("RGB", (2, 1))
    image.putpixel((0, 0), (255, 0, 0))
    image.putpixel((1, 0), (0, 0, 255))

    assert len(extract_colors(image, 0)) == 1