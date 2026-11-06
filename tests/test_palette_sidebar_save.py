from types import SimpleNamespace

from components import palette as palette_component
from palette_library import add_palette, load_palettes, subscribe_palettes
from palette_state import Palette
from pages import home


def test_sidebar_save_persists_current_palette_and_notifies(monkeypatch, tmp_path):
    notified = []
    unsubscribe = subscribe_palettes(notified.append)
    path = tmp_path / "palettes.json"
    monkeypatch.setattr(
        palette_component, "load_palettes", lambda: load_palettes(path),
    )
    monkeypatch.setattr(home, "load_palettes", lambda: load_palettes(path))
    monkeypatch.setattr(
        palette_component, "add_palette",
        lambda name, colors: add_palette(name, colors, path),
    )
    palette = Palette(colors=["#123456", "#abcdef"])
    home_page = SimpleNamespace(services=[])
    home_view = home.build(palette, home_page)

    sidebar = palette_component.palette_sidebar(palette)
    body = sidebar.controls[1]
    save_button = body.controls[5]
    save_button.on_click(None)
    palette.add("#fedcba")
    save_button.on_click(None)
    palette.remove("#123456")
    save_button.on_click(None)

    expected = [
        {"name": "Palette 3", "colors": ["#abcdef", "#fedcba"]},
        {"name": "Palette 2", "colors": ["#123456", "#abcdef", "#fedcba"]},
        {"name": "Palette 1", "colors": ["#123456", "#abcdef"]},
    ]
    assert load_palettes(path) == expected
    assert notified[-1] == expected
    assert home_view.controls[1].value == "Saved palettes (3)"
    saved_names = [
        home_view.controls[3 + index * 2].content.controls[0].controls[0].value
        for index in range(3)
    ]
    assert saved_names == ["Palette 3", "Palette 2", "Palette 1"]
    unsubscribe()