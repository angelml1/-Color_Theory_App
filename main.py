# main functionality
import flet as ft

from components.layout import build_shell
from palette_state import Palette
from pages import color_wheel, home, upload, color_theory


def main(page: ft.Page):
    page.title = "Color Theory App"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE
    palette = Palette()
    build_shell(page, palette, {
        "Home": lambda active_palette: home.build(active_palette, page),
        "Color Wheel": color_wheel.build,
        "Upload": lambda palette: upload.build(page, palette),
        "Sandbox": color_theory.build,

    })


ft.run(main)