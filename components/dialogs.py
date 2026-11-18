# definitions of dialog boxes and their behaviors
import asyncio
import threading

import flet as ft

from palette_state import MAX_COLORS

SWATCH_ADDED = "Swatch added"
SWATCH_REMOVED = "Swatch removed"
PALETTE_UPDATED = "Palette updated"
PALETTE_SAVED = "Palette saved"
PALETTE_FULL = f"Your palette is full ({MAX_COLORS} colors max)"

TOAST_SECONDS = 1.2
TOAST_WIDTH = 260  

_state = {"toast": None, "top": None}


def _open(page, dialog):
    if hasattr(page, "show_dialog"):           
        page.show_dialog(dialog)
    else:
        page.open(dialog)


def _close(page, dialog):
    if hasattr(page, "pop_dialog"):
        page.pop_dialog()
    else:
        page.close(dialog)


def _forget(dialog):
    if _state["toast"] is dialog:
        _state["toast"] = None
    if _state["top"] is dialog:
        _state["top"] = None


def _dismiss_toast(page):
    message = _state["toast"]
    if message is not None and _state["top"] is message:
        _forget(message)
        _close(page, message)
    else:
        _state["toast"] = None


def _run_later(page, seconds: float, fn):
    """Run fn() after a delay, on Flet's own event loop when it is available."""
    if hasattr(page, "run_task"):
        async def waiter():
            await asyncio.sleep(seconds)
            fn()
        page.run_task(waiter)
    else:
        timer = threading.Timer(seconds, fn)
        timer.daemon = True
        timer.start()


def show_dialog(page, dialog):
    _dismiss_toast(page)           
    _state["top"] = dialog
    _open(page, dialog)


def close_dialog(page, dialog):
    if _state["top"] is dialog:
        _state["top"] = None
    _close(page, dialog)


def toast(page, message: str, seconds: float = TOAST_SECONDS):
    """A short message in the center of the window. Closes itself."""
    _dismiss_toast(page)
    dialog = ft.AlertDialog(
        content=ft.Container(
            content=ft.Text(message, size=16, text_align=ft.TextAlign.CENTER),
            width=TOAST_WIDTH,
        ),
        title_padding=0,                       
        actions_padding=0,                      
        content_padding=20,
        on_dismiss=lambda e: _forget(dialog), 
    )
    _state["toast"] = dialog
    _state["top"] = dialog
    _open(page, dialog)


    def close_me():
        if _state["toast"] is dialog and _state["top"] is dialog:
            _forget(dialog)
            try:
                _close(page, dialog)
                page.update()
            except Exception as ex:   
                print("toast close failed:", repr(ex))

    _run_later(page, seconds, close_me)