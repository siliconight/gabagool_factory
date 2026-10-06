extends Node
## Where does a split connection break? For each listed shell and point pair:
## bake at every grid origin; at an origin where the pair is connected, take
## the polygon route between them (breadth-first over shared edges, through
## each shared edge's midpoint); at an origin where it is not, walk that same
## route and report the first place it leaves the start's island. Measures;
## names no cause -- neck_finder.py names what stands nearest.
##
## SUPERSEDED, KEPT: the first version measured the closest approach between
## the two islands at the failing origin. That finds the thinnest WALL between
## them as readily as the neck: deli_a03 came out at 0.000 m, at its door,
## but gs_auto_shop, twin_a01 and primos_pizza came out 0.4 to 2.1 m apart
## beside windows and party walls (necks_closest_approach.txt).
##
## Reads res://neck_points.json:
##   {"offsets": [...], "pad": m,
##    "cases": [{"shell": s, "glb": "res://x.glb", "a": [x,y,z], "b": [x,y,z],
##               "above_a": m, "above_b": m, "pair": [name_a, name_b]}]}

const CELL_SIZE := 0.1
const CELL_HEIGHT := 0.15
const AGENT_RADIUS := 0.4
const AGENT_HEIGHT := 1.8
const AGENT_MAX_CLIMB := 0.15
const AGENT_MAX_SLOPE := 55.0
const SNAP_MAX := 2.0
const STEP_M := 0.2


func _ready() -> void:
	await get_tree().process_frame
	var spec: Dictionary = JSON.parse_string(
		FileAccess.get_file_as_string("res://neck_points.json"))
	var offsets: Array = spec["offsets"]
	var pad: float = float(spec["pad"])
	for c in spec["cases"]:
		var case: Dictionary = c
		var rep: Dictionary = await _one(case, offsets, pad)
		rep["shell"] = case["shell"]
		rep["pair"] = case["pair"]
		print("NECK_ROW " + JSON.stringify(rep))
	print("NECK_DONE")
	get_tree().quit()


func _one(case: Dictionary, offsets: Array, pad: float) -> Dictionary:
	var packed: PackedScene = load(str(case["glb"]))
	if packed == null:
		return {"error": "cannot load " + str(case["glb"])}
	var holder := Node3D.new()
	add_child(holder)
	holder.add_child(packed.instantiate())
	await get_tree().physics_frame
	await get_tree().physics_frame
	var src := NavigationMeshSourceGeometryData3D.new()
	NavigationServer3D.parse_source_geometry_data(_new_nm(), src, holder)
	var bounds: AABB = src.get_bounds()
	var a_arr: Array = case["a"]
	var b_arr: Array = case["b"]
	var pa := Vector3(float(a_arr[0]), float(a_arr[1]), float(a_arr[2]))
	var pb := Vector3(float(b_arr[0]), float(b_arr[1]), float(b_arr[2]))
	var above_a: float = float(case.get("above_a", INF))
	var above_b: float = float(case.get("above_b", INF))
	var connected: Array = []
	var pass_bake: Dictionary = {}
	var fail_bake: Dictionary = {}
	for off in offsets:
		var o: Array = off
		var nm := _new_nm()
		nm.filter_baking_aabb = AABB(
			bounds.position - Vector3(pad, pad, pad)
				+ Vector3(float(o[0]), float(o[1]), float(o[2])),
			bounds.size + Vector3(pad, pad, pad) * 2.0)
		NavigationServer3D.bake_from_source_geometry_data(nm, src)
		var adj := _poly_graph(nm)
		var comp := _islands(adj)
		var ha: Dictionary = _snap(nm, pa, above_a)
		var hb: Dictionary = _snap(nm, pb, above_b)
		var poly_a: int = ha["poly"]
		var poly_b: int = hb["poly"]
		var ok_a: bool = poly_a >= 0 and float(ha["dist"]) <= SNAP_MAX
		var ok_b: bool = poly_b >= 0 and float(hb["dist"]) <= SNAP_MAX
		var same: bool = ok_a and ok_b and int(comp[poly_a]) == int(comp[poly_b])
		connected.append(same)
		var bake := {"nm": nm, "adj": adj, "comp": comp, "a": poly_a,
					 "b": poly_b, "offset": o}
		if same and pass_bake.is_empty():
			pass_bake = bake
		if ok_a and ok_b and not same and fail_bake.is_empty():
			fail_bake = bake
	var rep := {"connected": connected}
	if pass_bake.is_empty() or fail_bake.is_empty():
		rep["note"] = "no origin of each kind; nothing to compare"
	else:
		rep["pass_offset"] = pass_bake["offset"]
		rep["fail_offset"] = fail_bake["offset"]
		rep["neck"] = _walk(pass_bake, fail_bake)
	holder.queue_free()
	await get_tree().process_frame
	return rep


