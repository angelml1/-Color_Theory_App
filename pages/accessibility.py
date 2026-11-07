# accessibility page
# heads up: home_nav deleted this file, so this got pulled back from main as is, nothing inside changed
import flet as ft

from color_math.conditions import VisionState, build_pipeline
from color_math.contrast import contrast_ratio, wcag_results
from color_math.vision_effects import apply_to_hex
from components.contrast_picker import ContrastPicker
from components.vision_controls import VisionControls
from components.vision_preview import VisionPreview
from education.contrast_info import CONTRAST_INFO
from education.vision_info import CONDITION_INFO, DISCLAIMER, OVERVIEW

GOOD, BAD = "#2e7d32", "#c62828"
ROWS = [
    ("aa_normal", "Normal text, AA (4.5:1)"),
    ("aaa_normal", "Normal text, AAA (7:1)"),
    ("aa_large", "Large text, AA (3:1)"),
    ("aaa_large", "Large text, AAA (4.5:1)"),
    ("aa_ui", "UI components and graphics, AA (3:1)"),
]


def _verdict(ok: bool) -> ft.Text:
    # Words as well as color, so the result isn't conveyed by color alone.
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


def build(palette) -> ft.Control:
    s = {"tab": "contrast", "vision": VisionState()}
    preview = VisionPreview()

    # --- controls that render() updates ------------------------------------
    ratio_text = ft.Text(size=22, weight=ft.FontWeight.BOLD)
    results = ft.Column(spacing=4)
    pair_text = ft.Text(size=16)
    warning = ft.Text(color=BAD, weight=ft.FontWeight.BOLD)
    blur_note = ft.Text("Blur changes how edges and small text look in the preview, "
                        "but it isn't part of the contrast numbers.", italic=True, size=12)
    condition_info = ft.Column(spacing=8)

    # --- rendering ---------------------------------------------------------
    def render():
        fg, bg = fg_slot.value, bg_slot.value
        ratio = contrast_ratio(fg, bg)
        ok = wcag_results(ratio)

        contrast_tab.visible = s["tab"] == "contrast"
        vision_tab.visible = s["tab"] == "vision"

        ratio_text.value = f"Contrast ratio: {ratio:.2f}:1"
        results.controls = [ft.Row([ft.Text(label, width=290), _verdict(ok[key])])
                            for key, label in ROWS]

        if s["tab"] == "vision":
            vision_state = s["vision"]
            effect = build_pipeline(vision_state)
            active = vision_state.cvd is not None or bool(vision_state.effects)

            sim_ratio = contrast_ratio(apply_to_hex(fg, effect), apply_to_hex(bg, effect))
            sim_ok = wcag_results(sim_ratio)
            if active:
                pair_text.value = (f"Your pair from the Contrast tab: {ratio:.2f}:1 with "
                                   f"typical vision, {sim_ratio:.2f}:1 under these conditions.")
            else:
                pair_text.value = (f"Your pair from the Contrast tab: {ratio:.2f}:1. "
                                   "Select a condition above to see how it changes.")
            warning.value = ("This pair passes AA for normal text with typical vision, "
                             "but fails under the selected conditions.")
            warning.visible = active and ok["aa_normal"] and not sim_ok["aa_normal"]
            blur_note.visible = "low_acuity" in vision_state.effects

            keys = ([vision_state.cvd[0]] if vision_state.cvd else []) \
                + list(vision_state.effects) or ["normal"]
            condition_info.controls = [
                ft.Column([ft.Text(CONDITION_INFO[k]["title"], weight=ft.FontWeight.BOLD),
                           ft.Text(CONDITION_INFO[k]["text"])], spacing=2)
                for k in keys
            ]
            preview.show(palette.colors, fg, bg, effect)

        try:            
            root.update()
        except Exception:
            pass

    # --- event handlers ----------------------------------------------------
    def on_tab(e):
        s["tab"] = next(iter(e.control.selected))
        render()

    def on_vision_change(new_state: VisionState):
        s["vision"] = new_state
        render()

    palette.subscribe(render)

    # --- widgets -----------------------------------------------------------
    fg_slot = ContrastPicker("Foreground", palette, "#222222", render)
    bg_slot = ContrastPicker("Background", palette, "#ffffff", render)
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
                  ratio_text, results),
            _card("Why contrast matters",
                  _info_block([CONTRAST_INFO["ratio"], CONTRAST_INFO["levels"],
                               CONTRAST_INFO["why"]])),
        ],
        spacing=16,
    )

    vision_tab = ft.Column(
        [
            ft.Row([vision.reset_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row(
                [_card("Color Blindness", vision.cvd_control, width=400),
                 _card("Vision Perception", vision.effects_control, width=400), 
                 _card("Preview", preview.control, pair_text, warning, blur_note,
					ft.Text("What you're seeing", weight=ft.FontWeight.BOLD), condition_info, width=600),],
                wrap=True, spacing=16, alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            
            _card("About these conditions", _info_block(list(OVERVIEW.values())),
                  ft.Text(DISCLAIMER, italic=True, size=12)),
        ],
        spacing=16, visible=False,
    )

    root = ft.Column(
        [ft.Row([tabs], alignment=ft.MainAxisAlignment.CENTER), contrast_tab, vision_tab],
        spacing=16, scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    render()
    return root