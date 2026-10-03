extends SceneTree
## Does switching a baked level's lightmap off at runtime hand its static
## lights back to real time? Three stations, read with the lightmap on, with
## `light_data` cleared, with it restored, and with it cleared plus every
## rig light hidden (the power cut's picture). Prints luminance and draws.
##     godot --path <baked walk copy> --script fallback_probe.gd


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


func _read(cam: Camera3D, tag: String, out_dir: String) -> void:
	var row: Array = []
	for s in SHOTS:
		cam.look_at_from_position(s[1], s[2], Vector3.UP)
		for _i in range(20):
			await process_frame
		var img: Image = root.get_viewport().get_texture().get_image()
		if out_dir != "":
			img.save_png("%s/fallback_%s_%s.png" % [out_dir, String(s[0]), tag])
		row.append("%s %.4f/%d" % [String(s[0]), _lum(img),
			int(RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME))])
	print("FALLBACK %-24s %s" % [tag, "  ".join(PackedStringArray(row))])


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var out_dir: String = args[0] if args.size() > 0 else ""
	change_scene_to_file("res://_walk.tscn")
	for _i in range(30):
		await process_frame
	var steady: int = 0
	var waited: int = 0
	while steady < 30 and waited < 6000:
		await process_frame
		waited += 1
		steady = steady + 1 if is_equal_approx(root.get_viewport().scaling_3d_scale, 1.0) else 0
	_hide_canvas(root)
	var lms: Array = root.find_children("*", "LightmapGI", true, false)
	if lms.is_empty():
		print("FALLBACK no LightmapGI")
		_exit(2)
		return
	var lm: LightmapGI = lms[0]
	var data: LightmapGIData = lm.light_data
	var cam := Camera3D.new()
	cam.fov = 70.0
	root.add_child(cam)
	cam.make_current()
	await _read(cam, "lightmap_on", out_dir)
	lm.light_data = null
	await _read(cam, "light_data_cleared", out_dir)
	lm.light_data = data
	await _read(cam, "light_data_restored", out_dir)
	lm.visible = false
	await _read(cam, "lightmapgi_hidden", out_dir)
	lm.visible = true
	await _read(cam, "lightmapgi_shown", out_dir)
	# the general fallback: the lightmap off AND every static light handed
	# back to real time by its bake mode
	lm.light_data = null
	var flipped: Array = []
	for l in root.find_children("*", "Light3D", true, false):
		if (l as Light3D).light_bake_mode == Light3D.BAKE_STATIC:
			(l as Light3D).light_bake_mode = Light3D.BAKE_DYNAMIC
			flipped.append(l)
	await _read(cam, "cleared_%d_static_to_dynamic" % flipped.size(), out_dir)
	for l in flipped:
		(l as Light3D).visible = false
	await process_frame
	for l in flipped:
		(l as Light3D).visible = true
	await _read(cam, "...and_each_light_re_added", out_dir)
	var holders: Array = []
	for g in root.find_children("*", "GeometryInstance3D", true, false):
		if (g as GeometryInstance3D).gi_mode == GeometryInstance3D.GI_MODE_STATIC:
			holders.append(g)
			(g as GeometryInstance3D).gi_mode = GeometryInstance3D.GI_MODE_DYNAMIC
	await _read(cam, "...and_%d_meshes_gi_dynamic" % holders.size(), out_dir)
	for g in holders:
		(g as GeometryInstance3D).gi_mode = GeometryInstance3D.GI_MODE_STATIC
	lm.light_data = data
	for l in flipped:
		(l as Light3D).light_bake_mode = Light3D.BAKE_STATIC
	await _read(cam, "lightmap_back_static_back", out_dir)
	# the power cut: the lightmap off and every registered rig light off
	lm.light_data = null
	var hidden: int = 0
	for l in root.find_children("*", "Light3D", true, false):
		if l is DirectionalLight3D:
			continue
		var p: Node = l.get_parent()
		if p != null and p.get(&"rig") != null:
			(l as Light3D).visible = false
			hidden += 1
	await _read(cam, "cut_%d_lights" % hidden, out_dir)
	print("FALLBACK done")
	_exit(0)
