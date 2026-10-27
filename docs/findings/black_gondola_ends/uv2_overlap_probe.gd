extends SceneTree
## Does a face's lightmap UV (UV2) overlap other triangles' in the same mesh? Prints and stops.
##
##     godot --headless --path <walk copy> --script res://uv2_overlap_probe.gd -- <scene> <mesh node path> <z>
##
## The face is every triangle on the world plane z = <z> (corners within 5 mm) whose stored normal points +z. For
## each such triangle: its UV2 corners; then every OTHER triangle of the mesh whose UV2 bounding box overlaps one of
## the face's by more than half a texel's worth (1e-4 in UV) is counted, and the first few printed with their world
## centroid and stored normal. Two triangles sharing UV2 share lightmap texels. Draws no conclusion.


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _initialize() -> void:
	_run.call_deferred()


func _box(a: Vector2, b: Vector2, c: Vector2) -> Rect2:
	var r := Rect2(a, Vector2.ZERO)
	r = r.expand(b)
	return r.expand(c)


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var scene: Node = (load(args[0]) as PackedScene).instantiate()
	root.add_child(scene)
	await process_frame
	var mi: MeshInstance3D = scene.get_node_or_null(NodePath(args[1])) as MeshInstance3D
	var pz: float = float(args[2])
	var xf: Transform3D = mi.global_transform
	var arr: Array = mi.mesh.surface_get_arrays(0)
	var v: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
	var nr: PackedVector3Array = arr[Mesh.ARRAY_NORMAL]
	var uv2: PackedVector2Array = arr[Mesh.ARRAY_TEX_UV2] if arr[Mesh.ARRAY_TEX_UV2] != null else PackedVector2Array()
	var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX]
	print("verts %d, UV2 %d, lightmap_size_hint %s" % [v.size(), uv2.size(), str((mi.mesh as ArrayMesh).lightmap_size_hint)])
	if uv2.is_empty():
		_exit(0)
		return
	var face: Array = []
	var others: Array = []
	for t in range(0, idx.size() - 2, 3):
		var a: Vector3 = xf * v[idx[t]]
		var b: Vector3 = xf * v[idx[t + 1]]
		var c: Vector3 = xf * v[idx[t + 2]]
		var sn: Vector3 = (xf.basis * (nr[idx[t]] + nr[idx[t + 1]] + nr[idx[t + 2]])).normalized()
		var r: Rect2 = _box(uv2[idx[t]], uv2[idx[t + 1]], uv2[idx[t + 2]])
		var on: bool = absf(a.z - pz) < 0.005 and absf(b.z - pz) < 0.005 and absf(c.z - pz) < 0.005 and sn.z > 0.9
		if on:
			face.append([t, r])
			print("FACE tri %d UV2 %s %s %s" % [t, str(uv2[idx[t]]), str(uv2[idx[t + 1]]), str(uv2[idx[t + 2]])])
		else:
			others.append([t, r, (a + b + c) / 3.0, sn])
	var hits: int = 0
	for f in face:
		var fr: Rect2 = f[1]
		for o in others:
			var inter: Rect2 = fr.intersection(o[1])
			if inter.size.x > 1e-4 and inter.size.y > 1e-4:
				hits += 1
				if hits <= 8:
					print("  OVERLAP face tri %d with tri %d at %s normal %s, UV2 overlap %s" % [f[0], o[0], str(o[2]),
						str(o[3]), str(inter.size)])
	print("face triangles %d, other triangles whose UV2 box overlaps one: %d" % [face.size(), hits])
	_exit(0)
