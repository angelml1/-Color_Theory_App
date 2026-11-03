# math for accessibility color contrast ratings
from color_math.convert import hex_to_rgb

# Minimum contrast ratios from WCAG 2.x
THRESHOLDS = {
    "aa_normal": 4.5,     # normal text, AA
    "aaa_normal": 7.0,    # normal text, AAA
    "aa_large": 3.0,      # large text, AA
    "aaa_large": 4.5,     # large text, AAA
    "aa_ui": 3.0,         # UI components and graphical objects (no AAA level exists)
}


def _linear(channel_8bit: int) -> float:
    c = channel_8bit / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    """0 (black) to 1 (white), using the Rec. 709 weights WCAG specifies."""
    r, g, b = hex_to_rgb(hex_color)
    return 0.2126 * _linear(r) + 0.7152 * _linear(g) + 0.0722 * _linear(b)


def contrast_ratio(color_a: str, color_b: str) -> float:
    """1.0 (identical) to 21.0 (black on white). Order doesn't matter."""
    la, lb = relative_luminance(color_a), relative_luminance(color_b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def wcag_results(ratio: float) -> dict[str, bool]:
    """Pass/fail for each requirement. Uses the exact ratio, not a rounded one,
    so a displayed '4.50' can still fail if the true value is 4.499."""
    return {name: ratio >= minimum for name, minimum in THRESHOLDS.items()}


def readable_text_color(background_hex: str) -> str:
    """Black or white, whichever has more contrast with the background."""
    black_ratio = contrast_ratio("#000000", background_hex)
    white_ratio = contrast_ratio("#ffffff", background_hex)
    return "#000000" if black_ratio >= white_ratio else "#ffffff"