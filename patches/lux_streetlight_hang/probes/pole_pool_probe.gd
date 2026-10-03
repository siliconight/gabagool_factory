extends SceneTree
## Scratch probe: how big and how bright is a streetlight's pool on the lot?
## Stands a camera 9 m from one steady pole's foot, looking at the ground
## under it, and shoots it with the pole as shipped and with its falloff and
## energy changed in place; prints the ground's luminance in three bands
## out from the foot (0-3 m, 3-6 m, 6-9 m, read off the frame's rows).

const OUT: String = "C:/Projects/gabagool_studios/gabagool_factory/docs/findings/light_cap/pool"
const POLE_NAME: String = "site_lamp_21"
## [spot_attenuation, energy factor]
const TRIALS: Array = [[2.0, 1.0], [1.0, 1.0], [0.7, 1.0], [2.0, 3.0], [1.0, 2.0], [1.0, 3.0], [2.0, 0.0]]


func _initialize() -> void:
	_run.call_deferred()


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _find(n: Node, out: Array) -> void:
	if n is SpotLight3D and String(n.get_parent().name) == POLE_NAME:
		out.append(n)
	for c in n.get_children():
		_find(c, out)


func _hide_canvas(n: Node) -> void:
	if n is CanvasLayer and not String(n.name).contains("Lux"):
		(n as CanvasLayer).visible = false
	for c: Node in n.get_children():
		_hide_canvas(c)


