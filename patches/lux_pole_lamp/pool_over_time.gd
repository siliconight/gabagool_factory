extends SceneTree
## One pole's pool sampled over time: every other light off, a camera 9 m
## from its foot, 30 readings 8 frames apart with its shadow on, then 30
## with it off. Also prints the lamp's energy and visibility at each read,
## and what its rig says it is doing, so a reading that moves can be pinned
## on the light, the shadow, or neither.
##     godot --path <walk copy> --script pool_over_time.gd -- <rig name>


func _initialize() -> void:
	_run.call_deferred()


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _walk(n: Node, lights: Array) -> void:
	if n is Light3D:
		lights.append(n)
	for c in n.get_children():
		_walk(c, lights)


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
	_walk(root, lights)
	var lamp: SpotLight3D = null
	for l in lights:
		if l is SpotLight3D and String(l.get_parent().name) == pole:
			lamp = l
		l.visible = false
	lamp.visible = true
	var rig: Node = lamp.get_parent()
	var lr: LuxLightRig = rig.get("rig")
	print("OVERTIME %s failing_kind %d flicker %.3f bake_mode %d rig processing %s" % [pole, lr.failing_kind,
		lr.flicker_amount, lr.bake_mode, str(rig.is_processing())])
	var cam := Camera3D.new()
	cam.fov = 60.0
	root.add_child(cam)
	cam.make_current()
	var foot := Vector3(lamp.global_position.x, 0.0, lamp.global_position.z)
	cam.look_at_from_position(foot + Vector3(9.0, 1.6, 0.0), foot + Vector3(0.0, 0.3, 0.0), Vector3.UP)
	for shadow in [true, false]:
		lamp.shadow_enabled = shadow
		var row: Array = []
		var lo: float = 9.0
		var hi: float = 0.0
		for k in range(30):
			for _i in range(8):
				await process_frame
			var v: float = _band(root.get_viewport().get_texture().get_image())
			lo = minf(lo, v)
			hi = maxf(hi, v)
			row.append("%.3f%s" % [v, "" if lamp.visible else "(hidden)"])
			if k % 10 == 0:
				print("OVERTIME   shadow %s read %d energy %.2f visible %s shadow_enabled %s" % [str(shadow), k,
					lamp.light_energy, str(lamp.visible), str(lamp.shadow_enabled)])
		print("OVERTIME shadow %s: min %.3f max %.3f  %s" % [str(shadow), lo, hi, " ".join(PackedStringArray(row))])
	# after the drop: which dial brings it back?
	lamp.shadow_enabled = true
	for _i in range(60):
		await process_frame
	var vp: Viewport = root.get_viewport()
	var base: float = _band(vp.get_texture().get_image())
	print("OVERTIME dials, settled shadowed %.3f; bias %.3f normal %.2f; atlas %d 16bit %s; quadrants %d/%d/%d/%d" % [base,
		lamp.shadow_bias, lamp.shadow_normal_bias, vp.positional_shadow_atlas_size, str(vp.positional_shadow_atlas_16_bits),
		vp.positional_shadow_atlas_quad_0, vp.positional_shadow_atlas_quad_1, vp.positional_shadow_atlas_quad_2, vp.positional_shadow_atlas_quad_3])
	var trials: Array = [["normal bias 2", "shadow_normal_bias", 2.0], ["normal bias 4", "shadow_normal_bias", 4.0],
		["bias 0.1", "shadow_bias", 0.1], ["bias 0.3", "shadow_bias", 0.3]]
	for t in trials:
		var was: Variant = lamp.get(t[1])
		lamp.set(t[1], t[2])
		for _i in range(20):
			await process_frame
		print("OVERTIME   %-16s %.3f" % [t[0], _band(vp.get_texture().get_image())])
		lamp.set(t[1], was)
	vp.positional_shadow_atlas_16_bits = false
	for _i in range(20):
		await process_frame
	print("OVERTIME   %-16s %.3f" % ["24-bit atlas", _band(vp.get_texture().get_image())])
	vp.positional_shadow_atlas_16_bits = true
	vp.positional_shadow_atlas_quad_0 = 1
	vp.positional_shadow_atlas_quad_1 = 1
	vp.positional_shadow_atlas_quad_2 = 1
	vp.positional_shadow_atlas_quad_3 = 1
	for _i in range(40):
		await process_frame
	print("OVERTIME   %-16s %.3f" % ["quadrants 1/1/1/1", _band(vp.get_texture().get_image())])
	print("OVERTIME done")
	_exit(0)
