extends SceneTree
## Shoots the whole row along the through road, from above and from the
## far sidewalk, with a plain fill so the night level reads, into the
## folder after `--`. Written by make_street_shots.py.
##     godot --path <walk copy> --script dumpster_shots.gd -- <out dir>

## [name, eye (Godot), target (Godot)]; plan (x, y) is Godot (x, -y)
const SHOTS: Array = [
	["street_above", Vector3(1.50, 55.00, 97.65), Vector3(1.50, 0.00, 7.65)],
	["street_down_the_row", Vector3(-89.00, 1.70, 34.15), Vector3(62.00, 3.00, 15.65)],
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
