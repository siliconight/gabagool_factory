extends SceneTree

## WHAT STANDS AT A DROP EDGE. For each point `walkable_edge.gd` reported (world
## metres, Y up: the midpoint between a standable cell and its neighbour), this
## prints what the rays and the capsule meet on both sides of it, by node path --
## so a residue edge can be attributed to a collider, a seam, or an absence.
##
## For a point (x, y, z) it looks at the two cells 0.25 m either side of it along
## the axis the edge spans (the midpoint sits between them), and for each cell:
##   * the column: every downward hit from y + 1.5 to y - 12, with the node that
##     owns the collider and the hit height;
##   * the body's capsule (0.20 x 1.80) standing on the hit nearest `y`: what it
##     overlaps, if anything;
## and across the edge, at y + 0.55 (the barrier height), the ray from one cell to
## the other: what it meets, if anything.
##
## Usage:
##   godot --headless --path <pkg> --script res://probe_at.gd -- <points.json> <out.json>

const STAND_M := 1.80
const PROBE_R := 0.20
const BARRIER_Y := 0.55


func _initialize() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() < 2:
		print("[probe_at] USAGE: <points.json> <out.json>")
		quit(2)
		return
	_run(args[0], args[1])


func _owner_path(hit: Dictionary) -> String:
	var c: Object = hit.get("collider")
	if c == null:
		return "?"
	var n: Node = c as Node
	if n == null:
		return str(c)
	return str(n.get_path())


func _column(space: PhysicsDirectSpaceState3D, x: float, z: float, top: float, bottom: float) -> Array:
	var out: Array = []
	var y: float = top
	var guard: int = 0
	while y > bottom and guard < 16:
		guard += 1
		var q := PhysicsRayQueryParameters3D.create(Vector3(x, y, z), Vector3(x, bottom, z))
		var hit: Dictionary = space.intersect_ray(q)
		if hit.is_empty():
			break
		out.append({"y": snappedf(float(hit["position"].y), 0.001), "node": _owner_path(hit)})
		y = float(hit["position"].y) - 0.04
	return out


func _run(points_path: String, out_path: String) -> void:
	await process_frame
	var main_scene: String = String(ProjectSettings.get_setting("application/run/main_scene", ""))
	var packed: PackedScene = load(main_scene) as PackedScene
	var scene: Node = packed.instantiate()
	root.add_child(scene)
	for i in range(20):
		await process_frame
	var space: PhysicsDirectSpaceState3D = root.world_3d.direct_space_state
	var capsule := CapsuleShape3D.new()
	capsule.radius = PROBE_R
	capsule.height = STAND_M
	var stand := PhysicsShapeQueryParameters3D.new()
	stand.shape = capsule
	stand.collide_with_areas = false
	stand.collide_with_bodies = true

	var fh: FileAccess = FileAccess.open(points_path, FileAccess.READ)
	var points: Array = JSON.parse_string(fh.get_as_text())
	fh.close()
	var report: Array = []
	for p in points:
		var x: float = float(p["x"])
		var y: float = float(p["y"])
		var z: float = float(p["z"])
		# The midpoint sits on a half-cell; the cells are 0.25 m either side along
		# whichever axis is off the 0.5 m grid.
		var along_x: bool = abs(fmod(x, 0.5)) > 0.1
		var a := Vector3(x - (0.25 if along_x else 0.0), y, z - (0.0 if along_x else 0.25))
		var b := Vector3(x + (0.25 if along_x else 0.0), y, z + (0.0 if along_x else 0.25))
		var row: Dictionary = {"place": p.get("place", ""), "x": x, "y": y, "z": z, "drop_m": p.get("drop_m", 0)}
		for side in [["a", a], ["b", b]]:
			var pt: Vector3 = side[1]
			var col: Array = _column(space, pt.x, pt.z, y + 1.5, y - 12.0)
			row[side[0] + "_column"] = col
			# the capsule standing on the surface nearest y (if any)
			var nearest: float = -1e9
			for h in col:
				if abs(float(h["y"]) - y) < abs(nearest - y):
					nearest = float(h["y"])
			if nearest > -1e8:
				stand.transform = Transform3D(Basis(), Vector3(pt.x, nearest + 0.02 + STAND_M * 0.5, pt.z))
				var over: Array = []
				for h in space.intersect_shape(stand, 6):
					over.append(_owner_path(h))
				row[side[0] + "_capsule_overlaps"] = over
		var q := PhysicsRayQueryParameters3D.create(
			Vector3(a.x, y + BARRIER_Y, a.z), Vector3(b.x, y + BARRIER_Y, b.z))
		var hit: Dictionary = space.intersect_ray(q)
		row["barrier_a_to_b"] = "" if hit.is_empty() else _owner_path(hit)
		var q2 := PhysicsRayQueryParameters3D.create(
			Vector3(b.x, y + BARRIER_Y, b.z), Vector3(a.x, y + BARRIER_Y, a.z))
		var hit2: Dictionary = space.intersect_ray(q2)
		row["barrier_b_to_a"] = "" if hit2.is_empty() else _owner_path(hit2)
		report.append(row)
		print("[probe_at] %s (%.2f, %.2f, %.2f) a:%d surfaces b:%d surfaces barrier a>b %s | b>a %s"
			% [row["place"], x, y, z, row["a_column"].size(), row["b_column"].size(),
			   row["barrier_a_to_b"], row["barrier_b_to_a"]])
	var out: FileAccess = FileAccess.open(out_path, FileAccess.WRITE)
	out.store_string(JSON.stringify(report, "  "))
	out.close()
	quit(0)
