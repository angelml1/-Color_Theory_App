from copy import deepcopy
from types import SimpleNamespace

from palette_state import Palette
from pages import home


def test_home_saved_palette_is_available_after_rebuild(monkeypatch):
    stored = []
    monkeypatch.setattr(home, "load_palettes", lambda: deepcopy(stored))
    monkeypatch.setattr(home, "save_palettes",
                        lambda palettes: stored.__setitem__(slice(None), deepcopy(palettes)))

    palette = Palette()
    page = SimpleNamespace(services=[])
    root = home.build(palette, page)
    palette.set(["#123456", "#abcdef"])

    name_field, save_button = root.controls[-2].controls
    name_field.value = "Evening"
    save_button.on_click(None)

    assert stored == [{"name": "Evening", "colors": ["#123456", "#abcdef"]}]

    rebuilt = home.build(Palette(), SimpleNamespace(services=[]))
    assert rebuilt.controls[1].value == "Saved palettes (1)"
    assert rebuilt.controls[2].visible is False
    assert rebuilt.controls[3].content.controls[0].controls[0].value == "Evening"


def test_home_saved_list_scrolls_and_renders_all_palettes(monkeypatch):
    palettes = [
        {"name": f"Palette {index}", "colors": [f"#{index:06x}"]}
        for index in range(1, 9)
    ]
    monkeypatch.setattr(home, "load_palettes", lambda: palettes)

    root = home.build(Palette(), SimpleNamespace(services=[]))
    assert root.scroll == home.ft.ScrollMode.AUTO
    assert root.controls[1].value == "Saved palettes (8)"
    saved_row_names = [
        root.controls[3 + index * 2].content.controls[0].controls[0].value
        for index in range(8)
    ]
    assert saved_row_names == [f"Palette {index}" for index in range(1, 9)]