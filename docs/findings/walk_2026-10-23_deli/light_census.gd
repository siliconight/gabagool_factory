extends SceneTree
# Finding 1: what light stands in each of deli_a03's storeys, as the walk copy builds the scene. Headless; loads
# res://_walk.tscn, walks the tree after one frame, and counts every Light3D whose global position falls inside the
# building's footprint, by storey (from its height over the building's origin, storey height 3.3 m): type, visible,
# energy, range, whether it is baked, and the rig it belongs to. Prints measurements only; quits.
# Args after --: <building node name> <x0> <z0> <x1> <z1> (the footprint in world metres)

var node_name: String
var box: Rect2


func _initialize() -> void:
	var a: PackedStringArray = OS.get_cmdline_user_args()
	node_name = a[0]
	box = Rect2(Vector2(float(a[1]), float(a[2])), Vector2(float(a[3]) - float(a[1]), float(a[4]) - float(a[2])))
	change_scene_to_file("res://_walk.tscn")
	_run.call_deferred()


func _lights(n: Node, out: Array) -> void:
	if n is Light3D:
		out.append(n)
	for c in n.get_children():
		_lights(c, out)


func _run() -> void:
	for f in range(4):
		await process_frame
	var all: Array = []
	_lights(root, all)
	var by: Dictionary = {}
	for n in all:
		var l: Light3D = n as Light3D
		var p: Vector3 = l.global_position
		if not box.has_point(Vector2(p.x, p.z)):
			continue
		var s: int = int(floor((p.y + 0.01) / 3.3))
		var key: String = "storey %d" % s
		if not by.has(key):
			by[key] = []
		var rng: float = 0.0
		if l is OmniLight3D:
			rng = (l as OmniLight3D).omni_range
		elif l is SpotLight3D:
			rng = (l as SpotLight3D).spot_range
		(by[key] as Array).append("%s vis=%s E=%.2f range=%.1f bake=%d at (%.1f, %.1f, %.1f) %s" % [
			l.get_class(), str(l.is_visible_in_tree()), l.light_energy, rng, l.light_bake_mode, p.x, p.y, p.z,
			String(l.get_parent().name)])
	print("lights in total in the scene: %d" % all.size())
	for k in by.keys():
		print("== %s: %d light(s)" % [k, (by[k] as Array).size()])
		for line in by[k]:
			print("   " + line)
	quit(0)
