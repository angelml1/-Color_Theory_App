import re

import flet as ft

from components.swatch import swatch
from palette_library import (load_palettes, next_palette_name, save_palettes,
                             subscribe_palettes)
from palette_state import MAX_COLORS


def build(palette, page: ft.Page) -> ft.Control:
    saved_palettes = load_palettes()
    picker = ft.FilePicker()
    page.services.append(picker)

    status = ft.Text(size=12, color=ft.Colors.GREY_700)
    current_count = ft.Text(size=12, color=ft.Colors.GREY_700)
    current_swatches = ft.Row(spacing=4, height=48)
    name_field = ft.TextField(
        hint_text="Palette name", dense=True, expand=True, max_length=40,
    )
    save_button = ft.FilledButton(
        "Save palette", icon=ft.Icons.SAVE_OUTLINED,
        on_click=lambda e: save_current(),
    )
    saved_empty = ft.Text("No palettes saved yet.", italic=True)
    saved_title = ft.Text(size=18, weight=ft.FontWeight.BOLD)
    root = None

    def set_status(message: str):
        status.value = message
        try:
            status.update()
        except Exception:
            pass

    def render():
        colors = list(palette.colors)
        current_count.value = f"{len(colors)} of {MAX_COLORS} colors"
        save_button.disabled = not colors
        current_swatches.controls = [
            ft.Container(
                expand=1,
                height=44,
                bgcolor=color,
                tooltip=f"Remove {color}",
                border=ft.Border.all(1, ft.Colors.BLACK_12),
                on_click=lambda e, color=color: palette.remove(color),
            )
            for color in colors
        ]
        if not colors:
            current_swatches.controls = [
                ft.Text("Your palette is empty. Add colors from Color Wheel or Upload.",
                        italic=True, color=ft.Colors.GREY_700)
            ]
        saved_title.value = f"Saved palettes ({len(saved_palettes)})"
        saved_empty.visible = not saved_palettes
        if root is not None:
            root.controls = [
                ft.Text("Home", size=22, weight=ft.FontWeight.BOLD),
                saved_title,
                saved_empty,
                *build_saved_rows(),
                ft.Divider(height=1),
                ft.Row(
                    [
                        ft.Text("Current palette", size=18, weight=ft.FontWeight.BOLD),
                        current_count,
                        ft.TextButton("Clear", on_click=lambda e: palette.set([])),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                current_swatches,
                ft.Row([name_field, save_button], spacing=8, wrap=True),
                status,
            ]
            try:
                root.update()
            except Exception:
                pass

    def save_current():
        if not palette.colors:
            set_status("Add colors before saving a palette.")
            return
        name = (name_field.value or "").strip() or next_palette_name(saved_palettes)
        saved_palettes.insert(0, {"name": name, "colors": list(palette.colors)})
        try:
            save_palettes(saved_palettes)
        except OSError:
            saved_palettes.pop(0)
            set_status("Couldn't save palette to disk.")
            return
        name_field.value = ""
        set_status(f"Saved {name}.")
        render()

    def on_saved_palettes_changed(items):
        saved_palettes[:] = items
        render()

    def use_saved(item):
        palette.set(item["colors"])
        set_status(f"Loaded {item['name']} into the current palette.")

    def add_saved(item):
        for color in item["colors"]:
            palette.add(color)
        set_status(f"Added colors from {item['name']}.")

    def delete_saved(index: int):
        deleted = saved_palettes.pop(index)
        try:
            save_palettes(saved_palettes)
        except OSError:
            saved_palettes.insert(index, deleted)
            set_status("Couldn't save palette changes to disk.")
            render()
            return
        set_status(f"Deleted {deleted['name']}.")

    def build_saved_rows():
        rows = []
        for index, item in enumerate(saved_palettes):
            swatches = ft.Row(
                [
                    ft.Container(
                        width=18, height=18, bgcolor=color,
                        border=ft.Border.all(1, ft.Colors.BLACK_12),
                        tooltip=color,
                    )
                    for color in item["colors"]
                ],
                spacing=3,
            )
            rows.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(item["name"], weight=ft.FontWeight.W_500),
                                    swatches,
                                    ft.Text(f"List of {len(item['colors'])} colors", size=11,
                                            color=ft.Colors.GREY_700),
                                ],
                                spacing=3,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CHECK,
                                tooltip="Replace current palette",
                                on_click=lambda e, item=item: use_saved(item),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ADD,
                                tooltip="Add colors to current palette",
                                on_click=lambda e, item=item: add_saved(item),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DOWNLOAD,
                                tooltip="Export palette",
                                on_click=lambda e, item=item: export_saved(item),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Delete palette",
                                on_click=lambda e, index=index: delete_saved(index),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    padding=ft.Padding.symmetric(vertical=7, horizontal=8),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                    border_radius=4,
                )
            )
            if index < len(saved_palettes) - 1:
                rows.append(ft.Divider(height=1))
        return rows

    async def export_saved(item):
        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", item["name"]).strip("._")
        safe_name = safe_name or "palette"
        content = "\n".join(item["colors"]) + "\n"
        await picker.save_file(
            dialog_title="Export palette",
            file_name=f"{safe_name}.txt",
            allowed_extensions=["txt"],
            src_bytes=content.encode("utf-8"),
        )

    palette.subscribe(render)
    root = ft.ListView(
        controls=[],
        spacing=12,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
    subscribe_palettes(on_saved_palettes_changed)
    render()
    return root