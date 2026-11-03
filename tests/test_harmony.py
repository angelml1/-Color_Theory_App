import pytest
from color_math.convert import hex_to_hsv
from color_math.harmony import HARMONIES, KINDS, harmony

BASE = "#d62828"


def test_none_returns_base_only():
    assert harmony(BASE, None) == [BASE]


def test_complementary_of_red_is_cyan():
    assert harmony("#ff0000", "complementary") == ["#ff0000", "#00ffff"]


@pytest.mark.parametrize("kind,n", [(k, len(v)) for k, v in HARMONIES.items()])
def test_color_counts(kind, n):
    assert len(harmony(BASE, kind)) == n


def test_analogous_middle_is_base():
    assert harmony(BASE, "analogous")[1] == BASE


def test_monochromatic_count_and_contains_base():
    out = harmony(BASE, "monochromatic", 5)
    assert len(out) == 5 and BASE in out


def test_monochromatic_keeps_hue():
    base_h = hex_to_hsv(BASE)[0]
    for c in harmony(BASE, "monochromatic", 5):
        assert abs(hex_to_hsv(c)[0] - base_h) < 3


def test_monochromatic_single_is_base():
    assert harmony(BASE, "monochromatic", 1) == [BASE]


@pytest.mark.parametrize("kind", [None] + KINDS)
def test_base_is_included(kind):
    assert BASE in harmony(BASE, kind)


@pytest.mark.parametrize("kind", [None] + KINDS)
def test_valid_hex(kind):
    for c in harmony(BASE, kind):
        assert len(c) == 7 and c[0] == "#"
        int(c[1:], 16)