func _walk(pass_bake: Dictionary, fail_bake: Dictionary) -> Dictionary:
	var nm_p: NavigationMesh = pass_bake["nm"]
	var route := _bfs(pass_bake["adj"], int(pass_bake["a"]), int(pass_bake["b"]))
	if route.is_empty():
		return {"found": false, "why": "no route at the passing origin"}
	var verts := nm_p.get_vertices()
	var way: Array = [_centroid(nm_p, int(route[0]))]
	for i in range(route.size() - 1):
		way.append(_shared_mid(nm_p, verts, int(route[i]), int(route[i + 1])))
	way.append(_centroid(nm_p, int(route[route.size() - 1])))
	var samples: Array = []
	for i in range(way.size() - 1):
		var p0: Vector3 = way[i]
		var p1: Vector3 = way[i + 1]
		var n := maxi(1, int(ceil(p0.distance_to(p1) / STEP_M)))
		for k in n:
			samples.append(p0.lerp(p1, float(k) / float(n)))
	samples.append(way[way.size() - 1])
	var nm_f: NavigationMesh = fail_bake["nm"]
	var comp_f: Array = fail_bake["comp"]
	var start_isl := int(comp_f[int(fail_bake["a"])])
	var seq: Array = []
	var neck_i := -1
	for i in samples.size():
		var s: Vector3 = samples[i]
		var poly := _under(nm_f, s)
		var isl: int = int(comp_f[poly]) if poly >= 0 else -1
		seq.append(isl)
		if neck_i < 0 and isl != start_isl:
			neck_i = i
	if neck_i < 0:
		return {"found": false, "why": "the passing route stays on one island at the failing origin",
				"samples": samples.size()}
	var at: Vector3 = samples[neck_i]
	var before: Vector3 = samples[maxi(0, neck_i - 1)]
	return {"found": true, "at": [at.x, at.y, at.z], "before": [before.x, before.y, before.z],
			"along_m": snappedf(float(neck_i) * STEP_M, 0.1),
			"route_m": snappedf(float(samples.size()) * STEP_M, 0.1),
			"sequence": _runs(seq)}


func _runs(seq: Array) -> String:
	## "3x5, -1x2, 7x40": island id x run length, in route order.
	var out: Array = []
	var cur: int = int(seq[0])
	var n := 0
	for v in seq:
		var iv: int = v
		if iv == cur:
			n += 1
		else:
			out.append("%dx%d" % [cur, n])
			cur = iv
			n = 1
	out.append("%dx%d" % [cur, n])
	return ", ".join(out)


func _bfs(adj: Array, s: int, t: int) -> Array:
	var prev := {s: -1}
	var queue: Array = [s]
	while not queue.is_empty():
		var n: int = queue.pop_front()
		if n == t:
			break
		for m in adj[n]:
			var mi: int = m
			if not prev.has(mi):
				prev[mi] = n
				queue.append(mi)
	if not prev.has(t):
		return []
	var path: Array = []
	var cur := t
	while cur != -1:
		path.push_front(cur)
		cur = int(prev[cur])
	return path


func _centroid(nm: NavigationMesh, poly: int) -> Vector3:
	var verts := nm.get_vertices()
	var c := Vector3.ZERO
	var ids := nm.get_polygon(poly)
	for vi in ids:
		c += verts[vi]
	return c / float(ids.size())


func _shared_mid(nm: NavigationMesh, verts: PackedVector3Array, u: int,
				 v: int) -> Vector3:
	var pu := nm.get_polygon(u)
	var pv := nm.get_polygon(v)
	var shared: Array = []
	for x in pu:
		if pv.has(x):
			shared.append(verts[x])
	if shared.size() >= 2:
		var s0: Vector3 = shared[0]
		var s1: Vector3 = shared[1]
		return (s0 + s1) / 2.0
	return (_centroid(nm, u) + _centroid(nm, v)) / 2.0


func _under(nm: NavigationMesh, p: Vector3) -> int:
	## The polygon a body standing at p stands on: a downward ray from 0.5 m
	## above, accepting a hit no more than 0.5 m below. -1 means no navmesh.
	var verts := nm.get_vertices()
	for i in nm.get_polygon_count():
		var poly := nm.get_polygon(i)
		if poly.size() < 3:
			continue
		var a: Vector3 = verts[poly[0]]
		for k in range(1, poly.size() - 1):
			var hit: Variant = Geometry3D.ray_intersects_triangle(
				p + Vector3(0, 0.5, 0), Vector3(0, -1, 0), a, verts[poly[k]],
				verts[poly[k + 1]])
			if hit != null:
				var hv: Vector3 = hit
				if hv.y >= p.y - 0.5:
					return i
	return -1


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
