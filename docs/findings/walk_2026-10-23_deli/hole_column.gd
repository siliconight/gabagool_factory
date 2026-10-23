extends SceneTree
## Every VisualInstance3D whose world AABB crosses a column over a hole, between two heights. Godot world metres,
## Y up. Prints measurements only.
## Column: x -58.55..-57.45, z 9.39..10.69 (deli_a03's ground-floor ladder through-hole, spec x -7.55..-6.45,
## y -13.2..-11.9, b0 at (-51, 0, -2.51)); y -0.6..0.6 (the slab and just above and below it).

const X0 := -58.55
const X1 := -57.45
const Z0 := 9.39
const Z1 := 10.69
const Y0 := -0.6
const Y1 := 0.6

var _frame := 0


func _initialize() -> void:
	var ps: PackedScene = load("res://_walk.tscn")
	root.add_child(ps.instantiate())


func _process(_d: float) -> bool:
	_frame += 1
	if _frame < 3:
		return false
	for n in root.find_children("*", "VisualInstance3D", true, false):
		var v: VisualInstance3D = n
		if not v.is_visible_in_tree():
			continue
		var bb: AABB = v.global_transform * v.get_aabb()
		if bb.position.x > X1 or bb.end.x < X0 or bb.position.z > Z1 or bb.end.z < Z0:
			continue
		if bb.position.y > Y1 or bb.end.y < Y0:
			continue
		var big: bool = bb.size.x > 8.0 or bb.size.z > 8.0
		var mat := ""
		if v is MeshInstance3D:
			var mi: MeshInstance3D = v
			if mi.mesh != null and mi.mesh.get_surface_count() > 0:
				var m: Material = mi.get_active_material(0)
				mat = m.resource_name if m != null else "null"
				if m is BaseMaterial3D:
					var bm: BaseMaterial3D = m
					mat += " albedo %s shading %d cull %d" % [bm.albedo_color, bm.shading_mode, bm.cull_mode]
		print("HIT %s big=%s class=%s y %.3f..%.3f x %.2f..%.2f z %.2f..%.2f mat=%s" % [
			v.get_path(), big, v.get_class(), bb.position.y, bb.end.y, bb.position.x, bb.end.x,
			bb.position.z, bb.end.z, mat])
	quit()
	return true
