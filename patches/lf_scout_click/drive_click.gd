extends SceneTree
# Clicking a building's row: through `click` (a handheld's path) and as a real mouse click on the overlay.

var w: Node


func _initialize() -> void:
	w = load("res://scout/scout_window.gd").new()
	w.set("package_root", "res://pkg")
	root.add_child(w)
	_run.call_deferred()


func _row_centre(i: int) -> Vector2:
	var rows: Array = w.get("_rows")
	return (rows[i]["node"] as Control).get_global_rect().get_center()


func _run() -> void:
	w.connect("building_selected", func(id: String) -> void: print("selected ", id))
	w.call("open", true)
	for f in range(10):
		await process_frame
	print("click row 2 via click(): hit ", w.call("click", _row_centre(2)))
	for f in range(5):
		await process_frame
	print("click empty screen via click(): hit ", w.call("click", Vector2(700, 300)))
	# the overlay: the screen's pixel mapped to the game window, pressed as a real mouse button
	var shown: TextureRect = w.get("_shown")
	var r: Rect2 = shown.get_global_rect()
	var at: Vector2 = r.position + _row_centre(1) * r.size / Vector2(w.get("screen_size"))
	var e := InputEventMouseButton.new()
	e.button_index = MOUSE_BUTTON_LEFT
	e.pressed = true
	e.position = at
	e.global_position = at
	Input.parse_input_event(e)
	for f in range(5):
		await process_frame
	print("dragging after the row click: ", w.get("_dragging"))
	quit(0)
