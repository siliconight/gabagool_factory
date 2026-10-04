extends SceneTree
## Lists every MeshInstance3D whose world AABB centre falls inside one plan
## box, with its node path, world AABB size and the world direction of its
## local Y axis. Prints what it measured and stops.
##     godot --headless --path <walk copy> --script empty_mesh_census.gd -- x0 x1 z0 z1
## Box in Godot world metres (x, z); plan (x, y) is Godot (x, -y).


func _initialize() -> void:
	_run.call_deferred()


func _walk(n: Node, box: Array, out: Array) -> void:
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi != null and mi.mesh != null:
		var ab: AABB = mi.global_transform * mi.get_aabb()
		var c: Vector3 = ab.get_center()
		if c.x >= float(box[0]) and c.x <= float(box[1]) and c.z >= float(box[2]) and c.z <= float(box[3]):
			var up: Vector3 = mi.global_transform.basis.y.normalized()
			out.append("%s | size %s | centre %s | local-Y %s" % [
				String(mi.get_path()), str(ab.size.snappedf(0.01)),
				str(c.snappedf(0.01)), str(up.snappedf(0.01))])
	for ch: Node in n.get_children():
		_walk(ch, box, out)


func _run() -> void:
	var a: PackedStringArray = OS.get_cmdline_user_args()
	var ps: PackedScene = load("res://mission.tscn") as PackedScene
	if ps == null:
		print("CENSUS no res://mission.tscn")
		quit(2)
		return
	var inst: Node = ps.instantiate()
	root.add_child(inst)
	await process_frame
	var out: Array = []
	_walk(inst, [a[0], a[1], a[2], a[3]], out)
	out.sort()
	for line in out:
		print("CENSUS ", line)
	print("CENSUS %d mesh(es)" % out.size())
	quit(0)
