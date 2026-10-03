extends SceneTree
## Scratch probe: does a positional light with shadow_enabled render at all in
## this walk? One dead pole (site_lamp_21): its shadow state at runtime, the
## ground under it with its shadow toggled; then a fresh spot on its transform
## with shadow on and off; and the viewport's shadow atlas. Prints what it saw.

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
	print("SHADOW %-52s ground=%.3f" % [label, _band(root.get_viewport().get_texture().get_image())])


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
		print("SHADOW CANNOT SHOOT")
		_exit(2)
		return
	_hide_canvas(root)
	var vp: Viewport = root.get_viewport()
	print("SHADOW viewport atlas size=%d quadrants=%d/%d/%d/%d  project atlas_size=%s 16_bits=%s" % [
		vp.positional_shadow_atlas_size, vp.positional_shadow_atlas_quad_0, vp.positional_shadow_atlas_quad_1,
		vp.positional_shadow_atlas_quad_2, vp.positional_shadow_atlas_quad_3,
		str(ProjectSettings.get_setting("rendering/lights_and_shadows/positional_shadow/atlas_size", "default")),
		str(ProjectSettings.get_setting("rendering/lights_and_shadows/positional_shadow/atlas_16_bits", "default"))])
	var all: Array = []
	_all_lights(root, all)
	var shadowed: Array = []
	var lamp: SpotLight3D = null
	for l in all:
		if (l as Light3D).shadow_enabled:
			shadowed.append(String(l.get_parent().name) + "/" + String(l.name))
		if l is SpotLight3D and String(l.get_parent().name) == POLE_NAME:
			lamp = l
		l.visible = false
	print("SHADOW lights with shadow_enabled at runtime: %d %s" % [shadowed.size(), str(shadowed)])
	if lamp == null:
		print("SHADOW no pole")
		_exit(2)
		return
	var cam := Camera3D.new()
	cam.fov = 60.0
	root.add_child(cam)
	cam.make_current()
	var foot: Vector3 = Vector3(lamp.global_position.x, 0.0, lamp.global_position.z)
	cam.look_at_from_position(foot + Vector3(9.0, 1.6, 0.0), foot + Vector3(0.0, 0.3, 0.0), Vector3.UP)
	lamp.visible = true
	print("SHADOW pole shadow_enabled at runtime=%s" % str(lamp.shadow_enabled))
	await _shot("pole as is (shadow=%s)" % str(lamp.shadow_enabled))
	lamp.shadow_enabled = false
	await _shot("pole shadow set false")
	lamp.shadow_enabled = true
	await _shot("pole shadow set true")
	RenderingServer.light_set_shadow(lamp.get_base(), false)
	await _shot("pole server light_set_shadow false")
	lamp.visible = false
	var fresh := SpotLight3D.new()
	fresh.spot_range = lamp.spot_range
	fresh.spot_angle = lamp.spot_angle
	fresh.light_energy = lamp.light_energy
	fresh.light_color = lamp.light_color
	fresh.spot_angle_attenuation = lamp.spot_angle_attenuation
	root.add_child(fresh)
	fresh.global_transform = lamp.global_transform
	await _shot("fresh spot, shadow off")
	fresh.shadow_enabled = true
	await _shot("fresh spot, shadow on")
	fresh.shadow_enabled = false
	await _shot("fresh spot, shadow on then off")
	fresh.queue_free()
	var fresh2 := SpotLight3D.new()
	fresh2.spot_range = lamp.spot_range
	fresh2.spot_angle = lamp.spot_angle
	fresh2.light_energy = lamp.light_energy
	fresh2.light_color = lamp.light_color
	fresh2.shadow_enabled = true
	root.add_child(fresh2)
	fresh2.global_transform = lamp.global_transform
	await _shot("fresh spot born with shadow on")
	var om := OmniLight3D.new()
	om.omni_range = 14.0
	om.light_energy = 19.0
	om.shadow_enabled = true
	root.add_child(om)
	om.global_position = lamp.global_position
	fresh2.visible = false
	await _shot("fresh OMNI born with shadow on")
	om.shadow_enabled = false
	await _shot("fresh OMNI shadow off")
	for l in all:
		l.visible = true
	print("SHADOW done")
	_exit(0)
