extends SceneTree
## What casts the sun's shadow at run time that the bake cannot see? (roadmap 243, 2026-10-12)
##
##     godot --headless --path <an imported copy of a package> -s res://sun_casters.gd
##
## Cold run 9265 (Lux 0.76.0, the sun baked) lights facades that 9264's live sun leaves dark, at a sun
## 4 degrees up, while arm A (the live sun unshadowed) lights the same ones: both agree on which faces
## the sun reaches, and disagree on what stands in the way. Level Factory bakes `bake.tscn` -- the
## presentation scene and its LightmapGI -- while the game's `mission.tscn` also loads the dressing
## and `site_backdrop.tscn`. This loads the game's scene the way the game does, reads the sun's
## direction, and counts every visible shadow-casting GeometryInstance3D by the scene it came from and
## whether the bake holds it (under `Bake`, gi_mode static), with each group's tallest top and how far
## a top that tall throws a shadow at this sun. It measures and stops.
##
## REFUTED, KEPT (`sun_casters_9264.first.out.txt`): the first run built a MultiMesh's box from
## `MultiMesh.get_instance_transform`, and headless that returns the identity for every instance --
## the dummy rendering server keeps no instance buffer -- so every backdrop box sat at the origin and
## a rowhome's "top" was half its height (5.5 m for an 11 m home, 20.0 m for the 40 m water tower,
## each mesh centred on its own origin). The counts were right. Now a MultiMesh reports its instance
## count and its mesh's own height, and says its placements were not read; `backdrop_casters.py`
## reads them from the scene file's buffers.

const UP_TO: int = 12


func _initialize() -> void:
	_main.call_deferred()


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


## A placed caster's world box; a MultiMesh's own mesh box, unplaced (see the docstring).
func _box(g: GeometryInstance3D) -> AABB:
	if g is MeshInstance3D:
		var mesh: Mesh = (g as MeshInstance3D).mesh
		return AABB() if mesh == null else g.global_transform * mesh.get_aabb()
	if g is MultiMeshInstance3D:
		var mm: MultiMesh = (g as MultiMeshInstance3D).multimesh
		return AABB() if mm == null or mm.mesh == null else mm.mesh.get_aabb()
	return g.get_aabb()


func _instances(g: GeometryInstance3D) -> int:
	if g is MultiMeshInstance3D:
		var mm: MultiMesh = (g as MultiMeshInstance3D).multimesh
		return 0 if mm == null else mm.instance_count
	return -1


func _group(g: Node, top: Node) -> String:
	var n: Node = g
	while n.get_parent() != null and n.get_parent() != top:
		n = n.get_parent()
	return String(n.name)


func _walk(node: Node, out: Array) -> void:
	if node is GeometryInstance3D:
		out.append(node)
	for child in node.get_children():
		_walk(child, out)


func _main() -> void:
	var path: String = str(ProjectSettings.get_setting("application/run/main_scene", ""))
	var packed: PackedScene = load(path) as PackedScene
	if packed == null:
		print("could not load the main scene %s" % path)
		_exit(2)
		return
	var top: Node = packed.instantiate()
	root.add_child(top)
	for i in 10:
		await process_frame
	var sun: DirectionalLight3D = null
	var found: Array = []
	_walk(root, found)
	for n in root.find_children("LuxSun", "DirectionalLight3D", true, false):
		sun = n
	if sun == null:
		print("NO LuxSun")
		_exit(2)
		return
	var to_sun: Vector3 = sun.global_transform.basis.z.normalized()
	var elev: float = rad_to_deg(asin(clampf(to_sun.y, -1.0, 1.0)))
	print("the sun: toward it (%.3f, %.3f, %.3f), %.1f degrees up; bake mode %d, shadow %s" % [
		to_sun.x, to_sun.y, to_sun.z, elev, sun.light_bake_mode, str(sun.shadow_enabled)])
	var reach_per_m: float = 1.0 / tan(deg_to_rad(maxf(elev, 0.1)))
	print("a top 1 m up throws a shadow %.1f m along the ground at this sun" % reach_per_m)
	var groups: Dictionary = {}
	for g in found:
		var gi: GeometryInstance3D = g
		if not gi.is_visible_in_tree():
			continue
		if gi.cast_shadow == GeometryInstance3D.SHADOW_CASTING_SETTING_OFF:
			continue
		var name: String = _group(gi, top)
		var baked: bool = str(gi.get_path()).contains("/Bake/") \
			and gi.gi_mode == GeometryInstance3D.GI_MODE_STATIC
		var key: String = "%s, %s" % [name, "in the bake" if baked else "NOT in the bake"]
		if not groups.has(key):
			groups[key] = []
		groups[key].append([gi, _box(gi)])
	print("visible shadow casters by the scene they came from (a MultiMesh's placements not read):")
	var keys: Array = groups.keys()
	keys.sort()
	for key in keys:
		var rows: Array = groups[key]
		var placed: int = 0
		var tallest: float = -INF
		var multis: int = 0
		var instances: int = 0
		var mesh_h: float = -INF
		for r in rows:
			var b: AABB = r[1]
			var count: int = _instances(r[0])
			if count >= 0:
				multis += 1
				instances += count
				mesh_h = maxf(mesh_h, b.size.y)
			elif b.size != Vector3.ZERO:
				placed += 1
				tallest = maxf(tallest, b.end.y)
		var text: String = "  %-42s %5d casters" % [key, rows.size()]
		if placed > 0:
			text += "; %d placed, the tallest top %.1f m (a shadow %.0f m long)" % [
				placed, tallest, maxf(tallest, 0.0) * reach_per_m]
		if multis > 0:
			text += "; %d MultiMeshes of %d instances, the tallest mesh %.1f m high (%.0f m)" % [
				multis, instances, mesh_h, maxf(mesh_h, 0.0) * reach_per_m]
		print(text)
	for key in keys:
		if not String(key).ends_with("NOT in the bake"):
			continue
		var rows: Array = groups[key]
		rows.sort_custom(func(a, b): return (a[1] as AABB).size.y > (b[1] as AABB).size.y)
		print("%s, the tallest %d:" % [key, mini(UP_TO, rows.size())])
		for i in mini(UP_TO, rows.size()):
			var b: AABB = rows[i][1]
			var count: int = _instances(rows[i][0])
			var where: String = "%d instances, placements not read" % count if count >= 0 \
				else "top %.1f m at (%.1f, %.1f)" % [b.end.y, b.get_center().x, b.get_center().z]
			print("    %5.1f m high, %5.1f x %5.1f, %s  %s" % [b.size.y, b.size.x, b.size.z, where,
				String((rows[i][0] as Node).name).left(64)])
	_exit(0)
