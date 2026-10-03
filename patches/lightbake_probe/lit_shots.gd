extends SceneTree
## The bake probe's frames: the level's own lights only (no fill), from the
## walker's spots and a few more, into the folder after `--`, tagged. Also
## prints each frame's draw calls, the mean luminance, and the lightmap the
## scene carries, so a baked and an unbaked build can be compared row by row.
##     godot --path <walk copy> --script lit_shots.gd -- <out dir> <tag>

const SHOTS: Array = [
	["lot_north", Vector3(-32.6, 1.7, -14.5), Vector3(-40.0, 0.5, 0.0)],
	["bank_west", Vector3(32.8, 1.6, 14.9), Vector3(44.0, 1.0, -10.0)],
	["station_front", Vector3(-59.0, 1.7, 14.0), Vector3(-59.0, 1.0, -5.0)],
	["bank_front", Vector3(54.0, 1.7, 20.0), Vector3(53.0, 1.0, 5.0)],
	["street", Vector3(0.0, 1.7, 26.0), Vector3(30.0, 1.0, 21.0)],
	["above", Vector3(0.0, 40.0, 40.0), Vector3(0.0, 0.0, -5.0)],
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


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() < 2:
		print("LIT need <out dir> <tag>")
		_exit(2)
		return
	DirAccess.make_dir_recursive_absolute(args[0])
	change_scene_to_file("res://_walk.tscn")
	for _i in range(30):
		await process_frame
	var steady: int = 0
	var waited: int = 0
	while steady < 30 and waited < 6000:
		await process_frame
		waited += 1
		steady = steady + 1 if is_equal_approx(root.get_viewport().scaling_3d_scale, 1.0) else 0
	if steady < 30:
		print("LIT CANNOT SHOOT")
		_exit(2)
		return
	_hide_canvas(root)
	var lms: Array = root.find_children("*", "LightmapGI", true, false)
	for lm in lms:
		var d: LightmapGIData = (lm as LightmapGI).light_data
		var desc: String = "none"
		if d != null:
			var parts: Array = []
			for t in d.get_lightmap_textures():
				if t != null:
					parts.append("%dx%dx%d" % [t.get_width(), t.get_height(), t.get_layers() if t is TextureLayered else 1])
			desc = "users %d textures %s" % [d.get_user_count(), ", ".join(PackedStringArray(parts))]
		print("LIT lightmap ", lm.name, ": ", desc)
	if lms.is_empty():
		print("LIT lightmap: none in the scene")
	var cam := Camera3D.new()
	cam.fov = 70.0
	root.add_child(cam)
	cam.make_current()
	for s in SHOTS:
		cam.look_at_from_position(s[1], s[2], Vector3.UP)
		for _i in range(20):
			await process_frame
		var img: Image = root.get_viewport().get_texture().get_image()
		img.save_png("%s/%s_%s.png" % [args[0], String(s[0]), args[1]])
		print("LIT %-14s draws %5d  luminance %.4f" % [String(s[0]),
			int(RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME)), _lum(img)])
	print("LIT done")
	_exit(0)
