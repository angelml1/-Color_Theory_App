import pytest
from color_math.convert import hex_to_hsv, hsv_to_hex, parse_color


def test_roundtrip_is_exact_for_8bit_colors():
    for c in ["#000000", "#ffffff", "#3a7bd5", "#ff0000", "#12ab9f"]:
        assert hsv_to_hex(*hex_to_hsv(c)) == c


@pytest.mark.parametrize("text,expected", [
    ("#3a7bd5", "#3a7bd5"),
    ("3A7BD5", "#3a7bd5"),
    ("#abc", "#aabbcc"),
    ("  #FFF  ", "#ffffff"),
    ("58, 123, 213", "#3a7bd5"),
    ("58 123 213", "#3a7bd5"),
    ("rgb(58,123,213)", "#3a7bd5"),
    ("0,0,0", "#000000"),
])
def test_valid(text, expected):
    assert parse_color(text) == expected


@pytest.mark.parametrize("text", ["", "hello", "#12", "#12345", "256, 0, 0",
                                  "1, 2", "1, 2, 3, 4", "#gggggg", None])
def test_invalid(text):
    assert parse_color(text) is None