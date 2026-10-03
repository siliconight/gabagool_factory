extends SceneTree
## Which mesh darkens one pole's shadowed pool? Every other light off, the
## pole's lamp shadowed, a camera 9 m from its foot: the ground's luminance
## with the lamp unshadowed is the target; then every mesh except the ground
## under the pool is hidden, and halves of them are shown back until the one
## mesh that pulls the reading down is found. Prints each step's reading and
## the culprit's path, box and material.
##     godot --path <walk copy> --script bisect_probe.gd -- <rig name>


func _initialize() -> void:
	_run.call_deferred()


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _walk(n: Node, lights: Array, meshes: Array) -> void:
	if n is Light3D:
		lights.append(n)
	if n is GeometryInstance3D:
		meshes.append(n)
	for c in n.get_children():
		_walk(c, lights, meshes)


func _hide_canvas(n: Node) -> void:
	if n is CanvasLayer and not String(n.name).contains("Lux"):
		(n as CanvasLayer).visible = false
	for c: Node in n.get_children():
		_hide_canvas(c)


func _band(img: Image) -> float:
	var w: int = img.get_width()
	var h: int = img.get_height()
	var s: float = 0.0
	var n: int = 0
	for y in range(int(h * 0.50), int(h * 0.70), 2):
		for x in range(int(w * 0.3), int(w * 0.7), 2):
			s += img.get_pixel(x, y).get_luminance()
			n += 1
	return s / float(n)


func _read() -> float:
	for _i in range(8):
		await process_frame
	return _band(root.get_viewport().get_texture().get_image())


func _show(set: Array, on: bool) -> void:
	for g in set:
		(g as GeometryInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if on \
			else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var pole: String = args[0] if args.size() > 0 else "site_lamp_30"
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
	var lights: Array = []
	var meshes: Array = []
	_walk(root, lights, meshes)
	var lamp: SpotLight3D = null
	for l in lights:
		if l is SpotLight3D and String(l.get_parent().name) == pole:
			lamp = l
		l.visible = false
	if lamp == null:
		print("BISECT no pole ", pole)
		_exit(2)
		return
	lamp.visible = true
	lamp.shadow_enabled = true
	var cam := Camera3D.new()
	cam.fov = 60.0
	root.add_child(cam)
	cam.make_current()
	var foot := Vector3(lamp.global_position.x, 0.0, lamp.global_position.z)
	cam.look_at_from_position(foot + Vector3(9.0, 1.6, 0.0), foot + Vector3(0.0, 0.3, 0.0), Vector3.UP)
	var shadowed: float = await _read()
	lamp.shadow_enabled = false
	var free: float = await _read()
	lamp.shadow_enabled = true
	print("BISECT %s lamp at %s: shadowed %.3f, unshadowed %.3f" % [pole, str(lamp.global_position), shadowed, free])
	# Casting is what is bisected, not visibility: the frame keeps every
	# surface it shows, and only the shadow map loses casters.
	var suspects: Array = []
	for g in meshes:
		if (g as GeometryInstance3D).cast_shadow != GeometryInstance3D.SHADOW_CASTING_SETTING_OFF:
			suspects.append(g)
	_show(suspects, false)
	var none: float = await _read()
	print("BISECT %d casters; with none casting: %.3f" % [suspects.size(), none])
	if none < free * 0.8:
		print("BISECT no caster explains it: with nothing casting the pool still reads %.3f against %.3f" % [none, free])
		_show(suspects, true)
		_exit(0)
		return
	var lo: Array = suspects
	var step: int = 0
	while lo.size() > 1 and step < 20:
		step += 1
		var half: Array = lo.slice(0, lo.size() / 2)
		var rest: Array = lo.slice(lo.size() / 2)
		_show(half, true)
		var r: float = await _read()
		_show(half, false)
		print("BISECT step %d: %d casters on -> %.3f" % [step, half.size(), r])
		lo = half if r < free * 0.8 else rest
	var culprit: GeometryInstance3D = lo[0]
	_show([culprit], true)
	var alone: float = await _read()
	var box: AABB = culprit.global_transform * culprit.get_aabb()
	print("BISECT culprit %s (%s) box %s..%s alone casting -> %.3f" % [String(culprit.get_path()), culprit.get_class(),
		str(box.position), str(box.end), alone])
	_show(suspects, true)
	print("BISECT done")
	_exit(0)
