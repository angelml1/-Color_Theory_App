from PIL import Image

from color_math.imaging import pixel_at


def test_pixel_at_reads_color():
    im = Image.new("RGB", (4, 4), (10, 20, 30))
    assert pixel_at(im, 1.9, 2.2) == "#0a141e"


def test_pixel_at_clamps_out_of_range():
    im = Image.new("RGB", (4, 4), (255, 0, 0))
    assert pixel_at(im, -5, 99) == "#ff0000"