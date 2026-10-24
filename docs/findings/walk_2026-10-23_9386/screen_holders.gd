extends SceneTree
## Every surface in the walk copy whose material name carries `StockScreen` (a desk monitor's lit screen, Zoo 1.115.0;
## finding 5) or `CRT_Screen` (the club TVs): the mesh's path, the scene file it came from, the material's name and
## whether it already carries a next_pass. Says where the monitors live -- an imported GLB the worldskin pass reaches
## on a re-import, or a merged mesh it does not -- and how many there are. Measurements only.

var _frame := 0


func _initialize() -> void:
	var ps: PackedScene = load("res://_walk.tscn")
	root.add_child(ps.instantiate())


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _owner_file(n: Node) -> String:
	var p: Node = n
	while p != null:
		if p.scene_file_path != "":
			return p.scene_file_path
		p = p.get_parent()
	return "?"


func _process(_d: float) -> bool:
	_frame += 1
	if _frame < 3:
		return false
	var count := {}
	for n in root.find_children("*", "MeshInstance3D", true, false):
		var mi: MeshInstance3D = n
		if mi.mesh == null:
			continue
		for s in mi.mesh.get_surface_count():
			var m: Material = mi.get_active_material(s)
			if m == null:
				continue
			var nm := String(m.resource_name)
			if not (nm.contains("StockScreen") or nm.contains("CRT_Screen")):
				continue
			var kind := "StockScreen" if nm.contains("StockScreen") else "CRT_Screen"
			count[kind] = int(count.get(kind, 0)) + 1
			print("SCREEN %s %s from=%s mat=%s next_pass=%s" % [kind, mi.get_path(), _owner_file(mi), nm,
				m.next_pass != null])
	print("COUNT %s" % [count])
	_exit(0)
	return true
