extends SceneTree
## Shoots the Empties across the through road, each view with the plain
## fill and without it, into the folder after `--`. Written by
## make_empty_shots.py.
##     godot --path <walk copy> --script dumpster_shots.gd -- <out dir>

## [name, eye (Godot), target (Godot)]; plan (x, y) is Godot (x, -y)
const SHOTS: Array = [
	["empties_across_the_street", Vector3(4.60, 1.70, 21.15), Vector3(4.60, 4.50, 37.65)],
	["empties_down_the_row", Vector3(-95.35, 1.70, 34.15), Vector3(-43.35, 4.00, 38.65)],
	["empties_one_front", Vector3(4.60, 1.70, 31.65), Vector3(4.60, 3.00, 37.65)],
	["empties_from_above", Vector3(4.60, 30.00, 2.65), Vector3(4.60, 0.00, 43.80)],
	["empties_roofs", Vector3(19.60, 22.00, 69.95), Vector3(4.60, 8.00, 37.65)],
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
	for lit in [true, false]:
		fill.visible = lit
		for s in SHOTS:
			cam.look_at_from_position(s[1], s[2], Vector3.UP)
			for _i in range(12):
				await process_frame
			var tag: String = "fill" if lit else "night"
			var path: String = "%s/%s_%s.png" % [args[0], String(s[0]), tag]
			root.get_viewport().get_texture().get_image().save_png(path)
			print("SHOTS wrote ", path)
	print("SHOTS done")
	_exit(0)
