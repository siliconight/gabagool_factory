extends SceneTree
## Cold run 9392: the visible MeshInstance3D nodes under one Site child, each with its name, its first surface's
## albedo and that material's resource name (the per-side merge's key),
## and the rest of that key: the surface format and the material's uv1 scale and triplanar flags -- to see whether the door hardware shares the stoop railing's mesh. Headless; measurements only.
##
##     godot --headless --path <walk copy> --script res://meshes_under.gd -- <child name>

var _frame := 0


func _initialize() -> void:
	var ps: PackedScene = load("res://_walk.tscn")
	root.add_child(ps.instantiate())


func _process(_d: float) -> bool:
	_frame += 1
	if _frame < 3:
		return false
	var args := OS.get_cmdline_user_args()
	var hits := root.find_children(args[0], "", true, false)
	if hits.is_empty():
		print("NO NODE NAMED %s: nothing measured" % args[0])
		quit(2)
		return true
	for mi in (hits[0] as Node).find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		if not m.is_visible_in_tree() or m.mesh == null:
			continue
		var mat: Material = m.get_active_material(0)
		var alb := "?"
		if mat is BaseMaterial3D:
			alb = str((mat as BaseMaterial3D).albedo_color)
		print("MESH %s surfaces %d albedo %s material %s" % [m.name, m.mesh.get_surface_count(), alb,
			(mat.resource_name if mat != null else "<none>")])
		var am := m.mesh as ArrayMesh
		var bm := mat as BaseMaterial3D
		print("  KEY format %d uv1_scale %s triplanar %s world_triplanar %s" % [
			(am.surface_get_format(0) if am != null else -1), (str(bm.uv1_scale) if bm != null else "?"),
			(str(bm.uv1_triplanar) if bm != null else "?"), (str(bm.uv1_world_triplanar) if bm != null else "?")])
	quit()
	return true
