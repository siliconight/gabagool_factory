extends SceneTree
## Cold run 9391's price: how many visible MeshInstance3D nodes wear a material whose name contains each given
## substring, and under which parents -- to attribute the draws a change added. Headless; measurements only.
##
##     godot --headless --path <walk copy> --script res://count_materials.gd -- <substring>,<substring>,...

var _frame := 0
var _needles: PackedStringArray = PackedStringArray()


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() >= 1:
		_needles = args[0].split(",")
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
	var total := 0
	for s in _needles:
		var n := 0
		var by_parent := {}
		for node in root.find_children("*", "MeshInstance3D", true, false):
			var mi: MeshInstance3D = node
			if mi.mesh == null or not mi.is_visible_in_tree():
				continue
			var hit := false
			for k in mi.mesh.get_surface_count():
				var m: Material = mi.get_active_material(k)
				if m != null and String(m.resource_name).find(s) >= 0:
					hit = true
			if hit:
				n += 1
				var p := String(mi.get_parent().get_parent().name) if mi.get_parent().get_parent() != null else "-"
				by_parent[p] = int(by_parent.get(p, 0)) + 1
		print("MATERIAL %s: %d mesh instance(s); by grandparent %s" % [s, n, str(by_parent)])
		total += n
	print("total: %d" % total)
	_exit(0)
	return true
