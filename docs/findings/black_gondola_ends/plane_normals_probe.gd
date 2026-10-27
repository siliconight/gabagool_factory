extends SceneTree
## The triangles of one mesh instance that lie ON a world plane z = <z> (all three corners within 5 mm of it): each
## group's stored normal (world), winding normal, area and z-extent. Prints and stops.
##
##     godot --headless --path <walk copy> --script res://plane_normals_probe.gd -- <scene> <mesh node path> <z>
##
## Picks triangles by their corners lying on the plane, never by a centroid within a radius: `vertex_probe.gd`'s
## centroid test read a panel's INNER face for its outer one, 2 cm away (the first reading in this folder's README).
## Draws no conclusion.


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
	var mi: MeshInstance3D = scene.get_node_or_null(NodePath(args[1])) as MeshInstance3D
	if mi == null:
		print("no mesh at ", args[1])
		_exit(1)
		return
	var pz: float = float(args[2])
	var xf: Transform3D = mi.global_transform
	var groups: Dictionary = {}
	for s in range(mi.mesh.get_surface_count()):
		var arr: Array = mi.mesh.surface_get_arrays(s)
		var v: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
		var nr: PackedVector3Array = arr[Mesh.ARRAY_NORMAL]
		var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX]
		for t in range(0, idx.size() - 2, 3):
			var a: Vector3 = xf * v[idx[t]]
			var b: Vector3 = xf * v[idx[t + 1]]
			var c: Vector3 = xf * v[idx[t + 2]]
			if absf(a.z - pz) > 0.005 or absf(b.z - pz) > 0.005 or absf(c.z - pz) > 0.005:
				continue
			var wn: Vector3 = (c - a).cross(b - a)
			var sn: Vector3 = (xf.basis * (nr[idx[t]] + nr[idx[t + 1]] + nr[idx[t + 2]])).normalized()
			var key: String = "winding (%.0f,%.0f,%.0f) stored (%.2f,%.2f,%.2f)" % [wn.normalized().x,
				wn.normalized().y, wn.normalized().z, sn.x, sn.y, sn.z]
			if not groups.has(key):
				groups[key] = [0.0, 1e9, -1e9, 0]
			groups[key][0] += wn.length() * 0.5
			groups[key][1] = minf(groups[key][1], minf(a.y, minf(b.y, c.y)))
			groups[key][2] = maxf(groups[key][2], maxf(a.y, maxf(b.y, c.y)))
			groups[key][3] += 1
	for key in groups:
		print("ON z=%.3f  %s  %d tris  area %.3f m2  y %.2f..%.2f" % [pz, key, groups[key][3], groups[key][0],
			groups[key][1], groups[key][2]])
	_exit(0)
