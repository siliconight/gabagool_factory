extends SceneTree
## Scratch probe: do the roller grill's rollers and the slush's churn MOVE in a
## shipped level? Loads a walk copy as it is, finds the grill and the station
## by the materials they wear, checks what the import did to those materials,
## stands a camera at each, shoots three frames half a second apart and prints
## the pixel difference between them -- and the same for a still control view,
## so the number has a floor. Windowed, drives itself, quits itself. Prints
## what it measured and stops.

const OUT: String = "C:/Projects/gabagool_studios/gabagool_factory/docs/findings/moving_parts"
const GAP_S: float = 0.5
const WANT: Array = [
	["grill", "M_Roller_metal_bare_turn", 1.5, 0.35],
	["slush", "M_Slush_", 2.0, 0.1],
]


func _initialize() -> void:
	_run.call_deferred()


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _wearing(n: Node, prefix: String, out: Array) -> void:
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi != null and mi.mesh != null:
		for i: int in range(mi.mesh.get_surface_count()):
			var m: Material = mi.get_active_material(i)
			if m != null and String(m.resource_name).begins_with(prefix):
				out.append([mi.global_transform * mi.get_aabb(), mi, i, m])
				break
	for c: Node in n.get_children():
		_wearing(c, prefix, out)


func _hide_canvas(n: Node) -> void:
	if n is CanvasLayer and not String(n.name).contains("Lux"):
		(n as CanvasLayer).visible = false
	for c: Node in n.get_children():
		_hide_canvas(c)


func _diff(a: Image, b: Image) -> Array:
	## [mean absolute difference 0..255 over the frame, pixels differing by more than 8]
	var w: int = mini(a.get_width(), b.get_width())
	var h: int = mini(a.get_height(), b.get_height())
	var total: float = 0.0
	var moved: int = 0
	for y in range(0, h, 2):
		for x in range(0, w, 2):
			var p: Color = a.get_pixel(x, y)
			var q: Color = b.get_pixel(x, y)
			var d: float = (absf(p.r - q.r) + absf(p.g - q.g) + absf(p.b - q.b)) / 3.0 * 255.0
			total += d
			if d > 8.0:
				moved += 1
	var n: int = (w / 2) * (h / 2)
	return [total / float(n), moved, n]


func _shoot3(cam: Camera3D, label: String, from: Vector3, at: Vector3) -> void:
	cam.look_at_from_position(from, at, Vector3.UP)
	for _i in range(10):
		await process_frame
	var frames: Array = []
	for k in range(3):
		var t0: float = Time.get_ticks_msec() / 1000.0
		while Time.get_ticks_msec() / 1000.0 - t0 < (GAP_S if k > 0 else 0.0):
			await process_frame
		var img: Image = root.get_viewport().get_texture().get_image()
		img.save_png("%s/%s_%d.png" % [OUT, label, k])
		frames.append(img)
	var draws: int = int(RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME))
	var d01: Array = _diff(frames[0], frames[1])
	var d12: Array = _diff(frames[1], frames[2])
	print("MOVE %s from %s: draws=%d  frame0->1 mean=%.2f moved=%d/%d  frame1->2 mean=%.2f moved=%d/%d"
		% [label, str(from), draws, float(d01[0]), int(d01[1]), int(d01[2]), float(d12[0]), int(d12[1]), int(d12[2])])


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
	print("MOVE warm-up waited ", waited, " frames")
	if steady < 30:
		print("MOVE CANNOT SHOOT: the warm-up never finished")
		_exit(2)
		return
	_hide_canvas(root)
	# what the import did to the materials
	var turning: Array = []
	_wearing(root, "M_Roller_metal_bare_turn", turning)
	var dogs: Array = []
	_wearing(root, "M_Roller_metal_painted_turn", dogs)
	var slush: Array = []
	_wearing(root, "M_Slush_", slush)
	print("MOVE rollers=", turning.size(), " dog surfaces=", dogs.size(), " slush faces=", slush.size())
	for e in turning + dogs:
		var m: Material = e[3]
		var sm: ShaderMaterial = m as ShaderMaterial
		print("MOVE   ", m.resource_name, " shader=", sm != null,
			" rate_rad_s=", sm.get_shader_parameter("rate_rad_s") if sm != null else "-",
			" axis=", sm.get_shader_parameter("axis") if sm != null else "-")
	for e in slush:
		var m: Material = e[3]
		var bm: BaseMaterial3D = m as BaseMaterial3D
		var np: Material = bm.next_pass if bm != null else null
		if not String(m.resource_name).ends_with("_Face"):
			continue
		print("MOVE   ", m.resource_name, " base=", bm != null, " next_pass=", np.resource_name if np != null else "none",
			" period=", (np as ShaderMaterial).get_shader_parameter("period_s") if np is ShaderMaterial else "-")
	var cam: Camera3D = Camera3D.new()
	cam.fov = 50.0
	root.add_child(cam)
	cam.make_current()
	# the grill: the rollers' box, looked at from the customer's side and above
	if not turning.is_empty():
		var box: AABB = turning[0][0]
		var mid: Vector3 = box.get_center()
		# the customer stands on the long side; the long axis is the rollers'
		var along: Vector3 = Vector3(1, 0, 0) if box.size.x > box.size.z else Vector3(0, 0, 1)
		var fwd: Vector3 = along.cross(Vector3.UP)
		# pick the side that faces open floor: try +fwd, the probe does not know the room, so both are shot
		await _shoot3(cam, "grill_a", mid + fwd * 0.9 + Vector3.UP * 0.55, mid)
		await _shoot3(cam, "grill_b", mid - fwd * 0.9 + Vector3.UP * 0.55, mid)
		await _shoot3(cam, "grill_close", mid + fwd * 0.45 + Vector3.UP * 0.3, mid)
	if not slush.is_empty():
		var best: Array = []
		for e in slush:
			if String((e[3] as Material).resource_name).ends_with("_Face"):
				best = e
				break
		if not best.is_empty():
			var box: AABB = best[0]
			var mid: Vector3 = box.get_center()
			var along: Vector3 = Vector3(1, 0, 0) if box.size.x > box.size.z else Vector3(0, 0, 1)
			var fwd: Vector3 = along.cross(Vector3.UP)
			await _shoot3(cam, "slush_a", mid + fwd * 1.6 + Vector3.UP * 0.1, mid)
			await _shoot3(cam, "slush_b", mid - fwd * 1.6 + Vector3.UP * 0.1, mid)
	# the control: a still view of something that must not move -- the ceiling over the grill
	if not turning.is_empty():
		var mid: Vector3 = (turning[0][0] as AABB).get_center()
		await _shoot3(cam, "control_ceiling", mid + Vector3(0.0, 0.2, 0.0), mid + Vector3(0.0, 3.0, 0.3))
	print("MOVE done")
	_exit(0)
