import numpy as np
import pytest
from color_math.color_blindness import KINDS, simulate


@pytest.mark.parametrize("kind", KINDS)
def test_gray_is_unchanged(kind):
    img = np.full((2, 2, 3), 0.5)
    assert np.allclose(simulate(img, kind, 1.0), img, atol=1e-3)


@pytest.mark.parametrize("kind", KINDS)
def test_severity_zero_is_identity(kind):
    img = np.random.default_rng(0).random((4, 4, 3))
    assert np.array_equal(simulate(img, kind, 0.0), img)


@pytest.mark.parametrize("kind", KINDS)
def test_output_stays_in_range(kind):
    img = np.random.default_rng(1).random((8, 8, 3))
    out = simulate(img, kind, 1.0)
    assert out.shape == img.shape and out.min() >= 0 and out.max() <= 1


@pytest.mark.parametrize("kind,color", [("protan", (1, 0, 0)), ("deutan", (1, 0, 0)),
                                        ("tritan", (0, 0, 1))])
def test_affected_color_changes(kind, color):
    img = np.array([[color]], dtype=float)
    assert np.abs(simulate(img, kind, 1.0) - img).max() > 0.2


def test_partial_severity_is_between():
    img = np.array([[[1.0, 0.0, 0.0]]])
    full = np.abs(simulate(img, "deutan", 1.0) - img).max()
    half = np.abs(simulate(img, "deutan", 0.5) - img).max()
    assert 0 < half < full