extends SceneTree
## WHAT ONE VIEW SUBMITS, BRANCH BY BRANCH -- for the slice's over-budget headings.
##
## The method is level_factory/tools/station_census.gd's (attribution by subtraction): measure the view, hide one
## branch, measure again; the drop is that branch's submissions in THAT view. The camera is perf_stations.gd's:
## the package's main scene, any walk player removed, fov 75, far 500, `rotation.y` = the yaw in radians, the eye
## where the price report put it. Branches are the main scene's children and its children's children, bucketed by
## name with trailing digits and suffixes stripped, so `b0`..`b3`, `cover_*` and the like each read as one row.
##
## THE CONTROL: everything hidden must fall to about zero, or no row is evidence.
## Prints what it measured. It does not say why.
##
## Usage: godot --path <package copy> --script res://station_draws.gd -- <ex> <ey> <ez> <yaw_deg> <out.json> [path]
##
## `path` (a node path under the main scene, e.g. Bake/Site) buckets THAT node's children instead: the slice's whole
## level sits under one branch, which the two-level default reads as a single row.
## A NOISE FLOOR, measured on its first run: hiding almost any small group dropped 101-110 draws, the warm-up and the
## occluders included -- so a row under about 150 is not a contribution.

const W := 1280
const H := 720
## Settled 30 frames (the price harness's WARMUP) and read once. TWO THINGS TRIED AND RETRACTED, KEPT:
## (1) settling 6 frames -- 3,555 draws where the harness read 2,370 at the same eye and yaw; (2) settling 30 and taking
## the MAXIMUM over 60 frames as the harness does -- still 3,555, and every row's floor rose to ~1,350, because each
## hide-and-show makes a spike frame inside the window. So occlusion settling is not the difference, and neither is
## the scene: price_batch.py copies the same export package (`.level_factory/exports/<pkg>`) -- that guess was checked
## and is wrong. NOT YET KNOWN why the totals differ. Until they agree, only this probe's shares are evidence.
const SETTLE := 30

var _groups: Dictionary = {}


func _initialize() -> void:
	_run()


func _bucket(n: String) -> String:
	var s := n
	var re := RegEx.new()
	re.compile("[_-]?[0-9]+.*$")
	s = re.sub(s, "")
	return s if s != "" else n


func _run() -> void:
	await process_frame
	var a: PackedStringArray = OS.get_cmdline_user_args()
	var eye := Vector3(float(a[0]), float(a[1]), float(a[2]))
	var yaw: float = float(a[3])
	var out_path: String = a[4]
	DisplayServer.window_set_size(Vector2i(W, H))
	root.content_scale_size = Vector2i(W, H)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	var main_path: String = String(ProjectSettings.get_setting("application/run/main_scene", ""))
	var scene: Node = (load(main_path) as PackedScene).instantiate()
	current_scene = scene
	root.add_child(scene)
	for i in range(60):
		await process_frame
	var stack: Array = [scene]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is CharacterBody3D:
			n.get_parent().remove_child(n)
			n.queue_free()
			break
		for c in n.get_children():
			stack.append(c)
	var under: Node = scene.get_node_or_null(NodePath(a[5])) if a.size() > 5 else null
	if under != null:
		for k in under.get_children():
			if k is Node3D:
				var gk: String = _bucket(String(k.name))
				if not _groups.has(gk):
					_groups[gk] = []
				_groups[gk].append(k)
	# two levels: the main scene's children, and each child's children
	for c in (scene.get_children() if under == null else []):
		var kids: Array = c.get_children()
		var named: Array = kids.filter(func(k): return k is Node3D)
		if named.size() > 1:
			for k in named:
				var g: String = String(c.name) + "/" + _bucket(String(k.name))
				if not _groups.has(g):
					_groups[g] = []
				_groups[g].append(k)
		elif c is Node3D:
			var g2: String = _bucket(String(c.name))
			if not _groups.has(g2):
				_groups[g2] = []
			_groups[g2].append(c)
	var cam := Camera3D.new()
	cam.fov = 75.0
	cam.far = 500.0
	root.add_child(cam)
	cam.make_current()
	cam.global_position = eye
	cam.rotation = Vector3(0.0, deg_to_rad(yaw), 0.0)
	var base: Array = await _sample()
	print("VIEW eye=%s yaw=%.1f objects=%d draws=%d" % [str(eye), yaw, base[0], base[1]])
	var rows: Array = []
	var names: Array = _groups.keys()
	names.sort()
	for g in names:
		_vis(g, false)
		var cut: Array = await _sample()
		_vis(g, true)
		var d: int = int(base[1]) - int(cut[1])
		rows.append({"group": g, "branches": (_groups[g] as Array).size(), "draws_attributed": d,
			"objects_attributed": int(base[0]) - int(cut[0])})
	rows.sort_custom(func(x, y): return int(x["draws_attributed"]) > int(y["draws_attributed"]))
	for r in rows:
		if int(r["draws_attributed"]) != 0:
			print("  %-40s branches=%4d draws=%5d objects=%5d" % [r["group"], r["branches"],
				r["draws_attributed"], r["objects_attributed"]])
	for g in names:
		_vis(g, false)
	var allcut: Array = await _sample()
	print("  CONTROL all hidden: objects=%d draws=%d (must be ~0)" % [allcut[0], allcut[1]])
	var fh: FileAccess = FileAccess.open(out_path, FileAccess.WRITE)
	fh.store_string(JSON.stringify({"eye": [eye.x, eye.y, eye.z], "yaw": yaw, "objects": base[0],
		"draws": base[1], "rows": rows, "control": allcut}, "  "))
	fh.close()
	quit(0)


func _vis(g: String, v: bool) -> void:
	for n in _groups[g]:
		(n as Node3D).visible = v


func _sample() -> Array:
	for i in range(SETTLE):
		await process_frame
	return [int(RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_OBJECTS_IN_FRAME)),
		int(RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME))]
