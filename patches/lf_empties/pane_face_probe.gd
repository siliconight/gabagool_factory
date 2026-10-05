extends SceneTree
## For the painted panes of the Empty nearest x = 0: which triangles carry an
## atlas CELL (UVs spanning more than a frame point), which way each of those
## faces points in WORLD space, and which way the street is from the pane.
## Prints what it measured and stops.
##     godot --headless --path <walk copy> --script pane_face_probe.gd -- x0 x1 z0 z1
## Box in Godot world metres; plan (x, y) is Godot (x, -y).


func _initialize() -> void:
	_run.call_deferred()


func _panes(n: Node, box: Array, out: Array) -> void:
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi != null and mi.mesh != null and String(mi.name).contains("Glass"):
		var c: Vector3 = (mi.global_transform * mi.get_aabb()).get_center()
		if c.x >= float(box[0]) and c.x <= float(box[1]) and c.z >= float(box[2]) and c.z <= float(box[3]):
			out.append(mi)
	for ch: Node in n.get_children():
		_panes(ch, box, out)


func _run() -> void:
	var a: PackedStringArray = OS.get_cmdline_user_args()
	var ps: PackedScene = load("res://mission.tscn") as PackedScene
	var inst: Node = ps.instantiate()
	root.add_child(inst)
	await process_frame
	var found: Array = []
	_panes(inst, [a[0], a[1], a[2], a[3]], found)
	print("PANEFACE %d pane mesh(es) in the box" % found.size())
	for mi_v in found:
		var mi: MeshInstance3D = mi_v as MeshInstance3D
		var arr: Array = mi.mesh.surface_get_arrays(0)
		var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
		var uvs: PackedVector2Array = arr[Mesh.ARRAY_TEX_UV]
		var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX]
		var basis: Basis = mi.global_transform.basis
		var lines: Dictionary = {}
		for t in range(0, idx.size(), 3):
			var i0: int = idx[t]
			var i1: int = idx[t + 1]
			var i2: int = idx[t + 2]
			var span: float = maxf(absf(uvs[i0].x - uvs[i1].x), absf(uvs[i0].x - uvs[i2].x))
			var n_local: Vector3 = (verts[i1] - verts[i0]).cross(verts[i2] - verts[i0]).normalized()
			var n_world: Vector3 = (basis * n_local).normalized()
			var kind: String = "CELL" if span > 0.05 else "frame point"
			var key: String = "%s face, world normal %s" % [kind, str(n_world.snappedf(0.01))]
			lines[key] = int(lines.get(key, 0)) + 1
		var centre: Vector3 = (mi.global_transform * mi.get_aabb()).get_center()
		print("PANEFACE %s at %s" % [String(mi.get_path()).get_slice("/", 5), str(centre.snappedf(0.01))])
		for k in lines.keys():
			print("PANEFACE   %d tri(s): %s" % [int(lines[k]), k])
		break
	quit(0)
