extends SceneTree
## Every hit steeper than a body stands on, along the drop-edge instrument's own column walk, at its lattice points
## moved (dx, dz): where each is, what it hit, and the normal Godot reported. A probe: prints what it measured and
## stops.
##
##   godot --headless --path <package copy> --script res://steep_hits.gd -- <out.json> <cell> <x0,z0,x1,z1> <dx> <dz>
##
## The walk is walkable_edge.gd's `_columns` without its capsule (which decides free or occupied, never steep): a
## ray from above the drawn geometry straight down; a hit steeper than FLOOR_MAX_DEG is counted, a hit that is not is
## counted too, and either way the walk goes on 2 * EPS under it. The lattice is the instrument's: the rectangle
## snapped out to the cell, the drawn geometry's height range. Frame: Godot metres, site space.

const FLOOR_MAX_DEG := 45.0
const EPS := 0.02
const MAX_ROWS := 20000


func _walk(n: Node, out: Array) -> void:
	out.append(n)
	for c in n.get_children():
		_walk(c, out)


func _owner_tail(hit: Dictionary) -> String:
	var c: Object = hit.get("collider")
	var n: Node = c as Node
	if n == null:
		return str(c)
	var parts: PackedStringArray = str(n.get_path()).split("/")
	if parts.size() >= 2:
		return parts[parts.size() - 2] + "/" + parts[parts.size() - 1]
	return str(n.get_path())


func _initialize() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() < 5:
		print("[steep] USAGE: <out.json> <cell> <x0,z0,x1,z1> <dx> <dz>")
		quit(2)
		return
	var out_path: String = args[0]
	var cell: float = float(args[1])
	var rect: PackedStringArray = args[2].split(",")
	var dx: float = float(args[3])
	var dz: float = float(args[4])
	await process_frame
	var main_scene: String = String(ProjectSettings.get_setting("application/run/main_scene", ""))
	var packed: PackedScene = load(main_scene) as PackedScene
	var scene: Node = packed.instantiate()
	root.add_child(scene)
	for i in range(20):
		await process_frame
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
	var rx0: float = floorf(minf(float(rect[0]), float(rect[2])) / cell) * cell
	var rz0: float = floorf(minf(float(rect[1]), float(rect[3])) / cell) * cell
	var rx1: float = ceilf(maxf(float(rect[0]), float(rect[2])) / cell) * cell
	var rz1: float = ceilf(maxf(float(rect[1]), float(rect[3])) / cell) * cell
	box = AABB(Vector3(rx0, box.position.y, rz0), Vector3(rx1 - rx0, box.size.y, rz1 - rz0))
	var top: float = box.position.y + box.size.y + 1.0
	var bottom: float = box.position.y - 1.0
	var nx: int = int(box.size.x / cell) + 1
	var nz: int = int(box.size.z / cell) + 1
	var space: PhysicsDirectSpaceState3D = root.world_3d.direct_space_state
	var cos_max: float = cos(deg_to_rad(FLOOR_MAX_DEG))
	var hits: int = 0
	var steep: int = 0
	var by_owner: Dictionary = {}
	var rows: Array = []
	for ix in range(nx):
		for iz in range(nz):
			var x: float = box.position.x + float(ix) * cell + dx
			var z: float = box.position.z + float(iz) * cell + dz
			var y: float = top
			var guard: int = 0
			while y > bottom and guard < 24:
				guard += 1
				var q := PhysicsRayQueryParameters3D.create(Vector3(x, y, z), Vector3(x, bottom, z))
				var hit: Dictionary = space.intersect_ray(q)
				if hit.is_empty():
					break
				hits += 1
				var hy: float = float(hit["position"].y)
				var nrm: Vector3 = hit.get("normal", Vector3.UP)
				if nrm.y < cos_max:
					steep += 1
					var who: String = _owner_tail(hit)
					by_owner[who] = int(by_owner.get(who, 0)) + 1
					if rows.size() < MAX_ROWS:
						rows.append({"x": x, "z": z, "y": snappedf(hy, 0.001), "nx": snappedf(nrm.x, 0.0001),
							"ny": snappedf(nrm.y, 0.0001), "nz": snappedf(nrm.z, 0.0001), "owner": who})
				y = hy - EPS * 2.0
	var report: Dictionary = {"cell": cell, "dx": dx, "dz": dz, "nx": nx, "nz": nz,
		"x0": box.position.x, "z0": box.position.z, "top": top, "bottom": bottom,
		"hits": hits, "steep": steep, "steep_by_owner": by_owner, "rows": rows}
	var fh: FileAccess = FileAccess.open(out_path, FileAccess.WRITE)
	fh.store_string(JSON.stringify(report, "  "))
	fh.close()
	print("[steep] %d x %d columns of %.2f m moved (%.4f, %.4f): %d hits, %d steep" % [nx, nz, cell, dx, dz, hits, steep])
	quit(0)
