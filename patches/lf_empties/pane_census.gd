extends SceneTree
## Counts every surface wearing the painted-window material in the loaded
## mission, and reads what Godot imported it as: the class, emission on/off,
## the emission and albedo textures, the energy, and whether Lux's emissive
## binder's name test matches it. Prints what it measured and stops.
##     godot --headless --path <walk copy> --script pane_census.gd


func _initialize() -> void:
	_run.call_deferred()


func _walk(n: Node, out: Array) -> void:
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi != null and mi.mesh != null:
		for i in range(mi.mesh.get_surface_count()):
			var m: Material = mi.get_surface_override_material(i)
			if m == null:
				m = mi.mesh.surface_get_material(i)
			if m != null and String(m.resource_name).contains("pane"):
				out.append(m)
	for c: Node in n.get_children():
		_walk(c, out)


func _run() -> void:
	var ps: PackedScene = load("res://mission.tscn") as PackedScene
	if ps == null:
		print("PANES no res://mission.tscn")
		quit(2)
		return
	var inst: Node = ps.instantiate()
	root.add_child(inst)
	await process_frame
	var found: Array = []
	_walk(inst, found)
	var shapes: Dictionary = {}
	for m in found:
		var mat: Material = m as Material
		var key: String = "%s | class %s" % [String(mat.resource_name), mat.get_class()]
		var bm: BaseMaterial3D = mat as BaseMaterial3D
		if bm != null:
			key += " | emission %s | emission_texture %s | albedo_texture %s | energy %.2f" % [
				str(bm.emission_enabled), str(bm.emission_texture != null),
				str(bm.albedo_texture != null), bm.emission_energy_multiplier]
		var name_ok: bool = String(mat.resource_name).begins_with("M_") \
			and String(mat.resource_name).ends_with("_Face")
		key += " | binder name test %s" % str(name_ok)
		shapes[key] = int(shapes.get(key, 0)) + 1
	for k in shapes.keys():
		print("PANES %d surface(s): %s" % [int(shapes[k]), k])
	print("PANES %d painted-window surface(s) in total" % found.size())
	quit(0)
