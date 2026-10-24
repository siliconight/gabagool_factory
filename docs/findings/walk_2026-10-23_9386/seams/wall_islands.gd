extends SceneTree
## Finding 2: the lightmap islands of one wall. Every MeshInstance3D triangle lying on a plane of constant Z (within
## TOL of WALL_Z, facing +Z or -Z, inside the X and Y box), grouped per mesh surface into islands -- triangles joined
## by shared vertex indices -- each printed with its mesh, its world X span (Godot metres) and its UV2 rectangle. Where
## two islands meet along the wall, the bake's texels change hands; a band that sits exactly there is a lightmap seam.
## Headless: reads mesh data, draws nothing. Measurements only.
##
##     godot --headless --path <walk copy> --script res://wall_islands.gd -- <wall_z> <x0> <x1>

const TOL := 0.25
const Y0 := 0.0
const Y1 := 3.4

var _frame := 0
var _wall_z := -10.6
var _x0 := -20.0
var _x1 := 10.0


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() >= 3:
		_wall_z = float(args[0])
		_x0 = float(args[1])
		_x1 = float(args[2])
	var ps: PackedScene = load("res://_walk.tscn")
	root.add_child(ps.instantiate())


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _process(_d: float) -> bool:
	_frame += 1
	if _frame < 3:
		return false
	print("WALL z=%.2f x %.2f..%.2f y %.1f..%.1f tol %.2f" % [_wall_z, _x0, _x1, Y0, Y1, TOL])
	for n in root.find_children("*", "MeshInstance3D", true, false):
		var mi: MeshInstance3D = n
		if mi.mesh == null or not (mi.mesh is ArrayMesh) or not mi.is_visible_in_tree():
			continue
		var bb: AABB = mi.global_transform * mi.get_aabb()
		if bb.position.z - TOL > _wall_z or bb.end.z + TOL < _wall_z:
			continue
		var am: ArrayMesh = mi.mesh
		var xf: Transform3D = mi.global_transform
		for s in am.get_surface_count():
			var arr: Array = am.surface_get_arrays(s)
			var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
			var uv2v = arr[Mesh.ARRAY_TEX_UV2]
			var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX] if arr[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
			if uv2v == null or (uv2v as PackedVector2Array).size() == 0:
				continue
			var uv2: PackedVector2Array = uv2v
			if idx.size() == 0:
				for i in verts.size():
					idx.append(i)
			# union-find over vertex indices, triangles on the wall only
			var parent := {}
			var tris: Array = []
			for t in range(0, idx.size(), 3):
				var a: Vector3 = xf * verts[idx[t]]
				var b: Vector3 = xf * verts[idx[t + 1]]
				var c: Vector3 = xf * verts[idx[t + 2]]
				var nrm: Vector3 = (b - a).cross(c - a)
				if nrm.length() < 1e-9:
					continue
				nrm = nrm.normalized()
				if absf(nrm.z) < 0.95:
					continue
				var mz := (a.z + b.z + c.z) / 3.0
				if absf(mz - _wall_z) > TOL:
					continue
				var mx := (a.x + b.x + c.x) / 3.0
				var my := (a.y + b.y + c.y) / 3.0
				if mx < _x0 or mx > _x1 or my < Y0 or my > Y1:
					continue
				tris.append([idx[t], idx[t + 1], idx[t + 2], a, b, c])
				for k in [idx[t], idx[t + 1], idx[t + 2]]:
					if not parent.has(k):
						parent[k] = k
				_union(parent, idx[t], idx[t + 1])
				_union(parent, idx[t], idx[t + 2])
			var islands := {}
			for tr in tris:
				var r: int = _find(parent, tr[0])
				if not islands.has(r):
					islands[r] = {"xmin": INF, "xmax": -INF, "u0": INF, "v0": INF, "u1": -INF, "v1": -INF, "n": 0}
				var isl: Dictionary = islands[r]
				isl["n"] = int(isl["n"]) + 1
				for j in 3:
					var p: Vector3 = tr[3 + j]
					var uv: Vector2 = uv2[tr[j]]
					isl["xmin"] = minf(isl["xmin"], p.x)
					isl["xmax"] = maxf(isl["xmax"], p.x)
					isl["u0"] = minf(isl["u0"], uv.x)
					isl["v0"] = minf(isl["v0"], uv.y)
					isl["u1"] = maxf(isl["u1"], uv.x)
					isl["v1"] = maxf(isl["v1"], uv.y)
			for r in islands:
				var isl: Dictionary = islands[r]
				print("ISLAND %s s%d tris %d x %.3f..%.3f uv2 (%.4f,%.4f)-(%.4f,%.4f)" % [
					mi.get_path(), s, isl["n"], isl["xmin"], isl["xmax"], isl["u0"], isl["v0"], isl["u1"], isl["v1"]])
	_exit(0)
	return true


func _find(parent: Dictionary, k: int) -> int:
	var r: int = k
	while int(parent[r]) != r:
		r = int(parent[r])
	return r


func _union(parent: Dictionary, a: int, b: int) -> void:
	var ra := _find(parent, a)
	var rb := _find(parent, b)
	if ra != rb:
		parent[rb] = ra
