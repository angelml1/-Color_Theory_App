# accessibility page
import threading

import flet as ft

from color_math.conditions import VisionState, build_pipeline
from color_math.contrast import contrast_ratio, wcag_results
from color_math.vision_effects import apply_to_hex
from components.color_slot import ColorSlot
from components.pair_picker import PairPicker
from components.vision_controls import VisionControls
from components.vision_preview import PREVIEW_WIDTH, VisionPreview
from education.contrast_info import CONTRAST_INFO
from education.vision_info import CONDITION_INFO, DISCLAIMER, OVERVIEW

GOOD, BAD = "#2e7d32", "#c62828"
SAMPLE = "The quick brown fox jumped over the lazy dog"
ROWS = [
    ("aa_normal", "AA Normal text(4.5:1)"),
    ("aa_large", "AA Large text (3:1)"),
    ("aa_ui", "AA UI components and graphics (3:1)"),
    ("aaa_normal", "AAA Normal text (7:1)"),
    ("aaa_large", "AAA Large text (4.5:1)"),
]


def _verdict(ok: bool) -> ft.Text:
    return ft.Text("✓ Pass" if ok else "✗ Fail", color=GOOD if ok else BAD,
                   weight=ft.FontWeight.BOLD, width=110)


def _card(title: str, *controls, width: int | None = None) -> ft.Container:
    return ft.Container(
        content=ft.Column([ft.Text(title, size=18, weight=ft.FontWeight.BOLD), *controls],
                          spacing=10),
        padding=16, border=ft.Border.all(1, "#888888"), border_radius=12, width=width,
    )


def _info_block(items) -> ft.Column:
    return ft.Column(
        [ft.Column([ft.Text(i["title"], weight=ft.FontWeight.BOLD), ft.Text(i["text"])],
                   spacing=2)
         for i in items],
        spacing=12,
    )


def _safe_update(control):
    try:
        control.update()
    except Exception:                       
        pass


