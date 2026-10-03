extends SceneTree
## Scratch probe: which dial brings a shadowed SPOT back in this walk? A fresh
## spot on site_lamp_21's transform, every other light off; each line changes
## one thing from the shipped shape and prints the ground under it.

const POLE_NAME: String = "site_lamp_21"


func _initialize() -> void:
	_run.call_deferred()


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _all_lights(n: Node, out: Array) -> void:
	if n is Light3D:
		out.append(n)
	for c in n.get_children():
		_all_lights(c, out)


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
	print("DIAL %-52s ground=%.3f" % [label, _band(root.get_viewport().get_texture().get_image())])


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
		print("DIAL CANNOT SHOOT")
		_exit(2)
		return
	_hide_canvas(root)
	var all: Array = []
	_all_lights(root, all)
	var lamp: SpotLight3D = null
	for l in all:
		if l is SpotLight3D and String(l.get_parent().name) == POLE_NAME:
			lamp = l
		l.visible = false
	var cam := Camera3D.new()
	cam.fov = 60.0
	root.add_child(cam)
	cam.make_current()
	var foot: Vector3 = Vector3(lamp.global_position.x, 0.0, lamp.global_position.z)
	cam.look_at_from_position(foot + Vector3(9.0, 1.6, 0.0), foot + Vector3(0.0, 0.3, 0.0), Vector3.UP)
	var vp: Viewport = root.get_viewport()
	var sp := SpotLight3D.new()
	sp.spot_range = 14.0
	sp.spot_angle = 55.0
	sp.light_energy = 19.2
	sp.spot_angle_attenuation = 1.2
	sp.shadow_enabled = true
	root.add_child(sp)
	sp.global_transform = lamp.global_transform
	await _shot("fresh shadowed spot, shipped shape")
	sp.rotation_degrees = Vector3(-75.0, 0.0, 0.0)
	await _shot("tilted 15 deg")
	sp.global_transform = lamp.global_transform
	sp.spot_angle = 30.0
	await _shot("angle 30")
	sp.spot_angle = 55.0
	sp.spot_range = 8.0
	await _shot("range 8")
	sp.spot_range = 14.0
	sp.shadow_bias = 0.5
	sp.shadow_normal_bias = 5.0
	await _shot("bias 0.5 / normal bias 5")
	sp.shadow_bias = 0.1
	sp.shadow_normal_bias = 2.0
	sp.shadow_reverse_cull_face = true
	await _shot("reverse cull face")
	sp.shadow_reverse_cull_face = false
	sp.shadow_caster_mask = 0
	await _shot("caster mask 0 (nothing casts)")
	sp.shadow_caster_mask = 0xFFFFFFFF
	RenderingServer.viewport_set_positional_shadow_atlas_size(vp.get_viewport_rid(), 4096, false)
	await _shot("24-bit atlas")
	RenderingServer.viewport_set_positional_shadow_atlas_size(vp.get_viewport_rid(), 8192, true)
	await _shot("8192 atlas")
	RenderingServer.viewport_set_positional_shadow_atlas_size(vp.get_viewport_rid(), 4096, true)
	sp.global_position = foot + Vector3(0.0, 3.0, 0.0)
	await _shot("3 m up instead of 5.9")
	sp.global_transform = lamp.global_transform
	sp.global_position = foot + Vector3(4.0, 5.922, 0.0)
	await _shot("moved 4 m toward camera")
	sp.global_transform = lamp.global_transform
	sp.light_cull_mask = 1
	await _shot("cull mask layer 1 only")
	sp.light_cull_mask = 0xFFFFFFFF
	# a shadowed spot, same shape, hung over the camera's own position looking at the foot
	sp.global_position = foot + Vector3(9.0, 5.9, 0.0)
	sp.look_at(foot)
	await _shot("over the camera, aimed at the foot")
	print("DIAL done")
	_exit(0)
