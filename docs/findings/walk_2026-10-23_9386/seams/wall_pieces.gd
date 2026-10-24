extends SceneTree
## Finding 2: which meshes make up one wall face, and where each begins and ends along it. For a wall plane of
## constant X or Z (axis "x" or "z", at <at>), every visible MeshInstance3D with a triangle lying on that plane (within
## TOL, facing along the axis) inside the box <lo>..<hi> along the wall and Y0..Y1: its path, its span along the wall
## (the other horizontal axis), its span in Y, and its triangle count there. Where one mesh ends and another begins
## the bake's texels change hands between two lightmap rects. Headless: reads mesh data, draws nothing.
## Frame: Godot world, metres. Measurements only.
##
##     godot --headless --path <walk copy> --script res://wall_pieces.gd -- <x|z> <at> <lo> <hi>

const TOL := 0.06
const Y0 := 0.0
const Y1 := 3.4

var _frame := 0
var _axis := "x"
var _at := 4.85
var _lo := -7.0
var _hi := 1.0


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() >= 4:
		_axis = args[0]
		_at = float(args[1])
		_lo = float(args[2])
		_hi = float(args[3])
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
	if _axis != "x" and _axis != "z":
		print("AXIS MUST BE x OR z, not %s: nothing measured" % _axis)
		_exit(2)
		return true
	var ax: int = 0 if _axis == "x" else 2
	var along: int = 2 if _axis == "x" else 0
	print("WALL %s = %.3f, along %s %.2f..%.2f, y %.1f..%.1f, tol %.2f" % [_axis, _at, "z" if _axis == "x" else "x", _lo, _hi, Y0, Y1, TOL])
	var rows: Array = []
	for n in root.find_children("*", "MeshInstance3D", true, false):
		var mi: MeshInstance3D = n
		if mi.mesh == null or not (mi.mesh is ArrayMesh) or not mi.is_visible_in_tree():
			continue
		var bb: AABB = mi.global_transform * mi.get_aabb()
		if bb.position[ax] - TOL > _at or bb.end[ax] + TOL < _at:
			continue
		var am: ArrayMesh = mi.mesh
		var xf: Transform3D = mi.global_transform
		var a_lo := INF
		var a_hi := -INF
		var y_lo := INF
		var y_hi := -INF
		var count := 0
		var facing := ""
		for s in am.get_surface_count():
			var arr: Array = am.surface_get_arrays(s)
			var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
			var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX] if arr[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
			if idx.size() == 0:
				for i in verts.size():
					idx.append(i)
			for t in range(0, idx.size(), 3):
				var a: Vector3 = xf * verts[idx[t]]
				var b: Vector3 = xf * verts[idx[t + 1]]
				var c: Vector3 = xf * verts[idx[t + 2]]
				var cr: Vector3 = (b - a).cross(c - a)
				if cr.length() < 1e-9:
					continue
				var fn: Vector3 = cr.normalized()
				if absf(fn[ax]) < 0.95:
					continue
				var cen: Vector3 = (a + b + c) / 3.0
				if absf(cen[ax] - _at) > TOL or cen[along] < _lo or cen[along] > _hi or cen.y < Y0 or cen.y > Y1:
					continue
				count += 1
				facing = "+" if fn[ax] > 0.0 else "-"
				for v in [a, b, c]:
					a_lo = minf(a_lo, v[along])
					a_hi = maxf(a_hi, v[along])
					y_lo = minf(y_lo, v.y)
					y_hi = maxf(y_hi, v.y)
		if count > 0:
			rows.append([a_lo, "PIECE %s facing %s%s  along %.3f..%.3f  y %.3f..%.3f  triangles %d" % [
				mi.get_path(), facing, _axis, a_lo, a_hi, y_lo, y_hi, count]])
	rows.sort_custom(func(p: Array, q: Array) -> bool: return float(p[0]) < float(q[0]))
	for r in rows:
		print(r[1])
	print("pieces: %d" % rows.size())
	_exit(0)
	return true
