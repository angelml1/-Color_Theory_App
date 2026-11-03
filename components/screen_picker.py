# lets eyedropper tool select a color outside of the app in color contrast mode on the accessibility page
import time

import flet as ft

from color_math.imaging import grab_screen, image_to_b64, pixel_at


def _show(page, dialog):
    if hasattr(page, "show_dialog"):
        page.show_dialog(dialog)
    else:
        page.open(dialog)


def _close(page, dialog):
    if hasattr(page, "pop_dialog"):
        page.pop_dialog()
    else:
        page.close(dialog)


def _toast(page, message: str):
    _show(page, ft.SnackBar(ft.Text(message)))


def _xy(e):
    """Local click position."""
    pos = getattr(e, "local_position", None)
    if pos is not None:
        return pos.x, pos.y
    return e.local_x, e.local_y


def _capture(page):
    """Minimize the app (so it isn't covering what you want to sample), grab the
    screen, restore. If minimizing doesn't work, the screenshot just includes the app."""
    window = getattr(page, "window", None)
    try:
        if window is not None:
            window.minimized = True
            page.update()
            time.sleep(0.8)
        return grab_screen()
    finally:
        if window is not None:
            window.minimized = False
            page.update()


def pick_from_screen(page, on_pick):
    """Open a screenshot; the clicked pixel's '#rrggbb' goes to on_pick."""
    if getattr(page, "web", False):
        _toast(page, "Screen picking only works in the desktop app.")
        return
    try:
        shot = _capture(page)
    except Exception as ex:
        _toast(page, f"Couldn't capture the screen: {ex}")
        return

    width = int(min(1000, max(300, (getattr(page, "width", None) or 1000) - 160)))
    scale = shot.width / width 
    height = max(1, round(shot.height / scale))
    shown = shot.resize((width, height))

    chosen = {"hex": None}
    chip = ft.Container(width=36, height=36, border_radius=6,
                        border=ft.Border.all(1, "#888888"))
    readout = ft.Text("Click anywhere on the picture to sample a color")
    use_btn = ft.FilledButton("Use this color", disabled=True)

    def on_tap(e):
        x, y = _xy(e)
        hex_color = pixel_at(shot, x * scale, y * scale)
        chosen["hex"] = hex_color
        chip.bgcolor = hex_color
        readout.value = hex_color
        use_btn.disabled = False
        chip.update()
        readout.update()
        use_btn.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Pick a color from the screen"),
        content=ft.Column(
            [ft.GestureDetector(
                content=ft.Image(src=image_to_b64(shown), width=width, height=height),
                on_tap_down=on_tap),
             ft.Row([chip, readout])],
            tight=True, scroll=ft.ScrollMode.AUTO),
        actions=[use_btn, ft.TextButton("Cancel", on_click=lambda e: _close(page, dialog))],
    )

    def use(e):
        _close(page, dialog)
        if chosen["hex"]:
            on_pick(chosen["hex"])

    use_btn.on_click = use
    _show(page, dialog)