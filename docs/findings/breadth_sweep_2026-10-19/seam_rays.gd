extends SceneTree
## Rays straight down across the seam at site x -64.0 (deli_a03's stair cut edge and its discharge plate's west
## face), at z -9.0 and -9.5: what each meets first, by node, at x -64.02 .. -63.98. A probe: prints and stops.


func _owner_path(hit: Dictionary) -> String:
	var c: Object = hit.get("collider")
	if c is Node:
		return str((c as Node).get_path())
	return str(c)


func _initialize() -> void:
	await process_frame
	var main_scene: String = String(ProjectSettings.get_setting("application/run/main_scene", ""))
	var packed: PackedScene = load(main_scene) as PackedScene
	var scene: Node = packed.instantiate()
	root.add_child(scene)
	for i in range(20):
		await process_frame
	var space: PhysicsDirectSpaceState3D = root.world_3d.direct_space_state
	for z in [-9.0, -9.5]:
		for x in [-64.02, -64.01, -64.0, -63.99, -63.98]:
			var q := PhysicsRayQueryParameters3D.create(Vector3(x, 4.8, z), Vector3(x, -1.0, z))
			var hit: Dictionary = space.intersect_ray(q)
			var what: String = "nothing"
			if not hit.is_empty():
				what = "%s at %.3f" % [_owner_path(hit), float(hit["position"].y)]
			print("[seam] x %.2f z %.2f -> %s" % [x, z, what])
	quit(0)
