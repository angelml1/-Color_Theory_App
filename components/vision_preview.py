# preview of vision effects using palette swatches
import flet as ft
import numpy as np

from color_math.imaging import make_scene, to_png_b64

PREVIEW_WIDTH = 520


class VisionPreview:
    """Palette bands + sample text, seen through a vision pipeline.

    One Image control lives for the whole session. Only its src changes, and
    gapless_playback keeps the previous frame on screen until the next one is
    ready, which is what prevents the flash while a slider moves.

    show() only changes the control. The caller decides what to update."""

    def __init__(self):
        self.image = ft.Image(
            src=to_png_b64(np.ones((1, 1, 3))),
            width=PREVIEW_WIDTH,
            gapless_playback=True, 
        )
        self.control = self.image
        self._key = None
        self._scene = None

    def show(self, colors: list[str], fg: str, bg: str, effect):
        key = (tuple(colors), fg, bg)
        if key != self._key:      
            self._scene = make_scene(colors, fg, bg, width=PREVIEW_WIDTH) 
            self._key = key
        self.image.src = to_png_b64(effect(self._scene))