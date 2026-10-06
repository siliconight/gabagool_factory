extends Node
## Bake every listed shell at several grid origins with the site's navmesh
## settings and record, for each of its probe points, the polygon-graph island
## it stands on at each origin. Measures; names no cause. The Python driver
## (grid_census.py) decides what changed between origins.
##
## Reads res://census_points.json:
##   {"offsets": [[dx, dy, dz], ...], "pad": m,
##    "shells": {name: {"glb": "res://x.glb", "points": {pname: [x, y, z]}}}}
## Points are in the shell's Godot frame. Prints one fenced JSON line per
## shell, so a crash part-way still leaves every finished shell readable.

const CELL_SIZE := 0.1
const CELL_HEIGHT := 0.15
const AGENT_RADIUS := 0.4
const AGENT_HEIGHT := 1.8
const AGENT_MAX_CLIMB := 0.15
const AGENT_MAX_SLOPE := 55.0
const SNAP_MAX := 1.0


func _ready() -> void:
	await get_tree().process_frame
	var spec: Dictionary = JSON.parse_string(
		FileAccess.get_file_as_string("res://census_points.json"))
	var offsets: Array = spec["offsets"]
	var pad: float = float(spec["pad"])
	var shells: Dictionary = spec["shells"]
	for shell_name in shells.keys():
		var sh: Dictionary = shells[shell_name]
		var rep: Dictionary = await _census_one(str(sh["glb"]), sh["points"],
			offsets, pad)
		rep["shell"] = shell_name
		print("CENSUS_ROW " + JSON.stringify(rep))
	print("CENSUS_DONE")
	get_tree().quit()


func _census_one(glb: String, pts: Dictionary, offsets: Array,
				 pad: float) -> Dictionary:
	var packed: PackedScene = load(glb)
	if packed == null:
		return {"error": "cannot load " + glb}
	var holder := Node3D.new()
	add_child(holder)
	holder.add_child(packed.instantiate())
	await get_tree().physics_frame
	await get_tree().physics_frame
	var src := NavigationMeshSourceGeometryData3D.new()
	NavigationServer3D.parse_source_geometry_data(_new_nm(), src, holder)
	var bounds: AABB = src.get_bounds()
	var bakes: Array = []
	for off in offsets:
		var o: Array = off
		var nm := _new_nm()
		nm.filter_baking_aabb = AABB(
			bounds.position - Vector3(pad, pad, pad)
				+ Vector3(float(o[0]), float(o[1]), float(o[2])),
			bounds.size + Vector3(pad, pad, pad) * 2.0)
		NavigationServer3D.bake_from_source_geometry_data(nm, src)
		var comp := _islands(_poly_graph(nm))
		var row := {}
		for k in pts.keys():
			var a: Array = pts[k]
			var hit := _snap(nm, Vector3(float(a[0]), float(a[1]), float(a[2])))
			var poly: int = hit["poly"]
			var d: float = hit["dist"]
			row[k] = int(comp[poly]) if poly >= 0 and d <= SNAP_MAX else -1
		bakes.append({"polys": nm.get_polygon_count(), "islands": row})
	holder.queue_free()
	await get_tree().process_frame
	return {"bakes": bakes}


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


func _snap(nm: NavigationMesh, p: Vector3) -> Dictionary:
	## Nearest polygon by its true closest point, skipping any surface more
	## than 1 m above p (the ceiling over a storey is not its floor).
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
			if q.y - p.y > 1.0:
				continue
			var d := p.distance_to(q)
			if d < best_d:
				best_d = d
				best = i
	return {"poly": best, "dist": best_d}
