# math for the sandbox page: glow, colored light + shadow, relighting a palette

import numpy as np

from color_math.convert import hex_to_rgb, linear_to_srgb, rgb_to_hex, srgb_to_linear

GLOW_MODES = ("cast", "bloom")      # light that tints the surface / additive haze
GLOW_SHAPES = ("circle", "bar")

# HELPER FUNCS

# hex code to linear rgb
def hex_to_linear(hex_color: str) -> np.ndarray:
    return srgb_to_linear(np.array(hex_to_rgb(hex_color), dtype=float) / 255)

# reverse of previous func
def linear_to_hex(lin) -> str:
    rgb = linear_to_srgb(np.clip(np.asarray(lin, dtype=float), 0.0, 1.0)) * 255
    return rgb_to_hex(*rgb)

# calculate color being directly lit
def lit_color(albedo_hex: str, light_hex: str, intensity: float = 1.0,
              ambient_hex: str | None = None, ambient: float = 0.0) -> str:
    light = hex_to_linear(light_hex) * intensity
    if ambient_hex is not None:
        light = light + hex_to_linear(ambient_hex) * ambient
    return linear_to_hex(hex_to_linear(albedo_hex) * light)

# calculate color in shadow
def shadow_color(albedo_hex: str, ambient_hex: str, ambient: float) -> str:
    return linear_to_hex(hex_to_linear(albedo_hex) * hex_to_linear(ambient_hex) * ambient)

# render math data back into display view
def _to_image(lin: np.ndarray) -> np.ndarray:
    return linear_to_srgb(np.clip(lin, 0.0, 1.0))

# smooth stepping for gradient and shadows
def _smoothstep(e0, e1, x):
    t = np.clip((x - e0) / max(e1 - e0, 1e-9), 0.0, 1.0)
    return t * t * (3 - 2 * t)

# generates grid for preview canvas
def _grid(width: int, height: int):
    ys, xs = np.mgrid[0:height, 0:width].astype(float)
    return xs, ys

# GLOW

# calculates amount of "light" pixel gets based on inv square falloff
def glow_falloff(dist, spread: float):
    return 1.0 / (1.0 + (np.maximum(dist, 0.0) / max(spread, 1e-6)) ** 2) ** 2

# simulates lighting on a sampled pixel and returns proper hex
def glow_sample(surface_hex: str, emitter_hex: str, *, intensity: float, ambient: float,
                mode: str, falloff: float) -> str:
    surface = hex_to_linear(surface_hex)
    emit = hex_to_linear(emitter_hex)
    base = surface * ambient
    if mode == "bloom":
        return linear_to_hex(base + emit * intensity * falloff)
    return linear_to_hex(base + surface * emit * intensity * falloff)

# renders glow preview
def render_glow(surface: str, emitter: str, *, intensity: float = 1.0,
                spread: float = 90.0, ambient: float = 0.35, mode: str = "cast",
                shape: str = "circle", width: int = 720, height: int = 360) -> np.ndarray:
    xs, ys = _grid(width, height)
    cx, cy = width / 2, height / 2

    if shape == "bar":
        half_len, half_thick = width * 0.28, 9.0
        # signed-ish distance to a horizontal rounded bar
        dx = np.maximum(np.abs(xs - cx) - half_len, 0.0)
        dy = np.abs(ys - cy)
        dist = np.hypot(dx, dy) - half_thick
    else:
        dist = np.hypot(xs - cx, ys - cy) - 26.0          # 26 px radius emitter

    fall = glow_falloff(dist, spread)
    surface_lin = hex_to_linear(surface)
    emit_lin = hex_to_linear(emitter)

    base = surface_lin * ambient
    glow = emit_lin * intensity * fall[..., None]
    lin = base + (glow if mode == "bloom" else surface_lin * glow)

    # the emitter itself is the emitter color (not multiplied by anything)
    core = (1.0 - _smoothstep(-1.5, 1.5, dist))[..., None]
    lin = lin * (1 - core) + emit_lin * core
    return _to_image(lin)

# SHADOW

# renders shadow preview
def render_shadow(surface: str, obj: str, key: str, fill: str, *,
                  intensity: float = 1.0, ambient: float = 0.25,
                  azimuth: float = 135.0, elevation: float = 45.0,
                  softness: float = 0.25, width: int = 720, height: int = 400) -> np.ndarray:

    xs, ys = _grid(width, height)
    cx, cy, radius = width / 2, height / 2, min(width, height) * 0.2
    az, el = np.radians(azimuth), np.radians(np.clip(elevation, 5, 89))
    lx, ly, lz = np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)

    key_lin = hex_to_linear(key) * intensity
    fill_lin = hex_to_linear(fill) * ambient
    floor_albedo, obj_albedo = hex_to_linear(surface), hex_to_linear(obj)

    # shadow of a sphere resting on the floor: an ellipse stretched along the light
    # direction, shifted away from the light.
    shift = radius / np.tan(el)
    sx, sy = cx - shift * np.cos(az), cy - shift * np.sin(az)
    u = (xs - sx) * np.cos(az) + (ys - sy) * np.sin(az)      # along the light
    v = -(xs - sx) * np.sin(az) + (ys - sy) * np.cos(az)     # across it
    q = np.sqrt((u / (radius / np.sin(el))) ** 2 + (v / radius) ** 2)
    w = 0.02 + 0.45 * softness
    in_shadow = 1.0 - _smoothstep(1 - w, 1 + w, q)

    floor_light = key_lin * (1 - in_shadow[..., None]) + fill_lin * in_shadow[..., None]
    lin = floor_albedo * floor_light

    # the sphere: lit side gets the key light, the side turned away gets the fill light,
    # blended by how much it faces the light
    dx, dy = (xs - cx) / radius, (ys - cy) / radius
    r2 = dx ** 2 + dy ** 2
    nz = np.sqrt(np.clip(1 - r2, 0.0, 1.0))
    lambert = np.clip(dx * lx + dy * ly + nz * lz, 0.0, 1.0)
    obj_light = key_lin * lambert[..., None] + fill_lin * (1 - lambert)[..., None]
    mask = (1.0 - _smoothstep(1.0 - 1.5 / radius, 1.0, np.sqrt(r2)))[..., None]
    lin = lin * (1 - mask) + obj_albedo * obj_light * mask
    return _to_image(lin)

# calculates light and shadow parts of surface and object
def shadow_readout(surface: str, obj: str, key: str, fill: str, *, intensity: float,
                   ambient: float) -> dict[str, str]:
    """The four colors that matter, matching what render_shadow draws:
    surface_lit, surface_shadow, object_lit (side facing the light), object_shadow.
    The lit colors depend only on key/intensity, the shadow colors only on fill/ambient."""
    light = hex_to_linear(key) * intensity
    dark = hex_to_linear(fill) * ambient
    floor, ball = hex_to_linear(surface), hex_to_linear(obj)
    return {"surface_lit": linear_to_hex(floor * light),
            "surface_shadow": linear_to_hex(floor * dark),
            "object_lit": linear_to_hex(ball * light),
            "object_shadow": linear_to_hex(ball * dark)}

# RELIGHT

# calculates relit (in light and shadow) colors of palette
def relight_palette(colors: list[str], light: str, *, intensity: float = 1.0,
                    fill: str = "#ffffff", ambient: float = 0.25) -> list[tuple[str, str, str]]:
    return [(c, lit_color(c, light, intensity), shadow_color(c, fill, ambient))
            for c in colors]
