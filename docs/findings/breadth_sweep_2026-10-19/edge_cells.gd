extends SceneTree
## The drop-edge instrument's own questions, asked of named cell pairs in both arms: each cell's column (every
## surface its walk finds, top down: height, owner, whether the body fits), the surface the body moves to in the
## neighbour, the drop, the barrier ray, the block capsule and the sky ray -- with the column and sky rays on the
## lattice (Level Factory 0.218.2) and moved SEAM_NUDGE off it (0.219.0). A probe: prints what it measured and stops.
##
##   godot --headless --path <package copy> --script res://edge_cells.gd -- <pairs.txt>
##
## pairs.txt: one pair a line, "ax,az,bx,bz" in site metres (cell centres on the gate's lattice). The constants and
## the order of the tests are walkable_edge.gd's, read in the same session; reach (the flood) is not replicated, so
## every free surface of a cell is asked. Frame: Godot metres, site space, y up.

const FALL_M := 0.50
const BARRIER_MARGIN := 0.05
const STAND_M := 1.80
const FLOOR_MAX_DEG := 45.0
const EPS := 0.02
const PROBE_R := 0.20
const BLOCK_H := STAND_M - FALL_M - EPS
const NUDGE_X := 0.0031
const NUDGE_Z := 0.0023

var _stand: PhysicsShapeQueryParameters3D
var _block: PhysicsShapeQueryParameters3D


func _tail(c: Object) -> String:
	var n: Node = c as Node
	if n == null:
		return str(c)
	var parts: PackedStringArray = str(n.get_path()).split("/")
	return parts[parts.size() - 2] + "/" + parts[parts.size() - 1] if parts.size() >= 2 else str(n.get_path())


func _columns(space: PhysicsDirectSpaceState3D, x: float, z: float, top: float, bottom: float) -> Array:
	var out: Array = []
	var y: float = top
	var guard: int = 0
	while y > bottom and guard < 24:
		guard += 1
		var hit: Dictionary = space.intersect_ray(PhysicsRayQueryParameters3D.create(
			Vector3(x, y, z), Vector3(x, bottom, z)))
		if hit.is_empty():
			break
		var hy: float = float(hit["position"].y)
		var nrm: Vector3 = hit.get("normal", Vector3.UP)
		var cos_t: float = clampf(nrm.y, -1.0, 1.0)
		if cos_t < cos(deg_to_rad(FLOOR_MAX_DEG)):
			y = hy - EPS * 2.0
			continue
		var lift: float = PROBE_R * tan(acos(cos_t))
		_stand.transform = Transform3D(Basis(), Vector3(x, hy + EPS + lift + STAND_M * 0.5, z))
		var over: Array = space.intersect_shape(_stand, 1)
		out.append([hy, _tail(hit.get("collider")), over.is_empty(),
			"" if over.is_empty() else _tail(over[0].get("collider"))])
		y = hy - EPS * 2.0
	return out


func _transition(col: Array, y: float) -> int:
	var best: int = -1
	var best_y: float = -1e18
	for k in range(col.size()):
		var hh: float = float(col[k][0])
		if hh <= y + FALL_M + 0.01 and hh > best_y:
			best_y = hh
			best = k
	return best


func _fmt(col: Array) -> String:
	var parts: PackedStringArray = []
	for s in col:
		parts.append("%.3f %s %s" % [float(s[0]), s[1], "free" if s[2] else "OCCUPIED by " + str(s[3])])
	return " | ".join(parts) if parts.size() > 0 else "(nothing)"


func _initialize() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var fh: FileAccess = FileAccess.open(args[0], FileAccess.READ)
	var lines: PackedStringArray = fh.get_as_text().split("\n", false)
	fh.close()
	await process_frame
	var packed: PackedScene = load(String(ProjectSettings.get_setting("application/run/main_scene", ""))) as PackedScene
	var scene: Node = packed.instantiate()
	root.add_child(scene)
	for i in range(20):
		await process_frame
	var space: PhysicsDirectSpaceState3D = root.world_3d.direct_space_state
	var probe := CapsuleShape3D.new()
	probe.radius = PROBE_R
	probe.height = STAND_M
	_stand = PhysicsShapeQueryParameters3D.new()
	_stand.shape = probe
	var above := CapsuleShape3D.new()
	above.radius = PROBE_R
	above.height = BLOCK_H
	_block = PhysicsShapeQueryParameters3D.new()
	_block.shape = above
	var top: float = 60.0
	var bottom: float = -10.0
	for ln in lines:
		var v: PackedStringArray = ln.strip_edges().split(",")
		if v.size() != 4:
			continue
		var ax: float = float(v[0])
		var az: float = float(v[1])
		var bx: float = float(v[2])
		var bz: float = float(v[3])
		for arm in ["0.218.2 on", "0.219.0 off"]:
			var dx: float = 0.0 if arm.ends_with("on") else NUDGE_X
			var dz: float = 0.0 if arm.ends_with("on") else NUDGE_Z
			var ca: Array = _columns(space, ax + dx, az + dz, top, bottom)
			var cb: Array = _columns(space, bx + dx, bz + dz, top, bottom)
			print("[cells] %s  A (%.2f, %.2f): %s" % [arm, ax, az, _fmt(ca)])
			print("[cells] %s  B (%.2f, %.2f): %s" % [arm, bx, bz, _fmt(cb)])
			for s in ca:
				if not s[2]:
					continue
				var y: float = float(s[0])
				var k: int = _transition(cb, y)
				var verdict: String = ""
				if k >= 0 and not cb[k][2]:
					verdict = "into a thing (%s)" % cb[k][1]
				else:
					var drop: float = 1e9 if k < 0 else y - float(cb[k][0])
					if drop <= FALL_M:
						verdict = "no drop (%.3f to %s)" % [drop, cb[k][1]]
					else:
						var by: float = y + FALL_M + BARRIER_MARGIN
						var bar: Dictionary = space.intersect_ray(PhysicsRayQueryParameters3D.create(
							Vector3(ax, by, az), Vector3(bx, by, bz)))
						_block.transform = Transform3D(Basis(), Vector3(bx, y + FALL_M + EPS + BLOCK_H * 0.5, bz))
						var blk: Array = space.intersect_shape(_block, 1)
						var sky: Dictionary = space.intersect_ray(PhysicsRayQueryParameters3D.create(
							Vector3(ax + dx, y + STAND_M, az + dz), Vector3(ax + dx, y + 100.0, az + dz)))
						verdict = "drop %.3f to %s; barrier %s; block %s; overhead %s" % [
							minf(drop, 999.0), "nothing" if k < 0 else str(cb[k][1]),
							"nothing" if bar.is_empty() else _tail(bar.get("collider")),
							"nothing" if blk.is_empty() else _tail(blk[0].get("collider")),
							"sky" if sky.is_empty() else _tail(sky.get("collider"))]
				print("[cells] %s    from %.3f on %s: %s" % [arm, y, s[1], verdict])
	quit(0)
