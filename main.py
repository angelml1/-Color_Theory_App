# main functionality
import flet as ft

from components.layout import build_shell
from palette_state import Palette
from pages import accessibility, color_wheel, upload


def main(page: ft.Page):
    page.title = "Color Theory App"
    palette = Palette()
    build_shell(page, palette, {
        # "Home": home.build,
        "Color Wheel": color_wheel.build,
        "Upload": lambda palette: upload.build(page, palette),
        # "Sandbox": color_theory.build,
        "Accessibility": accessibility.build,
    })


ft.run(main)