def build(palette) -> ft.Control:
    s = {"tab": "contrast", "vision": VisionState()}
    lv = {"running": False, "dirty": False}
    lv_lock = threading.Lock()
    preview = VisionPreview()

    # --- controls that render() updates ------------------------------------
    ratio_text = ft.Text(size=22, weight=ft.FontWeight.BOLD)
    results = ft.Column(spacing=4)
    sample_large = ft.Text(SAMPLE, size=24, weight=ft.FontWeight.BOLD)
    sample_normal = ft.Text(SAMPLE, size=16)
    sample_box = ft.Container(
        content=ft.Column([sample_large, sample_normal], spacing=8),
        padding=16, border_radius=8, border=ft.Border.all(1, "#888888"),
    )
    pair_text = ft.Text(size=16)
    warning = ft.Text(color=BAD, weight=ft.FontWeight.BOLD)
    blur_note = ft.Text("Blur changes how edges and small text look in the preview, "
                        "but it isn't part of the contrast numbers.", italic=True, size=12)
    condition_info = ft.Column(spacing=8)

    # --- rendering ---------------------------------------------------------
    def fill_vision(rebuild_text: bool = True):
        """Sets the Vision tab's values. Doesn't update the page."""
        fg, bg = fg_slot.value, bg_slot.value
        ratio = contrast_ratio(fg, bg)
        ok = wcag_results(ratio)
        vision_state = s["vision"]
        effect = build_pipeline(vision_state)
        active = vision_state.cvd is not None or bool(vision_state.effects)

        sim_ratio = contrast_ratio(apply_to_hex(fg, effect), apply_to_hex(bg, effect))
        sim_ok = wcag_results(sim_ratio)
        if active:
            pair_text.value = (f"This pair: {ratio:.2f}:1 with typical vision, "
                               f"{sim_ratio:.2f}:1 under these conditions.")
        else:
            pair_text.value = (f"This pair: {ratio:.2f}:1. "
                               "Select a condition on the left to see how it changes.")
        warning.value = ("This pair passes AA for normal text with typical vision, "
                         "but fails under the selected conditions.")
        warning.visible = active and ok["aa_normal"] and not sim_ok["aa_normal"]
        blur_note.visible = "low_acuity" in vision_state.effects

        if rebuild_text:                  
            keys = ([vision_state.cvd[0]] if vision_state.cvd else []) \
                + list(vision_state.effects) or ["normal"]
            condition_info.controls = [
                ft.Column([ft.Text(CONDITION_INFO[k]["title"], weight=ft.FontWeight.BOLD),
                           ft.Text(CONDITION_INFO[k]["text"])], spacing=2)
                for k in keys
            ]
        preview.show(palette.colors, fg, bg, effect)

    def render():
        fg, bg = fg_slot.value, bg_slot.value
        ratio = contrast_ratio(fg, bg)
        ok = wcag_results(ratio)

        contrast_tab.visible = s["tab"] == "contrast"
        vision_tab.visible = s["tab"] == "vision"

        ratio_text.value = f"Contrast ratio: {ratio:.2f}:1"
        results.controls = [ft.Row([ft.Text(label, width=290), _verdict(ok[key])])
                            for key, label in ROWS]
        sample_box.bgcolor = bg
        sample_large.color = fg
        sample_normal.color = fg
        pair_picker.refresh()

        if s["tab"] == "vision":         
            fill_vision()

        _safe_update(root)

    # --- live slider updates -----------------------------------------------
    def update_live():
        fill_vision(rebuild_text=False)
        for control in (preview.image, pair_text, warning):
            _safe_update(control)        

    def request_live_update():
        """Latest value wins: ticks that arrive during a render collapse into one more render."""
        with lv_lock:
            if lv["running"]:
                lv["dirty"] = True
                return
            lv["running"] = True
        try:
            while True:
                update_live()
                with lv_lock:
                    if not lv["dirty"]:
                        lv["running"] = False
                        return
                    lv["dirty"] = False
        except BaseException:
            with lv_lock:
                lv["running"] = False
            raise

    # --- event handlers ----------------------------------------------------
    def on_tab(e):
        s["tab"] = next(iter(e.control.selected))
        render()

    def on_vision_change(new_state: VisionState, live: bool = False):
        s["vision"] = new_state
        if live and s["tab"] == "vision":
            request_live_update()
        else:
            render()

    palette.subscribe(render)          

    # --- widgets -----------------------------------------------------------
    fg_slot = ColorSlot("Foreground", palette, "#222222", render)
    bg_slot = ColorSlot("Background", palette, "#ffffff", render)
    pair_picker = PairPicker(palette, fg_slot, bg_slot)
    vision = VisionControls(on_vision_change)

    tabs = ft.SegmentedButton(
        selected=["contrast"], on_change=on_tab,
        segments=[ft.Segment(value="contrast", label=ft.Text("Contrast")),
                  ft.Segment(value="vision", label=ft.Text("Vision"))],
    )

    contrast_tab = ft.Column(
        [
            _card("Contrast Checker",
                  ft.Row([fg_slot.control, bg_slot.control], spacing=40, wrap=True),
                  sample_box,
                  ft.Text("Shown at large (24 px) and normal (16 px) sizes.",
                          size=11, italic=True),
                  ratio_text, results),
            _card("Why contrast matters",
                  _info_block([CONTRAST_INFO["ratio"], CONTRAST_INFO["levels"],
                               CONTRAST_INFO["why"]])),
        ],
        spacing=16, scroll=ft.ScrollMode.AUTO, expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Left: controls (scrolls on its own). Right: preview (always in view).
    vision_left = ft.Column(
        [
            ft.Row([vision.reset_button]),
            _card("Pair to test", pair_picker.control),
            ft.Row(
                [_card("Color Blindness", vision.cvd_control, width=360),
                 _card("Vision Perception", vision.effects_control, width=360)],
                wrap=True, spacing=16, vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            _card("About these conditions", _info_block(list(OVERVIEW.values())),
                  ft.Text(DISCLAIMER, italic=True, size=12)),
        ],
        spacing=16, scroll=ft.ScrollMode.AUTO, expand=True,
    )
    vision_right = ft.Column(
        [_card("Preview", preview.control, pair_text, warning, blur_note,
               ft.Text("What you're seeing", weight=ft.FontWeight.BOLD), condition_info,
               width=PREVIEW_WIDTH + 40)],
        scroll=ft.ScrollMode.AUTO, width=PREVIEW_WIDTH + 40,
    )
    vision_tab = ft.Row(
        [vision_left, vision_right],
        spacing=16, expand=True, visible=False,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    root = ft.Column(
        [ft.Row([tabs], alignment=ft.MainAxisAlignment.CENTER), contrast_tab, vision_tab],
        spacing=16, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    render()
    return root