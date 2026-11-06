import json

from palette_library import load_palettes, next_palette_name, save_palettes


def test_saved_palettes_persist_across_loads(tmp_path):
    path = tmp_path / "app-data" / "palettes.json"
    palettes = [
        {"name": "Evening", "colors": ["#112233", "#AABBCC"]},
        {"name": "Ocean", "colors": ["#010203"]},
    ]

    save_palettes(palettes, path)

    assert load_palettes(path) == [
        {"name": "Evening", "colors": ["#112233", "#aabbcc"]},
        {"name": "Ocean", "colors": ["#010203"]},
    ]


def test_load_ignores_invalid_records_and_colors(tmp_path):
    path = tmp_path / "palettes.json"
    path.write_text(json.dumps([
        {"name": "Valid", "colors": ["#123456", "bad", "#123456"]},
        {"name": "Empty", "colors": ["not-a-color"]},
        None,
    ]), encoding="utf-8")

    assert load_palettes(path) == [{"name": "Valid", "colors": ["#123456"]}]


def test_missing_or_malformed_file_loads_empty_list(tmp_path):
    path = tmp_path / "missing.json"
    assert load_palettes(path) == []

    path.write_text("{invalid", encoding="utf-8")
    assert load_palettes(path) == []


def test_next_palette_name_skips_existing_default_names():
    palettes = [
        {"name": "Palette 1", "colors": ["#112233"]},
        {"name": "Named palette", "colors": ["#445566"]},
        {"name": "Palette 3", "colors": ["#778899"]},
    ]

    assert next_palette_name(palettes) == "Palette 2"