extends SceneTree
## The vertex colours and normals of a merged mesh's triangles near a world point. Prints and stops.
##
##     godot --headless --path <walk copy> --script res://vertex_probe.gd -- <scene> <mesh node path> <x> <y> <z> <r>
##
## The mesh is named by its path under the scene's root (`Level/Bake/Site/b1/MergedR_150`): a merged mesh's name
## is unique only within its building, and the first draft's search by name found the deli's.
##
## For every triangle of the named MeshInstance3D whose centroid (world space) lies within <r> m of the point:
## its face normal in world space, the mean of its corners' COLOR_0 and the material's albedo colour; then a count of
## those triangles by normal direction, with their mean STORED normal (what shading uses), the first two's UVs,
## and the material's UV mapping. Draws no conclusion.


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _find(n: Node, name: String) -> Node:
	if String(n.name) == name:
		return n
	for c in n.get_children():
		var got: Node = _find(c, name)
		if got != null:
			return got
	return null


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var scene: Node = (load(args[0]) as PackedScene).instantiate()
	root.add_child(scene)
	await process_frame
	var mi: MeshInstance3D = scene.get_node_or_null(NodePath(args[1])) as MeshInstance3D
	if mi == null:
		print("no mesh named ", args[1])
		_exit(1)
		return
	var at := Vector3(float(args[2]), float(args[3]), float(args[4]))
	var r: float = float(args[5])
	var xf: Transform3D = mi.global_transform
	for s in range(mi.mesh.get_surface_count()):
		var arr: Array = mi.mesh.surface_get_arrays(s)
		var v: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
		var col: PackedColorArray = arr[Mesh.ARRAY_COLOR] if arr[Mesh.ARRAY_COLOR] != null else PackedColorArray()
		var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX]
		var mat: BaseMaterial3D = mi.get_active_material(s) as BaseMaterial3D
		print("surface %d: %d verts, colours %s, material albedo %s vertex_color_use_as_albedo %s" % [s, v.size(),
			str(col.size() > 0), (str(mat.albedo_color) if mat != null else "-"),
			(str(mat.vertex_color_use_as_albedo) if mat != null else "-")])
		if mat != null:
			print("  uv1 scale %s triplanar %s world %s albedo_texture %s" % [str(mat.uv1_scale), str(mat.uv1_triplanar),
				str(mat.uv1_world_triplanar), (mat.albedo_texture.resource_path if mat.albedo_texture != null else "-")])
		var uv: PackedVector2Array = arr[Mesh.ARRAY_TEX_UV] if arr[Mesh.ARRAY_TEX_UV] != null else PackedVector2Array()
		var nrms: PackedVector3Array = arr[Mesh.ARRAY_NORMAL] if arr[Mesh.ARRAY_NORMAL] != null else PackedVector3Array()
		var by_normal: Dictionary = {}
		var n: int = idx.size() if idx.size() > 0 else v.size()
		for t in range(0, n - 2, 3):
			var i0: int = idx[t] if idx.size() > 0 else t
			var i1: int = idx[t + 1] if idx.size() > 0 else t + 1
			var i2: int = idx[t + 2] if idx.size() > 0 else t + 2
			var a: Vector3 = xf * v[i0]
			var b: Vector3 = xf * v[i1]
			var c: Vector3 = xf * v[i2]
			if ((a + b + c) / 3.0).distance_to(at) > r:
				continue
			var nrm: Vector3 = (b - a).cross(c - a).normalized()
			var key: String = "(%.0f,%.0f,%.0f)" % [nrm.x, nrm.y, nrm.z]
			var cc: Color = Color(1, 1, 1)
			if col.size() > 0:
				cc = (col[i0] + col[i1] + col[i2]) / 3.0
			if not by_normal.has(key):
				by_normal[key] = [0, Color(0, 0, 0), []]
			by_normal[key][0] += 1
			by_normal[key][1] += cc
			if uv.size() > 0:
				(by_normal[key][2] as Array).append([uv[i0], uv[i1], uv[i2]])
			if nrms.size() > 0:
				if by_normal[key].size() < 4:
					by_normal[key].append(Vector3.ZERO)
				by_normal[key][3] += (xf.basis * (nrms[i0] + nrms[i1] + nrms[i2])).normalized()
		for key in by_normal:
			var cnt: int = by_normal[key][0]
			var sum: Color = by_normal[key][1]
			var stored: String = "-"
			if by_normal[key].size() > 3:
				var sn: Vector3 = (by_normal[key][3] as Vector3) / cnt
				stored = "(%.2f, %.2f, %.2f)" % [sn.x, sn.y, sn.z]
			print("  normal %s: %d triangles, stored normal %s, mean COLOR_0 (%.2f, %.2f, %.2f), UVs %s" % [key, cnt,
				stored, sum.r / cnt, sum.g / cnt, sum.b / cnt, str((by_normal[key][2] as Array).slice(0, 2))])
	_exit(0)
