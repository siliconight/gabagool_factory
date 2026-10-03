extends SceneTree
## Scratch probe: do the crowns sway in a shipped level, and are they
## invisible at rest? Loads a walk copy as it is, finds every crown node,
## says what material each wears, stands a camera at the first tree against
## the sky, shoots it with the wind set to ZERO (the rest frame, compared by
## hand against the previous build's same frame), then with the project's
## wind: three frames half a second apart and the pixel difference between
## them, plus the same with the wind at zero as the control. Windowed,
## drives itself, quits itself. Prints what it measured and stops.
##
##   godot --path <walk copy> --script _wind_probe.gd -- <out dir>

const GAP_S: float = 0.5


func _initialize() -> void:
	_run.call_deferred()


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _crowns(n: Node, out: Array) -> void:
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi != null and mi.mesh != null and String(mi.name).begins_with("StreetTree_Crown"):
		out.append(mi)
	for c: Node in n.get_children():
		_crowns(c, out)


func _hide_canvas(n: Node) -> void:
	if n is CanvasLayer and not String(n.name).contains("Lux"):
		(n as CanvasLayer).visible = false
	for c: Node in n.get_children():
		_hide_canvas(c)


func _diff(a: Image, b: Image) -> Array:
	var w: int = mini(a.get_width(), b.get_width())
	var h: int = mini(a.get_height(), b.get_height())
	var total: float = 0.0
	var moved: int = 0
	for y in range(0, h, 2):
		for x in range(0, w, 2):
			var p: Color = a.get_pixel(x, y)
			var q: Color = b.get_pixel(x, y)
			var d: float = (absf(p.r - q.r) + absf(p.g - q.g) + absf(p.b - q.b)) / 3.0 * 255.0
			total += d
			if d > 8.0:
				moved += 1
	var n: int = (w / 2) * (h / 2)
	return [total / float(n), moved, n]


func _shoot3(out: String, label: String) -> void:
	for _i in range(10):
		await process_frame
	var frames: Array = []
	for k in range(3):
		var t0: float = Time.get_ticks_msec() / 1000.0
		while Time.get_ticks_msec() / 1000.0 - t0 < (GAP_S if k > 0 else 0.0):
			await process_frame
		var img: Image = root.get_viewport().get_texture().get_image()
		img.save_png("%s/%s_%d.png" % [out, label, k])
		frames.append(img)
	var d01: Array = _diff(frames[0], frames[1])
	var d12: Array = _diff(frames[1], frames[2])
	print("WIND %s: frame0->1 mean=%.2f moved=%d/%d  frame1->2 mean=%.2f moved=%d/%d"
		% [label, float(d01[0]), int(d01[1]), int(d01[2]), float(d12[0]), int(d12[1]), int(d12[2])])


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var out: String = args[0] if args.size() > 0 else "C:/Projects/gabagool_studios/gabagool_factory/docs/findings/wind"
	DirAccess.make_dir_recursive_absolute(out)
	change_scene_to_file("res://_walk.tscn")
	for _i in range(30):
		await process_frame
	var steady: int = 0
	var waited: int = 0
	while steady < 30 and waited < 6000:
		await process_frame
		waited += 1
		steady = steady + 1 if is_equal_approx(root.get_viewport().scaling_3d_scale, 1.0) else 0
	print("WIND warm-up waited ", waited, " frames")
	if steady < 30:
		print("WIND CANNOT SHOOT: the warm-up never finished")
		_exit(2)
		return
	_hide_canvas(root)
	var wind: Variant = ProjectSettings.get_setting("shader_globals/lf_wind", null)
	print("WIND project lf_wind=", wind)
	var crowns: Array = []
	_crowns(root, crowns)
	crowns.sort_custom(func(a, b): return String(a.get_path()) < String(b.get_path()))
	var shader_count: int = 0
	for mi in crowns:
		var m: Material = mi.get_active_material(0)
		if m is ShaderMaterial:
			shader_count += 1
	print("WIND crowns=", crowns.size(), " wearing the sway shader=", shader_count)
	if crowns.is_empty():
		print("WIND CANNOT SHOOT: no crown")
		_exit(2)
		return
	var tree: MeshInstance3D = crowns[0]
	var box: AABB = tree.global_transform * tree.get_aabb()
	var mid: Vector3 = box.get_center()
	print("WIND first crown ", tree.get_path(), " centre=", mid, " size=", box.size)
	var cam: Camera3D = Camera3D.new()
	cam.fov = 55.0
	root.add_child(cam)
	cam.make_current()
	# from the road side, low, the crown against the sky: 9 m off along -z
	cam.look_at_from_position(mid + Vector3(2.0, -2.2, 9.0), mid + Vector3(0.0, 0.3, 0.0), Vector3.UP)
	# the rest frame: wind zero, then a second zero frame as the control
	RenderingServer.global_shader_parameter_set("lf_wind", Vector3.ZERO)
	await _shoot3(out, "crown_calm")
	# the project's wind
	var v: Vector3 = Vector3(1.5, 0.0, 0.0)
	if wind is Dictionary and (wind as Dictionary).has("value"):
		v = (wind as Dictionary)["value"]
	RenderingServer.global_shader_parameter_set("lf_wind", v)
	print("WIND set lf_wind=", v)
	await _shoot3(out, "crown_wind")
	# a storm, to see the lean at its cap
	RenderingServer.global_shader_parameter_set("lf_wind", Vector3(9.0, 0.0, 0.0))
	await _shoot3(out, "crown_storm")
	RenderingServer.global_shader_parameter_set("lf_wind", v)
	var draws: int = int(RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME))
	print("WIND draws at this view=", draws)
	print("WIND done")
	_exit(0)
