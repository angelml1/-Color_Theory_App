# choosing colors to test on the vision tab
import flet as ft

from components.swatch import swatch


class PairPicker:
    """Vision tab: click palette swatches to choose the text and background
    colors. Uses the same two ColorSlots as the Contrast tab, so both tabs
    always agree. Call refresh() after any change; it doesn't update the page."""

    def __init__(self, palette, fg_slot, bg_slot):
        self.palette, self.fg, self.bg = palette, fg_slot, bg_slot

        self.current_text = ft.Text("Aa  Current pair", weight=ft.FontWeight.BOLD)
        self.current = ft.Container(self.current_text, padding=10, border_radius=8,
                                    border=ft.Border.all(1, "#888888"))
        self.fg_row = ft.Row(wrap=True, spacing=6)
        self.bg_row = ft.Row(wrap=True, spacing=6)
        self.empty = ft.Text("Your palette is empty. Add colors on the Color Wheel page.", italic=True, size=12)

        self.control = ft.Column(
            [ft.Row([self.current,
                     ft.TextButton("Swap", icon=ft.Icons.SWAP_HORIZ,
                                   tooltip="Swaps the foreground and background colors",
                                   on_click=self._swap)]),
             ft.Text("Foreground", size=12), self.fg_row,
             ft.Text("Background", size=12), self.bg_row,
             self.empty,],
            spacing=6,
        )
        self.refresh()

    def _row(self, slot) -> list:
        return [swatch(c, size=32, selected=(c == slot.value),
                       on_click=lambda e, c=c, slot=slot: slot.set(c))
                for c in self.palette.colors]

    def refresh(self):
        self.fg_row.controls = self._row(self.fg)
        self.bg_row.controls = self._row(self.bg)
        self.empty.visible = not self.palette.colors
        self.current.bgcolor = self.bg.value
        self.current_text.color = self.fg.value

    def _swap(self, e):
        a, b = self.fg.value, self.bg.value
        self.fg.set(b, notify=False)
        self.bg.set(a)    