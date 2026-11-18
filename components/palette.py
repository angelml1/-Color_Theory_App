# persistent palette widget
import flet as ft

from components.color_info import show_color_info
from components.dialogs import PALETTE_SAVED, toast
from components.swatch import swatch
from palette_library import add_palette, load_palettes, next_palette_name

PANEL_WIDTH = 150
SWATCH_SIZE = 40


def palette_sidebar(palette) -> ft.Control:
    pick = palette.pick

    swatch_col = ft.Column(
        spacing=8, scroll=ft.ScrollMode.AUTO, expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    empty = ft.Text("No colors yet", italic=True, size=12)
    hint = ft.Text("Click a color for its codes. Hover it and click 'X' to remove it.",
                   size=11, italic=True, text_align=ft.TextAlign.CENTER)
    banner_text = ft.Text(size=12)
    banner = ft.Container(
        content=ft.Column(
            [banner_text, ft.TextButton("Cancel", on_click=lambda e: pick.cancel())],
            spacing=2),
        padding=8, border_radius=8, bgcolor=ft.Colors.PRIMARY_CONTAINER, visible=False,
    )
    
    undo = ft.TextButton("Undo", icon=ft.Icons.UNDO,
                                 tooltip="Undo last action",
                                 on_click=lambda e: palette.undo())
    header = ft.Row([ft.Text("Palette", weight=ft.FontWeight.BOLD), undo],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    save_btn = ft.TextButton("Save palette", icon=ft.Icons.SAVE,
                             tooltip="Save this palette to your library")

    body = ft.Column([header, banner, swatch_col, hint, save_btn],
                     width=PANEL_WIDTH, spacing=8,
                     horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    panel = ft.Container(body, padding=10, border_radius=12,
                         border=ft.Border.all(1, "#888888"))
    toggle_btn = ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT)
    # STRETCH gives the panel the full height of the window area.
    root = ft.Row([ft.Column([toggle_btn]), panel],
                  vertical_alignment=ft.CrossAxisAlignment.STRETCH)

    # --- saving ---------------------------------------------------------------------
    def save_current(e):
        if not palette.colors:
            toast(root.page, "Your palette is empty")
            return
        try:
            add_palette(next_palette_name(load_palettes()), list(palette.colors))
        except OSError:      
            toast(root.page, "Couldn't save the palette")
            return
        toast(root.page, PALETTE_SAVED)

    save_btn.on_click = save_current

    # --- swatches ---------------------------------------------------------------------
    def make_swatch(c: str, picking: bool):
        if picking:  
            return swatch(c, size=SWATCH_SIZE, selected=True,
                          on_click=lambda e, c=c: pick.choose(c))
        return swatch(
            c, size=SWATCH_SIZE,
            on_click=lambda e, c=c: show_color_info(
                root.page, c, on_remove=lambda: palette.remove(c)),
            on_remove=lambda c=c: palette.remove(c),
        )

    def refresh():
        picking = pick.active
        banner.visible = picking
        if picking:
            banner_text.value = (f"Eyedropper: click a color to use it as {pick.label}."
                                 if palette.colors else
                                 "Your palette is empty. Add colors on the Color Wheel page.")
            panel.visible = True   
            toggle_btn.icon = ft.Icons.CHEVRON_RIGHT

        undo.disabled = not palette.history
        save_btn.disabled = not palette.colors
        swatch_col.controls = [make_swatch(c, picking) for c in palette.colors] or [empty]
        hint.visible = bool(palette.colors) and not picking
        try:
            root.update()
        except Exception:     
            pass

    def toggle(e):
        panel.visible = not panel.visible
        toggle_btn.icon = (ft.Icons.CHEVRON_RIGHT if panel.visible
                           else ft.Icons.CHEVRON_LEFT)
        root.update()

    toggle_btn.on_click = toggle
    palette.subscribe(refresh)
    pick.subscribe(refresh)
    refresh()
    return root