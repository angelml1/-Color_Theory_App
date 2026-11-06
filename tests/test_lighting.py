import numpy as np
import pytest

from color_math.lighting import (GLOW_MODES, GLOW_SHAPES, glow_falloff, glow_sample,
                                 hex_to_linear, lit_color, linear_to_hex,
                                 relight_palette, render_glow, render_shadow,
                                 shadow_color, shadow_readout)


def test_linear_roundtrip():
    for c in ("#000000", "#ffffff", "#3a7bd5", "#c9a27e"):
        assert linear_to_hex(hex_to_linear(c)) == c


def test_white_light_leaves_color_alone():
    assert lit_color("#3a7bd5", "#ffffff") == "#3a7bd5"


def test_red_light_on_pure_green_is_black():
    # a green surface reflects no red, so red light has nothing to bounce
    assert lit_color("#00ff00", "#ff0000") == "#000000"


def test_light_on_white_shows_the_light_color():
    assert lit_color("#ffffff", "#ff8800") == "#ff8800"


def _brightness(h):
    return sum(int(h[i:i + 2], 16) for i in (1, 3, 5))


def test_shadow_is_darker_than_lit():
    r = shadow_readout("#c9a27e", "#3a7bd5", "#ffd27f", "#6fa8ff", intensity=1.0, ambient=0.25)
    assert _brightness(r["surface_lit"]) > _brightness(r["surface_shadow"])
    assert _brightness(r["object_lit"]) > _brightness(r["object_shadow"])


def test_shadow_takes_the_fill_light_color():
    # blue fill on a neutral gray surface: the shadow leans blue
    dark = shadow_color("#808080", "#4060ff", 0.5)
    r, g, b = (int(dark[i:i + 2], 16) for i in (1, 3, 5))
    assert b > g > r


def test_falloff_is_one_at_edge_and_decreasing():
    d = np.array([0.0, 30.0, 90.0, 300.0])
    f = glow_falloff(d, 90.0)
    assert f[0] == pytest.approx(1.0) and np.all(np.diff(f) < 0)
    assert glow_falloff(-5.0, 90.0) == pytest.approx(1.0)      # inside the emitter


def test_bloom_ignores_surface_but_cast_does_not():
    kw = dict(intensity=1.0, ambient=0.0, falloff=1.0)
    # pure green surface, red emitter
    assert glow_sample("#00ff00", "#ff0000", mode="cast", **kw) == "#000000"
    assert glow_sample("#00ff00", "#ff0000", mode="bloom", **kw) == "#ff0000"


def test_zero_intensity_is_just_ambient():
    out = glow_sample("#3a7bd5", "#ff8800", intensity=0.0, ambient=1.0,
                      mode="cast", falloff=1.0)
    assert out == "#3a7bd5"


@pytest.mark.parametrize("mode", GLOW_MODES)
@pytest.mark.parametrize("shape", GLOW_SHAPES)
def test_render_glow_shape_range_and_core(mode, shape):
    img = render_glow("#3a7bd5", "#ff8800", mode=mode, shape=shape, width=200, height=100)
    assert img.shape == (100, 200, 3)
    assert np.all(np.isfinite(img)) and img.min() >= 0 and img.max() <= 1
    # centre pixel is the emitter color itself
    assert linear_to_hex(hex_to_linear("#ff8800")) == "#ff8800"
    centre = tuple(np.round(img[50, 100] * 255).astype(int))
    assert centre == (255, 136, 0)


def test_render_shadow_shape_range():
    img = render_shadow("#c9a27e", "#3a7bd5", "#ffd27f", "#6fa8ff", width=200, height=120)
    assert img.shape == (120, 200, 3)
    assert np.all(np.isfinite(img)) and img.min() >= 0 and img.max() <= 1


def test_shadow_moves_away_from_the_light():
    kw = dict(width=300, height=300, softness=0.0)
    # light from the right (azimuth 0) -> shadow on the left half
    img = render_shadow("#ffffff", "#ffffff", "#ffffff", "#000000",
                        intensity=1.0, ambient=0.0, azimuth=0.0, elevation=30, **kw)
    left, right = img[150, 40].mean(), img[150, 260].mean()
    assert left < right


def _px(img, x, y):
    return tuple(int(v) for v in np.round(img[int(y), int(x)] * 255))


def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def test_render_shadow_matches_readout():
    kw = dict(intensity=1.0, ambient=0.25)
    colors = ("#c9a27e", "#3a7bd5", "#ffd27f", "#6fa8ff")
    w, h, az, el = 720, 400, 135.0, 45.0
    img = render_shadow(*colors, azimuth=az, elevation=el, width=w, height=h, softness=0.0, **kw)
    r = shadow_readout(*colors, **kw)
    # open floor, far from the object and its shadow
    assert _px(img, 5, 5) == _rgb(r["surface_lit"])
    # a point on the sphere facing the light, and one turned away from it
    cx, cy, rad = w / 2, h / 2, min(w, h) * 0.2
    a, e = np.radians(az), np.radians(el)
    lit = _px(img, cx + rad * np.cos(e) * np.cos(a), cy + rad * np.cos(e) * np.sin(a))
    dark = _px(img, cx - 0.9 * rad * np.cos(a), cy - 0.9 * rad * np.sin(a))
    assert max(abs(x - y) for x, y in zip(lit, _rgb(r["object_lit"]))) <= 2
    assert max(abs(x - y) for x, y in zip(dark, _rgb(r["object_shadow"]))) <= 2


def test_light_height_does_not_change_floor_brightness():
    kw = dict(width=300, height=200, azimuth=135.0)
    low = render_shadow("#c9a27e", "#3a7bd5", "#ffd27f", "#6fa8ff", elevation=15, **kw)
    high = render_shadow("#c9a27e", "#3a7bd5", "#ffd27f", "#6fa8ff", elevation=80, **kw)
    assert _px(low, 3, 3) == _px(high, 3, 3)


def test_relight_palette_rows():
    rows = relight_palette(["#ff0000", "#00ff00"], "#ff0000", intensity=1.0,
                           fill="#ffffff", ambient=0.0)
    assert [r[0] for r in rows] == ["#ff0000", "#00ff00"]
    assert rows[0][1] == "#ff0000" and rows[1][1] == "#000000"
    assert relight_palette([], "#ffffff") == []
