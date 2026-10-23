extends SceneTree
# What a floor hole shows: deli_a03's open-to-below hole (storey 1, spec x 7.4..9.6, y -5.1..-2.9, over the kitchen),
# photographed in a walk copy from above it and from the kitchen under it, after the level's warm-up. Prints the
# building's transform and the cameras' world positions; saves frames; quits.
# Args after --: <out prefix> <building node name, e.g. b0>
# Frame: spec metres (x east, y north, z up) map to the building's local Godot frame as (x, z, -y).

var prefix: String
var node_name: String


func _initialize() -> void:
	var a: PackedStringArray = OS.get_cmdline_user_args()
	prefix = a[0]
	node_name = a[1]
	change_scene_to_file("res://_walk.tscn")
	_run.call_deferred()


func _find(n: Node, want: String) -> Node:
	if n.name == want:
		return n
	for c in n.get_children():
		var hit: Node = _find(c, want)
		if hit != null:
			return hit
	return null


func _find_warmup(n: Node) -> Node:
	if n.has_signal("warmup_finished"):
		return n
	for c in n.get_children():
		var hit: Node = _find_warmup(c)
		if hit != null:
			return hit
	return null


func _spec(gt: Transform3D, x: float, y: float, z: float) -> Vector3:
	return gt * Vector3(x, z, -y)


func _shot(cam: Camera3D, at: Vector3, look: Vector3, tag: String) -> void:
	cam.global_position = at
	cam.look_at(look, Vector3.UP if absf((look - at).normalized().y) < 0.99 else Vector3.FORWARD)
	cam.make_current()
	for f in range(30):
		await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("%s_%s.png" % [prefix, tag])
	print("%s: camera at %s looking at %s" % [tag, str(at), str(look)])


func _run() -> void:
	var started: int = Time.get_ticks_msec()
	var warm: Node = null
	while warm == null and Time.get_ticks_msec() - started < 20000:
		await process_frame
		warm = _find_warmup(root)
	if warm != null:
		var done := [false]
		warm.connect("warmup_finished", func(_f: int, _ms: float) -> void: done[0] = true)
		while not done[0] and Time.get_ticks_msec() - started < 150000:
			await process_frame
	var b: Node3D = _find(root, node_name) as Node3D
	if b == null:
		print("no node ", node_name)
		quit(1)
		return
	var gt: Transform3D = b.global_transform
	print("building %s at %s, basis x %s z %s" % [node_name, str(gt.origin), str(gt.basis.x), str(gt.basis.z)])
	var cam := Camera3D.new()
	cam.fov = 70.0
	current_scene.add_child(cam)
	if OS.get_cmdline_user_args().size() > 2 and OS.get_cmdline_user_args()[2] == "stairwell":
		# the ground floor's stair opening down to the basement (storey 0, spec x -17..-14.6, y 6.2..11.3): from its
		# south edge looking down, then from the basement under it looking up, then straight down
		await _shot(cam, _spec(gt, -15.8, 5.0, 1.65), _spec(gt, -15.8, 8.7, -3.3), "sw_above")
		await _shot(cam, _spec(gt, -12.0, 4.0, -3.3 + 1.65), _spec(gt, -15.8, 8.7, -3.3), "sw_basement")
		await _shot(cam, _spec(gt, -15.8, 8.7, 1.0), _spec(gt, -15.8, 8.7, -3.3), "sw_down")
		quit(0)
		return
	# from storey 1, standing at the hole's south edge, eye height, looking down into it
	await _shot(cam, _spec(gt, 8.5, -6.4, 3.3 + 1.65), _spec(gt, 8.5, -4.0, 0.0), "above")
	# from the kitchen, under the hole's south-east, looking at the floor beneath it
	await _shot(cam, _spec(gt, 12.0, -7.5, 1.65), _spec(gt, 8.5, -4.0, 0.0), "kitchen")
	# straight down through the hole from a metre over it
	await _shot(cam, _spec(gt, 8.5, -4.0, 3.3 + 1.0), _spec(gt, 8.5, -4.0, 0.0), "down")
	quit(0)
