extends SceneTree
## Every traffic signal Lot placed in the walk copy (any node instancing a `traffic_signal` scene) (cold run 9386; findings 11 and 12): the node's path, its world
## origin (the pole, the module's centre), and in PLAN (Godot x, -z) the direction its arm reaches (local +X) and the
## direction its heads face (local +Z: Zoo's recipe hangs them facing Blender -Y, which the Y-up glTF export makes
## local +Z -- the mapping `site_furniture.plate_facing` records as measured). Godot world metres. Measurements only.

var _frame := 0


func _initialize() -> void:
	var ps: PackedScene = load("res://_walk.tscn")
	root.add_child(ps.instantiate())


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _process(_d: float) -> bool:
	_frame += 1
	if _frame < 3:
		return false
	# Lot names a signal's slot `cover_<n>` in the site scene: match the scene it instances
	for n in root.find_children("*", "Node3D", true, false):
		var s: Node3D = n
		if not s.scene_file_path.contains("traffic_signal"):
			continue
		var b: Basis = s.global_transform.basis
		var o: Vector3 = s.global_transform.origin
		print("SIGNAL %s origin_plan (%.2f, %.2f) arm_plan (%.3f, %.3f) face_plan (%.3f, %.3f)" % [
			s.get_path(), o.x, -o.z, b.x.x, -b.x.z, b.z.x, -b.z.z])
	_exit(0)
	return true
