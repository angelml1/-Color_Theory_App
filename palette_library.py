import json
import re
from pathlib import Path

from palette_state import MAX_COLORS

DEFAULT_LIBRARY_PATH = Path.home() / ".color_theory_app" / "palettes.json"
HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}\Z")
_listeners = []


def _clean_palettes(data) -> list[dict[str, object]]:
    if not isinstance(data, list):
        return []

    palettes = []
    for item in data:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        colors = item.get("colors")
        if not isinstance(name, str) or not name.strip() or not isinstance(colors, list):
            continue
        valid_colors = []
        for color in colors:
            if isinstance(color, str) and HEX_COLOR.fullmatch(color):
                normalized = color.lower()
                if normalized not in valid_colors:
                    valid_colors.append(normalized)
            if len(valid_colors) >= MAX_COLORS:
                break
        if valid_colors:
            palettes.append({"name": name.strip(), "colors": valid_colors})
    return palettes


def load_palettes(path: Path = DEFAULT_LIBRARY_PATH) -> list[dict[str, object]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return _clean_palettes(data)


def save_palettes(palettes: list[dict[str, object]],
                  path: Path = DEFAULT_LIBRARY_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(path.name + ".tmp")
    cleaned = _clean_palettes(palettes)
    payload = json.dumps(cleaned, indent=2)
    temporary_path.write_text(payload + "\n", encoding="utf-8")
    temporary_path.replace(path)
    for listener in list(_listeners):
        listener(cleaned)


def add_palette(name: str, colors: list[str],
                path: Path = DEFAULT_LIBRARY_PATH) -> list[dict[str, object]]:
    palettes = load_palettes(path)
    palettes.insert(0, {"name": name, "colors": colors})
    save_palettes(palettes, path)
    return palettes


def next_palette_name(palettes: list[dict[str, object]]) -> str:
    names = {item.get("name") for item in palettes if isinstance(item, dict)}
    index = 1
    while f"Palette {index}" in names:
        index += 1
    return f"Palette {index}"


def subscribe_palettes(listener):
    _listeners.append(listener)

    def unsubscribe():
        if listener in _listeners:
            _listeners.remove(listener)

    return unsubscribe