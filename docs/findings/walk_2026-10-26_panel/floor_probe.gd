extends SceneTree
## Floor probe: what a body standing inside each building at grade would stand on, read from the physics the walk
## preview actually runs. Loads the preview's main scene (walk.tscn), lets physics settle, then casts rays straight
## down on a grid inside each building's footprint and prints what each hit and at what height. Measurements only.
##
## FRAME AND UNITS: Godot metres, Y up. A building's footprint is its `buildings.json` origin (site.tscn instance
## origin) +- half its footprint, x across and z deep (rot 0 only; the script refuses another rotation). Rays start
## at y = START_Y above the building origin and run DOWN_M down; the grid is offset 0.31 / 0.47 m off round numbers
## so a ray does not run down a collider seam (the factory's probes-off-round-coordinates rule).
##
##     godot --headless --path <preview> --script <this file> -- <footprints json>
##
## The footprints json: [{"node": "b1", "id": "...", "at": [x, y, z], "size": [x, z]}, ...].

const START_Y := 1.0
const DOWN_M := 5.0
const STEP := 1.0
const INSET := 0.6


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var footprints: Array = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	var scene: PackedScene = load("res://walk.tscn")
	var level: Node = scene.instantiate()
	root.add_child(level)
	for i in 6:
		await physics_frame
	var space: PhysicsDirectSpaceState3D = level.get_viewport().world_3d.direct_space_state
	for fp in footprints:
		var b: Dictionary = fp
		var at: Array = b["at"]
		var size: Array = b["size"]
		var x0: float = float(at[0]) - float(size[0]) / 2.0 + INSET
		var z0: float = float(at[2]) - float(size[1]) / 2.0 + INSET
		var nx := int((float(size[0]) - 2.0 * INSET) / STEP)
		var nz := int((float(size[1]) - 2.0 * INSET) / STEP)
		var misses: Array = []
		var heights := {}
		var colliders := {}
		for ix in nx + 1:
			for iz in nz + 1:
				var x := x0 + ix * STEP + 0.31
				var z := z0 + iz * STEP + 0.47
				var from := Vector3(x, float(at[1]) + START_Y, z)
				var q := PhysicsRayQueryParameters3D.create(from, from + Vector3(0, -DOWN_M, 0))
				var hit: Dictionary = space.intersect_ray(q)
				if hit.is_empty():
					misses.append([snappedf(x, 0.01), snappedf(z, 0.01)])
					continue
				var y := snappedf(hit["position"].y, 0.05)
				heights[y] = int(heights.get(y, 0)) + 1
				var c: Object = hit["collider"]
				var cname := str(c.get_path()) if c is Node else str(c)
				# group by the collider's owner chain, last three path parts
				var parts := cname.split("/")
				var key := "/".join(parts.slice(max(0, parts.size() - 3)))
				colliders[key] = int(colliders.get(key, 0)) + 1
		var total := (nx + 1) * (nz + 1)
		print("== %s %s: %d rays, %d hit nothing within %.1f m below y=%.1f" % [b["node"], b["id"], total,
			misses.size(), DOWN_M, float(at[1]) + START_Y])
		var hs := heights.keys()
		hs.sort()
		var hline := ""
		for h in hs:
			hline += " %.2f:%d" % [h, heights[h]]
		print("  hit heights (m: rays):" + hline)
		var cs := colliders.keys()
		cs.sort_custom(func(a, c): return colliders[a] > colliders[c])
		for k in cs.slice(0, 8):
			print("  %5d  %s" % [colliders[k], k])
		if not misses.is_empty():
			print("  misses (x, z), first 40: %s" % str(misses.slice(0, 40)))
	quit(0)
