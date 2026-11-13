# page layout (header, etc)
import flet as ft

from components.palette import palette_sidebar

PAGE_HINTS = {
    "Home": "Saved palettes, your current palette and the theme toggle",
    "Color Wheel": "Pick a color and explore harmonies",
    "Upload": "Extract colors from an image",
    "Sandbox": "Experiment with color theory: surround, glow, shadow and relight",
    "Accessibility": "Check contrast and simulate color vision conditions",
}


def build_shell(page: ft.Page, palette, pages: dict):
    """pages: {"Home": home.build, ...}, each build(palette) -> ft.Control."""
    cache = {}
    content = ft.Container(expand=True, padding=16)
    nav_buttons = {}

    def show(name: str):
        palette.pick.cancel()
        if name not in cache:
            cache[name] = pages[name](palette)
        content.content = cache[name]
        for n, b in nav_buttons.items():
            b.style = ft.ButtonStyle(
                color=ft.Colors.ON_INVERSE_SURFACE,
                bgcolor=(ft.Colors.with_opacity(0.2, ft.Colors.ON_INVERSE_SURFACE)
                         if n == name else None))
        page.update()

    for name in pages:
        nav_buttons[name] = ft.TextButton(
            name, tooltip=PAGE_HINTS.get(name), on_click=lambda e, n=name: show(n))

    nav = ft.Container(
        ft.Row(list(nav_buttons.values()), spacing=4),
        padding=8,
        bgcolor=ft.Colors.INVERSE_SURFACE,
    )
    body = ft.Container(
        content=ft.Row(
            [content, palette_sidebar(palette)],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        expand=True,
    )

    page.add(
        ft.Container(
            content=ft.Column([nav, ft.Divider(height=1), body], expand=True),
            expand=True,
        )
    )
    show(next(iter(pages)))