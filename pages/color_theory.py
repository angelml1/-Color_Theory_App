# color theory sandbox page: try palette colors as surrounds, matches, glows, lights and shadows

# TABS:
#    surround
#     - Shows how colors are perceptually shifted based on the background they are on
#     - Provides swatches on 
#    match
#     - Similar to previous tab, but instead provides
#    glow
#     - Demonstrates the gradient shown from light emitting from a color on top of another color
#    light & shadow
#     - Shows how shadows can be influenced by colored light
#    relight
#     - Shows how colors in the palette change based on different light/shadows

import flet as ft

from color_math.imaging import to_png_b64
from color_math.lighting import (glow_falloff, glow_sample, relight_palette, render_glow,
                                 render_shadow, shadow_readout)
from color_math.surround import (describe_shift, effect_strength, matching_color,
                                 oklch, perceived_color, render_surround)
from components.contrast_picker import ContrastPicker
from components.color_theory_ui import (Slider as _Slider, VisionPanel, card as _card,
                                   result_swatch, segmented as _segmented, upd as _upd)
from components.swatch import swatch
from education.color_theory_info import THEORY_INFO

# surround/match previews
PREVIEW_W, PREVIEW_H = 640, 280
GLOW_H, SHADOW_H = 320, 360

DEFAULT_GRAY = "#808080"

# default colors for surround and match tab
DEFAULT_BACKGROUNDS = ["#d62828", "#2a9d8f", "#f4e285", "#202020"]
DEFAULT_MATCH_A, DEFAULT_MATCH_B = "#202020", "#e0e0e0"

# default colors for light and shadow tab
DEFAULT_SURFACE, DEFAULT_OBJECT, DEFAULT_EMITTER = "#3a7bd5", "#c9a27e", "#ff8800"
DEFAULT_KEY, DEFAULT_FILL = "#ffd27f", "#6fa8ff"


GLOW_MODE_LABELS = {"bloom": "Bloom", "cast": "Light on surface"}
SHAPE_LABELS = {"circle": "Circle", "bar": "Bar"}
BORDERS = {"none": "None", "gray": "Gray", "white": "White"}
BORDER_HEX = {"none": None, "gray": "#808080", "white": "#ffffff"}
MAX_BACKGROUNDS = 4

# func to return info from education/color_theory_info
def _info(key: str) -> ft.Column:
    item = THEORY_INFO[key]
    return ft.Column([ft.Text(item["title"], weight=ft.FontWeight.BOLD),
                      ft.Text(item["text"])], spacing=2)

# func to turn info from color_math/surround's describe_shift() into text
# e.g. "looks lighter/darker and drifts toward x"
def _words(shift: dict) -> str:
    parts = []
    if abs(shift["d_lightness"]) >= 0.004:
        parts.append("lighter" if shift["d_lightness"] > 0 else "darker")
    if shift["toward"]:
        parts.append(f"drifts toward {shift['toward']}")
    return "Looks " + " and ".join(parts) if parts else "Looks almost unchanged"

