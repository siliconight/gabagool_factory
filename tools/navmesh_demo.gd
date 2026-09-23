extends SceneTree

## BAKE A NAVMESH FROM A SHIPPED PACKAGE AND WALK IT, so the claim "our levels
## are navigable" is a measurement rather than a slide.
##
## WHAT IT IS FOR. The package ships `navmesh: bake_required` and no
## `NavigationRegion3D` (roadmap 172 and the notes beside it), so nobody can
## see a navmesh by opening the level. This bakes one with THIS PIPELINE'S OWN
## agent dimensions, paths a body from the player start to every objective and
## extraction anchor, and reports what it found. The demo project it leaves
## behind can be opened, so the blue overlay is visible to a human as well.
##
## THE PARAMETERS ARE THE CONTRACT'S, PASSED IN, NOT GUESSED HERE.
## `deli_counter/agent_contract.json` is the single source of truth for the
## body and every clearance derived from it, and it does not ship in the
## package, so the Python driver reads it and hands the numbers over. A second
## spelling of them in this file is exactly the drift CLAUDE.md keeps
## recording, and a bake at Godot's defaults would answer a different question:
## its max slope is 45 degrees against this pipeline's 55, and 20 of 38
## buildings emit stair ramps between 45.0 and 51.3, so the defaults would
## disconnect stairs this pipeline considers walkable.
##
## IT REFUSES RATHER THAN REPORTING A GOOD NUMBER IT DID NOT EARN. A bake that
## produces no polygons, a scene that will not load, or a run with no start
## anchor writes `ok: false` with a reason. A demo that cannot fail is a slide.
##
## Usage:
##   godot --headless --path <pkg> --script res://navmesh_demo.gd -- <out.json>
##     <radius> <height> <max_climb> <max_slope_deg> <cell_size> <cell_height>

const PATH_OPTIMIZE := true
#: A path is "found" when the server returns at least this many points. One
#: point means the query snapped to a polygon and went nowhere.
const MIN_PATH_POINTS := 2
#: How far an anchor may be from the mesh and still count as on it. The bake
#: shrinks by the agent radius, so an anchor authored against a wall sits just
#: off the polygon that serves it.
const SNAP_M := 2.0


func _initialize() -> void:
	var a: PackedStringArray = OS.get_cmdline_user_args()
	if a.size() < 7:
		print("[navdemo] USAGE: <out.json> <radius> <height> <climb> <slope> <cell> <cellh>")
		quit(2)
		return
	_run(a[0], float(a[1]), float(a[2]), float(a[3]), float(a[4]),
		float(a[5]), float(a[6]))


func _walk(n: Node, out: Array) -> void:
	out.append(n)
	for c in n.get_children():
		_walk(c, out)


func _anchors(kinds: Array) -> Array:
	## Anchors of the given types, as [type, Vector3]. Read from the package's
	## own `gameplay_anchors.json` rather than from node names, because that
	## file is the handover contract and node names are for humans.
	var out: Array = []
	var fh: FileAccess = FileAccess.open("res://gameplay_anchors.json",
		FileAccess.READ)
	if fh == null:
		return out
	var parsed = JSON.parse_string(fh.get_as_text())
	fh.close()
	if typeof(parsed) != TYPE_DICTIONARY:
		return out
	for rec in (parsed.get("anchors", []) as Array):
		var kind: String = String(rec.get("anchor_type", ""))
		if not kinds.has(kind):
			continue
		var tf = rec.get("transform", {})
		var t = tf.get("translation", tf.get("position", null)) if typeof(tf) == TYPE_DICTIONARY else null
		if typeof(t) != TYPE_ARRAY or (t as Array).size() < 3:
			continue
		out.append([kind, Vector3(float(t[0]), float(t[1]), float(t[2]))])
	return out


