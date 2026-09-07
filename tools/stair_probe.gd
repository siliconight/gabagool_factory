extends SceneTree
## What is above, and what is under, every tread of every stair in a build.
##
##     godot --path <walk project> --headless --script stair_probe.gd
##
## WHY IT EXISTS. Roadmap 114 was six refuted static hypotheses deep --
## stair width at three values, two crate placements, an undersized slab cut,
## a missing discharge bridge -- before anything was measured in the physics
## world, and then two throwaway probes found it in two runs. The first cast
## UP from each tread and found an interior wall 2.05 m over the climber where
## the navmesh bake quantises a 2.0 m agent to 2.10. The second cast DOWN the
## travel axis and found a door lintel standing between the walker and the
## ramp. Both are here, both driven off the treads the build actually emitted,
## so neither needs a coordinate typed in by hand.
##
## READ IT LIKE THIS. `up` is headroom: compare it against the bake's agent
## height, remembering that Recast rounds that UP to a whole number of cell
## heights (`ceil(height / cell_height) * cell_height`), so 2.0 m of contract
## is 2.10 m of bake at the usual 0.15. `over` is the first thing a ray finds
## coming DOWN from above the building at the same spot: on a healthy stair it
## is the tread itself or the ramp under it, and ANY other name means a solid
## is interposed between the sky and the step -- which is how a wall drawn
## across a staircase shows up.
##
## It prints what it measured and stops. Whether a given number is fatal
## depends on the bake settings, and that comparison belongs in the reply.

const UP := Vector3(0.0, 1.0, 0.0)
const PROBE_LEN := 6.0
const EPS := 0.05
const SKY := 40.0
const SETTLE_FRAMES := 12


func _init() -> void:
	var scene: String = String(ProjectSettings.get_setting(
		"application/run/main_scene", "res://walk.tscn"))
	var ps: PackedScene = load(scene)
	if ps == null:
		print("stair_probe: cannot load " + scene)
		quit(1)
		return
	var root_node: Node = ps.instantiate()
	get_root().add_child(root_node)
	# Physics bodies from a glTF `-colonly` suffix exist only once the scene
	# has entered the tree and a physics step has run.
	for _i in range(SETTLE_FRAMES):
		await physics_frame

	var by_stair: Dictionary = {}
	for n in root_node.find_children("stair*", "Node3D", true, false):
		var nm: String = String(n.name)
		# treads are `stair<i><ch>_<story>_<step>`; ramps, landings, dividers
		# and discharge plates all carry a word after `stair<i>` and are the
		# surfaces we expect to FIND, not the ones we sample from.
		if nm.contains("ramp") or nm.contains("land") or nm.contains("col") \
				or nm.contains("divider") or nm.contains("discharge"):
			continue
		var parts: PackedStringArray = nm.split("_")
		if parts.size() < 3:
			continue
		if not parts[parts.size() - 1].is_valid_int():
			continue
		var key: String = parts[0]
		if not by_stair.has(key):
			by_stair[key] = []
		(by_stair[key] as Array).append(n)

	if by_stair.is_empty():
		print("stair_probe: no treads in " + scene)
		quit(1)
		return

	var keys: Array = by_stair.keys()
	keys.sort()
	for key in keys:
		var steps: Array = by_stair[key]
		# One line, on purpose: GDScript has no implicit line continuation,
		# and a lambda body split across lines is a parse error at load.
		steps.sort_custom(func(a, b): return (a as Node3D).global_position.y < (b as Node3D).global_position.y)
		var first: Node3D = steps[0]
		var space: PhysicsDirectSpaceState3D = \
			first.get_world_3d().direct_space_state
		print("")
		print("%s: %d treads in %s" % [key, steps.size(), scene])
		var head: String = "%-18s %7s %7s %7s   %-22s %s"
		print(head % ["tread", "x", "y", "up", "first hit above",
			"first hit from the sky"])
		for s in steps:
			var t: Node3D = s
			var p: Vector3 = t.global_position + UP * EPS
			var clear: float = PROBE_LEN
			var above: String = "-- nothing within %.1f m" % PROBE_LEN
			var q: PhysicsRayQueryParameters3D = \
				PhysicsRayQueryParameters3D.create(p, p + UP * PROBE_LEN)
			q.hit_back_faces = true
			var hit: Dictionary = space.intersect_ray(q)
			if not hit.is_empty():
				clear = (hit["position"] as Vector3).y - p.y
				above = _name_of(hit["collider"])
			var sky: Vector3 = Vector3(p.x, SKY, p.z)
			var qd: PhysicsRayQueryParameters3D = \
				PhysicsRayQueryParameters3D.create(sky, Vector3(p.x, -SKY, p.z))
			qd.hit_back_faces = true
			var down: Dictionary = space.intersect_ray(qd)
			var over: String = "-- nothing"
			if not down.is_empty():
				over = "%s at %.2f" % [_name_of(down["collider"]),
					(down["position"] as Vector3).y]
			print(head % [String(t.name), "%.2f" % p.x, "%.2f" % p.y,
				"%.2f" % clear, above, over])
	quit(0)


func _name_of(col: Object) -> String:
	return String((col as Node).name) if col is Node else str(col)
