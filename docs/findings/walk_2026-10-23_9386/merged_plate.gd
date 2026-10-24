extends SceneTree
## One merged mesh, whole: its world AABB, surface count, triangle count, and every triangle with all three corners
## between Y_LO and Y_HI (world metres, Y up), grouped into connected-by-shared-vertex islands with each island's
## bounds. Measurements only. NODE is b2's MergedR_250 in cold run 9386's walk copy (finding 4).

const NODE := "_walk/Mission/Bake/Site/b2/MergedR_250"
const Y_LO := 3.28
const Y_HI := 3.31

var _frame := 0


func _initialize() -> void:
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
	var mi: MeshInstance3D = root.get_node(NODE)
	var xf: Transform3D = mi.global_transform
	var faces: PackedVector3Array = mi.mesh.get_faces()
	print("NODE %s aabb %s surfaces %d tris %d" % [NODE, xf * mi.get_aabb(), mi.mesh.get_surface_count(), faces.size() / 3])
	var tris: Array = []
	for i in range(0, faces.size(), 3):
		var a: Vector3 = xf * faces[i]
		var b: Vector3 = xf * faces[i + 1]
		var c: Vector3 = xf * faces[i + 2]
		var ys: Array[float] = [a.y, b.y, c.y]
		if ys.min() >= Y_LO and ys.max() <= Y_HI:
			tris.append([a, b, c])
	# islands: union triangles sharing a vertex (rounded to 1 mm)
	var owner := {}
	var island: Array[int] = []
	for t in range(tris.size()):
		island.append(t)
	for t in range(tris.size()):
		for v in tris[t]:
			var vv: Vector3 = v
			var key := "%d,%d,%d" % [roundi(vv.x * 1000.0), roundi(vv.y * 1000.0), roundi(vv.z * 1000.0)]
			if owner.has(key):
				var a2: int = owner[key]
				while island[a2] != a2:
					a2 = island[a2]
				var b2: int = t
				while island[b2] != b2:
					b2 = island[b2]
				island[b2] = a2
			else:
				owner[key] = t
	var groups := {}
	for t in range(tris.size()):
		var r: int = t
		while island[r] != r:
			r = island[r]
		if not groups.has(r):
			groups[r] = []
		groups[r].append(t)
	for r in groups:
		var lo := Vector3(INF, INF, INF)
		var hi := Vector3(-INF, -INF, -INF)
		for t in groups[r]:
			for v in tris[t]:
				lo = lo.min(v)
				hi = hi.max(v)
		print("ISLAND tris %d lo %s hi %s" % [groups[r].size(), lo, hi])
	_exit(0)
	return true