# main build function
def build(palette) -> ft.Control:
    # default options on segmented switches
    defaults = {"tab": "surround",     # default tab
         "bg_count": "2",       # surround - default # of backgrounds
         "sr_border": "none",   # surround - default border
         "m_border": "none",    # match - default border 
         "glow_mode": "bloom",  # glow - default glow mode
         "shape": "circle",     # glow - default shape
        }

    # func to populate colors in various tabs, else fallback to defaults
    def seed(i: int, default: str) -> str:
        return palette.colors[i] if i < len(palette.colors) else default

    # WIDGETS

    # surround tab widgets
    sr_center = ContrastPicker("Center color", palette, seed(0, DEFAULT_GRAY),
                               lambda: render())
    sr_bgs = [ContrastPicker(f"Background {i + 1}", palette,
                             seed(i + 1, DEFAULT_BACKGROUNDS[i]), lambda: render())
              for i in range(MAX_BACKGROUNDS)]
    sr_count = _segmented({str(n): str(n) for n in range(1, MAX_BACKGROUNDS + 1)},
                          defaults["bg_count"], lambda v: (defaults.update(bg_count=v), render()))
    sr_border = _segmented({k: v for k, v in BORDERS.items()}, defaults["sr_border"],
                           lambda v: (defaults.update(sr_border=v), render()))
    sr_size = _Slider("Center size (share of each panel)", 0.1, 0.8, 0.3,
                      lambda: render(), divisions=14)
    sr_vision = VisionPanel(lambda: render())
    sr_image = ft.Container()
    sr_readout = ft.Column(spacing=10)

    # match tab widgets
    m_target = ContrastPicker("Color to match", palette, seed(0, DEFAULT_GRAY),
                              lambda: render())
    m_a = ContrastPicker("Background A (where it looks the way you want)", palette,
                         seed(1, DEFAULT_MATCH_A), lambda: render())
    m_b = ContrastPicker("Background B (where you need to use it)", palette,
                         seed(2, DEFAULT_MATCH_B), lambda: render())
    m_border = _segmented({k: v for k, v in BORDERS.items()}, defaults["m_border"],
                          lambda v: (defaults.update(m_border=v), render()))
    m_size = _Slider("Center size (share of each panel)", 0.1, 0.8, 0.3,
                     lambda: render(), divisions=14)
    m_vision = VisionPanel(lambda: render())
    m_image = ft.Container()
    m_readout = ft.Column(spacing=10)

    # glow tab widgets
    g_surface = ContrastPicker("Surface", palette, seed(0, DEFAULT_SURFACE), lambda: render())
    g_emitter = ContrastPicker("Glowing color", palette, seed(1, DEFAULT_EMITTER),
                               lambda: render())
    g_intensity = _Slider("Glow strength", 0.0, 2.0, 1.0, lambda: render(), divisions=40)
    g_spread = _Slider("Glow spread", 20, 250, 90, lambda: render(), divisions=46,
                       fmt="{:.0f} px")
    g_ambient = _Slider("Ambient light (lower = darker room)", 0.0, 1.0, 0.35,
                        lambda: render(), divisions=20)
    g_mode = _segmented(GLOW_MODE_LABELS, defaults["glow_mode"],
                        lambda v: (defaults.update(glow_mode=v), render()))
    g_shape = _segmented(SHAPE_LABELS, defaults["shape"], lambda v: (defaults.update(shape=v), render()))
    g_image = ft.Container()
    g_samples = ft.Row(wrap=True, spacing=12)

    # shadow tab widgets
    s_surface = ContrastPicker("Surface", palette, seed(0, DEFAULT_OBJECT), lambda: render())
    s_object = ContrastPicker("Object", palette, seed(1, DEFAULT_SURFACE), lambda: render())
    s_key = ContrastPicker("Light color", palette, DEFAULT_KEY, lambda: render())
    s_fill = ContrastPicker("Shadow tint", palette, DEFAULT_FILL, lambda: render())
    s_darkness = _Slider("Shadow darkness", 0.0, 1.0, 0.75, lambda: render(), divisions=20,
                         hint="Only changes the shadowed areas. 1 = pitch black.")
    s_length = _Slider("Shadow length", 0.0, 1.0, 0.53, lambda: render(), divisions=20,
                       hint="How low the light is. It doesn't change brightness.")
    s_direction = _Slider("Shadow direction", 0, 360, 315, lambda: render(), divisions=72,
                          fmt="{:.0f}°", hint="Which way the shadow points (0° = right, "
                                              "90° = down).")
    s_intensity = _Slider("Light brightness", 0.0, 2.0, 1.0, lambda: render(), divisions=40,
                          hint="Only changes the lit (sunny) areas.")
    s_softness = _Slider("Shadow edge softness", 0.0, 1.0, 0.25, lambda: render(),
                         divisions=20, hint="Sharp edge to blurry edge. Colors don't change.")
    s_advanced = ft.ExpansionTile(title=ft.Text("Advanced"),
                                  controls=[ft.Column([s_intensity.control,
                                                       s_softness.control], spacing=8)])
    s_image = ft.Container()
    s_samples = ft.Column(spacing=8)

    # relight tab widgets
    r_light = ContrastPicker("Light", palette, DEFAULT_KEY, lambda: render())
    r_fill = ContrastPicker("Fill light (shadow color)", palette, DEFAULT_FILL,
                            lambda: render())
    r_intensity = _Slider("Light strength", 0.0, 2.0, 1.0, lambda: render(), divisions=40)
    r_ambient = _Slider("Fill light strength", 0.0, 1.0, 0.25, lambda: render(), divisions=20)
    r_table = ft.Column(spacing=8)

    # HELPERS

    def chip(label: str, hex_color: str, width: int | None = None) -> ft.Control:
        """A result color. Click to add it to the palette."""
        return result_swatch(palette, label, hex_color, width)

    def picture(holder: ft.Container, arr, width: int = PREVIEW_W):
        holder.content = ft.Image(src=to_png_b64(arr), width=width)

    # RENDERING

    def render_surround_tab():
        center = sr_center.value
        count = int(defaults["bg_count"])
        for i, picker in enumerate(sr_bgs):
            picker.control.visible = i < count
        backgrounds = [p.value for p in sr_bgs[:count]]

        border = BORDER_HEX[defaults["sr_border"]]
        strength = effect_strength(sr_size.value, border is not None)
        scene = render_surround(center, backgrounds, center_fraction=sr_size.value,
                                border=border, width=PREVIEW_W, height=PREVIEW_H)
        picture(sr_image, sr_vision.effect()(scene))

        L0, C0, _ = oklch(center)
        rows = [ft.Text("Click any color to add it to your palette. \"Looks like\" is a "
                        "modeled estimate, not a measurement.", size=12, italic=True)]
        for bg in backgrounds:
            seen = perceived_color(center, bg, strength)
            L1, C1, _ = oklch(seen)
            rows.append(ft.Row([
                chip("Background", bg, 84), chip("Actual", center, 84),
                chip("Looks like", seen, 84),
                ft.Column([ft.Text(_words(describe_shift(center, seen)),
                                   weight=ft.FontWeight.BOLD),
                           ft.Text(f"Lightness {L0:.2f} → {L1:.2f}, "
                                   f"chroma {C0:.2f} → {C1:.2f}", size=12)],
                          spacing=2, expand=True)],
                vertical_alignment=ft.CrossAxisAlignment.START, spacing=8))
        sr_readout.controls = rows

    def render_match_tab():
        target, bg_a, bg_b = m_target.value, m_a.value, m_b.value
        border = BORDER_HEX[defaults["m_border"]]
        strength = effect_strength(m_size.value, border is not None)
        match = matching_color(target, bg_a, bg_b, strength)
        adjusted = match["color"]

        scene = render_surround([target, target, adjusted], [bg_a, bg_b, bg_b],
                                center_fraction=m_size.value, border=border,
                                width=PREVIEW_W, height=PREVIEW_H)
        picture(m_image, m_vision.effect()(scene))

        shift = describe_shift(target, adjusted)
        if shift["toward"] or abs(shift["d_lightness"]) >= 0.004:
            how = _words(shift).replace("Looks", "To match, make it", 1).replace(
                "drifts toward", "shift it toward")
        else:
            how = "No adjustment needed"
        names = ft.Row([ft.Text(n, size=12, italic=True, expand=True,
                                text_align=ft.TextAlign.CENTER)
                        for n in ("Original color on A", "Original color on B",
                                  "Adjusted color on B")])
        m_readout.controls = [
            names,
            ft.Text("Panels 1 and 3 should look like the same color, while panel 2 is the "
                    "original color on B, where it looks different.", size=12, italic=True),
            ft.Row([chip("Original", target, 84), chip("Adjusted", adjusted, 84),
                    ft.Column([ft.Text(how, weight=ft.FontWeight.BOLD),
                               ft.Text("This match is as close as your screen can show."
                                       if match["exact"] else
                                       "This is the closest match your screen can show; the "
                                       "ideal color is outside what a display can make, so a "
                                       "small difference will remain.", size=12)],
                              spacing=2, expand=True)],
                   vertical_alignment=ft.CrossAxisAlignment.START, spacing=8),
            ft.Text("Click a color to add it to your palette. The match uses a simple model "
                    "of simultaneous contrast, not a measurement.", size=12, italic=True),
        ]

    def render_glow_tab():
        surface, emitter = g_surface.value, g_emitter.value
        kw = dict(intensity=g_intensity.value, ambient=g_ambient.value, mode=defaults["glow_mode"])
        spread = g_spread.value
        picture(g_image, render_glow(surface, emitter, spread=spread, shape=defaults["shape"],
                                     width=PREVIEW_W, height=GLOW_H, **kw))
        # sample the surface at a few distances from the emitter's edge
        steps = [("At the edge", 0.0), ("Near", 0.4), ("Mid", 1.0), ("Far away", 2.0)]
        g_samples.controls = [chip("Surface, no glow",
                                   glow_sample(surface, emitter, falloff=0.0, **kw))] + [
            chip(label, glow_sample(surface, emitter,
                                    falloff=float(glow_falloff(m * spread, spread)), **kw))
            for label, m in steps]

    def render_shadow_tab():
        surface, obj, key, fill = (s_surface.value, s_object.value, s_key.value, s_fill.value)
        ambient = 1.0 - s_darkness.value                    # shadow darkness 1 = no fill light
        elevation = 85 - 75 * s_length.value                # longer shadow = lower light
        azimuth = (s_direction.value + 180) % 360           # light comes from the far side
        picture(s_image, render_shadow(surface, obj, key, fill, intensity=s_intensity.value,
                                       ambient=ambient, azimuth=azimuth, elevation=elevation,
                                       softness=s_softness.value, width=PREVIEW_W,
                                       height=SHADOW_H))
        c = shadow_readout(surface, obj, key, fill, intensity=s_intensity.value,
                           ambient=ambient)
        s_samples.controls = [
            ft.Text("Click a color to add it to your palette", size=12, italic=True),
            ft.Row([ft.Text("Surface", weight=ft.FontWeight.BOLD, width=70),
                    chip("In light", c["surface_lit"], 84),
                    chip("In shadow", c["surface_shadow"], 84)], spacing=8),
            ft.Row([ft.Text("Object", weight=ft.FontWeight.BOLD, width=70),
                    chip("Lit side", c["object_lit"], 84),
                    chip("Shadow side", c["object_shadow"], 84)], spacing=8)]

    def render_relight_tab():
        if not palette.colors:
            r_table.controls = [ft.Text("Your palette is empty. Add colors on the Color "
                                        "Wheel page to relight them here.", italic=True)]
            return
        rows = relight_palette(palette.colors, r_light.value,
                               intensity=r_intensity.value, fill=r_fill.value,
                               ambient=r_ambient.value)
        header = ft.Row([ft.Text(t, weight=ft.FontWeight.BOLD, width=92)
                         for t in ("Original", "In light", "In shadow")], spacing=12)
        r_table.controls = [header] + [
            ft.Row([ft.Column([swatch(c, size=44, on_click=lambda e, c=c: palette.add(c)),
                               ft.Text(c, size=11)], spacing=2, width=92,
                              horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                    for c in row], spacing=12)
            for row in rows]

    renderers = {"surround": render_surround_tab, "match": render_match_tab,
                 "glow": render_glow_tab, "shadow": render_shadow_tab,
                 "relight": render_relight_tab}

    def render():
        for name, tab in tab_bodies.items():
            tab.visible = defaults["tab"] == name
        renderers[defaults["tab"]]()
        _upd(root)

    def on_tab(value):
        defaults["tab"] = value
        palette.pick.cancel()
        render()

    palette.subscribe(render)

    # LAYOUTS
    tabs = _segmented({"surround": "Surround", "match": "Match", "glow": "Glow",
                       "shadow": "Light & Shadow", "relight": "Relight Palette"},
                      defaults["tab"], on_tab)

    def two_col(left: ft.Control, right: ft.Control) -> ft.Row:
        return ft.Row([left, right], wrap=True, spacing=16, run_spacing=16,
                      alignment=ft.MainAxisAlignment.CENTER,
                      vertical_alignment=ft.CrossAxisAlignment.START)

    # 
    surround_tab = ft.Column([
        two_col(
            _card("Surround settings",
                  sr_center.control,
                  ft.Text("Number of backgrounds", size=12), sr_count,
                  ft.Row([sr_bgs[0].control, sr_bgs[1].control], spacing=30, wrap=True),
                  ft.Row([sr_bgs[2].control, sr_bgs[3].control], spacing=30, wrap=True),
                  ft.Text("Border between center and background", size=12), sr_border,
                  sr_size.control, sr_vision.control, width=420),
            _card("Preview", sr_image, sr_readout, width=PREVIEW_W + 34)),
        _card("About surround effects", _info("surround"), _info("model")),
    ], spacing=16)

    match_tab = ft.Column([
        two_col(
            _card("Match settings",
                  m_target.control, m_a.control, m_b.control,
                  ft.Text("Border between center and background", size=12), m_border,
                  m_size.control, m_vision.control, width=420),
            _card("Preview", m_image, m_readout, width=PREVIEW_W + 34)),
        _card("About matching colors", _info("match")),
    ], spacing=16, visible=False)

    glow_tab = ft.Column([
        two_col(
            _card("Glow settings",
                  ft.Row([g_surface.control, g_emitter.control], spacing=30, wrap=True),
                  ft.Text("Glow type", size=12), g_mode,
                  ft.Text("Light shape", size=12), g_shape,
                  g_intensity.control, g_spread.control, g_ambient.control, width=420),
            _card("Preview", g_image,
                  ft.Text("Click a color to add it to your palette", size=12, italic=True),
                  g_samples, width=PREVIEW_W + 34)),
        _card("About glow", _info("glow"), _info("model")),
    ], spacing=16, visible=False)

    def heading(text: str, note: str | None = None) -> ft.Control:
        items = [ft.Text(text, weight=ft.FontWeight.BOLD, size=14)]
        if note:
            items.append(ft.Text(note, size=11, italic=True))
        return ft.Column(items, spacing=0)

    shadow_tab = ft.Column([
        two_col(
            _card("Light & shadow settings",
                  heading("Colors", "The materials, before any light hits them"),
                  ft.Row([s_surface.control, s_object.control], spacing=30, wrap=True),
                  heading("Lit areas", "Where the light hits directly"),
                  s_key.control,
                  heading("Shadows", "Where the light is blocked"),
                  s_fill.control, s_darkness.control, s_length.control, s_direction.control,
                  s_advanced, width=420),
            _card("Preview (top-down view)", s_image, s_samples, width=PREVIEW_W + 34)),
        _card("About colored light and shadows", _info("shadow"), _info("model")),
    ], spacing=16, visible=False)

    relight_tab = ft.Column([
        two_col(
            _card("Light settings",
                  r_light.control, r_fill.control, r_intensity.control, r_ambient.control,
                  width=420),
            _card("Your palette, relit", r_table, width=PREVIEW_W + 34)),
        _card("About relighting", _info("relight"), _info("model")),
    ], spacing=16, visible=False)

    tab_bodies = {"surround": surround_tab, "match": match_tab, "glow": glow_tab,
                  "shadow": shadow_tab, "relight": relight_tab}

    root = ft.Column(
        [ft.Row([tabs], alignment=ft.MainAxisAlignment.CENTER), *tab_bodies.values()],
        spacing=16, scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    render()
    return root
