extends SceneTree
## Scratch, in the Lux project: a shaft, head and lens like Zoo's pole, a
## shadowed spot; the ground 9 m off over cull modes and lamp heights.


func _initialize() -> void:
	_main.call_deferred()


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


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


func _box(parent: Node, size: Vector3, at: Vector3, mat: Material) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = size
	mi.mesh = bm
	mi.material_override = mat
	parent.add_child(mi)
	mi.position = at
	return mi


func _main() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color.BLACK
	e.ambient_light_source = Environment.AMBIENT_SOURCE_DISABLED
	env.environment = e
	world.add_child(env)
	var grey := StandardMaterial3D.new()
	grey.albedo_color = Color(0.6, 0.6, 0.6)
	var body := StandardMaterial3D.new()
	body.albedo_color = Color(0.3, 0.3, 0.3)
	var ground := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(40.0, 40.0)
	ground.mesh = pm
	ground.material_override = grey
	world.add_child(ground)
	var mount: float = 6.0
	var shaft := MeshInstance3D.new()
	var cm := CylinderMesh.new()
	cm.top_radius = 0.06
	cm.bottom_radius = 0.06
	cm.height = mount
	cm.radial_segments = 8
	shaft.mesh = cm
	shaft.material_override = body
	world.add_child(shaft)
	shaft.position = Vector3(0.0, mount * 0.5, 0.0)
	var head := _box(world, Vector3(0.7, 0.16, 0.3), Vector3(0.0, mount + 0.02 + 0.08, 0.0), body)
	var lens := _box(world, Vector3(0.56, 0.02, 0.225), Vector3(0.0, mount + 0.015, 0.0), grey)
	var cam := Camera3D.new()
	cam.fov = 60.0
	world.add_child(cam)
	cam.make_current()
	cam.look_at_from_position(Vector3(9.0, 1.6, 0.0), Vector3(0.0, 0.3, 0.0), Vector3.UP)
	var sp := SpotLight3D.new()
	sp.spot_range = 14.0
	sp.spot_angle = 55.0
	sp.light_energy = 19.2
	sp.spot_angle_attenuation = 1.2
	sp.shadow_enabled = true
	sp.shadow_bias = 0.03
	sp.shadow_normal_bias = 1.0
	world.add_child(sp)
	sp.rotation_degrees = Vector3(-90.0, 0.0, 0.0)
	print("SWEEP renderer %s" % RenderingServer.get_current_rendering_method())
	for cull in [BaseMaterial3D.CULL_BACK, BaseMaterial3D.CULL_DISABLED]:
		body.cull_mode = cull
		for dy in [0.005, 0.0, -0.02, -0.05, -0.10]:
			sp.position = Vector3(0.0, mount + float(dy), 0.0)
			var v: float = await _read()
			print("SWEEP body cull %-8s lamp %+.3f from the cap  ground=%.3f" % ["BACK" if cull == BaseMaterial3D.CULL_BACK else "DISABLED", float(dy), v])
	body.cull_mode = BaseMaterial3D.CULL_BACK
	sp.position = Vector3(0.0, mount + 0.005, 0.0)
	head.visible = false
	print("SWEEP head hidden, lamp +0.005, cull BACK  ground=%.3f" % (await _read()))
	head.visible = true
	lens.visible = false
	print("SWEEP lens hidden, lamp +0.005, cull BACK  ground=%.3f" % (await _read()))
	lens.visible = true
	shaft.visible = false
	print("SWEEP shaft hidden, lamp +0.005, cull BACK  ground=%.3f" % (await _read()))
	shaft.visible = true
	sp.shadow_enabled = false
	print("SWEEP no shadow  ground=%.3f" % (await _read()))
	print("SWEEP done")
	_exit(0)
