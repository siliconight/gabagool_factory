extends SceneTree
## Cold run 9391's price: visible MeshInstance3D nodes under each child of the level's `Site` node -- a building, an
## Empty, the backdrop, the street furniture -- to say where a change's added draws stand. Material names do not
## survive the import (count_materials.gd read 0 drop safes in a level that has three), so this counts by place.
## Headless; measurements only.
##
##     godot --headless --path <walk copy> --script res://count_by_site_child.gd

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
	var sites: Array = root.find_children("Site", "", true, false)
	if sites.size() != 1:
		print("EXPECTED ONE Site, found %d: nothing measured" % sites.size())
		_exit(2)
		return true
	var site: Node = sites[0]
	var total := 0
	for c in site.get_children():
		var n := 0
		for m in (c as Node).find_children("*", "MeshInstance3D", true, false):
			if (m as MeshInstance3D).mesh != null and (m as MeshInstance3D).is_visible_in_tree():
				n += 1
		if (c as Node) is MeshInstance3D and (c as MeshInstance3D).is_visible_in_tree():
			n += 1
		print("CHILD %s %d" % [(c as Node).name, n])
		total += n
	print("total: %d" % total)
	_exit(0)
	return true
