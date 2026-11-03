# main functionality
import flet as ft

from components.layout import build_shell
from palette_state import Palette
from pages import color_wheel, accessibility


def main(page: ft.Page):
    page.title = "Color Theory App"
    palette = Palette()
    build_shell(page, palette, {
        # "Home": home.build,
        "Color Wheel": color_wheel.build,
        # "Upload": upload.build,
        # "Sandbox": color_theory.build,
        "Accessibility": accessibility.build,
    })


ft.run(main)