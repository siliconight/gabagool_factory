extends Node
## Frames of the asset flags' boxes in a real walk copy: presses P and G from given places and saves what the screen shows.
##
## An autoload payload for `outline_frames.py`, which runs it through `tools/godot_probe.py` on a MIRROR of the walk
## copy, so the copy's own `asset_flags.jsonl` is never written. Waits out the level's shader warm-up as look_shots
## does, holds the walk player still and the mouse free, then for each shot: stands the player's camera at `eye`
## looking at `target`, lets the frame draw, calls the handler's own `flag(verdict)` -- the press, end to end -- lets
## the box and banner draw, and saves the frame. Prints what each press recorded and what box it drew, between fences.
## The F3 overlay stays as a walk shows it, so the frames say where the banner falls beside it.

const MARK_BEGIN := "<<<OUTLINE_FRAME_JSON"
const MARK_END := "OUTLINE_FRAME_JSON>>>"
const WARMUP_MAX_FRAMES := 5000
const SETTLE_FRAMES := 12

var _report: Dictionary = {"shots": [], "notes": []}


func _process(_delta: float) -> void:
	# the walk player captures the mouse on its _ready; a probe on somebody's desktop must not hold it
	if Input.mouse_mode != Input.MOUSE_MODE_VISIBLE:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE


func _ready() -> void:
	var out_dir: String = String(ProjectSettings.get_setting("outline_frame/out_dir", ""))
	var parsed: Variant = JSON.parse_string(String(ProjectSettings.get_setting("outline_frame/shots", "[]")))
	if out_dir == "" or not (parsed is Array):
		_emit({"error": "outline_frame/out_dir or outline_frame/shots not set by the driver"})
		return
	var shots: Array = parsed
	for _i in range(SETTLE_FRAMES):
		await get_tree().process_frame
	var scene: Node = get_tree().current_scene
	if scene == null:
		_emit({"error": "current_scene is null"})
		return
	var warm: Dictionary = await _await_warmups(scene)
	if warm.has("error"):
		_emit(warm)
		return
	_report["notes"].append("warm-up: " + JSON.stringify(warm))
	var flags: Node = scene.get_node_or_null(^"WalkAssetFlags")
	var player: Node = scene.get_node_or_null(^"Player")
	var cam: Camera3D = null if player == null else player.get_node_or_null(^"Camera") as Camera3D
	if flags == null or cam == null or not flags.has_method(&"outline"):
		_emit({"error": "no WalkAssetFlags with outline(), or no Player/Camera, in %s" % scene.scene_file_path})
		return
	player.set_process(false)
	player.set_physics_process(false)
	player.set_process_input(false)
	player.set_process_unhandled_input(false)
	cam.make_current()
	for s in shots:
		var d: Dictionary = s
		var eye := Vector3(float(d["eye"][0]), float(d["eye"][1]), float(d["eye"][2]))
		var target := Vector3(float(d["target"][0]), float(d["target"][1]), float(d["target"][2]))
		if d.has("sweep_for"):
			# the nearest thing under a scene path, by the handler's own pick, swept round the eye every 10 degrees
			# level and 10 degrees down; the camera then stands `stand_m` back from it along the line it was found on
			var found: Dictionary = _nearest_under(flags, eye, String(d["sweep_for"]))
			if found.is_empty():
				_report["notes"].append("%s: nothing under %s within reach" % [d["name"], d["sweep_for"]])
				continue
			target = found["point"]
			eye = target + (eye - target).normalized() * float(d.get("stand_m", 5.0))
			d["eye"] = [eye.x, eye.y, eye.z]
			d["target"] = [target.x, target.y, target.z]
		cam.global_position = eye
		cam.look_at(target, Vector3.UP)
		for _i in range(SETTLE_FRAMES):
			await RenderingServer.frame_post_draw
		var rec: Dictionary = flags.call(&"flag", String(d["verdict"]))
		for _i in range(SETTLE_FRAMES):
			await RenderingServer.frame_post_draw
		var path: String = out_dir.path_join(String(d["name"]) + ".png")
		var img: Image = get_viewport().get_texture().get_image()
		img.convert(Image.FORMAT_RGB8)
		var err: int = img.save_png(path)
		var boxes: Array = []
		var holder: Node = flags.get_node_or_null(^"AssetFlagOutlines")
		if holder != null:
			for b in holder.get_children():
				var mi: MeshInstance3D = b as MeshInstance3D
				var box: AABB = mi.global_transform * mi.mesh.get_aabb()
				boxes.append({"target": String(mi.get_meta(&"target", NodePath())), "verdict": mi.get_meta(&"verdict", ""),
					"min": [box.position.x, box.position.y, box.position.z], "size": [box.size.x, box.size.y, box.size.z]})
		_report["shots"].append({"name": d["name"], "eye": d["eye"], "target": d["target"], "verdict": d["verdict"],
			"frame": path, "saved": err == OK, "asset": rec.get("asset", ""), "node": rec.get("node", ""),
			"how": rec.get("how", ""), "distance_m": rec.get("distance_m", -1.0), "boxes": boxes})
	_report["engine"] = String(Engine.get_version_info().get("string", ""))
	_report["rendering_method"] = String(ProjectSettings.get_setting("rendering/renderer/rendering_method", ""))
	_report["adapter"] = RenderingServer.get_video_adapter_name()
	_report["viewport"] = [get_viewport().size.x, get_viewport().size.y]
	_emit(_report)


## {point, node} for the nearest render hit whose instanced ancestor's scene path begins with `prefix`, or {}.
func _nearest_under(flags: Node, eye: Vector3, prefix: String) -> Dictionary:
	var best: Dictionary = {}
	var best_d: float = INF
	for pitch_deg in [0.0, -10.0]:
		for step in range(36):
			var yaw: float = deg_to_rad(10.0 * float(step))
			var pitch: float = deg_to_rad(float(pitch_deg))
			var dir := Vector3(sin(yaw) * cos(pitch), sin(pitch), cos(yaw) * cos(pitch))
			var hit: Dictionary = flags.call(&"_render_hit", eye, dir)
			if hit.is_empty():
				continue
			var root: Node = flags.call(&"_instanced_ancestor", hit["node"])
			if root == null or not root.scene_file_path.begins_with(prefix):
				continue
			var p: Vector3 = hit["point"]
			if eye.distance_to(p) < best_d:
				best_d = eye.distance_to(p)
				best = hit
	return best


## look_shots.gd's warm-up wait: every node carrying `warmup_finished`, waited on while its `_running` holds.
func _await_warmups(scene: Node) -> Dictionary:
	var found: Array = []
	var waited := 0
	var warms: Array = []
	for n in scene.find_children("*", "", true, false):
		if n.has_signal(&"warmup_finished"):
			warms.append(n)
	for n in warms:
		if not is_instance_valid(n):
			continue
		var w: Node = n
		found.append(String(w.get_path()))
		if not (&"_running" in w):
			continue
		while bool(w.get(&"_running")) and waited < WARMUP_MAX_FRAMES:
			await get_tree().process_frame
			waited += 1
		if bool(w.get(&"_running")):
			return {"error": "warm-up at %s still running after %d frames; nothing shot" % [String(w.get_path()), waited]}
	return {"warmup": found, "waited_frames": waited}


func _emit(report: Dictionary) -> void:
	print(MARK_BEGIN)
	print(JSON.stringify(report, "  "))
	print(MARK_END)
	get_tree().quit()
	await get_tree().process_frame
	await get_tree().process_frame
	OS.kill(OS.get_process_id())
