extends SceneTree
## Shoots each parking field from the street and from above, and each
## dumpster's pad from in front, with a plain fill so the night level
## reads, into the folder after `--`. Written by make_shots.py.
##     godot --path <walk copy> --script dumpster_shots.gd -- <out dir>

## [name, eye (Godot), target (Godot)]; plan (x, y) is Godot (x, -y)
const SHOTS: Array = [
	["field_0_street", Vector3(-80.25, 1.70, 30.15), Vector3(-80.25, 0.60, 16.05)],
	["field_0_above", Vector3(-80.25, 14.00, 33.15), Vector3(-80.25, 0.00, 16.05)],
	["field_1_street", Vector3(29.50, 1.70, 30.15), Vector3(29.50, 0.60, 16.05)],
	["field_1_above", Vector3(29.50, 14.00, 33.15), Vector3(29.50, 0.00, 16.05)],
	["field_2_street", Vector3(-34.50, 1.70, -29.25), Vector3(-48.60, 0.60, -29.25)],
	["field_2_above", Vector3(-31.50, 14.00, -29.25), Vector3(-48.60, 0.00, -29.25)],
	["pad_0_b0", Vector3(-82.00, 2.20, -16.32), Vector3(-73.00, 0.40, -16.32)],
	["pad_1_b1", Vector3(13.32, 2.20, -44.00), Vector3(13.32, 0.40, -35.00)],
	["pad_2_b2", Vector3(78.32, 2.20, -36.00), Vector3(78.32, 0.40, -27.00)],
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
