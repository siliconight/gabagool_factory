extends SceneTree
## Finding 2: what each opening slot (`*_open<n>`) of one building holds -- the slots Level Factory's merge leaves
## whole (`merge_buildings.gd`, `_mergeable`). Per slot: whether it carries `interactive_id`, and per mesh surface its
## material, whether that material is transparent (BaseMaterial3D transparency, or a ShaderMaterial, which the merge
## also refuses), and its node path. A slot holding no transparent surface and no interactive tag is one the merge
## could bake as part of the wall. Headless: reads the scene, draws nothing. Measurements only.
##
##     godot --headless --path <walk copy> --script res://open_slots.gd -- <building node name>

var _frame := 0
var _building := "b1"


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() >= 1:
		_building = args[0]
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
	var b: Node = null
	for n in root.find_children(_building, "", true, false):
		if String((n as Node).get_parent().name) == "Site":
			b = n
	if b == null:
		print("NO BUILDING NODE %s UNDER Site: nothing measured" % _building)
		_exit(2)
		return true
	var slots := 0
	var clean := 0
	for c in b.get_children():
		var name := String((c as Node).name)
		if name.find("_open") < 0:
			continue
		slots += 1
		var inter: String = str((c as Node).get_meta("interactive_id")) if (c as Node).has_meta("interactive_id") else "-"
		var lines: Array = []
		var transparent := false
		for m in (c as Node).find_children("*", "MeshInstance3D", true, false):
			var mi: MeshInstance3D = m
			if mi.mesh == null:
				continue
			for s in mi.mesh.get_surface_count():
				var mat: Material = mi.get_active_material(s)
				var kind := "null"
				var tr := false
				if mat is ShaderMaterial:
					kind = "ShaderMaterial"
					tr = true
				elif mat is BaseMaterial3D:
					var bm: BaseMaterial3D = mat
					kind = "%s transparency %d" % [bm.resource_name, bm.transparency]
					tr = bm.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED
				if tr:
					transparent = true
				lines.append("    %s s%d %s%s" % [String(c.get_path_to(mi)), s, kind, "  TRANSPARENT" if tr else ""])
		if inter == "-" and not transparent:
			clean += 1
		print("SLOT %s interactive %s transparent %s" % [name, inter, transparent])
		for l in lines:
			print(l)
	print("opening slots: %d; neither interactive nor transparent: %d" % [slots, clean])
	_exit(0)
	return true
