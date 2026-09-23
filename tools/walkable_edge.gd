extends SceneTree

## CAN A BODY WALK OFF AN EDGE THE LEVEL DID NOT MEAN TO LEAVE OPEN?
##
## WHY THIS EXISTS. Every gate in this exporter measures traversal correctness
## (can a body get from A to B) or resource closure (does every reference
## resolve). None asks whether a body can FALL somewhere it should not. Three
## defects in three days were found by the walker and by none of the five
## gates that passed their packages -- a grey collar round every cut slab,
## occluders capping the openings they sat over, and this: a stairwell whose
## walk-on gap is sized 2.05 m and clipped to nothing, so 0.98 m of it hangs
## over a descending flight.
##
## WHAT IT MEASURES, and it is a measurement rather than a verdict. For every
## standable point on a grid, whether a neighbouring cell drops further than a
## body can step down, and whether anything solid stands between the two above
## the height a body can step over. An edge with a drop and no barrier is
## reported with its position and its depth. Whether a given edge SHOULD be
## open is a judgement about the level -- a loading dock and a kerb are edges
## somebody meant -- so this prints them and stops.
##
## THE NUMBERS ARE THE CONTRACT'S, not this file's:
##
##   FALL_M      characters.player.max_step_up_m (0.50). What a controller
##               lifts itself over, and by symmetry the largest drop it takes
##               deliberately. Below it a transition is a step -- every stair
##               riser in the library is well under it.
##   BARRIER_Y   the same 0.50, plus a margin. A solid no taller than what a
##               body steps over does not stop it walking off, so a guard is
##               only a guard above this line. Deli Counter builds rails at
##               GUARD_HEIGHT 1.07, comfortably over.
##   STAND_M     characters.player.height_m (1.80). A surface with less
##               headroom than this is not somewhere a body stands, so it is
##               not somewhere a body walks off.
##
## Usage:
##   godot --headless --path <pkg> --script res://walkable_edge.gd -- <out.json> [cell_m]

const FALL_M := 0.50
const BARRIER_MARGIN := 0.05
const STAND_M := 1.80
const BODY_R := 0.35
#: Probe from this far above a surface so a ray does not start inside it.
const EPS := 0.02
#: Cap the report; the JSON is evidence, not a phone book.
const MAX_ROWS := 4000


func _initialize() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() < 1:
		print("[edge] USAGE: <out.json> [cell_m]")
		quit(2)
		return
	_run(args[0], float(args[1]) if args.size() > 1 else 0.5)


func _walk(n: Node, out: Array) -> void:
	out.append(n)
	for c in n.get_children():
		_walk(c, out)


## Every surface under (x, z), top down, that a body could stand on.
func _columns(space: PhysicsDirectSpaceState3D, x: float, z: float,
		top: float, bottom: float) -> Array:
	var out: Array = []
	var y: float = top
	var guard: int = 0
	while y > bottom and guard < 24:
		guard += 1
		var q := PhysicsRayQueryParameters3D.create(
			Vector3(x, y, z), Vector3(x, bottom, z))
		var hit: Dictionary = space.intersect_ray(q)
		if hit.is_empty():
			break
		var hy: float = float(hit["position"].y)
		# Headroom: is there room for a body to stand on this surface?
		var up := PhysicsRayQueryParameters3D.create(
			Vector3(x, hy + EPS, z), Vector3(x, hy + STAND_M, z))
		if space.intersect_ray(up).is_empty():
			out.append(hy)
		y = hy - EPS * 2.0
	return out


func _nearest_below(col: Array, y: float) -> float:
	## The highest surface at or below `y` in that column, or -INF.
	var best: float = -1e18
	for h in col:
		var hh: float = float(h)
		if hh <= y + 0.01 and hh > best:
			best = hh
	return best


