extends SceneTree
## deli_a03's seam at site x -64.0, one float32 step either side: the composed global origins of the two colliders'
## bodies (printed with every digit Godot keeps), the cut edge and the plate face they put in site space, and a ray
## straight down at x -64.0 and at the representable values next to it (3.8 um above, 7.6 um below; a float32 near 64
## steps that coarsely), at z -9.0 and -9.5. A probe: prints what it measured and stops.
##
##   godot --headless --path <package copy> --script res://seam_ulps.gd


## Every building has a `slab_col_1`, so the search starts at deli_a03's own instance.
func _building(n: Node) -> Node:
	if n.scene_file_path.ends_with("lot/deli_a03/site.tscn"):
		return n
	for c in n.get_children():
		var f: Node = _building(c)
		if f != null:
			return f
	return null


func _body(scene: Node, nm: String) -> Node3D:
	var b: Node = _building(scene)
	if b == null:
		return null
	return b.find_child(nm, true, false) as Node3D


func _initialize() -> void:
	await process_frame
	var main_scene: String = String(ProjectSettings.get_setting("application/run/main_scene", ""))
	var packed: PackedScene = load(main_scene) as PackedScene
	var scene: Node = packed.instantiate()
	root.add_child(scene)
	for i in range(20):
		await process_frame
	for nm in ["slab_col_1", "stair1col_discharge_0"]:
		var b: Node3D = _body(scene, nm)
		if b == null:
			print("[ulp] no node named %s under deli_a03" % nm)
			continue
		var o: Vector3 = b.global_transform.origin
		print("[ulp] %s at %s: global origin x %.12f y %.12f z %.12f" % [nm, str(b.get_path()), o.x, o.y, o.z])
	var plate: Node3D = _body(scene, "stair1col_discharge_0")
	if plate != null:
		var half: float = 1.2000000476837158
		print("[ulp] the plate's west face in site space: %.12f (origin x minus its hull's 1.2000000477)"
			% (plate.global_transform.origin.x - half))
	var slab: Node3D = _body(scene, "slab_col_1")
	if slab != null:
		print("[ulp] the slab's cut edge in site space: %.12f (origin x plus its vertex -13.000000953674316)"
			% (slab.global_transform.origin.x - 13.000000953674316))
	var space: PhysicsDirectSpaceState3D = root.world_3d.direct_space_state
	var xs: Array = [-64.0 - 7.62939453125e-06, -64.0, -64.0 + 3.814697265625e-06]
	for z in [-9.0, -9.5]:
		for x in xs:
			var q := PhysicsRayQueryParameters3D.create(Vector3(x, 4.8, z), Vector3(x, -1.0, z))
			var hit: Dictionary = space.intersect_ray(q)
			var what: String = "nothing"
			if not hit.is_empty():
				var c: Object = hit.get("collider")
				var path: String = str((c as Node).get_path()) if c is Node else str(c)
				what = "%s at %.3f" % [path.get_file(), float(hit["position"].y)]
			print("[ulp] ray x %.9f z %.2f -> %s" % [x, z, what])
	quit(0)