func _run(out_path: String, radius: float, height: float, climb: float,
		slope: float, cell: float, cell_h: float) -> void:
	await process_frame
	var report: Dictionary = {
		"schema": "lf.navmesh_demo.v1", "ok": false, "error": "",
		"agent": {"radius_m": radius, "height_m": height,
			"max_climb_m": climb, "max_slope_deg": slope,
			"cell_size_m": cell, "cell_height_m": cell_h},
		"polygons": 0, "bake_ms": 0.0, "vertices": 0,
		"starts": 0, "destinations": 0, "reached": 0, "routes": [],
		# STAIRS ARE THE POINT, not a detail. A mesh that covers one floor
		# looks correct in a picture and proves nothing about a building.
		"mesh_y_min": 0.0, "mesh_y_max": 0.0, "storey_bands": 0,
		"routes_that_climb": 0,
		# The documented tension, measured rather than assumed: the bake walks
		# up to `agent_max_slope` (55) and a Godot body stands on
		# `floor_max_angle` (45, engine default, set by no controller here).
		# A stair between the two is connected on the navmesh and slid down by
		# a player. CLAUDE.md records 20 of 38 buildings emitting ramps at
		# 45.0-51.3 degrees.
		"stair_ramps": 0, "stair_ramps_over_45deg": 0,
		"steepest_stair_deg": 0.0,
	}
	var main_scene: String = String(ProjectSettings.get_setting(
		"application/run/main_scene", ""))
	var ps: PackedScene = load(main_scene) as PackedScene
	if ps == null:
		report["error"] = "main_scene %s did not load" % main_scene
		_write(out_path, report)
		quit(0)
		return
	var scene: Node = ps.instantiate()
	root.add_child(scene)
	for i in range(20):
		await process_frame

	var nm := NavigationMesh.new()
	nm.cell_size = cell
	nm.cell_height = cell_h
	nm.agent_radius = radius
	nm.agent_height = height
	nm.agent_max_climb = climb
	nm.agent_max_slope = slope
	# PHYSICS, not visual meshes. Godot's own navigation documentation
	# recommends it for cost, and this package ships `-colonly` bodies for
	# exactly the surfaces a body stands on, so it is also the more faithful
	# source: it is what the walker collides with.
	nm.geometry_parsed_geometry_type = NavigationMesh.PARSED_GEOMETRY_STATIC_COLLIDERS
	nm.geometry_source_geometry_mode = NavigationMesh.SOURCE_GEOMETRY_ROOT_NODE_CHILDREN

	var region := NavigationRegion3D.new()
	region.navigation_mesh = nm
	root.add_child(region)
	# The region parses its OWN children, so the level moves under it.
	root.remove_child(scene)
	region.add_child(scene)
	for i in range(5):
		await process_frame

	var t0: int = Time.get_ticks_usec()
	# on_thread = false: SceneTree parsing is main-thread only (Godot docs),
	# and a synchronous bake is what makes the timing below mean anything.
	region.bake_navigation_mesh(false)
	var baked: int = Time.get_ticks_usec() - t0
	report["bake_ms"] = snappedf(float(baked) / 1000.0, 0.01)
	report["polygons"] = nm.get_polygon_count()
	report["vertices"] = nm.get_vertices().size()

	if int(report["polygons"]) == 0:
		report["error"] = ("the bake produced no polygons -- refusing to "
			+ "report a navigable level that has no navigation mesh")
		_write(out_path, report)
		print("[navdemo] BAKE EMPTY: 0 polygons")
		quit(0)
		return

	# How far up does the mesh actually reach, and does it come in layers?
	var vy: PackedVector3Array = nm.get_vertices()
	var ylo: float = 1e9
	var yhi: float = -1e9
	var bands: Dictionary = {}
	for v in vy:
		ylo = minf(ylo, v.y)
		yhi = maxf(yhi, v.y)
		# a band is a half-metre bucket; storeys here are 2.9-3.4 m apart, so
		# this separates floors without pretending to identify them
		bands[int(floor(v.y * 2.0))] = true
	report["mesh_y_min"] = snappedf(ylo, 0.01)
	report["mesh_y_max"] = snappedf(yhi, 0.01)
	report["storey_bands"] = bands.size()

	# Every stair ramp the package ships, and its pitch. `stair<n>ramp_<s>` is
	# Deli Counter's smooth collider over the nosings -- the surface a body
	# actually meets -- so its pitch is the number that decides whether a
	# player climbs or slides, independent of what the navmesh connected.
	var nodes2: Array = []
	_walk(scene, nodes2)
	var ramps: int = 0
	var steep: int = 0
	var worst: float = 0.0
	for n in nodes2:
		if not String(n.name).contains("ramp"):
			continue
		var v3: VisualInstance3D = n as VisualInstance3D
		if v3 == null:
			continue
		var b: AABB = v3.global_transform * v3.get_aabb()
		var run: float = maxf(b.size.x, b.size.z)
		if run <= 0.01 or b.size.y <= 0.01:
			continue
		ramps += 1
		var deg: float = rad_to_deg(atan(b.size.y / run))
		worst = maxf(worst, deg)
		if deg > 45.0:
			steep += 1
	report["stair_ramps"] = ramps
	report["stair_ramps_over_45deg"] = steep
	report["steepest_stair_deg"] = snappedf(worst, 0.1)

	for i in range(10):
		await physics_frame
	var map: RID = region.get_navigation_map()
	NavigationServer3D.map_force_update(map)
	await physics_frame

	var starts: Array = _anchors(["player_start", "crew_spawn"])
	var dests: Array = _anchors(["objective", "extraction"])
	report["starts"] = starts.size()
	report["destinations"] = dests.size()
	if starts.is_empty():
		report["error"] = "no player_start or crew_spawn anchor to route from"
		_write(out_path, report)
		quit(0)
		return

	var origin: Vector3 = starts[0][1]
	var reached: int = 0
	var climbed: int = 0
	for d in dests:
		var target: Vector3 = d[1]
		var pts: PackedVector3Array = NavigationServer3D.map_get_path(
			map, origin, target, PATH_OPTIMIZE)
		var ok: bool = pts.size() >= MIN_PATH_POINTS
		var length: float = 0.0
		for i in range(1, pts.size()):
			length += pts[i].distance_to(pts[i - 1])
		# Did it actually arrive, or stop at the nearest polygon?
		var gap: float = (pts[pts.size() - 1].distance_to(target)
			if pts.size() > 0 else 1e9)
		if ok and gap > SNAP_M:
			ok = false
		if ok:
			reached += 1
		# Does the route go UP? A level whose every route stays on one floor
		# has not demonstrated a building.
		var plo: float = 1e9
		var phi: float = -1e9
		for pt in pts:
			plo = minf(plo, pt.y)
			phi = maxf(phi, pt.y)
		var climb: float = (phi - plo) if pts.size() > 0 else 0.0
		if ok and climb > 1.0:
			climbed += 1
		report["routes"].append({
			"to": String(d[0]), "reached": ok,
			"points": pts.size(),
			"length_m": snappedf(length, 0.01),
			"climb_m": snappedf(climb, 0.01),
			"gap_m": snappedf(minf(gap, 999.0), 0.01),
		})
	report["reached"] = reached
	report["routes_that_climb"] = climbed
	report["ok"] = true
	_write(out_path, report)
	print("[navdemo] %d polygon(s), %d vertices, baked in %.2f ms"
		% [int(report["polygons"]), int(report["vertices"]),
			float(report["bake_ms"])])
	print("[navdemo] mesh spans y %.2f..%.2f in %d half-metre band(s)"
		% [float(report["mesh_y_min"]), float(report["mesh_y_max"]),
			int(report["storey_bands"])])
	print("[navdemo] routed from %s: %d of %d destination(s) reached, %d of them climbing"
		% [str(origin), reached, dests.size(), climbed])
	print("[navdemo] stair ramps %d, steepest %.1f deg, %d over 45 (connected by the bake at %.0f, slid down by a body at 45)"
		% [int(report["stair_ramps"]), float(report["steepest_stair_deg"]),
			int(report["stair_ramps_over_45deg"]), slope])
	quit(0)


func _write(out_path: String, report: Dictionary) -> void:
	var fh: FileAccess = FileAccess.open(out_path, FileAccess.WRITE)
	if fh == null:
		push_error("[navdemo] could not write %s" % out_path)
		return
	fh.store_string(JSON.stringify(report, "  "))
	fh.close()
