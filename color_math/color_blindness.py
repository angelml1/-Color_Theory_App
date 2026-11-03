# color vision deficiency (color blindess) simulation math
import numpy as np

from color_math.convert import linear_to_srgb, srgb_to_linear

# Machado, Oliveira & Fernandes (2009), severity 1.0, applied in linear RGB.
MATRICES = {
    "protan": np.array([
        [0.152286, 1.052583, -0.204868],
        [0.114503, 0.786281, 0.099216],
        [-0.003882, -0.048116, 1.051998],
    ]),
    "deutan": np.array([
        [0.367322, 0.860646, -0.227968],
        [0.280085, 0.672501, 0.047413],
        [-0.011820, 0.042940, 0.968881],
    ]),
    "tritan": np.array([
        [1.255528, -0.076749, -0.178779],
        [-0.078411, 0.930809, 0.147602],
        [0.004733, 0.691367, 0.303900],
    ]),
}
KINDS = list(MATRICES)


def simulate(img: np.ndarray, kind: str, severity: float = 1.0) -> np.ndarray:
    """img: float array (H, W, 3), sRGB 0-1. severity 0 = typical vision,
    1 = complete (-opia); values between approximate the -anomaly forms."""
    severity = min(max(float(severity), 0.0), 1.0)
    if severity == 0.0:
        return img
    matrix = (1 - severity) * np.eye(3) + severity * MATRICES[kind]
    linear = srgb_to_linear(img)
    return linear_to_srgb(linear @ matrix.T)