func _run(out_path: String, cell: float) -> void:
	await process_frame
	var main_scene: String = String(ProjectSettings.get_setting(
		"application/run/main_scene", ""))
	var report: Dictionary = {
		"schema": "lf.walkable_edge.v1", "ok": true, "error": "",
		"cell_m": cell, "fall_m": FALL_M, "barrier_above_m": FALL_M + BARRIER_MARGIN,
		"main_scene": main_scene, "standable_cells": 0,
		"drop_edges": 0, "unguarded": 0, "unguarded_indoors": 0, "edges": [],
	}
	if main_scene == "":
		report["ok"] = false
		report["error"] = "no application/run/main_scene"
		_write(out_path, report)
		quit(0)
		return
	var packed: PackedScene = load(main_scene) as PackedScene
	if packed == null:
		report["ok"] = false
		report["error"] = "main_scene did not load"
		_write(out_path, report)
		quit(0)
		return
	var scene: Node = packed.instantiate()
	root.add_child(scene)
	for i in range(20):
		await process_frame

	# The site's extent, from what is drawn.
	var nodes: Array = []
	_walk(scene, nodes)
	var box := AABB()
	var first: bool = true
	for n in nodes:
		var v: VisualInstance3D = n as VisualInstance3D
		if v == null:
			continue
		var a: AABB = v.global_transform * v.get_aabb()
		if first:
			box = a
			first = false
		else:
			box = box.merge(a)
	if first:
		report["ok"] = false
		report["error"] = "no visual geometry: refusing to report a level with no edges"
		_write(out_path, report)
		quit(0)
		return

	var space: PhysicsDirectSpaceState3D = root.world_3d.direct_space_state
	var top: float = box.position.y + box.size.y + 1.0
	var bottom: float = box.position.y - 1.0
	var nx: int = int(box.size.x / cell) + 1
	var nz: int = int(box.size.z / cell) + 1
	print("[edge] %d x %d cells of %.2f m over x %.1f..%.1f z %.1f..%.1f"
		% [nx, nz, cell, box.position.x, box.position.x + box.size.x,
		   box.position.z, box.position.z + box.size.z])

	# Pass 1: the standable height map.
	var cols: Array = []
	cols.resize(nx * nz)
	var standable: int = 0
	for ix in range(nx):
		for iz in range(nz):
			var x: float = box.position.x + float(ix) * cell
			var z: float = box.position.z + float(iz) * cell
			var c: Array = _columns(space, x, z, top, bottom)
			cols[ix * nz + iz] = c
			standable += c.size()
	report["standable_cells"] = standable

	# Pass 2: edges, and only there does this raycast again.
	var edges: Array = []
	var drops: int = 0
	var unguarded: int = 0
	var indoor: int = 0
	var steps: Array = [[1, 0], [-1, 0], [0, 1], [0, -1]]
	for ix in range(nx):
		for iz in range(nz):
			var here: Array = cols[ix * nz + iz]
			for h in here:
				var y: float = float(h)
				for s in steps:
					var jx: int = ix + int(s[0])
					var jz: int = iz + int(s[1])
					if jx < 0 or jz < 0 or jx >= nx or jz >= nz:
						continue
					var there: Array = cols[jx * nz + jz]
					var below: float = _nearest_below(there, y)
					var drop: float = y - below
					if below < -1e17:
						drop = 1e9
					if drop <= FALL_M:
						continue
					drops += 1
					var x0: float = box.position.x + float(ix) * cell
					var z0: float = box.position.z + float(iz) * cell
					var x1: float = box.position.x + float(jx) * cell
					var z1: float = box.position.z + float(jz) * cell
					# A guard is only a guard ABOVE what a body steps over.
					var by: float = y + FALL_M + BARRIER_MARGIN
					var q := PhysicsRayQueryParameters3D.create(
						Vector3(x0, by, z0), Vector3(x1, by, z1))
					if not space.intersect_ray(q).is_empty():
						continue
					unguarded += 1
					# INDOORS OR UNDER THE SKY, and the difference is the
					# whole usefulness of this instrument. A body that walks
					# off an edge INSIDE a building has found a defect: a
					# stairwell nobody railed, a mezzanine with an open lip.
					# A roof edge or a dock is somebody's decision, and a gate
					# that refuses those refuses every level ever built. The
					# test is what is overhead: a slab or a roof means inside.
					var sky := PhysicsRayQueryParameters3D.create(
						Vector3(x0, y + STAND_M, z0),
						Vector3(x0, y + 100.0, z0))
					var indoors: bool = not space.intersect_ray(sky).is_empty()
					if indoors:
						indoor += 1
					if edges.size() < MAX_ROWS:
						edges.append({
							"x": snappedf((x0 + x1) * 0.5, 0.01),
							"y": snappedf(y, 0.01),
							"z": snappedf((z0 + z1) * 0.5, 0.01),
							"drop_m": snappedf(minf(drop, 999.0), 0.01),
							"indoors": indoors,
						})
	report["drop_edges"] = drops
	report["unguarded"] = unguarded
	report["unguarded_indoors"] = indoor
	edges.sort_custom(func(a, b): return float(a["drop_m"]) > float(b["drop_m"]))
	report["edges"] = edges
	_write(out_path, report)
	print("[edge] standable %d, drop edges %d, unguarded %d, UNGUARDED INDOORS %d"
		% [standable, drops, unguarded, indoor])
	quit(0)


func _write(out_path: String, report: Dictionary) -> void:
	var fh: FileAccess = FileAccess.open(out_path, FileAccess.WRITE)
	if fh == null:
		push_error("[edge] could not write %s" % out_path)
		return
	fh.store_string(JSON.stringify(report, "  "))
	fh.close()
