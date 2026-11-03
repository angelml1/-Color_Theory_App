# preview of vision effects using palette swatches
import flet as ft

from color_math.imaging import make_scene, to_png_b64

PREVIEW_WIDTH = 720


class VisionPreview:
    """Shows palette bands + sample text through a vision pipeline."""

    def __init__(self):
        self.control = ft.Container()

    def show(self, colors: list[str], fg: str, bg: str, effect):
        scene = make_scene(colors, fg, bg, width=PREVIEW_WIDTH)
        png_b64 = to_png_b64(effect(scene))
        self.control.content = ft.Image(src=png_b64, width=PREVIEW_WIDTH)