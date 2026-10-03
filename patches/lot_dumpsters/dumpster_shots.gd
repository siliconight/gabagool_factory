extends SceneTree
## Shoots each of the walker's lot's dumpsters from in front of it and from
## above, with a plain fill so the night level reads, into the folder after `--`.
##     godot --path <walk copy> --script dumpster_shots.gd -- <out dir>

## [name, eye (Godot), target (Godot)]; plan (x, y) is Godot (x, -y)
const SHOTS: Array = [
	["b0_front", Vector3(-40.5, 1.7, -2.0), Vector3(-47.2, 0.6, -3.5)],
	["b0_above", Vector3(-38.0, 9.0, 4.0), Vector3(-48.0, 0.0, -4.0)],
	["b1_front", Vector3(27.5, 1.7, -28.5), Vector3(24.5, 0.6, -21.8)],
	["b1_above", Vector3(30.0, 10.0, -32.0), Vector3(24.5, 0.0, -20.0)],
	["b2_front", Vector3(81.5, 1.7, -31.5), Vector3(78.5, 0.6, -24.8)],
	["b2_above", Vector3(84.0, 10.0, -35.0), Vector3(78.5, 0.0, -23.0)],
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


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() < 1:
		print("SHOTS need <out dir>")
		_exit(2)
		return
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
		print("SHOTS CANNOT SHOOT")
		_exit(2)
		return
	_hide_canvas(root)
	var cam := Camera3D.new()
	cam.fov = 65.0
	root.add_child(cam)
	cam.make_current()
	var fill := DirectionalLight3D.new()
	fill.light_energy = 0.6
	root.add_child(fill)
	fill.rotation_degrees = Vector3(-55.0, 200.0, 0.0)
	for s in SHOTS:
		cam.look_at_from_position(s[1], s[2], Vector3.UP)
		for _i in range(12):
			await process_frame
		var path: String = "%s/lot_%s.png" % [args[0], String(s[0])]
		root.get_viewport().get_texture().get_image().save_png(path)
		print("SHOTS wrote ", path)
	print("SHOTS done")
	_exit(0)
