extends SceneTree
## Lightmap texels per metre of a slot's meshes against the merged meshes near it. Prints and stops.
##
##     godot --headless --path <walk copy> --script res://lightmap_density_probe.gd -- <scene> <slot name> [...]
##
## For each named slot (a child of the building's root, searched anywhere in the scene) and for every `MergedR_*`
## within 3 m of it: each MeshInstance3D's `lightmap_size_hint` (the texels Godot packs for it), its mesh's surface
## area in m2 (summed over triangles, in world scale) and texels per metre (sqrt(texels / area)); and each surface's
## material's UV mapping (scale, offset, triplanar, world triplanar) and albedo texture. Draws no conclusion.


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _walk(n: Node, out: Array) -> void:
	out.append(n)
	for c in n.get_children():
		_walk(c, out)


func _area(mi: MeshInstance3D) -> float:
	var a: float = 0.0
	var b: Basis = mi.global_transform.basis
	for s in range(mi.mesh.get_surface_count()):
		var arr: Array = mi.mesh.surface_get_arrays(s)
		var v: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
		var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX]
		var n: int = idx.size() if idx.size() > 0 else v.size()
		for t in range(0, n - 2, 3):
			var i0: int = idx[t] if idx.size() > 0 else t
			var i1: int = idx[t + 1] if idx.size() > 0 else t + 1
			var i2: int = idx[t + 2] if idx.size() > 0 else t + 2
			a += 0.5 * ((b * (v[i1] - v[i0])).cross(b * (v[i2] - v[i0]))).length()
	return a


func _say(tag: String, mi: MeshInstance3D) -> void:
	var hint: Vector2i = mi.mesh.lightmap_size_hint if mi.mesh is ArrayMesh else Vector2i.ZERO
	var area: float = _area(mi)
	var tpm: float = sqrt(float(hint.x * hint.y) / area) if area > 0.0 else 0.0
	print("%s %s  hint %dx%d  area %.2f m2  texels/m %.2f  gi_mode %d  scale %d" % [tag, mi.name, hint.x, hint.y, area,
		tpm, mi.gi_mode, mi.gi_lightmap_scale])
	for s in range(mi.mesh.get_surface_count()):
		var bm: BaseMaterial3D = mi.get_active_material(s) as BaseMaterial3D
		if bm != null:
			print("    surface %d '%s' uv1 scale %s offset %s triplanar %s world %s albedo_tex %s" % [s, bm.resource_name,
				str(bm.uv1_scale), str(bm.uv1_offset), str(bm.uv1_triplanar), str(bm.uv1_world_triplanar),
				(bm.albedo_texture.resource_path.get_file() if bm.albedo_texture != null else "-")])


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var scene: Node = (load(args[0]) as PackedScene).instantiate()
	root.add_child(scene)
	await process_frame
	var nodes: Array = []
	_walk(scene, nodes)
	for i in range(1, args.size()):
		for n in nodes:
			if String((n as Node).name) != args[i] or not (n is Node3D):
				continue
			var at: Vector3 = (n as Node3D).global_position
			print("SLOT %s at %s" % [String(scene.get_path_to(n)), str(at)])
			var kids: Array = []
			_walk(n, kids)
			for k in kids:
				if k is MeshInstance3D and (k as MeshInstance3D).mesh != null:
					_say("  slot", k)
			for m in nodes:
				var mi: MeshInstance3D = m as MeshInstance3D
				if mi == null or not String(mi.name).begins_with("MergedR_") or mi.get_parent() != n.get_parent():
					continue
				if (mi.global_transform * mi.get_aabb()).grow(3.0).has_point(at):
					_say("  merged", mi)
	_exit(0)
