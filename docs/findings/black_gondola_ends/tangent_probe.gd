extends SceneTree
## Does a mesh carry tangents, and does its material ask for a normal map? Prints and stops.
##
##     godot --headless --path <walk copy> --script res://tangent_probe.gd -- <scene> <mesh node path> [...]
##
## For each named mesh instance and each of its surfaces: whether the surface's format carries tangents, how many of
## its tangents are zero-length, and the material's `normal_enabled` and normal texture. A normal-mapped material on a
## surface with no usable tangent shades from a degenerate frame. Draws no conclusion.


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var scene: Node = (load(args[0]) as PackedScene).instantiate()
	root.add_child(scene)
	await process_frame
	for i in range(1, args.size()):
		var mi: MeshInstance3D = scene.get_node_or_null(NodePath(args[i])) as MeshInstance3D
		if mi == null:
			print("no mesh at ", args[i])
			continue
		for s in range(mi.mesh.get_surface_count()):
			var fmt: int = (mi.mesh as ArrayMesh).surface_get_format(s) if mi.mesh is ArrayMesh else 0
			var arr: Array = mi.mesh.surface_get_arrays(s)
			var tan: PackedFloat32Array = arr[Mesh.ARRAY_TANGENT] if arr[Mesh.ARRAY_TANGENT] != null else PackedFloat32Array()
			var zero: int = 0
			for k in range(0, tan.size() - 3, 4):
				if Vector3(tan[k], tan[k + 1], tan[k + 2]).length() < 1e-4:
					zero += 1
			var m: BaseMaterial3D = mi.get_active_material(s) as BaseMaterial3D
			print("%s surface %d: format tangents %s, tangents %d (%d zero), normal_enabled %s normal_texture %s" % [
				args[i], s, str(fmt & Mesh.ARRAY_FORMAT_TANGENT != 0), tan.size() / 4, zero,
				(str(m.normal_enabled) if m != null else "-"),
				(m.normal_texture.resource_path.get_file() if m != null and m.normal_texture != null else "-")])
	_exit(0)
