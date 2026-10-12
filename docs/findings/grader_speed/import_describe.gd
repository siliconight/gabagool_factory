extends SceneTree
## The description `import_digest.gd` digests, printed whole, for the models named after `--`:
## every node's path, class and transform, and each mesh surface's primitive, vertex and index
## counts, second UV set, material name and albedo texture. For reading what two digests disagree
## about. Measures and prints; names no cause.
##
##   godot --headless --path <project> -s <this file> -- res://a.glb res://b.glb


func _initialize() -> void:
	for f in OS.get_cmdline_user_args():
		var path: String = String(f)
		var res: Resource = ResourceLoader.load(path, "", ResourceLoader.CACHE_MODE_IGNORE)
		print("==== %s" % path)
		if res == null:
			print("UNLOADABLE")
			continue
		if res is PackedScene:
			var root: Node = (res as PackedScene).instantiate()
			print(_describe(root, root))
			root.free()
		elif res is Mesh:
			print(_mesh_text(res as Mesh))
	quit(0)


func _describe(n: Node, root: Node) -> String:
	var t: String = ""
	var n3: Node3D = n as Node3D
	var xf: String = ""
	if n3 != null:
		var b: Basis = n3.transform.basis
		var o: Vector3 = n3.transform.origin
		xf = "%.4f,%.4f,%.4f|%.4f,%.4f,%.4f|%.4f,%.4f,%.4f|%.4f,%.4f,%.4f" % [
			b.x.x, b.x.y, b.x.z, b.y.x, b.y.y, b.y.z, b.z.x, b.z.y, b.z.z, o.x, o.y, o.z]
	# the counter in a name Godot made up is set aside, as in import_digest.gd
	var node_path: String = RegEx.create_from_string("@([A-Za-z0-9_]+)@[0-9]+").sub(
		String(root.get_path_to(n)), "@$1@", true)
	t += "%s:%s:%s\n" % [node_path, n.get_class(), xf]
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi != null and mi.mesh != null:
		t += _mesh_text(mi.mesh)
	for c in n.get_children():
		t += _describe(c, root)
	return t


func _mesh_text(m: Mesh) -> String:
	var t: String = ""
	for s in range(m.get_surface_count()):
		var arrays: Array = m.surface_get_arrays(s)
		var verts: int = 0
		var idx: int = 0
		var uv2: bool = false
		if arrays.size() > Mesh.ARRAY_VERTEX and arrays[Mesh.ARRAY_VERTEX] != null:
			verts = (arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array).size()
		if arrays.size() > Mesh.ARRAY_INDEX and arrays[Mesh.ARRAY_INDEX] != null:
			idx = (arrays[Mesh.ARRAY_INDEX] as PackedInt32Array).size()
		if arrays.size() > Mesh.ARRAY_TEX_UV2 and arrays[Mesh.ARRAY_TEX_UV2] != null:
			uv2 = true
		var mat: Material = m.surface_get_material(s)
		var mname: String = ""
		var tex: String = ""
		if mat != null:
			mname = mat.resource_name
			var bm: BaseMaterial3D = mat as BaseMaterial3D
			if bm != null and bm.albedo_texture != null:
				tex = "%s %dx%d" % [bm.albedo_texture.resource_path.get_slice("::", 0),
					bm.albedo_texture.get_width(), bm.albedo_texture.get_height()]
		t += "  s%d p%d v%d i%d uv2=%s m=%s tex=%s\n" % [
			s, int(m.surface_get_primitive_type(s)), verts, idx, str(uv2), mname, tex]
	return t
