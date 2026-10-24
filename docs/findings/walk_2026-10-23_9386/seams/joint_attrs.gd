extends SceneTree
## Finding 2: what a wall's vertices carry either side of each module joint. For every MeshInstance3D triangle lying
## on the wall plane (constant Z within TOL of WALL_Z, facing +Z or -Z, inside the X and Y box), each vertex within
## NEAR of a joint X is printed with the side of the joint its triangle lies on, its world normal, its vertex colour
## and its UV; then each surface's material. If the bands are a step in what the modules carry -- a normal tilted
## module to module, a wear colour per module -- it is in these numbers on both sides of a joint and absent in the
## middle of a module. Headless: reads mesh data, draws nothing. Measurements only.
## Frame: Godot world, metres. Colour: the mesh's ARRAY_COLOR, 0..1, "-" when the surface has none.
##
##     godot --headless --path <walk copy> --script res://joint_attrs.gd -- <wall_z> <x0> <x1> <joint x>,<joint x>,...

const TOL := 0.25
const Y0 := 0.0
const Y1 := 3.4
const NEAR := 0.02

var _frame := 0
var _wall_z := -6.34
var _x0 := -11.2
var _x1 := 5.2
var _joints: PackedFloat64Array = PackedFloat64Array()


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() >= 4:
		_wall_z = float(args[0])
		_x0 = float(args[1])
		_x1 = float(args[2])
		for s in args[3].split(","):
			_joints.append(float(s))
	var ps: PackedScene = load("res://_walk.tscn")
	root.add_child(ps.instantiate())


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _fmt3(v: Vector3) -> String:
	return "(%.4f,%.4f,%.4f)" % [v.x, v.y, v.z]


func _process(_d: float) -> bool:
	_frame += 1
	if _frame < 3:
		return false
	print("WALL z=%.2f x %.2f..%.2f y %.1f..%.1f tol %.2f near %.3f joints %s" % [_wall_z, _x0, _x1, Y0, Y1, TOL, NEAR, str(_joints)])
	if _joints.size() == 0:
		print("NO JOINTS GIVEN: nothing measured")
		_exit(2)
		return true
	var seen := 0
	for n in root.find_children("*", "MeshInstance3D", true, false):
		var mi: MeshInstance3D = n
		if mi.mesh == null or not (mi.mesh is ArrayMesh) or not mi.is_visible_in_tree():
			continue
		var bb: AABB = mi.global_transform * mi.get_aabb()
		if bb.position.z - TOL > _wall_z or bb.end.z + TOL < _wall_z:
			continue
		var am: ArrayMesh = mi.mesh
		var xf: Transform3D = mi.global_transform
		var nb: Basis = xf.basis.inverse().transposed()
		for s in am.get_surface_count():
			var arr: Array = am.surface_get_arrays(s)
			var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
			var nrmv = arr[Mesh.ARRAY_NORMAL]
			var colv = arr[Mesh.ARRAY_COLOR]
			var uvv = arr[Mesh.ARRAY_TEX_UV]
			var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX] if arr[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
			if idx.size() == 0:
				for i in verts.size():
					idx.append(i)
			var has_n: bool = nrmv != null and (nrmv as PackedVector3Array).size() == verts.size()
			var has_c: bool = colv != null and (colv as PackedColorArray).size() == verts.size()
			var has_uv: bool = uvv != null and (uvv as PackedVector2Array).size() == verts.size()
			var lines: Array = []
			for t in range(0, idx.size(), 3):
				var a: Vector3 = xf * verts[idx[t]]
				var b: Vector3 = xf * verts[idx[t + 1]]
				var c: Vector3 = xf * verts[idx[t + 2]]
				var fn: Vector3 = (b - a).cross(c - a)
				if fn.length() < 1e-9:
					continue
				fn = fn.normalized()
				if absf(fn.z) < 0.95:
					continue
				var cen: Vector3 = (a + b + c) / 3.0
				if absf(cen.z - _wall_z) > TOL or cen.x < _x0 or cen.x > _x1 or cen.y < Y0 or cen.y > Y1:
					continue
				for k in 3:
					var vi: int = idx[t + k]
					var w: Vector3 = xf * verts[vi]
					for j in _joints:
						if absf(w.x - j) > NEAR:
							continue
						var side := "L" if cen.x < j else "R"
						var nrm := "-"
						if has_n:
							nrm = _fmt3((nb * (nrmv as PackedVector3Array)[vi]).normalized())
						var col := "-"
						if has_c:
							var cc: Color = (colv as PackedColorArray)[vi]
							col = "(%.4f,%.4f,%.4f,%.4f)" % [cc.r, cc.g, cc.b, cc.a]
						var uv := "-"
						if has_uv:
							var u: Vector2 = (uvv as PackedVector2Array)[vi]
							uv = "(%.4f,%.4f)" % [u.x, u.y]
						lines.append("joint %7.2f %s  y %.3f  face_n %s  n %s  color %s  uv %s" % [j, side, w.y, _fmt3(fn), nrm, col, uv])
			if lines.size() == 0:
				continue
			lines.sort()
			var mat: Material = mi.get_active_material(s)
			var mname := "null"
			if mat != null:
				mname = "%s %s" % [mat.get_class(), mat.resource_name]
				if mat is BaseMaterial3D:
					var b3: BaseMaterial3D = mat
					mname += " vertex_color_use_as_albedo %s uv1_triplanar %s uv1_world_triplanar %s uv1_scale %s uv1_offset %s" % [
						b3.vertex_color_use_as_albedo, b3.uv1_triplanar, b3.uv1_world_triplanar, str(b3.uv1_scale), str(b3.uv1_offset)]
				if mat is ShaderMaterial and (mat as ShaderMaterial).shader != null:
					mname += " shader " + (mat as ShaderMaterial).shader.resource_path
			print("MESH %s s%d material %s  normals %s colors %s uv %s" % [mi.get_path(), s, mname, has_n, has_c, has_uv])
			for l in lines:
				print("  " + l)
			seen += lines.size()
	print("vertices at joints: %d" % seen)
	_exit(0)
	return true
