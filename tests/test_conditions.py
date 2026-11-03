import numpy as np
import pytest
from color_math.conditions import (CVD_CONDITIONS, EFFECT_CONDITIONS,
                                   VisionState, build_pipeline, CVD_GROUPS)

IMG = np.random.default_rng(3).random((8, 8, 3))
ALL = {**CVD_CONDITIONS, **EFFECT_CONDITIONS}


def test_empty_state_is_identity():
    assert np.array_equal(build_pipeline(VisionState())(IMG), IMG)


@pytest.mark.parametrize("key", ALL)
def test_severity_zero_is_identity(key):
    assert np.allclose(ALL[key].build(0.0)(IMG), IMG, atol=1e-6)


@pytest.mark.parametrize("key", ALL)
def test_full_severity_runs(key):
    out = ALL[key].build(1.0)(IMG)
    assert out.shape == IMG.shape and np.all(np.isfinite(out))


def test_effect_order_is_independent_of_click_order():
    a = VisionState(effects={"low_acuity": 0.5, "cataracts": 0.7, "low_contrast": 0.3})
    b = VisionState(effects={"low_contrast": 0.3, "cataracts": 0.7, "low_acuity": 0.5})
    assert np.allclose(build_pipeline(a)(IMG), build_pipeline(b)(IMG))


def test_achromatopsia_full_gives_equal_channels():
    out = build_pipeline(VisionState(cvd=("achromatopsia", 1.0)))(IMG)
    assert np.allclose(out[..., 0], out[..., 1]) and np.allclose(out[..., 1], out[..., 2])


def test_cvd_and_effects_stack():
    cvd_only = build_pipeline(VisionState(cvd=("deutan", 1.0)))(IMG)
    both = build_pipeline(VisionState(cvd=("deutan", 1.0),
                                      effects={"low_contrast": 0.5}))(IMG)
    assert not np.allclose(cvd_only, both)


def test_groups_cover_every_cvd_condition_exactly_once():
    keys = [k for group in CVD_GROUPS.values() for k in group]
    assert sorted(keys) == sorted(CVD_CONDITIONS)