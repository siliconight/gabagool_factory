extends Node
## Bake a scene (a building GLB or a whole site) with the site's NavigationMesh
## settings and report which probe points share a polygon-graph island.
## With a sweep, the bake's grid origin is moved by fractions of a cell through
## filter_baking_aabb, the same geometry each time. Measures; names no cause.
##
## Settings ([bake_sweep] in project.godot):
##   scene  -- res:// path of a PackedScene (GLB or .tscn)
##   points -- JSON {name: [x, y, z]} in the scene's Godot frame
##   sweep  -- JSON list of [dx, dy, dz] grid-origin offsets in metres; empty
##             means one bake over the geometry's own bounds
##   pad    -- metres added around the geometry's bounds for a swept bake

const CELL_SIZE := 0.1
const CELL_HEIGHT := 0.15
const AGENT_RADIUS := 0.4
const AGENT_HEIGHT := 1.8
const AGENT_MAX_CLIMB := 0.15
const AGENT_MAX_SLOPE := 55.0


func _ready() -> void:
	await get_tree().process_frame
	var scene_path: String = ProjectSettings.get_setting("bake_sweep/scene", "")
	var pts: Dictionary = JSON.parse_string(
		str(ProjectSettings.get_setting("bake_sweep/points", "{}")))
	var sweep: Array = JSON.parse_string(
		str(ProjectSettings.get_setting("bake_sweep/sweep", "[]")))
	var pad: float = float(ProjectSettings.get_setting("bake_sweep/pad", 2.0))
	var out := {"scene": scene_path, "bakes": []}
	var packed: PackedScene = load(scene_path)
	var holder := Node3D.new()
	add_child(holder)
	var inst: Node = packed.instantiate()
	holder.add_child(inst)
	await get_tree().physics_frame
	await get_tree().physics_frame
	var src := NavigationMeshSourceGeometryData3D.new()
	var parse_nm := _new_nm()
	NavigationServer3D.parse_source_geometry_data(parse_nm, src, holder)
	var bounds: AABB = src.get_bounds()
	out["bounds"] = [bounds.position.x, bounds.position.y, bounds.position.z,
					 bounds.size.x, bounds.size.y, bounds.size.z]
	if sweep.is_empty():
		out["bakes"].append(_bake(src, null, pts))
	else:
		for off in sweep:
			var o: Array = off
			var box := AABB(bounds.position - Vector3(pad, pad, pad)
				+ Vector3(float(o[0]), float(o[1]), float(o[2])),
				bounds.size + Vector3(pad, pad, pad) * 2.0)
			var rep := _bake(src, box, pts)
			rep["offset"] = o
			out["bakes"].append(rep)
	print("BAKE_SWEEP_BEGIN")
	print(JSON.stringify(out))
	print("BAKE_SWEEP_END")
	get_tree().quit()


func _new_nm() -> NavigationMesh:
	var nm := NavigationMesh.new()
	nm.agent_radius = AGENT_RADIUS
	nm.agent_height = AGENT_HEIGHT
	nm.agent_max_climb = AGENT_MAX_CLIMB
	nm.agent_max_slope = AGENT_MAX_SLOPE
	nm.cell_size = CELL_SIZE
	nm.cell_height = CELL_HEIGHT
	nm.geometry_parsed_geometry_type = NavigationMesh.PARSED_GEOMETRY_BOTH
	return nm


func _bake(src: NavigationMeshSourceGeometryData3D, box: Variant,
		   pts: Dictionary) -> Dictionary:
	var nm := _new_nm()
	if box != null:
		nm.filter_baking_aabb = box
	NavigationServer3D.bake_from_source_geometry_data(nm, src)
	var adj := _poly_graph(nm)
	var comp := _islands(adj)
	var sizes := {}
	for c in comp:
		var ci: int = c
		sizes[ci] = int(sizes.get(ci, 0)) + 1
	var res := {"polys": nm.get_polygon_count(), "islands": sizes.size(),
				"points": {}}
	if bool(ProjectSettings.get_setting("bake_sweep/dump", false)):
		var vs: Array = []
		for v in nm.get_vertices():
			vs.append([snappedf(v.x, 0.001), snappedf(v.y, 0.001), snappedf(v.z, 0.001)])
		var ps: Array = []
		for i in nm.get_polygon_count():
			ps.append([int(comp[i]), Array(nm.get_polygon(i))])
		res["verts"] = vs
		res["polys_list"] = ps
	for k in pts.keys():
		var a: Array = pts[k]
		var p := Vector3(float(a[0]), float(a[1]), float(a[2]))
		var hit := _snap(nm, p, 1.0)
		var poly: int = hit["poly"]
		var isl: int = comp[poly] if poly >= 0 else -1
		res["points"][k] = [isl, int(sizes.get(isl, 0)),
							snappedf(float(hit["dist"]), 0.01)]
	return res


func _poly_graph(nm: NavigationMesh) -> Array:
	var edges := {}
	var adj: Array = []
	for i in nm.get_polygon_count():
		adj.append([])
	for i in nm.get_polygon_count():
		var poly := nm.get_polygon(i)
		for k in poly.size():
			var a: int = poly[k]
			var b: int = poly[(k + 1) % poly.size()]
			var key := "%d_%d" % [mini(a, b), maxi(a, b)]
			if edges.has(key):
				var j: int = edges[key]
				adj[i].append(j)
				adj[j].append(i)
			else:
				edges[key] = i
	return adj


func _islands(adj: Array) -> Array:
	var comp: Array = []
	comp.resize(adj.size())
	comp.fill(-1)
	var next_id := 0
	for s in adj.size():
		if int(comp[s]) != -1:
			continue
		var queue: Array = [s]
		comp[s] = next_id
		while not queue.is_empty():
			var n: int = queue.pop_back()
			for m in adj[n]:
				var mi: int = m
				if int(comp[mi]) == -1:
					comp[mi] = next_id
					queue.append(mi)
		next_id += 1
	return comp


func _snap(nm: NavigationMesh, p: Vector3, max_above: float) -> Dictionary:
	var verts := nm.get_vertices()
	var best := -1
	var best_d := INF
	for i in nm.get_polygon_count():
		var poly := nm.get_polygon(i)
		if poly.size() < 3:
			continue
		var a: Vector3 = verts[poly[0]]
		for k in range(1, poly.size() - 1):
			var b: Vector3 = verts[poly[k]]
			var c: Vector3 = verts[poly[k + 1]]
			var q := Geometry3D.get_closest_point_to_segment(p, a, b)
			var tri: Variant = Geometry3D.ray_intersects_triangle(
				p + Vector3(0, 0.5, 0), Vector3(0, -1, 0), a, b, c)
			if tri != null:
				q = tri
			else:
				var q2 := Geometry3D.get_closest_point_to_segment(p, b, c)
				var q3 := Geometry3D.get_closest_point_to_segment(p, c, a)
				if p.distance_squared_to(q2) < p.distance_squared_to(q):
					q = q2
				if p.distance_squared_to(q3) < p.distance_squared_to(q):
					q = q3
			if q.y - p.y > max_above:
				continue
			var d := p.distance_to(q)
			if d < best_d:
				best_d = d
				best = i
	return {"poly": best, "dist": best_d}
