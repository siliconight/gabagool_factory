extends SceneTree
## Can a game read a drawing shipped with Godot's "keep" import -- the file as it is, no texture made -- and draw it?
## Reads res://b.svg as text, rasterises it with Image.load_svg_from_string, and asks whether res://a.svg (imported
## the default way) loads as a resource and whether res://b.svg does. Prints measurements only, then exits.


func _initialize() -> void:
	var text: String = FileAccess.get_file_as_string("res://b.svg")
	var img: Image = Image.new()
	var err: int = img.load_svg_from_string(text, 1.0)
	print("KEEP_PROBE b_text_chars=%d load_err=%d image=%dx%d" % [text.length(), err, img.get_width(), img.get_height()])
	print("KEEP_PROBE a_loads_as_resource=%s" % [load("res://a.svg") != null])
	print("KEEP_PROBE b_exists_as_resource=%s" % [ResourceLoader.exists("res://b.svg")])
	_exit(0)


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())
