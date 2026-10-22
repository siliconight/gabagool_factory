extends SceneTree
# Calls LFScoutWindow only through its seam, as a gameplay layer would; saves the screen texture and quits.

var w: Node


func _initialize() -> void:
	w = load("res://scout/scout_window.gd").new()
	w.set("package_root", "res://pkg")
	root.add_child(w)
	_run.call_deferred()


func _snap(tag: String) -> void:
	for f in range(12):
		await process_frame
	await RenderingServer.frame_post_draw
	var tex: ViewportTexture = w.call("get_screen_texture")
	tex.get_image().save_png(OS.get_cmdline_user_args()[0] + "_" + tag + ".png")


func _run() -> void:
	w.connect("building_selected", func(id: String) -> void: print("signal building_selected ", id))
	w.call("open", true)
	print("buildings ", w.call("buildings"), " open ", w.call("is_open"))
	await _snap("first")
	w.call("select", "pharmacy_a01")
	w.call("turn", 200.0)
	await _snap("pharmacy")
	w.call("select", "office")
	w.call("set_spread", 0.0)
	await _snap("office_stacked")
	w.call("set_points", "office", [{"label": "SCORE", "kind": "score", "at": Vector3(3, 8.6, 2), "storey": 2}])
	w.call("set_spread", 1.0)
	await _snap("office_override")
	w.call("close")
	print("closed, open ", w.call("is_open"))
	quit(0)
