extends SceneTree
## Cold run 9391: where the pieces its fixes touched stand, to aim look_shots at them. Every Node3D whose name contains
## one of the given substrings (case-insensitive): its path and global position. Headless; measurements only.
## Frame: Godot world, metres.
##
##     godot --headless --path <walk copy> --script res://find_nodes.gd -- <substring>,<substring>,...

var _frame := 0
var _needles: PackedStringArray = PackedStringArray()


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() >= 1:
		_needles = args[0].to_lower().split(",")
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
	if _needles.size() == 0:
		print("NO SUBSTRINGS GIVEN: nothing measured")
		_exit(2)
		return true
	var n := 0
	for node in root.find_children("*", "Node3D", true, false):
		var nm := String((node as Node).name).to_lower()
		for s in _needles:
			if nm.find(s) >= 0:
				var p: Vector3 = (node as Node3D).global_position
				print("NODE %s at (%.2f, %.2f, %.2f)" % [(node as Node).get_path(), p.x, p.y, p.z])
				n += 1
				break
	print("found: %d" % n)
	_exit(0)
	return true
