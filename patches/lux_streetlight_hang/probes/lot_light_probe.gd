extends SceneTree
## Scratch probe: why does a streetlight's pool not show on the lot? From the
## walker's pose, shoot the lot as it is; then with a test omni hung over it
## (can the ground be lit at all?); then with the nearby poles turned up
## fourfold (is it the poles?); and print the lot tiles' layers against the
## lights' cull masks and the tiles' materials. Prints what it measured.

const OUT: String = "C:/Projects/gabagool_studios/gabagool_factory/docs/findings/light_cap/lot"
const POSE := Vector3(-3.0, 1.6, 35.0)
const LOOK := Vector3(14.0, 1.0, 10.0)


func _initialize() -> void:
	_run.call_deferred()


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _walk(n: Node, lights: Array, meshes: Array) -> void:
	if n is OmniLight3D or n is SpotLight3D:
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


func _lum(img: Image, y0f: float, y1f: float) -> float:
	var w: int = img.get_width()
	var h: int = img.get_height()
	var s: float = 0.0
	var n: int = 0
	for y in range(int(h * y0f), int(h * y1f), 2):
		for x in range(0, w, 2):
			s += img.get_pixel(x, y).get_luminance()
			n += 1
	return s / float(n)


func _shoot(label: String) -> Image:
	for _i in range(10):
		await process_frame
	var img: Image = root.get_viewport().get_texture().get_image()
	img.save_png("%s/%s.png" % [OUT, label])
	print("LOT %-14s lower-half luminance=%.4f  draws=%d" % [label, _lum(img, 0.55, 1.0),
		int(RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME))])
	return img


func _run() -> void:
	DirAccess.make_dir_recursive_absolute(OUT)
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
		print("LOT CANNOT SHOOT")
		_exit(2)
		return
	_hide_canvas(root)
	var lights: Array = []
	var meshes: Array = []
	_walk(root, lights, meshes)
	# the lot tiles near the pose, their layers and materials; the poles' masks
	for mi in meshes:
		var path: String = String(mi.get_path())
		if not path.contains("/Ground/mesh_t"):
			continue
		var box: AABB = mi.global_transform * mi.get_aabb()
		if Vector2(box.get_center().x, box.get_center().z).distance_to(Vector2(POSE.x, POSE.z)) > 14.0:
			continue
		var m: Material = mi.get_active_material(0)
		var bm: BaseMaterial3D = m as BaseMaterial3D
		print("LOT tile %s layers=%d cast_shadow=%d gi=%d mat=%s %s rough=%s metal=%s unshaded=%s" % [
			path.replace("/root/_walk/Mission/Site/", ""), mi.layers, mi.cast_shadow, mi.gi_mode,
			m.resource_name if m != null else "none", m.get_class() if m != null else "",
			str(bm.roughness) if bm != null else "-", str(bm.metallic) if bm != null else "-",
			str(bm.shading_mode) if bm != null else "-"])
	var poles: Array = []
	for l in lights:
		var nm: String = String(l.get_parent().name)
		if nm.begins_with("site_lamp") and l.global_position.distance_to(POSE) < 25.0:
			poles.append(l)
			print("LOT pole %s at %s energy=%.1f range=%.1f cull_mask=%d visible=%s class=%s angle=%.0f" % [nm, str(l.global_position),
				l.light_energy, (l as SpotLight3D).spot_range if l is SpotLight3D else (l as OmniLight3D).omni_range,
				l.light_cull_mask, str(l.visible), l.get_class(), (l as SpotLight3D).spot_angle if l is SpotLight3D else -1.0])
	var cam := Camera3D.new()
	cam.fov = 70.0
	root.add_child(cam)
	cam.make_current()
	cam.look_at_from_position(POSE, LOOK, Vector3.UP)
	await _shoot("as_is")
	# a test omni over the lot
	var test := OmniLight3D.new()
	test.omni_range = 15.0
	test.light_energy = 8.0
	test.light_color = Color(1.0, 0.8, 0.5)
	root.add_child(test)
	test.global_position = Vector3(2.0, 6.0, 24.0)
	await _shoot("test_omni")
	test.queue_free()
	await process_frame
	# the poles turned up fourfold
	var base: Array = []
	for l in poles:
		base.append(l.light_energy)
		l.light_energy *= 4.0
	await _shoot("poles_x4")
	for i in range(poles.size()):
		(poles[i] as Light3D).light_energy = float(base[i])
	# and a test SPOT where a pole is, pointing down, to tell spot from omni
	if not poles.is_empty():
		var p: Light3D = poles[0]
		var ts := SpotLight3D.new()
		ts.spot_range = 14.0
		ts.spot_angle = 55.0
		ts.light_energy = 19.0
		root.add_child(ts)
		ts.global_transform = p.global_transform
		p.visible = false
		await _shoot("test_spot_at_pole")
		p.visible = true
		ts.queue_free()
	# how many of each kind are in the scene
	var n_spot: int = 0
	var n_omni: int = 0
	for l in lights:
		if l is SpotLight3D:
			n_spot += 1
		elif l is OmniLight3D:
			n_omni += 1
	print("LOT scene lights: spot=%d omni=%d total=%d max_renderable=%s" % [n_spot, n_omni, lights.size(),
		str(ProjectSettings.get_setting("rendering/limits/opengl/max_renderable_lights", "default"))])
	# a test SPOT near the camera, pointing down (3 m ahead): does a spot light anything at all?
	var near := SpotLight3D.new()
	near.spot_range = 14.0
	near.spot_angle = 55.0
	near.light_energy = 19.0
	root.add_child(near)
	near.global_position = POSE + Vector3(3.0, 4.0, -3.0)
	near.rotation_degrees = Vector3(-90.0, 0.0, 0.0)
	await _shoot("test_spot_near")
	near.queue_free()
	await process_frame
	# a test OMNI exactly where a pole's lamp is
	if not poles.is_empty():
		var p: Light3D = poles[0]
		var to := OmniLight3D.new()
		to.omni_range = 14.0
		to.light_energy = 19.0
		root.add_child(to)
		to.global_position = p.global_position
		await _shoot("test_omni_at_pole")
		to.queue_free()
		await process_frame
	# every other spot light in the scene switched off: does the pole's own spot come back?
	var off: Array = []
	for l in lights:
		if l is SpotLight3D and not String(l.get_parent().name).begins_with("site_lamp") and l.visible:
			l.visible = false
			off.append(l)
	await _shoot("only_pole_spots")
	for l in off:
		l.visible = true
	print("LOT switched off %d non-pole spots for that frame" % off.size())
	print("LOT done")
	_exit(0)
