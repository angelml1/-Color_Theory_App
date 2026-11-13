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

    list_view = root.content
    name_field, save_button = list_view.controls[3].controls
    name_field.value = "Evening"
    save_button.on_click(None)

    assert stored == [{"name": "Evening", "colors": ["#123456", "#abcdef"]}]

    rebuilt = home.build(Palette(), SimpleNamespace(services=[]))
    rebuilt_list = rebuilt.content
    assert rebuilt_list.controls[6].value == "Saved palettes (1)"
    assert rebuilt_list.controls[7].visible is False
    assert rebuilt_list.controls[8].content.controls[0].controls[0].value == "Evening"


def test_home_saved_list_scrolls_and_renders_all_palettes(monkeypatch):
    palettes = [
        {"name": f"Palette {index}", "colors": [f"#{index:06x}"]}
        for index in range(1, 9)
    ]
    monkeypatch.setattr(home, "load_palettes", lambda: palettes)

    root = home.build(Palette(), SimpleNamespace(services=[]))
    list_view = root.content
    assert list_view.scroll == home.ft.ScrollMode.AUTO
    assert list_view.tight is True
    assert list_view.expand is None
    assert list_view.controls[6].value == "Saved palettes (8)"
    saved_row_names = [
        list_view.controls[8 + index * 2].content.controls[0].controls[0].value
        for index in range(8)
    ]
    assert saved_row_names == [f"Palette {index}" for index in range(1, 9)]