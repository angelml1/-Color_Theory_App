"""Upload / extraction page (Flet).



Needs components/photoupload.py and components/colorextractor.py.
"""
import base64
import io
import flet as ft

from components.colorextractor import extract_palette, sample_patch
from components.photoupload import load_image, to_array

MAX_IMG_W, MAX_IMG_H = 520, 320   # largest size the image is shown at
N_EXTRACTED = 12                  # how many auto-extracted colours to offer
STEP = 32                         # colour detail for auto-extract 

DARK = "#1c1c1c"
MUTED = "#777777"
LINE = "#e3e3e3"
CARD_BG = "#fafafa"


def build(page, palette) -> ft.Control:
    upload = UploadPage(page, on_create_palette=palette.set)
    return upload.view


def text_on(rgb):
    """Black or white text, whichever is readable on this colour."""
    r, g, b = rgb
    return "#000000" if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else "#ffffff"


def card(content, width=None, expand=None):
    return ft.Container(
        content=content,
        padding=16,
        bgcolor=CARD_BG,
        border=ft.Border.all(1, LINE),
        border_radius=8,
        width=width,
        expand=expand,
    )


class UploadPage:
    def __init__(self, page, on_create_palette=None):
        self.page = page
        self.on_create_palette = on_create_palette

        self.mode = "click"
        self.arr = None
        self.img_b64 = None
        self.disp_w = 0
        self.disp_h = 0
        self.extracted = []
        self.picked = []
        self.current = None

        self.picker = ft.FilePicker()
        page.services.append(self.picker)

        self.view = ft.Column(spacing=12, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        self.refresh(update=False)

    # ------------------------------------------------------------ actions
    def notify(self, message):
        self.page.show_dialog(ft.SnackBar(ft.Text(message)))

    async def pick_image(self, e=None):
        files = await self.picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.IMAGE,
        )
        if not files:
            return
        f = files[0]
        try:
            data = getattr(f, "path", None) or await f.read()
            full = load_image(data)
            palette = extract_palette(data, n_colors=N_EXTRACTED, step=STEP)
        except ValueError as err:
            self.notify(str(err))
            return
        except Exception:
            self.notify("Couldn't read that file.")
            return

        shown = full.copy()
        shown.thumbnail((MAX_IMG_W, MAX_IMG_H))
        buf = io.BytesIO()
        shown.save(buf, format="PNG")

        self.img_b64 = base64.b64encode(buf.getvalue()).decode()
        self.disp_w, self.disp_h = shown.size
        self.arr = to_array(full)
        self.extracted = palette
        self.picked = []
        self.current = None
        self.refresh()

    def take_photo(self, e=None):
        self.notify("Taking a photo isn't set up yet.")

    def on_image_tap(self, e):
        if self.mode != "click" or self.arr is None:
            return
        h, w, _ = self.arr.shape
        local_x = e.local_position.x
        local_y = e.local_position.y
        x = local_x * w / self.disp_w
        y = local_y * h / self.disp_h
        sample = sample_patch(self.arr, x, y)
        sample.update(fx=local_x / self.disp_w, fy=local_y / self.disp_h, source="click")
        self.picked.append(sample)
        self.current = len(self.picked) - 1
        self.refresh()

    def toggle_extracted(self, c):
        for i, p in enumerate(self.picked):
            if p["source"] == "auto" and p["hex"] == c["hex"]:
                self.picked.pop(i)
                self.current = len(self.picked) - 1 if self.picked else None
                self.refresh()
                return
        self.picked.append({"hex": c["hex"], "rgb": c["rgb"], "source": "auto", "fx": None, "fy": None})
        self.current = len(self.picked) - 1
        self.refresh()

    def set_mode(self, mode):
        self.mode = mode
        self.refresh()

    def select(self, i):
        self.current = i
        self.refresh()

    def undo(self, e=None):
        if self.picked:
            self.picked.pop()
            self.current = len(self.picked) - 1 if self.picked else None
            self.refresh()

    def create_palette(self, e=None):
        if not self.picked:
            return
        if self.on_create_palette:
            self.on_create_palette([color["hex"] for color in self.picked])
        else:
            self.notify("Palette: " + ", ".join(p["hex"] for p in self.picked))

    # ------------------------------------------------------------- layout
    def refresh(self, update=True):
        top = self.click_top() if self.mode == "click" else self.extract_top()
        self.view.controls = [self.mode_toggle(), top, self.colours_card(), self.action_row()]
        if update:
            self.page.update()

    def mode_toggle(self):
        def btn(label, mode):
            active = self.mode == mode
            return ft.Button(
                content=label,
                on_click=lambda e, m=mode: self.set_mode(m),
                style=ft.ButtonStyle(
                    bgcolor=DARK if active else "#ffffff",
                    color="#ffffff" if active else DARK,
                ),
            )

        return ft.Row([btn("Click to sample", "click"), btn("Auto-extract", "extract")], spacing=0)

    def placeholder(self, text):
        return ft.Container(
            width=MAX_IMG_W,
            height=240,
            bgcolor="#e9e9e9",
            border_radius=6,
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                [
                    ft.Text(text, color=MUTED, size=13),
                    ft.Button(
                        content="Upload image",
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=self.pick_image,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def pin(self, i, s):
        size = 26
        active = i == self.current
        return ft.Container(
            left=s["fx"] * self.disp_w - size / 2,
            top=s["fy"] * self.disp_h - size / 2,
            width=size,
            height=size,
            border_radius=size / 2,
            bgcolor=DARK if active else "#ffffff",
            border=ft.Border.all(2, "#ffffff" if active else DARK),
            alignment=ft.Alignment(0, 0),
            content=ft.Text(
                str(i + 1), size=12, weight=ft.FontWeight.BOLD,
                color="#ffffff" if active else DARK,
            ),
        )

    def image_stack(self, with_pins):
        layers = [ft.Image(src=self.img_b64, width=self.disp_w, height=self.disp_h)]
        if with_pins:
            for i, s in enumerate(self.picked):
                if s.get("fx") is not None:
                    layers.append(self.pin(i, s))
        return ft.Stack(controls=layers, width=self.disp_w, height=self.disp_h)

    # ----- mode 1: click to sample
    def click_top(self):
        if self.img_b64:
            area = ft.Container(
                alignment=ft.Alignment(0, 0),
                content=ft.GestureDetector(
                    content=self.image_stack(with_pins=True),
                    on_tap_down=self.on_image_tap,
                    mouse_cursor=ft.MouseCursor.PRECISE,
                ),
            )
        else:
            area = self.placeholder("Upload an image to start sampling")

        left = card(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Sample from image", size=16, weight=ft.FontWeight.BOLD),
                            ft.Button(content="Replace image", on_click=self.pick_image),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text("Click the image to sample colours.", size=12, color=MUTED),
                    area,
                ],
                spacing=8,
            ),
            expand=True,
        )
        return ft.Row([left, self.current_panel()], vertical_alignment=ft.CrossAxisAlignment.START)

    def current_panel(self):
        s = self.picked[self.current] if self.current is not None else None

        def row(label, value):
            return ft.Row(
                [ft.Text(label, size=12, color=MUTED), ft.Text(value, size=12)],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )

        return card(
            ft.Column(
                [
                    ft.Text("Current colour", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Colour {self.current + 1}" if s else "Nothing selected yet", size=13),
                    ft.Container(height=70, bgcolor=s["hex"] if s else "#d0d0d0", border_radius=6),
                    row("HEX", s["hex"] if s else "—"),
                    row("RGB", ", ".join(str(v) for v in s["rgb"]) if s else "—"),
                ],
                spacing=8,
            ),
            width=240,
        )

    # ----- mode 2: auto-extract
    def extract_top(self):
        if self.img_b64:
            area = ft.Container(alignment=ft.Alignment(0, 0), content=self.image_stack(with_pins=False))
        else:
            area = self.placeholder("Uploaded or captured image will appear here")

        left = card(
            ft.Column(
                [
                    ft.Text("Image preview", size=16, weight=ft.FontWeight.BOLD),
                    area,
                    ft.Row(
                        [
                            ft.Button(
                                content="Upload image",
                                icon=ft.Icons.UPLOAD_FILE,
                                on_click=self.pick_image,
                            ),
                            ft.Button(
                                content="Take photo",
                                icon=ft.Icons.CAMERA_ALT_OUTLINED,
                                on_click=self.take_photo,
                            ),
                        ],
                        spacing=8,
                    ),
                ],
                spacing=10,
            ),
            expand=True,
        )

        chosen = {p["hex"] for p in self.picked if p["source"] == "auto"}
        chips = []
        for c in self.extracted:
            on = c["hex"] in chosen
            fg = text_on(c["rgb"])
            chips.append(
                ft.Container(
                    width=82,
                    height=30,
                    border_radius=15,
                    bgcolor=c["hex"],
                    border=ft.Border.all(2, DARK if on else LINE),
                    alignment=ft.Alignment(0, 0),
                    tooltip=f"{c['hex']}  ({c['percent']}% of image)",
                    on_click=lambda e, c=c: self.toggle_extracted(c),
                    content=ft.Row(
                        ([ft.Icon(ft.Icons.CHECK, size=13, color=fg)] if on else [])
                        + [ft.Text(c["hex"], size=11, color=fg)],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=3,
                    ),
                )
            )
        if not self.img_b64:
            chips = [
                ft.Container(width=82, height=30, border_radius=15, bgcolor="#eeeeee")
                for _ in range(N_EXTRACTED)
            ]

        right = card(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Extracted colors", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text("Select colours", size=12, color=MUTED),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(chips, wrap=True, spacing=8, run_spacing=8),
                ],
                spacing=12,
            ),
            width=300,
        )
        return ft.Row([left, right], vertical_alignment=ft.CrossAxisAlignment.START)

    # ----- shared bottom section
    def colours_card(self):
        chips = []
        for i, p in enumerate(self.picked):
            active = i == self.current
            chips.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                width=14, height=14, border_radius=3, bgcolor=p["hex"],
                                border=ft.Border.all(1, "#bbbbbb"),
                            ),
                            ft.Text(f"Colour {i + 1}", size=12),
                        ],
                        spacing=6,
                        tight=True,
                    ),
                    padding=ft.Padding(left=10, top=6, right=10, bottom=6),
                    bgcolor="#ffffff",
                    border_radius=6,
                    border=ft.Border.all(2 if active else 1, DARK if active else LINE),
                    on_click=lambda e, i=i: self.select(i),
                )
            )
        if not chips:
            hint = (
                "Click the image to sample colours."
                if self.mode == "click"
                else "Select colours above, then create your palette."
            )
            chips = [ft.Text(hint, size=12, color=MUTED)]

        n = len(self.picked)
        return card(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Your colours", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{n} {'colour' if n == 1 else 'colours'} selected",
                                    size=12, weight=ft.FontWeight.BOLD),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(chips, wrap=True, spacing=8, run_spacing=8),
                ],
                spacing=10,
            )
        )

    def action_row(self):
        empty = not self.picked
        return ft.Row(
            [
                ft.Button(
                    content="Undo last sample",
                    on_click=self.undo,
                    disabled=empty,
                    style=ft.ButtonStyle(
                        bgcolor="#ffffff",
                        color=DARK,
                    ),
                ),
                ft.Button(
                    content="Create palette",
                    on_click=self.create_palette,
                    disabled=empty,
                    style=ft.ButtonStyle(
                        bgcolor="#9a9a9a" if empty else DARK,
                        color="#ffffff",
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )


def main(page: ft.Page):
    page.title = "Colour extractor"
    page.padding = 0
    page.bgcolor = "#ffffff"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO

    upload = UploadPage(page)

    tabs = ["Upload", "Colors", "Palette"]
    pages = {"Upload": upload.view}

    nav = ft.Row(alignment=ft.MainAxisAlignment.SPACE_AROUND)
    body = ft.Container(padding=16)

    def nav_item(name, active):
        return ft.Container(
            content=ft.Text(name, weight=ft.FontWeight.BOLD if active else ft.FontWeight.NORMAL),
            padding=ft.Padding(left=14, top=6, right=14, bottom=6),
            bgcolor="#ffffff" if active else None,
            border_radius=6,
            on_click=lambda e, n=name: show(n),
        )

    def show(name):
        nav.controls = [nav_item(t, t == name) for t in tabs]
        body.content = pages.get(name) or ft.Text(f"{name} page isn't built yet.", color=MUTED)
        page.update()

    page.add(ft.Container(content=nav, bgcolor="#ebebeb", padding=8), body)
    show("Upload")