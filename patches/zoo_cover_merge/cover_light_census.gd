extends SceneTree
## Lights reaching each merged cover mesh, split by bake mode. Loads the
## mission, lets Lux spawn its lights, then for every MeshInstance3D named
## `Cover*` counts the non-directional lights whose range reaches its box --
## the perf harness's own test (`perf_stations.gd` `_light_census`) -- and how
## many of those are LIVE (bake mode not STATIC). GL Compatibility lights at
## most `max_lights_per_object` (8) positional lights per mesh at runtime, and
## a light baked STATIC into the lightmap is not one of them on a lightmapped
## mesh. Prints what it measured and stops.
##     godot --headless --path <walk copy> --script cover_light_census.gd

const CAP: int = 8
const SETTLE_FRAMES: int = 30


func _initialize() -> void:
	_run.call_deferred()


func _collect(n: Node, lights: Array, covers: Array) -> void:
	var l: Light3D = n as Light3D
	if l != null and not (l is DirectionalLight3D):
		lights.append(l)
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi != null and mi.mesh != null and String(mi.name).begins_with("Cover"):
		covers.append(mi)
	for c: Node in n.get_children():
		_collect(c, lights, covers)


func _surface_dist(mi: MeshInstance3D, p: Vector3) -> float:
	var lp: Vector3 = mi.global_transform.affine_inverse() * p
	var ab: AABB = mi.get_aabb()
	var q: Vector3 = Vector3(
		clampf(lp.x, ab.position.x, ab.position.x + ab.size.x),
		clampf(lp.y, ab.position.y, ab.position.y + ab.size.y),
		clampf(lp.z, ab.position.z, ab.position.z + ab.size.z))
	return (mi.global_transform * q).distance_to(p)


func _reach(l: Light3D) -> float:
	var sp: SpotLight3D = l as SpotLight3D
	if sp != null:
		return sp.spot_range
	var om: OmniLight3D = l as OmniLight3D
	if om != null:
		return om.omni_range
	return 0.0


func _run() -> void:
	var ps: PackedScene = load("res://mission.tscn") as PackedScene
	if ps == null:
		print("COVERLIGHTS no res://mission.tscn")
		quit(2)
		return
	var inst: Node = ps.instantiate()
	root.add_child(inst)
	for _i in range(SETTLE_FRAMES):
		await process_frame
	var lights: Array = []
	var covers: Array = []
	_collect(root, lights, covers)
	var modes: Dictionary = {}
	for o in lights:
		var l: Light3D = o as Light3D
		var key: String = "bake_mode %d visible %s" % [int(l.light_bake_mode), str(l.visible)]
		modes[key] = int(modes.get(key, 0)) + 1
	for k in modes.keys():
		print("COVERLIGHTS lights: %d with %s" % [int(modes[k]), k])
	var worst_all: int = 0
	var worst_live: int = 0
	var over_all: int = 0
	var over_live: int = 0
	for o in covers:
		var mi: MeshInstance3D = o as MeshInstance3D
		var n_all: int = 0
		var n_live: int = 0
		for p in lights:
			var l: Light3D = p as Light3D
			if _surface_dist(mi, l.global_position) <= _reach(l):
				n_all += 1
				if l.light_bake_mode != Light3D.BAKE_STATIC and l.visible:
					n_live += 1
		worst_all = maxi(worst_all, n_all)
		worst_live = maxi(worst_live, n_live)
		if n_all > CAP:
			over_all += 1
		if n_live > CAP:
			over_live += 1
		if n_all > CAP or n_live > 3:
			print("COVERLIGHTS %-70s reach %3d  live %3d" % [String(mi.get_path()), n_all, n_live])
	print("COVERLIGHTS %d cover mesh(es); over %d lights: %d counting every light, %d counting live ones; worst %d / %d live"
		% [covers.size(), CAP, over_all, over_live, worst_all, worst_live])
	quit(0)
