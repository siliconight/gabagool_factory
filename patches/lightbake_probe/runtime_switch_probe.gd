extends SceneTree
## A baked package as shipped, through Lux 0.66.0's own calls: is the
## lightmap bound at load, does `LuxRuntimeAPI.baked_lighting(false)` give
## the real-time picture and back, and does the power cut go dark and
## recover? Three stations, luminance and draws each.
##     godot --path <baked walk copy> --script runtime_switch_probe.gd


const SHOTS: Array = [
	["above", Vector3(0.0, 40.0, 40.0), Vector3(0.0, 0.0, -5.0)],
	["station_front", Vector3(-59.0, 1.7, 14.0), Vector3(-59.0, 1.0, -5.0)],
	["street", Vector3(0.0, 1.7, 26.0), Vector3(30.0, 1.0, 21.0)],
]


func _initialize() -> void:
	_run.call_deferred()


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _hide_canvas(n: Node) -> void:
	if n is CanvasLayer and not String(n.name).contains("Lux"):
		(n as CanvasLayer).visible = false
	for c: Node in n.get_children():
		_hide_canvas(c)


func _lum(img: Image) -> float:
	var s: float = 0.0
	var n: int = 0
	for y in range(0, img.get_height(), 4):
		for x in range(0, img.get_width(), 4):
			s += img.get_pixel(x, y).get_luminance()
			n += 1
	return s / float(n)


func _read(cam: Camera3D, tag: String) -> void:
	var row: Array = []
	for s in SHOTS:
		cam.look_at_from_position(s[1], s[2], Vector3.UP)
		for _i in range(20):
			await process_frame
		var img: Image = root.get_viewport().get_texture().get_image()
		row.append("%s %.4f/%d" % [String(s[0]), _lum(img),
			int(RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME))])
	print("SWITCH %-18s %s" % [tag, "  ".join(PackedStringArray(row))])


func _run() -> void:
	change_scene_to_file("res://_walk.tscn")
	for _i in range(30):
		await process_frame
	var steady: int = 0
	while steady < 30:
		await process_frame
		steady = steady + 1 if is_equal_approx(root.get_viewport().scaling_3d_scale, 1.0) else 0
	_hide_canvas(root)
	var lux: Node = LuxRuntimeAPI.get_root(self)
	print("SWITCH lux root %s, baked lighting at load: %s" % [str(lux != null), str(lux.baked_lighting() if lux != null else "-")])
	var cam := Camera3D.new()
	cam.fov = 70.0
	root.add_child(cam)
	cam.make_current()
	await _read(cam, "baked")
	LuxRuntimeAPI.baked_lighting(self, false)
	await _read(cam, "real time")
	LuxRuntimeAPI.baked_lighting(self, true)
	await _read(cam, "baked again")
	LuxRuntimeAPI.fixtures_powered(self, false)
	await _read(cam, "power cut")
	LuxRuntimeAPI.fixtures_powered(self, true)
	await _read(cam, "power back")
	print("SWITCH baked lighting at the end: %s" % str(lux.baked_lighting()))
	_exit(0)
