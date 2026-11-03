# main functionality
import flet as ft

from palette_state import Palette
from pages import home


def main(page: ft.Page):
    page.title = "Colour extractor"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE
    page.padding = 0
    palette = Palette()
    page.add(home.build(palette, page))


ft.run(main)