extends SceneTree
## Scratch probe: what sits between a shadowed pole's lamp and the ground?
## Lists every mesh whose world box holds site_lamp_21's light origin or
## crosses the cone just under it; then hides each candidate in turn with the
## pole's shadow on and prints the ground under the pole. Every other light
## off. Prints what it measured.

const POLE_NAME: String = "site_lamp_21"


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
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi != null and mi.mesh != null:
		meshes.append(mi)
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


func _shot(label: String) -> float:
	for _i in range(8):
		await process_frame
	var v: float = _band(root.get_viewport().get_texture().get_image())
	print("OCC %-60s ground=%.3f" % [label, v])
	return v


func _run() -> void:
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
		print("OCC CANNOT SHOOT")
		_exit(2)
		return
	_hide_canvas(root)
	var lights: Array = []
	var meshes: Array = []
	_walk(root, lights, meshes)
	var lamp: SpotLight3D = null
	for l in lights:
		if l is SpotLight3D and String(l.get_parent().name) == POLE_NAME:
			lamp = l
		l.visible = false
	var o: Vector3 = lamp.global_position
	print("OCC lamp origin %s shadow=%s bias=%.3f normal_bias=%.2f size=%.3f" % [str(o), str(lamp.shadow_enabled), lamp.shadow_bias, lamp.shadow_normal_bias, lamp.light_size])
	# candidates: boxes that hold the origin, or whose top is within 1.5 m under it and within 2 m sideways
	var cands: Array = []
	for mi in meshes:
		var box: AABB = mi.global_transform * mi.get_aabb()
		var holds: bool = box.has_point(o)
		var under: bool = box.end.y <= o.y + 0.05 and box.end.y >= o.y - 1.5 \
			and abs(box.get_center().x - o.x) < 2.0 + box.size.x * 0.5 and abs(box.get_center().z - o.z) < 2.0 + box.size.z * 0.5 \
			and box.size.x < 6.0 and box.size.z < 6.0
		if holds or under:
			cands.append(mi)
			print("OCC   %s %s box y %.3f..%.3f  x %.2f..%.2f z %.2f..%.2f cast_shadow=%d mat=%s" % [
				"HOLDS" if holds else "under", String(mi.get_path()).replace("/root/_walk/Mission/", "").left(80),
				box.position.y, box.end.y, box.position.x, box.end.x, box.position.z, box.end.z, mi.cast_shadow,
				mi.get_active_material(0).resource_name if mi.get_active_material(0) != null else "-"])
	var cam := Camera3D.new()
	cam.fov = 60.0
	root.add_child(cam)
	cam.make_current()
	var foot: Vector3 = Vector3(o.x, 0.0, o.z)
	cam.look_at_from_position(foot + Vector3(9.0, 1.6, 0.0), foot + Vector3(0.0, 0.3, 0.0), Vector3.UP)
	lamp.visible = true
	lamp.shadow_enabled = true
	await _shot("pole, shadow on, everything visible")
	for mi in cands:
		mi.visible = false
		await _shot("hidden: " + String(mi.get_path()).replace("/root/_walk/Mission/", "").left(50))
		mi.visible = true
	for mi in cands:
		mi.visible = false
	await _shot("all candidates hidden")
	for mi in cands:
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		mi.visible = true
	await _shot("all candidates visible, cast_shadow off")
	# raise the light origin in 2 cm steps below / above: where does the cone clear?
	for mi in cands:
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	var xf: Transform3D = lamp.global_transform
	for dy in [-0.05, -0.10, -0.15, -0.20, -0.30, -0.45]:
		lamp.global_transform = xf
		lamp.global_position = o + Vector3(0.0, float(dy), 0.0)
		await _shot("lamp lowered %.2f m" % -float(dy))
	lamp.global_transform = xf
	print("OCC done")
	_exit(0)
