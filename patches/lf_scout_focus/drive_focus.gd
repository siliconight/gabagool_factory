extends SceneTree
# The 0.236.0 window through its seam: focus a floor, tilt, and let it turn itself. Saves frames, quits.

var w: Node


func _initialize() -> void:
	w = load("res://scout/scout_window.gd").new()
	w.set("package_root", "res://pkg")
	root.add_child(w)
	_run.call_deferred()


func _snap(tag: String, frames: int) -> void:
	for f in range(frames):
		await process_frame
	await RenderingServer.frame_post_draw
	(w.call("get_screen_texture") as ViewportTexture).get_image().save_png(OS.get_cmdline_user_args()[0] + "_" + tag + ".png")


func _run() -> void:
	w.call("open", true)
	w.call("select", "deli_a03")
	await _snap("whole", 12)
	w.call("focus", 1)
	print("focused ", w.call("focused"))
	await _snap("floor2", 12)
	w.call("focus", 0)
	w.call("tilt", -20.0)
	await _snap("floor1_low", 12)
	var t0: int = Time.get_ticks_msec()
	await _snap("idle_turned", 300)
	print("idle frames ran for %d ms" % (Time.get_ticks_msec() - t0))
	quit(0)
