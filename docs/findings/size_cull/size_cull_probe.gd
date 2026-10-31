extends SceneTree
## WHAT A SIZE-DERIVED DRAW DISTANCE WOULD DROP, at the price harness's own views.
##
##     godot --headless --path <imported project> --script <this file> -- --stations <perf report.json> --out <json>
##
## Takes the stations and yaws from a `perf_stations.gd` report (`rows[].pos` is the ANCHOR; the eye is `EYE_H`
## above it, pitch 0, `rotation.y = deg_to_rad(yaw)`, 75 degree vertical FOV, far 500 -- all as the harness does,
## read from it 2026-10-30). At each heading it lists every visible MeshInstance3D and MultiMeshInstance3D whose
## world bounding sphere is inside the camera's frustum, and the height in pixels that sphere projects to at
## `SCREEN_H`: ``px = r / (d * tan(fov / 2)) * SCREEN_H / 2``.
##
## WHAT IT IS NOT. Frustum only: no occlusion, no shadow passes, no depth-prepass. Its instance counts are a
## SUPERSET of what the renderer submits, and its surface counts are a stand-in for draws, not a draw count. It
## prints what it measured; what that means for the price belongs in the README beside it.
##
## v2 (slice 21): also what is STILL DRAWN under 3 px -- an instance with no range, or nearer than its range's end
## -- by name, so a range that was kept on purpose (a lit part, a solid object's silhouette) can be told from one
## that never was set.
##
## Headless on purpose: nothing here needs a frame drawn. A watchdog ends it whatever happens.

const WATCHDOG_SEC := 300.0
const SCREEN_H := 1080.0
const FOV := 75.0
const FAR := 500.0
const EYE_H := 1.6
const THRESHOLDS := [2.0, 3.0, 4.0]
const TOP_NAMES := 12

var _out_path: String = "user://size_cull.json"
var _report: Dictionary = {"schema": "size_cull_probe.v2", "complete": false, "headings": []}


func _initialize() -> void:
	_run()
	_watchdog()


func _watchdog() -> void:
	var t0: int = Time.get_ticks_msec()
	while true:
		await process_frame
		if Time.get_ticks_msec() - t0 > int(WATCHDOG_SEC * 1000.0):
			print("[size_cull] WATCHDOG: %.0f s elapsed, quitting" % WATCHDOG_SEC)
			_write()
			_exit(2)
			return


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _arg(name: String, fallback: String) -> String:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	for i in range(args.size() - 1):
		if args[i] == name:
			return args[i + 1]
	return fallback


func _walk(n: Node, out: Array) -> void:
	out.append(n)
	for c in n.get_children():
		_walk(c, out)


func _write() -> void:
	var f: FileAccess = FileAccess.open(_out_path, FileAccess.WRITE)
	if f == null:
		print("[size_cull] cannot write %s" % _out_path)
		return
	f.store_string(JSON.stringify(_report, "  "))
	f.close()


## The model a node came from: the first ancestor whose name is not a generic container's, so a count can say
## "parking_meter" rather than "MeshInstance3D".
func _owner_name(n: Node, root: Node) -> String:
	var p: Node = n
	while p != null and p != root:
		var nm: String = String(p.name)
		if not nm.begins_with("MeshInstance") and not nm.begins_with("Node3D") and not nm.begins_with("@"):
			return nm
		p = p.get_parent()
	return String(n.name)


