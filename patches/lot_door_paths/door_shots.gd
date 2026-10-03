extends SceneTree
## Shoots the walker's spot at the bank's south face and two raised views of
## the walks, into the folder given after `--`, with the tag given after it.
##     godot --path <walk copy> --script door_shots.gd -- <out dir> <tag>

const SHOTS: Array = [
	["bank_walker", Vector3(54.2, 1.6, 14.3), Vector3(54.2, 1.2, 4.0)],
	["bank_above", Vector3(57.0, 9.0, 17.0), Vector3(55.0, 0.0, 6.0)],
	["station_above", Vector3(-60.0, 10.0, 16.0), Vector3(-61.0, 0.0, 2.0)],
	["between_above", Vector3(-38.0, 22.0, 14.0), Vector3(-38.0, 0.0, -5.0)],
	["walker_between", Vector3(-32.6, 1.7, 14.5), Vector3(-40.0, 0.5, 0.0)],
	["walker_bank_west", Vector3(42.3, 1.6, -26.7), Vector3(43.0, 0.5, -10.0)],
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
	if args.size() < 2:
		print("SHOTS need <out dir> <tag>")
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
		print("SHOTS CANNOT SHOOT")
		_exit(2)
		return
	_hide_canvas(root)
	var cam := Camera3D.new()
	cam.fov = 70.0
	root.add_child(cam)
	cam.make_current()
	# a plain white fill so the ground reads in a night level; the same in both builds
	var fill := DirectionalLight3D.new()
	fill.light_energy = 0.6
	root.add_child(fill)
	fill.rotation_degrees = Vector3(-60.0, 30.0, 0.0)
	for s in SHOTS:
		cam.look_at_from_position(s[1], s[2], Vector3.UP)
		for _i in range(12):
			await process_frame
		var path: String = "%s/%s_%s.png" % [args[0], String(s[0]), args[1]]
		root.get_viewport().get_texture().get_image().save_png(path)
		print("SHOTS wrote ", path)
	print("SHOTS done")
	_exit(0)
