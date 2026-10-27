extends SceneTree
## Which mesh instances a ray from an eye toward a target passes through, nearest first. Prints and stops.
##
##     godot --headless --path <walk copy> --script res://ray_probe.gd -- <scene> ex ey ez tx ty tz
##
## The ray runs from the eye 60 m toward the target (Godot metres, y up). For each MeshInstance3D whose world AABB the
## ray enters: the entry distance, its path, its mesh's surface count and vertex count, and each surface's material
## name and albedo. AABBs, not triangles: a big mesh's box can be entered where its triangles are not. Draws no
## conclusion.


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _walk(n: Node, out: Array) -> void:
	out.append(n)
	for c in n.get_children():
		_walk(c, out)


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var scene: Node = (load(args[0]) as PackedScene).instantiate()
	root.add_child(scene)
	await process_frame
	var eye := Vector3(float(args[1]), float(args[2]), float(args[3]))
	var tgt := Vector3(float(args[4]), float(args[5]), float(args[6]))
	var dir: Vector3 = (tgt - eye).normalized()
	var hits: Array = []
	var nodes: Array = []
	_walk(scene, nodes)
	for n in nodes:
		var mi: MeshInstance3D = n as MeshInstance3D
		if mi == null or mi.mesh == null or not mi.is_visible_in_tree():
			continue
		var box: AABB = mi.global_transform * mi.get_aabb()
		if box.size.length() > 200.0:
			continue
		var hit: Variant = box.intersects_ray(eye, dir)
		if hit == null:
			continue
		hits.append([eye.distance_to(hit as Vector3), mi])
	hits.sort_custom(func(a, b): return a[0] < b[0])
	for h in hits.slice(0, 12):
		var mi: MeshInstance3D = h[1]
		var verts: int = 0
		for s in range(mi.mesh.get_surface_count()):
			verts += (mi.mesh.surface_get_arrays(s)[Mesh.ARRAY_VERTEX] as PackedVector3Array).size()
		var mats: Array = []
		for s in range(mi.mesh.get_surface_count()):
			var m: BaseMaterial3D = mi.get_active_material(s) as BaseMaterial3D
			mats.append("%s %s" % [(m.resource_name if m != null else "-"), (str(m.albedo_color) if m != null else "")])
		print("%.2f m  %s  surfaces %d verts %d  %s" % [h[0], String(scene.get_path_to(mi)), mi.mesh.get_surface_count(),
			verts, " | ".join(mats)])
	_exit(0)
