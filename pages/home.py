import io
import re

import flet as ft
from PIL import Image, ImageOps

from color_math.extract import extract_colors
from color_math.imaging import image_to_b64, pixel_at
from components.color_wheel import ColorWheel
from pages import color_wheel
from palette_state import MAX_COLORS

EXTRACT_COUNT = min(6, MAX_COLORS)
IMAGE_EXTENSIONS = ["bmp", "gif", "jpeg", "jpg", "png", "webp"]


def build(palette, page: ft.Page) -> ft.Control:
	saved_palettes = []
	state = {
		"section": "Home", "image": None, "extracted": [], "selected": [],
		"samples": [], "extract_count": EXTRACT_COUNT, "mode": "auto",
	}
	picker = ft.FilePicker()
	page.services.append(picker)

	status = ft.Text(size=12, color=ft.Colors.GREY_700)
	palette_strip = ft.Row(spacing=3, height=52)
	palette_count = ft.Text(size=12, color=ft.Colors.GREY_700)
	name_field = ft.TextField(
		hint_text="Palette name", dense=True, expand=True, max_length=40,
	)
	home_name_field = ft.TextField(
		hint_text="Palette name", dense=True, expand=True, max_length=40,
	)
	save_button = ft.FilledButton(
		"Save palette", icon=ft.Icons.SAVE_OUTLINED,
		on_click=lambda e: save_palette(),
	)
	home_save_button = ft.FilledButton(
		"Save palette", icon=ft.Icons.SAVE_OUTLINED,
		on_click=lambda e: save_palette(home_name_field),
	)
	saved_list = ft.Column(spacing=0)
	saved_empty = ft.Text("Your saved palettes will appear here.", italic=True)
	home_saved_list = ft.Column(spacing=0)
	home_saved_empty = ft.Text("No palettes saved yet.", italic=True)

	preview_hint = ft.Column(
		[ft.Icon(ft.Icons.IMAGE_OUTLINED, size=34, color=ft.Colors.GREY_500),
		 ft.Text("No image selected", color=ft.Colors.GREY_700)],
		horizontal_alignment=ft.CrossAxisAlignment.CENTER,
		alignment=ft.MainAxisAlignment.CENTER,
		expand=True,
	)
	preview_image = ft.Image(
		src="", width=520, height=210, fit=ft.BoxFit.CONTAIN, visible=False,
	)
	preview_gesture = ft.GestureDetector(
		content=preview_image,
	)
	preview_frame = ft.Container(
		content=ft.Column(
			[preview_hint, preview_gesture],
			horizontal_alignment=ft.CrossAxisAlignment.CENTER,
			alignment=ft.MainAxisAlignment.CENTER,
			expand=True,
		),
		height=240,
		width=544,
		padding=12,
		bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
		border_radius=4,
	)
	extracted_row = ft.Row(spacing=6, wrap=True)
	selected_count = ft.Text(size=12, color=ft.Colors.GREY_700)
	mode = ft.SegmentedButton(
		selected=["auto"],
		segments=[
			ft.Segment(value="sample", label=ft.Text("Click to sample")),
			ft.Segment(value="auto", label=ft.Text("Auto-extract")),
		],
	)

	def set_status(message: str):
		status.value = message
		try:
			status.update()
		except Exception:
			pass

	def render():
		colors = list(palette.colors)
		palette_count.value = f"{len(colors)} of {MAX_COLORS} colors"
		palette_strip.controls = [
			ft.Container(
				expand=1,
				height=48,
				bgcolor=color,
				tooltip=f"Remove {color}",
				border=ft.Border.all(1, ft.Colors.BLACK_12),
				on_click=lambda e, color=color: palette.remove(color),
			)
			for color in colors
		]
		if not colors:
			palette_strip.controls = [
				ft.Text("Select colors from an image or open Colors to build a palette.",
						italic=True, color=ft.Colors.GREY_700)
			]
		save_button.disabled = not colors
		selected_count.value = f"{len(state['selected'])} colors selected"
		extracted_row.controls = [
			ft.Container(
				content=ft.Text(color.upper(), size=10,
								color=ft.Colors.WHITE if color in state["selected"] else ft.Colors.BLACK),
				width=68, height=30, bgcolor=color,
				border=ft.Border.all(2 if color in state["selected"] else 1,
								 ft.Colors.BLACK if color in state["selected"] else ft.Colors.WHITE),
				border_radius=16, alignment=ft.Alignment.CENTER,
				tooltip="Selected" if color in state["selected"] else "Select color",
				on_click=lambda e, color=color: toggle_extracted(color),
			)
			for color in state["extracted"]
		]
		saved_empty.visible = not saved_palettes
		home_saved_empty.visible = not saved_palettes
		saved_list.controls = build_saved_rows()
		home_saved_list.controls = build_saved_rows()
		try:
			root.update()
		except Exception:
			pass

	def save_palette(field=None):
		if not palette.colors:
			set_status("Add at least one color before saving a palette.")
			return
		field = field or name_field
		name = (field.value or "").strip() or f"Palette {len(saved_palettes) + 1}"
		saved_palettes.insert(0, {"name": name, "colors": list(palette.colors)})
		field.value = ""
		set_status(f"Saved {name}.")
		render()

	def use_saved(item):
		palette.set(item["colors"])
		set_status(f"Loaded {item['name']} into the current palette.")

	def add_saved(item):
		for color in item["colors"]:
			palette.add(color)
		set_status(f"Added colors from {item['name']}.")

	def toggle_extracted(color: str):
		if color in state["selected"]:
			state["selected"].remove(color)
		elif len(state["selected"]) < MAX_COLORS:
			state["selected"].append(color)
		render()

	def toggle_dialog_color(color: str, cell, dialog):
		toggle_extracted(color)
		cell.bgcolor = (ft.Colors.SECONDARY_CONTAINER
						if color in state["selected"] else ft.Colors.SURFACE)
		try:
			cell.update()
			dialog.update()
		except Exception:
			pass

	def create_palette(e):
		if not state["selected"]:
			set_status("Select at least one extracted color first.")
			return
		palette.set(state["selected"])
		set_status(f"Created a palette with {len(state['selected'])} colors.")

	def extract_image_colors():
		image = state["image"]
		if image is None:
			set_status("Upload an image before extracting colors.")
			return
		colors = extract_colors(image, state["extract_count"])
		state["extracted"] = colors
		state["selected"] = list(colors)
		state["samples"] = []
		set_status(f"Extracted {len(colors)} colors. Select the colors for your palette.")
		render()

	def on_mode_change(e):
		state["mode"] = next(iter(e.control.selected))
		if state["mode"] == "auto" and state["image"] is not None:
			extract_image_colors()
			open_extraction_dialog()
		else:
			set_status("Click the image to sample colors." if state["mode"] == "sample"
					   else "Select Auto-extract to find the dominant colors.")

	def sample_image(e):
		image = state["image"]
		if image is None or state["mode"] != "sample":
			return
		position = getattr(e, "local_position", None)
		x = position.x if position is not None else getattr(e, "local_x", 0)
		y = position.y if position is not None else getattr(e, "local_y", 0)
		display_width, display_height = 520, 210
		scale = min(display_width / image.width, display_height / image.height)
		shown_width, shown_height = image.width * scale, image.height * scale
		x_offset, y_offset = (display_width - shown_width) / 2, (display_height - shown_height) / 2
		if not (x_offset <= x < x_offset + shown_width and
				y_offset <= y < y_offset + shown_height):
			return
		color = pixel_at(image, (x - x_offset) / scale, (y - y_offset) / scale)
		if color in state["extracted"] or len(state["extracted"]) >= MAX_COLORS:
			return
		state["extracted"].append(color)
		state["selected"].append(color)
		state["samples"].append(color)
		set_status(f"Sampled {color} from the image.")
		render()

	def undo_sample(e):
		if not state["samples"]:
			return
		color = state["samples"].pop()
		state["extracted"].remove(color)
		if color in state["selected"]:
			state["selected"].remove(color)
		set_status(f"Removed the last sampled color ({color}).")
		render()

	preview_gesture.on_tap_down = sample_image
	mode.on_change = on_mode_change

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

	def delete_saved(index: int):
		deleted = saved_palettes.pop(index)
		set_status(f"Deleted {deleted['name']}.")
		render()

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
								[ft.Text(item["name"], weight=ft.FontWeight.W_500),
								 swatches,
								 ft.Text(f"List of {len(item['colors'])} colors", size=11,
										 color=ft.Colors.GREY_700)],
								spacing=3,
								expand=True,
							),
							ft.IconButton(
								icon=ft.Icons.ADD,
								tooltip="Add colors to current palette",
								on_click=lambda e, item=item: add_saved(item),
							),
							ft.IconButton(
								icon=ft.Icons.EDIT_OUTLINED,
								tooltip="Rename palette",
								on_click=lambda e, index=index: rename_saved(index),
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

	def rename_saved(index: int):
		field = ft.TextField(value=saved_palettes[index]["name"], label="Palette name")
		dialog = ft.AlertDialog(
			modal=True,
			title=ft.Text("Rename palette"),
			content=field,
			actions=[
				ft.TextButton("Cancel", on_click=lambda e: close_dialog(dialog)),
				ft.FilledButton("Save", on_click=lambda e: save_rename(index, field, dialog)),
			],
		)
		show_dialog(dialog)

	def save_rename(index: int, field, dialog):
		name = (field.value or "").strip()
		if not name:
			field.error_text = "Enter a palette name."
			field.update()
			return
		saved_palettes[index]["name"] = name
		close_dialog(dialog)
		set_status(f"Renamed palette to {name}.")
		render()

	def show_dialog(dialog):
		if hasattr(page, "show_dialog"):
			page.show_dialog(dialog)
		else:
			page.open(dialog)

	def close_dialog(dialog):
		if hasattr(page, "pop_dialog"):
			page.pop_dialog()
		else:
			page.close(dialog)

	def open_extraction_dialog(e=None):
		if not state["extracted"]:
			set_status("Upload an image or sample a color first.")
			return
		color_rows = []
		for start in range(0, len(state["extracted"]), 3):
			cells = []
			for color in state["extracted"][start:start + 3]:
				selected = color in state["selected"]
				cell = ft.Container(
						content=ft.Row(
							[ft.Container(width=22, height=22, bgcolor=color,
											 border=ft.Border.all(1, ft.Colors.BLACK_12)),
							 ft.Text(color.upper(), size=12)],
							spacing=8,
						),
						width=145, height=38, padding=6,
						bgcolor=ft.Colors.SECONDARY_CONTAINER if selected else ft.Colors.SURFACE,
						border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
						border_radius=4,
					)
				cell.on_click = lambda e, color=color, cell=cell: toggle_dialog_color(
					color, cell, dialog)
				cells.append(cell)
			color_rows.append(ft.Row(cells, spacing=6))
		dialog = ft.AlertDialog(
			modal=True,
			title=ft.Text("Extracted colors"),
			content=ft.Container(
				content=ft.Column(
					[
						ft.Row(
							[
								ft.Column(color_rows, spacing=6, scroll=ft.ScrollMode.AUTO),
								ft.Container(
									content=ft.OutlinedButton(
										"Select from color wheel",
										icon=ft.Icons.COLOR_LENS_OUTLINED,
										on_click=lambda e: open_wheel_dialog(dialog),
									),
									width=145,
									alignment=ft.Alignment.CENTER,
								),
							],
							spacing=12,
							vertical_alignment=ft.CrossAxisAlignment.CENTER,
						),
						ft.Row([selected_count], alignment=ft.MainAxisAlignment.END),
					],
					spacing=12,
					tight=True,
				),
				width=560,
			),
			actions=[
				ft.TextButton("Cancel", on_click=lambda e: close_dialog(dialog)),
				ft.FilledButton("Create palette", on_click=lambda e: create_palette_from_dialog(dialog)),
			],
		)
		show_dialog(dialog)

	def create_palette_from_dialog(dialog):
		if not state["selected"]:
			set_status("Select at least one extracted color first.")
			return
		close_dialog(dialog)
		create_palette(None)

	def open_wheel_dialog(parent_dialog=None):
		selected_color = {"value": palette.colors[-1] if palette.colors else "#3a7bd5"}
		color_preview = ft.Container(
			width=42, height=42, bgcolor=selected_color["value"], border_radius=4,
			border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
		)
		color_value = ft.Text(selected_color["value"].upper())

		def on_wheel_pick(color: str):
			selected_color["value"] = color
			color_preview.bgcolor = color
			color_value.value = color.upper()
			try:
				color_preview.update()
				color_value.update()
			except Exception:
				pass

		wheel = ColorWheel(on_wheel_pick, initial=selected_color["value"])
		dialog = ft.AlertDialog(
			modal=True,
			title=ft.Text("Select a color"),
			content=ft.Column([wheel.control, ft.Row([color_preview, color_value])], tight=True),
			actions=[
				ft.TextButton("Cancel", on_click=lambda e: cancel_wheel_dialog(
					dialog, parent_dialog)),
				ft.FilledButton("Add color", on_click=lambda e: add_wheel_color(
					selected_color["value"], dialog, parent_dialog)),
			],
		)
		if parent_dialog is not None:
			close_dialog(parent_dialog)
		show_dialog(dialog)

	def cancel_wheel_dialog(dialog, parent_dialog):
		close_dialog(dialog)
		if parent_dialog is not None:
			open_extraction_dialog()

	def add_wheel_color(color: str, dialog, parent_dialog):
		if color not in state["extracted"] and len(state["extracted"]) < MAX_COLORS:
			state["extracted"].append(color)
			state["selected"].append(color)
		close_dialog(dialog)
		render()
		if parent_dialog is not None:
			open_extraction_dialog()
		else:
			palette.add(color)

	async def choose_image(e, dialog_title="Choose an image"):
		try:
			files = await picker.pick_files(
				dialog_title=dialog_title,
				file_type=ft.FilePickerFileType.IMAGE,
				allowed_extensions=IMAGE_EXTENSIONS,
				with_data=True,
			)
			if not files:
				return
			selected = files[0]
			source = io.BytesIO(selected.bytes) if selected.bytes else selected.path
			if source is None:
				raise ValueError("The selected file could not be read.")
			with Image.open(source) as opened:
				image = ImageOps.exif_transpose(opened).convert("RGB")
				image.thumbnail((1200, 800))
			state["image"] = image
			preview_image.src = image_to_b64(image)
			preview_image.visible = True
			preview_hint.visible = False
			if state["mode"] == "auto":
				extract_image_colors()
				set_status(f"Loaded {selected.name}. Select colors, then create a palette.")
				open_extraction_dialog()
			else:
				state["extracted"] = []
				state["selected"] = []
				state["samples"] = []
				set_status(f"Loaded {selected.name}. Click the image to sample colors.")
				render()
		except Exception as error:
			set_status(f"Couldn't read that image: {error}")

	async def choose_photo(e):
		await choose_image(e, dialog_title="Choose a photo")

	def clear_image(e):
		state["image"] = None
		state["extracted"] = []
		state["selected"] = []
		state["samples"] = []
		preview_image.src = ""
		preview_image.visible = False
		preview_hint.visible = True
		set_status("Image preview cleared.")
		render()

	palette.subscribe(render)

	image_panel = ft.Container(
		content=ft.Column(
			[
				ft.Text("Image preview", size=18, weight=ft.FontWeight.BOLD),
				preview_frame,
				ft.Row(
					[
						ft.OutlinedButton("Upload image", icon=ft.Icons.UPLOAD_FILE,
									  on_click=choose_image),
						ft.OutlinedButton("Take photo", icon=ft.Icons.CAMERA_ALT,
									  tooltip="Choose a photo from this device",
								  on_click=choose_photo),
						ft.TextButton("Extracted colors", on_click=open_extraction_dialog),
						ft.TextButton("Clear image", on_click=clear_image),
					],
					spacing=8,
					wrap=True,
				),
				mode,
				ft.TextButton("Undo last sample", on_click=undo_sample),
			],
			spacing=10,
		),
		padding=12,
		border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
		border_radius=4,
		bgcolor=ft.Colors.SURFACE,
	)
	current_palette = ft.Column(
		[
			ft.Row(
				[ft.Text("Current Palette", size=18, weight=ft.FontWeight.BOLD),
				 palette_count,
				 ft.IconButton(icon=ft.Icons.ADD, tooltip="Add a color from the wheel",
							   on_click=lambda e: open_wheel_dialog()),
				 ft.TextButton("Clear palette", on_click=lambda e: palette.set([]))],
				alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
			),
			palette_strip,
			ft.Row([home_name_field, home_save_button], spacing=8, wrap=True),
		],
		spacing=10,
	)
	home_view = ft.Column(
		[
			image_panel,
			current_palette,
			ft.Row(
				[ft.Text("Recent palettes", size=18, weight=ft.FontWeight.BOLD),
				 ft.TextButton("View library", on_click=lambda e: show_section("Library"))],
				alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
			),
			home_saved_empty,
			home_saved_list,
			status,
		],
		spacing=16,
		scroll=ft.ScrollMode.AUTO,
	)
	colors_view = color_wheel.build(palette)
	palette_view = ft.Column(
		[
			ft.Text("Library", size=22, weight=ft.FontWeight.BOLD),
			ft.Row([name_field, save_button], spacing=8, wrap=True),
			saved_empty,
			saved_list,
		],
		spacing=12,
		scroll=ft.ScrollMode.AUTO,
	)
	count_field = ft.TextField(
		label="Colors to extract", value=str(state["extract_count"]), width=180,
		keyboard_type=ft.KeyboardType.NUMBER, dense=True,
	)

	def set_extract_count(e):
		try:
			count = int(count_field.value)
			if count < 2 or count > MAX_COLORS:
				raise ValueError
		except (TypeError, ValueError):
			count_field.error_text = f"Choose a number from 2 to {MAX_COLORS}."
			count_field.update()
			return
		state["extract_count"] = count
		count_field.error_text = None
		set_status(f"Auto-extraction will find {count} colors.")
		if state["mode"] == "auto" and state["image"] is not None:
			extract_image_colors()
		else:
			count_field.update()

	count_field.on_submit = set_extract_count
	count_field.on_blur = set_extract_count
	settings_view = ft.Column(
		[
			ft.Text("Settings", size=22, weight=ft.FontWeight.BOLD),
			ft.Text("Choose how many dominant colors are found in an image."),
			count_field,
		],
		spacing=12,
	)
	sections = {
		"Home": home_view,
		"Color Wheel": colors_view,
		"Library": palette_view,
		"Settings": settings_view,
	}
	section_content = ft.Container(content=home_view, expand=True, padding=16)
	nav_buttons = {}

	def show_section(name: str):
		palette.pick.cancel()
		state["section"] = name
		section_content.content = sections[name]
		for label, button in nav_buttons.items():
			selected = label == name
			button.style = ft.ButtonStyle(
				bgcolor=ft.Colors.BLACK if selected else None,
				color=ft.Colors.WHITE if selected else ft.Colors.GREY_700,
				shape=ft.RoundedRectangleBorder(radius=18),
				padding=ft.Padding.symmetric(horizontal=22, vertical=10),
			)
		try:
			root.update()
		except Exception:
			pass

	for section in sections:
		nav_buttons[section] = ft.TextButton(
			section, on_click=lambda e, section=section: show_section(section),
		)

	nav = ft.Row(
		[
			ft.Row([ft.Icon(ft.Icons.COLOR_LENS_OUTLINED),
					ft.Text("Colour extractor", weight=ft.FontWeight.BOLD)], spacing=8),
			ft.Row(list(nav_buttons.values()), spacing=4),
		],
		alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
		vertical_alignment=ft.CrossAxisAlignment.CENTER,
		wrap=True,
	)
	root = ft.Column(
		[
			ft.Container(content=nav, padding=ft.Padding.symmetric(horizontal=18, vertical=10),
					  bgcolor=ft.Colors.SURFACE_CONTAINER_LOW),
			ft.Divider(height=1, thickness=1),
			section_content,
		],
		expand=True,
		spacing=0,
	)
	render()
	return root