func _band(img: Image, y0f: float, y1f: float) -> float:
	var w: int = img.get_width()
	var h: int = img.get_height()
	var s: float = 0.0
	var n: int = 0
	for y in range(int(h * y0f), int(h * y1f), 2):
		for x in range(int(w * 0.3), int(w * 0.7), 2):
			s += img.get_pixel(x, y).get_luminance()
			n += 1
	return s / float(n)


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
		print("POOL CANNOT SHOOT")
		_exit(2)
		return
	_hide_canvas(root)
	var found: Array = []
	_find(root, found)
	if found.is_empty():
		print("POOL no pole ", POLE_NAME)
		_exit(2)
		return
	var lamp: SpotLight3D = found[0]
	var foot: Vector3 = Vector3(lamp.global_position.x, 0.0, lamp.global_position.z)
	print("POOL %s lamp at %s energy=%.2f range=%.1f angle=%.0f attenuation=%.2f angle_attenuation=%.2f" % [POLE_NAME,
		str(lamp.global_position), lamp.light_energy, lamp.spot_range, lamp.spot_angle, lamp.spot_attenuation, lamp.spot_angle_attenuation])
	var cam := Camera3D.new()
	cam.fov = 60.0
	root.add_child(cam)
	cam.make_current()
	# from the lot side (toward +x of the pole, which is the lot), low, looking at the foot
	cam.look_at_from_position(foot + Vector3(9.0, 1.6, 0.0), foot + Vector3(0.0, 0.3, 0.0), Vector3.UP)
	var e0: float = lamp.light_energy
	var a0: float = lamp.spot_attenuation
	for t in TRIALS:
		lamp.spot_attenuation = float(t[0])
		lamp.light_energy = e0 * float(t[1])
		for _i in range(10):
			await process_frame
		var img: Image = root.get_viewport().get_texture().get_image()
		var tag: String = "pole_att%s_x%s" % [str(t[0]).replace(".", "_"), str(t[1]).replace(".", "_")]
		img.save_png("%s/%s.png" % [OUT, tag])
		# the frame's rows: the foot sits near the middle; nearer ground is lower in the frame
		print("POOL att=%.1f x%.1f energy=%.2f  ground near foot=%.3f  mid=%.3f  near camera=%.3f" % [float(t[0]), float(t[1]), lamp.light_energy,
			_band(img, 0.50, 0.62), _band(img, 0.62, 0.78), _band(img, 0.78, 0.98)])
	lamp.spot_attenuation = a0
	lamp.light_energy = e0
	# every other light in the scene, and the walk's own lights
	var all: Array = []
	_all_lights(root, all)
	var spots: int = 0
	var omnis: int = 0
	var other: int = 0
	for l in all:
		if l is SpotLight3D:
			spots += 1
		elif l is OmniLight3D:
			omnis += 1
		else:
			other += 1
	print("POOL lights in the running walk: spot=%d omni=%d other=%d (max_renderable %s)" % [spots, omnis, other,
		str(ProjectSettings.get_setting("rendering/limits/opengl/max_renderable_lights", "default"))])
	var off: Array = []
	for l in all:
		if l != lamp and l is SpotLight3D and l.visible:
			l.visible = false
			off.append(l)
	for _i in range(10):
		await process_frame
	var img2: Image = root.get_viewport().get_texture().get_image()
	img2.save_png("%s/pole_only_spot.png" % OUT)
	print("POOL other spots OFF (%d): ground near foot=%.3f mid=%.3f near camera=%.3f" % [off.size(), _band(img2, 0.50, 0.62), _band(img2, 0.62, 0.78), _band(img2, 0.78, 0.98)])
	for l in all:
		if l != lamp and l is OmniLight3D and l.visible:
			l.visible = false
			off.append(l)
	for _i in range(10):
		await process_frame
	var img3: Image = root.get_viewport().get_texture().get_image()
	img3.save_png("%s/pole_only_light.png" % OUT)
	print("POOL every other light OFF (%d): ground near foot=%.3f mid=%.3f near camera=%.3f" % [off.size(), _band(img3, 0.50, 0.62), _band(img3, 0.62, 0.78), _band(img3, 0.78, 0.98)])
	# a fresh spot on the pole's transform, with the pole's own light hidden
	var fresh := SpotLight3D.new()
	fresh.spot_range = lamp.spot_range
	fresh.spot_angle = lamp.spot_angle
	fresh.light_energy = lamp.light_energy
	fresh.light_color = lamp.light_color
	root.add_child(fresh)
	fresh.global_transform = lamp.global_transform
	lamp.visible = false
	for _i in range(10):
		await process_frame
	var img4: Image = root.get_viewport().get_texture().get_image()
	img4.save_png("%s/pole_fresh_spot.png" % OUT)
	print("POOL FRESH spot on the pole, pole hidden, others off: near foot=%.3f mid=%.3f near camera=%.3f" % [_band(img4, 0.50, 0.62), _band(img4, 0.62, 0.78), _band(img4, 0.78, 0.98)])
	# every property that differs between the pole's light and the fresh one
	for prop in lamp.get_property_list():
		var nm: String = prop["name"]
		if prop["usage"] & PROPERTY_USAGE_STORAGE == 0:
			continue
		var a: Variant = lamp.get(nm)
		var b: Variant = fresh.get(nm)
		if str(a) != str(b):
			print("POOL   differs %s: pole=%s fresh=%s" % [nm, str(a).left(60), str(b).left(60)])
	print("POOL pole parent=%s owner=%s path=%s" % [lamp.get_parent().get_class(), lamp.owner.name if lamp.owner != null else "null", String(lamp.get_path()).left(90)])
	fresh.queue_free()
	lamp.visible = true
	await process_frame
	print("POOL pole visible_in_tree=%s  parent visible=%s  rig visible=%s" % [str(lamp.is_visible_in_tree()), str((lamp.get_parent() as Node3D).visible), str((lamp.get_parent().get_parent() as Node3D).visible if lamp.get_parent().get_parent() is Node3D else "-")])
	# 1. push the energy straight at the rendering server
	RenderingServer.light_set_param(lamp.get_base(), RenderingServer.LIGHT_PARAM_ENERGY, 19.2)
	for _i in range(10):
		await process_frame
	var i5: Image = root.get_viewport().get_texture().get_image()
	print("POOL after light_set_param energy 19.2: near foot=%.3f" % _band(i5, 0.50, 0.62))
	# 2. toggle visibility
	lamp.visible = false
	await process_frame
	lamp.visible = true
	for _i in range(10):
		await process_frame
	var i6: Image = root.get_viewport().get_texture().get_image()
	print("POOL after visible off/on: near foot=%.3f" % _band(i6, 0.50, 0.62))
	# 3. reparent the light to the root, keeping its world transform
	var xf: Transform3D = lamp.global_transform
	lamp.reparent(root, true)
	lamp.global_transform = xf
	for _i in range(10):
		await process_frame
	var i7: Image = root.get_viewport().get_texture().get_image()
	print("POOL after reparent to root: near foot=%.3f" % _band(i7, 0.50, 0.62))
	# 4. the rig's own state
	var rig: Node = root.get_node_or_null("/root/_walk/Mission/Site/LuxClub/site_lamp_21")
	if rig != null:
		print("POOL rig class=%s process=%s lights=%s rig.energy=%s failing=%s" % [rig.get_class(), str(rig.is_processing()), str((rig.get("_lights") as Array).size() if rig.get("_lights") != null else -1), str((rig.get("rig") as LuxLightRig).energy if rig.get("rig") != null else "-"), str((rig.get("rig") as LuxLightRig).failing_kind if rig.get("rig") != null else "-")])
	for l in off:
		l.visible = true
	print("POOL done")
	_exit(0)


func _all_lights(n: Node, out: Array) -> void:
	if n is Light3D:
		out.append(n)
	for c in n.get_children():
		_all_lights(c, out)