func _run() -> void:
	await process_frame
	_out_path = _arg("--out", _out_path)
	var spec_path: String = _arg("--stations", "")
	if spec_path == "" or not FileAccess.file_exists(spec_path):
		print("[size_cull] REFUSED: no --stations report at '%s'" % spec_path)
		_exit(2)
		return
	var spec: Variant = JSON.parse_string(FileAccess.get_file_as_string(spec_path))
	if typeof(spec) != TYPE_DICTIONARY or not (spec as Dictionary).has("rows"):
		print("[size_cull] REFUSED: %s has no rows" % spec_path)
		_exit(2)
		return
	var rows: Array = (spec as Dictionary)["rows"]

	var main_path: String = String(ProjectSettings.get_setting("application/run/main_scene", ""))
	var packed: PackedScene = load(main_path) as PackedScene
	if packed == null:
		print("[size_cull] REFUSED: no main scene at %s" % main_path)
		_exit(2)
		return
	var scene: Node = packed.instantiate()
	current_scene = scene
	root.add_child(scene)
	for i in range(30):
		await process_frame

	var nodes: Array = []
	_walk(scene, nodes)
	for n in nodes:
		var body: CharacterBody3D = n as CharacterBody3D
		if body != null:
			body.get_parent().remove_child(body)
			body.queue_free()
			print("[size_cull] removed a walk player")
			break
	await process_frame
	nodes = []
	_walk(scene, nodes)

	var items: Array = []
	for n in nodes:
		var gi: GeometryInstance3D = n as GeometryInstance3D
		if gi == null or not gi.is_visible_in_tree():
			continue
		var surfaces: int = 0
		var mi: MeshInstance3D = n as MeshInstance3D
		var mm: MultiMeshInstance3D = n as MultiMeshInstance3D
		if mi != null and mi.mesh != null:
			surfaces = mi.mesh.get_surface_count()
		elif mm != null and mm.multimesh != null and mm.multimesh.mesh != null:
			surfaces = mm.multimesh.mesh.get_surface_count()
		else:
			continue
		var box: AABB = gi.global_transform * gi.get_aabb()
		items.append({"c": box.get_center(), "r": box.size.length() / 2.0, "s": surfaces,
			"name": _owner_name(n, scene), "range": gi.visibility_range_end})
	print("[size_cull] %d geometry instance(s) in the scene" % items.size())
	if items.is_empty():
		print("[size_cull] REFUSED: no geometry -- the project is not imported or not the level")
		_exit(2)
		return

	var cam := Camera3D.new()
	cam.fov = FOV
	cam.far = FAR
	root.add_child(cam)
	cam.make_current()
	var k: float = (SCREEN_H / 2.0) / tan(deg_to_rad(FOV) / 2.0)
	for row in rows:
		var r: Dictionary = row as Dictionary
		var pv: Array = r["pos"] as Array
		var eye := Vector3(float(pv[0]), float(pv[1]), float(pv[2])) + Vector3.UP * EYE_H
		for hd in (r["headings"] as Array):
			var yaw: float = float((hd as Dictionary)["yaw"])
			cam.global_position = eye
			cam.rotation = Vector3(0.0, deg_to_rad(yaw), 0.0)
			await process_frame
			var planes: Array = cam.get_frustum()
			var vis_i: int = 0
			var vis_s: int = 0
			var under_i: Array = [0, 0, 0]
			var under_s: Array = [0, 0, 0]
			var by_name: Dictionary = {}
			var drawn_s: int = 0
			var drawn_by_name: Dictionary = {}
			for it in items:
				var c: Vector3 = it["c"]
				var rad: float = it["r"]
				var inside: bool = true
				for pl in planes:
					var plane: Plane = pl
					if plane.distance_to(c) > rad:
						inside = false
						break
				if not inside:
					continue
				var d: float = eye.distance_to(c)
				if d - rad > FAR:
					continue
				vis_i += 1
				vis_s += int(it["s"])
				var px: float = rad / maxf(d, 0.01) * k
				for t in range(THRESHOLDS.size()):
					if px < float(THRESHOLDS[t]):
						under_i[t] = int(under_i[t]) + 1
						under_s[t] = int(under_s[t]) + int(it["s"])
				if px < float(THRESHOLDS[1]):
					var nm: String = it["name"]
					by_name[nm] = int(by_name.get(nm, 0)) + int(it["s"])
					var end: float = float(it["range"])
					if end <= 0.0 or d < end:
						drawn_s += int(it["s"])
						drawn_by_name[nm] = int(drawn_by_name.get(nm, 0)) + int(it["s"])
			var top: Array = []
			for nm in by_name.keys():
				top.append([int(by_name[nm]), String(nm)])
			top.sort()
			top.reverse()
			top = top.slice(0, TOP_NAMES)
			var drawn_top: Array = []
			for nm in drawn_by_name.keys():
				drawn_top.append([int(drawn_by_name[nm]), String(nm)])
			drawn_top.sort()
			drawn_top.reverse()
			drawn_top = drawn_top.slice(0, TOP_NAMES * 2)
			var rec: Dictionary = {"station": r.get("station", "?"), "yaw": yaw, "visible_instances": vis_i,
				"visible_surfaces": vis_s, "thresholds_px": THRESHOLDS, "under_instances": under_i,
				"under_surfaces": under_s, "top_under_3px_by_surfaces": top, "drawn_under_3px_surfaces": drawn_s,
				"top_drawn_under_3px_by_surfaces": drawn_top}
			(_report["headings"] as Array).append(rec)
			print("[size_cull] %s yaw %.0f: %d inst / %d surf in frustum; under 2/3/4 px: %d/%d/%d surf"
				% [String(r.get("station", "?")), yaw, vis_i, vis_s, int(under_s[0]), int(under_s[1]), int(under_s[2])])
	_report["complete"] = true
	_write()
	print("[size_cull] wrote %s" % _out_path)
	_exit(0)
