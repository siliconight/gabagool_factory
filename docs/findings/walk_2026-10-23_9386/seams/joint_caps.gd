extends SceneTree
## Finding 2: what stands at a wall's module joints that the bake can see, and how the bake was set. For every
## MeshInstance3D triangle facing +X or -X (|n.x| >= 0.95) whose centroid lies within NEAR of a joint X, between the
## wall's face Z and DEPTH behind it, and inside Y0..Y1: its mesh, joint, facing, centroid and area -- an end face
## buried in the wall at the joint, which a texel's rays starting at the face can strike. Then every LightmapGI's
## bake settings. Headless: reads data, draws nothing. Measurements only. Frame: Godot world, metres.
##
##     godot --headless --path <walk copy> --script res://joint_caps.gd -- <wall_z> <depth> <joint x>,<joint x>,...

const NEAR := 0.03
const Y0 := 0.0
const Y1 := 3.4

var _frame := 0
var _wall_z := -6.34
var _depth := -0.4
var _joints: PackedFloat64Array = PackedFloat64Array()


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() >= 3:
		_wall_z = float(args[0])
		_depth = float(args[1])
		for s in args[2].split(","):
			_joints.append(float(s))
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
	var z0: float = minf(_wall_z, _wall_z + _depth)
	var z1: float = maxf(_wall_z, _wall_z + _depth)
	print("JOINT CAPS z %.3f..%.3f y %.1f..%.1f near %.3f joints %s" % [z0, z1, Y0, Y1, NEAR, str(_joints)])
	if _joints.size() == 0:
		print("NO JOINTS GIVEN: nothing measured")
		_exit(2)
		return true
	var found := 0
	for n in root.find_children("*", "MeshInstance3D", true, false):
		var mi: MeshInstance3D = n
		if mi.mesh == null or not (mi.mesh is ArrayMesh) or not mi.is_visible_in_tree():
			continue
		var bb: AABB = mi.global_transform * mi.get_aabb()
		if bb.position.z > z1 + NEAR or bb.end.z < z0 - NEAR:
			continue
		var am: ArrayMesh = mi.mesh
		var xf: Transform3D = mi.global_transform
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
				if absf(fn.x) < 0.95:
					continue
				var cen: Vector3 = (a + b + c) / 3.0
				if cen.z < z0 - NEAR or cen.z > z1 + NEAR or cen.y < Y0 or cen.y > Y1:
					continue
				for j in _joints:
					if absf(cen.x - j) <= NEAR:
						found += 1
						print("CAP %s s%d joint %7.2f facing %s centroid (%.3f,%.3f,%.3f) area %.4f m2 z %.3f..%.3f" % [
							mi.get_path(), s, j, "+x" if fn.x > 0.0 else "-x", cen.x, cen.y, cen.z, cr.length() * 0.5,
							minf(a.z, minf(b.z, c.z)), maxf(a.z, maxf(b.z, c.z))])
	print("end faces at joints: %d" % found)
	for n in root.find_children("*", "LightmapGI", true, false):
		var lm: LightmapGI = n
		print("LIGHTMAPGI %s quality %d bounces %d denoiser %s strength %.3f range %d bias %.5f texel_scale %.3f max_texture_size %d interior %s directional %s use_texture_for_bounces %s" % [
			lm.get_path(), lm.quality, lm.bounces, lm.use_denoiser, lm.denoiser_strength, lm.denoiser_range,
			lm.bias, lm.texel_scale, lm.max_texture_size, lm.interior, lm.directional, lm.use_texture_for_bounces])
	_exit(0)
	return true
