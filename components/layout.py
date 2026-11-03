# page layout (header, etc)
import flet as ft

from components.palette import palette_sidebar


def build_shell(page: ft.Page, palette, pages: dict):
    """pages: {"Home": home.build, ...}, each build(palette) -> ft.Control."""
    cache = {}                           
    content = ft.Container(expand=True, padding=16)
    nav_buttons = {}

    def show(name: str):
        if name not in cache:
            cache[name] = pages[name](palette)
        content.content = cache[name]
        for n, b in nav_buttons.items():
            b.style = ft.ButtonStyle(
                bgcolor=ft.Colors.SECONDARY_CONTAINER if n == name else None)
        page.update()

    for name in pages:
        nav_buttons[name] = ft.TextButton(name, on_click=lambda e, n=name: show(n))

    nav = ft.Container(ft.Row(list(nav_buttons.values()), spacing=4), padding=8)
    body = ft.Row([content, palette_sidebar(palette)],
                  expand=True, vertical_alignment=ft.CrossAxisAlignment.START)

    page.add(ft.Column([nav, ft.Divider(height=1), body], expand=True))
    show(next(iter(pages)))