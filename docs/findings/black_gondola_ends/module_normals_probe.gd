extends SceneTree
## A module GLB's large faces at a plane x = +-<x>, as Godot imports it: each face's stored normal and its winding's.
## Prints and stops.
##
##     godot --headless --path <project> --script res://module_normals_probe.gd -- <res:// glb> <x> <min area m2>
##
## Read in the module's own frame (before any slot transform or merge). A face whose stored normal and winding normal
## disagree is drawn lit from the side it does not face. Draws no conclusion.


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
	var px: float = float(args[1])
	var min_area: float = float(args[2])
	var nodes: Array = []
	_walk(scene, nodes)
	for n in nodes:
		var mi: MeshInstance3D = n as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var xf: Transform3D = (scene as Node3D).global_transform.affine_inverse() * mi.global_transform
		for s in range(mi.mesh.get_surface_count()):
			var arr: Array = mi.mesh.surface_get_arrays(s)
			var v: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
			var nr: PackedVector3Array = arr[Mesh.ARRAY_NORMAL]
			var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX]
			var area_by: Dictionary = {}
			for t in range(0, idx.size() - 2, 3):
				var a: Vector3 = xf * v[idx[t]]
				var b: Vector3 = xf * v[idx[t + 1]]
				var c: Vector3 = xf * v[idx[t + 2]]
				var ctr: Vector3 = (a + b + c) / 3.0
				if absf(absf(ctr.x) - px) > 0.04:
					continue
				var wn: Vector3 = (c - a).cross(b - a)
				var ar: float = wn.length() * 0.5
				var sn: Vector3 = (xf.basis * (nr[idx[t]] + nr[idx[t + 1]] + nr[idx[t + 2]])).normalized()
				var key: String = "%s x=%.3f winding (%.0f,%.0f,%.0f) stored (%.2f,%.2f,%.2f)" % [String(mi.name), ctr.x,
					wn.normalized().x, wn.normalized().y, wn.normalized().z, sn.x, sn.y, sn.z]
				area_by[key] = float(area_by.get(key, 0.0)) + ar
			for key in area_by:
				if float(area_by[key]) >= min_area:
					print("FACE %s area %.2f" % [key, area_by[key]])
	_exit(0)
