extends SceneTree
## Every surface in the walk copy whose material is named `M_TrafficSignal_Lens_*` (findings 11 and 12): the mesh's
## path, the material's class, and for a ShaderMaterial its shader's first line and its clock parameters. Says whether
## Level Factory's signal lens pass (0.165.0) reached the package. Measurements only.

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
	for n in root.find_children("*", "MeshInstance3D", true, false):
		var mi: MeshInstance3D = n
		if mi.mesh == null:
			continue
		for s in mi.mesh.get_surface_count():
			var m: Material = mi.get_active_material(s)
			if m == null or not String(m.resource_name).begins_with("M_TrafficSignal_Lens_"):
				continue
			var extra := ""
			if m is ShaderMaterial:
				var sm: ShaderMaterial = m
				extra = " cycle_s=%s lit=%s..%s energy=%s" % [sm.get_shader_parameter("cycle_s"),
					sm.get_shader_parameter("lit_from_s"), sm.get_shader_parameter("lit_to_s"),
					sm.get_shader_parameter("energy")]
			elif m is BaseMaterial3D:
				var bm: BaseMaterial3D = m
				extra = " emission=%s energy=%s" % [bm.emission_enabled, bm.emission_energy_multiplier]
			print("LENS %s surface %d %s %s%s" % [mi.get_path(), s, m.get_class(), m.resource_name, extra])
	_exit(0)
	return true
