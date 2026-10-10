extends SceneTree
## Roadmap 220: every drawn surface and lamp near a door sign, from the walked level itself.
##
##   godot --headless --path <walk project> --script <this file> -- CX,CY,CZ HX,HY,HZ
##
## Loads the walk scene, lets it settle, and prints every VisualInstance3D (mesh, MultiMesh,
## decal, light) whose world AABB meets the box centred on C with half-extents H, Godot metres,
## Y up. For each: its path, its class, its world AABB, its mesh's resource path and, for a
## mesh, each surface's material and whether that material is emissive. Prints what it found
## and stops; it names no cause.

var _frames: int = 0
var _box := AABB()


func _initialize() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() < 2:
		print("NEAR_SIGN usage: -- CX,CY,CZ HX,HY,HZ")
		quit(2)
		return
	var c: PackedStringArray = args[0].split(",")
	var h: PackedStringArray = args[1].split(",")
	var centre := Vector3(float(c[0]), float(c[1]), float(c[2]))
	var half := Vector3(float(h[0]), float(h[1]), float(h[2]))
	_box = AABB(centre - half, half * 2.0)
	var ps: PackedScene = load("res://_walk.tscn") as PackedScene
	if ps == null:
		print("NEAR_SIGN no _walk.tscn")
		quit(2)
		return
	root.add_child(ps.instantiate())


func _process(_delta: float) -> bool:
	_frames += 1
	if _frames < 20:
		return false
	var found: int = 0
	for n in root.find_children("*", "VisualInstance3D", true, false):
		var vi: VisualInstance3D = n as VisualInstance3D
		if vi == null or not vi.is_visible_in_tree():
			continue
		var wb: AABB = vi.global_transform * vi.get_aabb()
		if not wb.intersects(_box):
			continue
		found += 1
		var line: String = "NEAR_SIGN %s | %s | aabb pos %s size %s" % [
			str(vi.get_path()), vi.get_class(), str(wb.position), str(wb.size)]
		print(line)
		if vi is MeshInstance3D:
			var mi: MeshInstance3D = vi as MeshInstance3D
			if mi.mesh != null:
				print("    mesh %s surfaces %d" % [mi.mesh.resource_path, mi.mesh.get_surface_count()])
				for s in mi.mesh.get_surface_count():
					var m: Material = mi.get_active_material(s)
					var desc: String = "none"
					if m != null:
						desc = "%s %s" % [m.get_class(), m.resource_name]
						if m is BaseMaterial3D:
							var bm: BaseMaterial3D = m as BaseMaterial3D
							desc += " emission %s x%.2f albedo %s" % [
								str(bm.emission_enabled), bm.emission_energy_multiplier,
								str(bm.albedo_color)]
					print("    surface %d: %s" % [s, desc])
		elif vi is Light3D:
			var l: Light3D = vi as Light3D
			print("    light energy %.3f colour %s bake_mode %d" % [
				l.light_energy, str(l.light_color), l.light_bake_mode])
	print("NEAR_SIGN found %d in %s" % [found, str(_box)])
	return true
