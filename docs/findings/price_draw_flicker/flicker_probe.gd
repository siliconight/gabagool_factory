## One price heading, frame by frame: draw calls and how many lights are dark.
##
##     godot --path <package> --script res://flicker_probe.gd -- --pos -17,1.6,22.91 --yaw 0 --seconds 80 [--hold]
##         [--pre-yaw 180] [--pre-pos 83,1.6,22.91]
##
## Loads the package's main scene as `perf_stations.gd` does (60 frames to
## settle, any walk player removed), stands one camera at --pos (the eye, as the
## harness reports it) facing --yaw degrees, and for --seconds records every
## frame's RENDER_TOTAL_DRAW_CALLS_IN_FRAME and objects, and the number of
## visible Light3D whose light_energy is at or under 0.001. --hold first calls
## rest() on every node that has one and stops its processing, so no rig's
## clock moves while it records. Windowed, vsync off, 1280x720, quits itself.
## Prints what it measured and stops; writes res://flicker_probe.json.
extends SceneTree

var _args: Dictionary = {}


func _initialize() -> void:
	_run()


func _arg(name: String, fallback: String) -> String:
	var a: PackedStringArray = OS.get_cmdline_user_args()
	for i in range(a.size() - 1):
		if a[i] == name:
			return a[i + 1]
	return fallback


func _flag(name: String) -> bool:
	return OS.get_cmdline_user_args().has(name)


func _walk(n: Node, out: Array) -> void:
	out.append(n)
	for c in n.get_children():
		_walk(c, out)


func _run() -> void:
	await process_frame
	DisplayServer.window_set_size(Vector2i(1280, 720))
	root.content_scale_size = Vector2i(1280, 720)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	var parts: PackedStringArray = _arg("--pos", "0,1.6,0").split(",")
	var eye := Vector3(float(parts[0]), float(parts[1]), float(parts[2]))
	var yaw: float = float(_arg("--yaw", "0"))
	var seconds: float = float(_arg("--seconds", "80"))
	var hold: bool = _flag("--hold")
	var main_path: String = String(ProjectSettings.get_setting("application/run/main_scene", ""))
	var packed: PackedScene = load(main_path) as PackedScene
	if packed == null:
		print("[flicker] REFUSED: no main scene at %s" % main_path)
		quit(2)
		return
	var scene: Node = packed.instantiate()
	current_scene = scene
	root.add_child(scene)
	for i in range(60):
		await process_frame
	var nodes: Array = []
	_walk(scene, nodes)
	for n in nodes:
		var body: CharacterBody3D = n as CharacterBody3D
		if body != null:
			body.get_parent().remove_child(body)
			body.queue_free()
			break
	var lights: Array = []
	var rested := 0
	for n in nodes:
		if not is_instance_valid(n):
			continue
		if n is Light3D:
			lights.append(n)
		if hold and (n as Node).has_method("rest"):
			n.call("rest")
			(n as Node).set_process(false)
			(n as Node).set_physics_process(false)
			rested += 1
	var cam := Camera3D.new()
	root.add_child(cam)
	cam.make_current()
	cam.global_position = eye
	cam.rotation = Vector3(0.0, deg_to_rad(yaw), 0.0)
	# --pre-yaw: stand at the place facing that way for 3 s first, then turn to --yaw -- a turn in place,
	# which is what the harness does between a station's headings
	# --pre-pos: stand somewhere else for 3 s first, then move to --pos -- a move between stations
	if _arg("--pre-pos", "") != "":
		var pp: PackedStringArray = _arg("--pre-pos", "").split(",")
		cam.global_position = Vector3(float(pp[0]), float(pp[1]), float(pp[2]))
		var tq: int = Time.get_ticks_msec()
		while Time.get_ticks_msec() - tq < 3000:
			await process_frame
		cam.global_position = eye
	if _arg("--pre-yaw", "") != "":
		cam.rotation = Vector3(0.0, deg_to_rad(float(_arg("--pre-yaw", "0"))), 0.0)
		var tp: int = Time.get_ticks_msec()
		while Time.get_ticks_msec() - tp < 3000:
			await process_frame
		cam.rotation = Vector3(0.0, deg_to_rad(yaw), 0.0)
	for i in range(30):
		await process_frame
	var frames: Array = []
	var t0: int = Time.get_ticks_msec()
	while float(Time.get_ticks_msec() - t0) / 1000.0 < seconds:
		await process_frame
		var dark := 0
		for l in lights:
			var lt: Light3D = l
			if is_instance_valid(lt) and lt.is_visible_in_tree() and lt.light_energy <= 0.001:
				dark += 1
		frames.append([Time.get_ticks_msec() - t0,
			int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)),
			int(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)), dark])
	var by_draws: Dictionary = {}
	for f in frames:
		var k: String = str(f[1])
		if not by_draws.has(k):
			by_draws[k] = {"frames": 0, "dark_min": 1 << 30, "dark_max": -1}
		var e: Dictionary = by_draws[k]
		e["frames"] = int(e["frames"]) + 1
		e["dark_min"] = mini(int(e["dark_min"]), int(f[3]))
		e["dark_max"] = maxi(int(e["dark_max"]), int(f[3]))
	var doc := {"pos": [eye.x, eye.y, eye.z], "yaw": yaw, "seconds": seconds, "hold": hold,
		"rested": rested, "lights": lights.size(), "frames": frames.size(), "by_draws": by_draws,
		"trace": frames}
	var fh := FileAccess.open("res://flicker_probe.json", FileAccess.WRITE)
	fh.store_string(JSON.stringify(doc))
	fh.close()
	print("[flicker] hold=%s rested=%d lights=%d frames=%d" % [str(hold), rested, lights.size(), frames.size()])
	for k in by_draws.keys():
		var e2: Dictionary = by_draws[k]
		print("[flicker] draws %s: %d frame(s), dark lights %d..%d" % [k, e2["frames"], e2["dark_min"], e2["dark_max"]])
	quit(0)
