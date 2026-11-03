import pytest
from color_math.contrast import (contrast_ratio, readable_text_color,
                                 relative_luminance, wcag_results)


def test_black_on_white_is_21():
    assert contrast_ratio("#000000", "#ffffff") == pytest.approx(21.0)


def test_identical_colors_are_1():
    assert contrast_ratio("#3a7bd5", "#3a7bd5") == pytest.approx(1.0)


def test_order_does_not_matter():
    assert contrast_ratio("#123456", "#fedcba") == contrast_ratio("#fedcba", "#123456")


def test_luminance_extremes():
    assert relative_luminance("#000000") == 0.0
    assert relative_luminance("#ffffff") == pytest.approx(1.0)


def test_known_aa_boundary_on_white():
    assert contrast_ratio("#767676", "#ffffff") >= 4.5     # smallest passing gray
    assert contrast_ratio("#777777", "#ffffff") < 4.5


def test_wcag_thresholds():
    r = wcag_results(4.5)
    assert r["aa_normal"] and r["aaa_large"] and not r["aaa_normal"]
    assert not wcag_results(4.49)["aa_normal"]
    assert wcag_results(7.0)["aaa_normal"]
    assert wcag_results(3.0)["aa_ui"] and not wcag_results(2.99)["aa_ui"]


def test_readable_text_color():
    assert readable_text_color("#ffffff") == "#000000"
    assert readable_text_color("#000000") == "#ffffff"