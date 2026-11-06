import numpy as np
import pytest

from color_math.surround import (describe_shift, effect_strength, hue_name, oklch,
                                 perceived_color, render_surround)

GRAY = "#808080"


def test_gray_looks_lighter_on_dark_and_darker_on_light():
    on_dark = perceived_color(GRAY, "#202020")
    on_light = perceived_color(GRAY, "#e0e0e0")
    assert oklch(on_dark)[0] > oklch(GRAY)[0] > oklch(on_light)[0]


def test_gray_on_red_drifts_away_from_red():
    shift = describe_shift(GRAY, perceived_color(GRAY, "#ff0000"))
    assert shift["toward"] in ("cyan", "green")          # the complement side of red


def test_same_background_changes_nothing_in_lightness():
    assert perceived_color(GRAY, GRAY) == GRAY


def test_zero_strength_is_identity():
    assert perceived_color("#3a7bd5", "#ff0000", strength=0.0) == "#3a7bd5"


def test_border_and_size_change_strength():
    assert effect_strength(0.2, True) < effect_strength(0.2, False)
    assert effect_strength(0.7, False) < effect_strength(0.2, False)
    assert 0 < effect_strength(0.9, True) <= 1


def test_gray_has_no_chroma():
    assert oklch(GRAY)[1] < 1e-3


@pytest.mark.parametrize("deg,name", [(29, "red"), (264, "blue"), (142, "green"),
                                      (359, "pink"), (20, "red")])
def test_hue_name(deg, name):
    assert hue_name(deg) == name


def test_describe_shift_no_change():
    d = describe_shift("#3a7bd5", "#3a7bd5")
    assert d["d_lightness"] == 0 and d["toward"] is None


def test_render_surround_panels_and_center():
    img = render_surround("#ff0000", ["#000000", "#ffffff"], width=200, height=100)
    assert img.shape == (100, 200, 3)
    assert np.allclose(img[50, 100 // 2], [1, 0, 0]) and np.allclose(img[50, 150], [1, 0, 0])
    assert np.allclose(img[2, 5], 0) and np.allclose(img[2, 195], 1)


def test_render_surround_border_is_drawn():
    plain = render_surround("#ff0000", ["#000000"], center_fraction=0.3, width=200, height=100)
    framed = render_surround("#ff0000", ["#000000"], center_fraction=0.3, border="#ffffff",
                             width=200, height=100)
    assert not np.array_equal(plain, framed) and framed.max() == 1.0


def test_matching_color_round_trips_when_in_gamut():
    from color_math.surround import matching_color, hex_to_oklab
    r = matching_color("#808080", "#202020", "#e0e0e0")
    assert r["exact"] and r["error"] < 0.015
    # on the light background the match has to be a different, lighter color
    assert oklch(r["color"])[0] > oklch("#808080")[0]
    # and it now looks like the target does on the dark background
    seen = perceived_color(r["color"], "#e0e0e0")
    assert np.linalg.norm(hex_to_oklab(seen) - hex_to_oklab(r["looks_like"])) < 0.015


def test_matching_with_same_surround_is_the_target():
    from color_math.surround import matching_color
    assert matching_color("#3a7bd5", "#ff0000", "#ff0000")["color"] == "#3a7bd5"


def test_matching_reports_when_it_cannot_match():
    from color_math.surround import matching_color
    r = matching_color("#ff0000", "#00ffff", "#ff0000")      # needs a redder-than-red
    assert not r["exact"] and r["error"] > 0.015


def test_render_surround_accepts_one_center_per_panel():
    img = render_surround(["#ff0000", "#0000ff"], ["#000000", "#ffffff"], width=200, height=100)
    assert np.allclose(img[50, 50], [1, 0, 0]) and np.allclose(img[50, 150], [0, 0, 1])
