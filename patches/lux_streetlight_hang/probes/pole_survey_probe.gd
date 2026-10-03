extends SceneTree
## Scratch survey: which streetlights' own lights render? For every pole: the
## camera 9 m from its foot, every other light off, a frame with the pole's
## own lamp; then its lamp hidden and a fresh spot on its transform. The
## ground's luminance near the foot in both says alive or dead. Prints each
## pole with its position, order in the tree, failing kind and the verdict.

const OUT: String = "C:/Projects/gabagool_studios/gabagool_factory/docs/findings/light_cap/survey"


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
		print("SURVEY CANNOT SHOOT")
		_exit(2)
		return
	_hide_canvas(root)
	var all: Array = []
	_all_lights(root, all)
	var poles: Array = []
	var order: int = 0
	for l in all:
		if l is SpotLight3D and String(l.get_parent().name).begins_with("site_lamp"):
			poles.append([l, order])
		order += 1
	for l in all:
		if l is Light3D:
			l.visible = false
	var cam := Camera3D.new()
	cam.fov = 60.0
	root.add_child(cam)
	cam.make_current()
	var dead: Array = []
	var alive: Array = []
	for entry in poles:
		var lamp: SpotLight3D = entry[0]
		var foot: Vector3 = Vector3(lamp.global_position.x, 0.0, lamp.global_position.z)
		cam.look_at_from_position(foot + Vector3(9.0, 1.6, 0.0), foot + Vector3(0.0, 0.3, 0.0), Vector3.UP)
		lamp.visible = true
		for _i in range(8):
			await process_frame
		var own: float = _band(root.get_viewport().get_texture().get_image())
		lamp.visible = false
		var fresh := SpotLight3D.new()
		fresh.spot_range = lamp.spot_range
		fresh.spot_angle = lamp.spot_angle
		fresh.light_energy = lamp.light_energy
		fresh.light_color = lamp.light_color
		root.add_child(fresh)
		fresh.global_transform = lamp.global_transform
		for _i in range(8):
			await process_frame
		var copy: float = _band(root.get_viewport().get_texture().get_image())
		fresh.queue_free()
		await process_frame
		var rig: Node = lamp.get_parent()
		var lr: LuxLightRig = rig.get("rig")
		var verdict: String = "ALIVE" if own > copy * 0.5 else "DEAD"
		if verdict == "DEAD":
			dead.append(String(rig.name))
		else:
			alive.append(String(rig.name))
		print("SURVEY %-13s order=%2d at (%6.1f, %5.1f) failing=%d energy=%5.2f own=%.3f copy=%.3f %s" % [
			String(rig.name), int(entry[1]), lamp.global_position.x, lamp.global_position.z,
			lr.failing_kind if lr != null else -1, lamp.light_energy, own, copy, verdict])
	for l in all:
		if l is Light3D:
			l.visible = true
	print("SURVEY alive=", alive.size(), " ", alive)
	print("SURVEY dead=", dead.size(), " ", dead)
	print("SURVEY done")
	_exit(0)
