import numpy as np
from color_math.vision_effects import (apply_to_hex, blur, grayscale, haze,
                                       pipeline, reduce_contrast, yellow_tint)

IMG = np.random.default_rng(2).random((16, 16, 3))


def test_empty_pipeline_is_identity():
    assert np.array_equal(pipeline()(IMG), IMG)


def test_grayscale_full_has_equal_channels():
    out = grayscale(IMG, 1.0)
    assert np.allclose(out[..., 0], out[..., 1]) and np.allclose(out[..., 1], out[..., 2])


def test_grayscale_zero_is_identity():
    assert np.allclose(grayscale(IMG, 0.0), IMG)


def test_full_contrast_loss_is_flat_gray():
    assert np.allclose(reduce_contrast(IMG, 1.0), 0.5)


def test_haze_full_is_white():
    assert np.allclose(haze(IMG, 1.0), 1.0)


def test_yellow_tint_cuts_blue_on_white():
    white = np.ones((1, 1, 3))
    out = yellow_tint(white, 1.0)[0, 0]
    assert out[2] < out[0]


def test_blur_zero_is_identity():
    assert np.array_equal(blur(IMG, 0.0), IMG)


def test_blur_softens_an_edge():
    img = np.zeros((8, 64, 3))
    img[:, 32:] = 1.0
    out = blur(img, 1.0)
    assert 0.0 < out[4, 31, 0] < out[4, 32, 0] < 1.0


def test_apply_to_hex_grayscale_red():
    out = apply_to_hex("#ff0000", lambda im: grayscale(im, 1.0))
    r, g, b = out[1:3], out[3:5], out[5:7]
    assert r == g == b