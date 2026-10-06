extends Node
## Bake one imported building three ways and report which probe points share
## a navmesh island. Measures; names no cause.
##
## Settings (project.godot [bake_modes]): glb (res:// path), points (JSON
## {name: [x, y, z]} in the building's Godot frame), skip (JSON list of node
## name substrings whose collision shapes are removed before the bake).

const CELL_SIZE := 0.1
const CELL_HEIGHT := 0.15
const AGENT_RADIUS := 0.4
const AGENT_HEIGHT := 1.8
const AGENT_MAX_CLIMB := 0.15
const AGENT_MAX_SLOPE := 55.0


func _ready() -> void:
	await get_tree().process_frame
	var glb: String = ProjectSettings.get_setting("bake_modes/glb", "")
	var pts_json: String = ProjectSettings.get_setting("bake_modes/points", "{}")
	var skip_json: String = ProjectSettings.get_setting("bake_modes/skip", "[]")
	var pts: Dictionary = JSON.parse_string(pts_json)
	var skip: Array = JSON.parse_string(skip_json)
	var out := {"glb": glb, "modes": {}, "removed": []}
	var packed: PackedScene = load(glb)
	var holder := Node3D.new()
	add_child(holder)
	var inst: Node3D = packed.instantiate()
	holder.add_child(inst)
	await get_tree().physics_frame
	await get_tree().physics_frame
	if not skip.is_empty():
		out["removed"] = _remove_shapes(inst, skip)
	for mode in [0, 1, 2]:
		out["modes"][str(mode)] = _bake(holder, mode, pts)
	print("BAKE_MODES_BEGIN")
	print(JSON.stringify(out))
	print("BAKE_MODES_END")
	get_tree().quit()


func _remove_shapes(node: Node, skip: Array) -> Array:
	var removed: Array = []
	var stack: Array = [node]
	while not stack.is_empty():
		var nd: Node = stack.pop_back()
		for c in nd.get_children():
			stack.append(c)
		if nd is CollisionShape3D:
			var path_s: String = str(nd.get_parent().name) + "/" + str(nd.name)
			for s in skip:
				var sub: String = s
				if path_s.contains(sub):
					(nd as CollisionShape3D).disabled = true
					nd.get_parent().remove_child(nd)
					removed.append(path_s)
					break
	return removed


func _bake(root_node: Node, mode: int, pts: Dictionary) -> Dictionary:
	var nm := NavigationMesh.new()
	nm.agent_radius = AGENT_RADIUS
	nm.agent_height = AGENT_HEIGHT
	nm.agent_max_climb = AGENT_MAX_CLIMB
	nm.agent_max_slope = AGENT_MAX_SLOPE
	nm.cell_size = CELL_SIZE
	nm.cell_height = CELL_HEIGHT
	nm.geometry_parsed_geometry_type = mode
	var src := NavigationMeshSourceGeometryData3D.new()
	NavigationServer3D.parse_source_geometry_data(nm, src, root_node)
	NavigationServer3D.bake_from_source_geometry_data(nm, src)
	var adj := _poly_graph(nm)
	var comp := _islands(adj)
	var sizes := {}
	for c in comp:
		var ci: int = c
		sizes[ci] = int(sizes.get(ci, 0)) + 1
	var res := {"polys": nm.get_polygon_count(), "islands": sizes.size(),
				"points": {}}
	for k in pts.keys():
		var a: Array = pts[k]
		var p := Vector3(float(a[0]), float(a[1]), float(a[2]))
		var hit := _snap(nm, p, 1.0)
		var poly: int = hit["poly"]
		var isl: int = comp[poly] if poly >= 0 else -1
		res["points"][k] = {"island": isl,
							"island_polys": int(sizes.get(isl, 0)),
							"snap_m": snappedf(float(hit["dist"]), 0.01)}
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
