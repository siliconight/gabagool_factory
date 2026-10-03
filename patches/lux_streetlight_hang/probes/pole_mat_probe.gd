extends SceneTree
## Scratch: the pole mesh's materials and surfaces in the walk; and a sweep
## of the pole's own shadowed lamp over heights, with the pole's body mesh
## cull mode as shipped and then disabled. Every other light off.

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


func _shot(label: String) -> void:
	for _i in range(8):
		await process_frame
	print("MAT %-56s ground=%.3f" % [label, _band(root.get_viewport().get_texture().get_image())])


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
		print("MAT CANNOT SHOOT")
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
	var body: MeshInstance3D = null
	for mi in meshes:
		var p: String = String(mi.get_path())
		if p.contains("cover_21/"):
			var m: Mesh = mi.mesh
			for si in range(m.get_surface_count()):
				var mat: Material = mi.get_active_material(si)
				var bm: BaseMaterial3D = mat as BaseMaterial3D
				var arr: Array = m.surface_get_arrays(si)
				var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
				var top_y: float = -1e9
				var near_cap: int = 0
				for v in verts:
					var wy: float = (mi.global_transform * v).y
					top_y = maxf(top_y, wy)
					if absf(wy - o.y) < 0.12:
						near_cap += 1
				print("MAT %s surface %d mat=%s class=%s cull=%s transparency=%s verts=%d top_y=%.3f verts within 12 cm of the lamp=%d" % [
					p.replace("/root/_walk/Mission/Site/", ""), si, mat.resource_name if mat != null else "-",
					mat.get_class() if mat != null else "-", str(bm.cull_mode) if bm != null else (str((mat as ShaderMaterial).shader.resource_path) if mat is ShaderMaterial else "-"),
					str(bm.transparency) if bm != null else "-", verts.size(), top_y, near_cap])
			if p.ends_with("Streetlight_metal_delco_1997"):
				body = mi
	var cam := Camera3D.new()
	cam.fov = 60.0
	root.add_child(cam)
	cam.make_current()
	var foot: Vector3 = Vector3(o.x, 0.0, o.z)
	cam.look_at_from_position(foot + Vector3(9.0, 1.6, 0.0), foot + Vector3(0.0, 0.3, 0.0), Vector3.UP)
	lamp.visible = true
	lamp.shadow_enabled = true
	var xf: Transform3D = lamp.global_transform
	for dy in [0.0, 0.02, 0.05, -0.02, -0.05, -0.10]:
		lamp.global_transform = xf
		lamp.global_position = o + Vector3(0.0, float(dy), 0.0)
		await _shot("shipped body, lamp %+.2f m" % float(dy))
	lamp.global_transform = xf
	var bmat: BaseMaterial3D = body.get_active_material(0) as BaseMaterial3D
	if bmat != null:
		var was: int = bmat.cull_mode
		bmat.cull_mode = BaseMaterial3D.CULL_BACK
		await _shot("body cull BACK, lamp at origin")
		bmat.cull_mode = BaseMaterial3D.CULL_FRONT
		await _shot("body cull FRONT, lamp at origin")
		bmat.cull_mode = BaseMaterial3D.CULL_DISABLED
		await _shot("body cull DISABLED, lamp at origin")
		bmat.cull_mode = was
	body.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY
	await _shot("body shadows-only")
	body.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_DOUBLE_SIDED
	await _shot("body cast double-sided")
	body.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	print("MAT done")
	_exit(0)
