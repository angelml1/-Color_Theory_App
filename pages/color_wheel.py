# color wheel palette generator page
import flet as ft

from color_math.convert import parse_color
from color_math.harmony import KINDS, harmony
from components.color_wheel import ColorWheel
from components.swatch import swatch
from education.harmony_info import HARMONY_INFO
from palette_state import MAX_COLORS

MIN_COUNT = 2
NONE = "none"
LABELS = {
    NONE: "None",
    "complementary": "Complementary",
    "split-complementary": "Split-Complementary",
    "triadic": "Triadic",
    "tetradic": "Tetradic",
    "analogous": "Analogous",
    "monochromatic": "Monochromatic",
}


def build(palette) -> ft.Control:
    s = {"mode": "manual", "base": "#3a7bd5", "kind": None,
         "count": 5, "format": "HEX"}

    # --- controls that render() updates ------------------------------------
    color_input = ft.TextField(
        width=210, dense=True, text_align=ft.TextAlign.CENTER,
        hint_text="#RRGGBB or R, G, B",
    )
    suggestion_row = ft.Row(wrap=True, spacing=10, alignment=ft.MainAxisAlignment.CENTER)
    preview_row = ft.Row(wrap=True, spacing=10, alignment=ft.MainAxisAlignment.CENTER)
    info_title = ft.Text(weight=ft.FontWeight.BOLD, size=16)
    info_text = ft.Text()

	# Number of colors for monochromatic option
    count_field = ft.TextField(
        value=str(s["count"]), width=70, text_align=ft.TextAlign.CENTER,
        keyboard_type=ft.KeyboardType.NUMBER, dense=True,
    )
    count_row = ft.Row( 
        [ft.Text("Colors"),
         ft.IconButton(ft.Icons.REMOVE, on_click=lambda e: set_count(s["count"] - 1)),
         count_field,
         ft.IconButton(ft.Icons.ADD, on_click=lambda e: set_count(s["count"] + 1))],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    
    manual_box = ft.Column(
        [ft.Text("Click a color to add it to (or remove it from) your palette"),
         suggestion_row],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    generate_box = ft.Column(
        [ft.Text("Preview"), preview_row,
         ft.FilledButton("Generate", on_click=lambda e: generate())],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # --- logic -------------------------------------------------------------
    def colors() -> list[str]:
        return harmony(s["base"], s["kind"], s["count"])

	# add/remove colors from palette in manual mode
    def toggle(hex_color: str):
        if hex_color in palette.colors:
            palette.remove(hex_color)
        else:
            palette.add(hex_color)

    def generate(): 
        palette.set(colors())

    def set_count(value):
        try:
            n = int(value)
        except (TypeError, ValueError):
            n = s["count"]
        s["count"] = max(MIN_COUNT, min(MAX_COLORS, n))
        count_field.value = str(s["count"])
        render()

    count_field.on_submit = lambda e: set_count(e.control.value)
    count_field.on_blur = lambda e: set_count(e.control.value)

    # --- rendering ---------------------------------------------------------
    def render():
        manual = s["mode"] == "manual"
        cols = colors()

        manual_box.visible = manual
        generate_box.visible = not manual
        count_row.visible = s["kind"] == "monochromatic"

        suggestion_row.controls = [
            swatch(c, selected=c in palette.colors, on_click=lambda e, c=c: toggle(c))
            for c in cols
        ]
        preview_row.controls = [swatch(c) for c in cols]

        base = s["base"]
        color_input.error_text = None
        if s["format"] == "RGB":
            r, g, b = (int(base[i:i + 2], 16) for i in (1, 3, 5))
            color_input.value = f"rgb({r}, {g}, {b})"
        else:
            color_input.value = base

        info = HARMONY_INFO.get(s["kind"] or NONE, {})
        info_title.value = info.get("title", "")
        info_text.value = info.get("text", "")

        try:     
            root.update()
        except Exception:
            pass

    # --- event handlers ----------------------------------------------------
    def on_pick(hex_color: str):
        s["base"] = hex_color
        render()

    def on_mode(e):
        s["mode"] = next(iter(e.control.selected))
        render()

    def on_format(e):
        s["format"] = next(iter(e.control.selected))
        render()

    def on_kind(e):
        value = e.control.value
        s["kind"] = None if value == NONE else value
        render()

    def apply_input(e):
        parsed = parse_color(color_input.value)
        if parsed is None:
            color_input.error_text = "Use #RRGGBB or R, G, B (0 to 255)"
            color_input.update()
            return
        wheel.set(parsed) 
        on_pick(parsed)

    color_input.on_submit = apply_input
    color_input.on_blur = apply_input

    palette.subscribe(render) 

    # --- widgets -----------------------------------------------------------
    wheel = ColorWheel(on_pick, initial=s["base"])

    mode = ft.SegmentedButton(
        selected=["manual"], on_change=on_mode,
        segments=[ft.Segment(value="manual", label=ft.Text("Manual")),
                  ft.Segment(value="generate", label=ft.Text("Generate"))],
    )
    fmt = ft.SegmentedButton(
        selected=["HEX"], on_change=on_format,
        segments=[ft.Segment(value="RGB", label=ft.Text("RGB")),
                  ft.Segment(value="HEX", label=ft.Text("HEX"))],
    )
    kind_group = ft.RadioGroup(
        value=NONE, on_change=on_kind,
        content=ft.Row(
            [ft.Radio(value=k, label=LABELS[k]) for k in [NONE] + KINDS],
            wrap=False, scroll=ft.ScrollMode.AUTO,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )

    root = ft.Column(
        [ft.Row([mode], alignment=ft.MainAxisAlignment.CENTER),
         wheel.control,
         ft.Row([fmt, color_input], alignment=ft.MainAxisAlignment.CENTER),
         count_row,
         manual_box,
         generate_box,
         ft.Divider(),
         kind_group,
         info_title, info_text],
        spacing=16, scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    render()
    return root