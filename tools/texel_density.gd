extends SceneTree
## Effective WORLD texel density per kit surface, and the spread across them.
##
##     godot --path <walk-project> --headless --script tools/texel_density.gd
##
## WHY THIS EXISTS, and it is the instrument two other ones failed to be.
## Roadmap 88 is "a scaled module stretches its texture", and for a whole
## session it was judged by comparing RENDERS against a reference build. Both
## metrics tried were wrong in opposite directions:
##
##   * `look_shots` MEAN LUMA is blind to it. Re-projecting or blurring a
##     texture moves texels around and leaves the average where it was, so it
##     scored a build with the fix switched OFF as a 0.14 match against the
##     build with it on. An instrument that passes the unfixed build has not
##     tested anything.
##   * PER-PIXEL difference is oversensitive. It read 24.18% of pixels
##     differing between two routes whose material state was identical on
##     6474 surfaces across nineteen fields, and the person who reported the
##     defect called both "good enough". A gate nobody can see is not a gate.
##
## The defect is not a picture, so stop photographing it. Density is the
## quantity the defect is ABOUT, it is a property of the scene rather than of
## a frame, it needs no reference build, and it does not care where the
## cameras point.
##
## THE ARITHMETIC. Without triplanar the texture rides the mesh's own UVs, so
## a node scaled onto a slot remainder divides its density by that scale:
## world density is `uv1_scale / node_scale`, per axis. World triplanar
## projects from world position instead and node scale drops out entirely, so
## world density IS `uv1_scale`. That is why changing a skin's
## `meters_per_tile` cannot fix a stretched filler -- it scales both a
## filler and its neighbour and cancels -- and why world projection can.
##
## Measured on `precinct_yard_001`, concrete, 2434 kit surfaces: shipping
## spans 0.106 to 5.000 (47.0x mismatch between surfaces, 47.0x stretch within
## one surface); with world triplanar every surface reads 1.200 (1.0x, 1.0x).
##
## Reports the numbers and stops. Whether a given spread is acceptable is an
## art call and belongs in the reply, not in this file.

const SCENE := "res://site_walk.tscn"


## True when any ancestor is a Deli Counter wall slot. The same `ext_*` /
## `int_*` naming `repetition_census.py`, `look_shots.gd` and
## `walk_triplanar.gd` read, so the tools agree on what a wall is.
func _is_kit(n: Node) -> bool:
	var cur: Node = n
	while cur != null:
		var nm: String = String(cur.name)
		if nm.begins_with("ext_") or nm.begins_with("int_"):
			return true
		cur = cur.get_parent()
	return false


func _init() -> void:
	var ps: PackedScene = load(SCENE)
	if ps == null:
		print("texel_density: cannot load " + SCENE)
		quit(1)
		return
	var root_node: Node = ps.instantiate()
	get_root().add_child(root_node)
	# One frame is not enough: the walk project's runtime passes mutate
	# materials in _ready, and instanced subtrees are not all present yet.
	for _i in range(20):
		await process_frame

	var per_skin: Dictionary = {}
	var surfaces: int = 0
	for n in root_node.find_children("*", "MeshInstance3D", true, false):
		var mi: MeshInstance3D = n
		if mi.mesh == null or not _is_kit(mi):
			continue
		var sc: Vector3 = mi.global_transform.basis.get_scale()
		for s in range(mi.mesh.get_surface_count()):
			var bm: BaseMaterial3D = mi.get_active_material(s) as BaseMaterial3D
			if bm == null:
				continue
			var k: float = bm.uv1_scale.x
			var dx: float = k
			var dy: float = k
			if not bm.uv1_triplanar:
				dx = k / maxf(absf(sc.x), 0.0001)
				dy = k / maxf(absf(sc.y), 0.0001)
			var skin: String = bm.resource_name
			if not per_skin.has(skin):
				# lo, hi, worst per-surface anisotropy, count, triplanar
				per_skin[skin] = [INF, -INF, 1.0, 0, bm.uv1_triplanar]
			var r: Array = per_skin[skin]
			r[0] = minf(r[0], minf(dx, dy))
			r[1] = maxf(r[1], maxf(dx, dy))
			r[2] = maxf(r[2], maxf(dx / maxf(dy, 0.0001), dy / maxf(dx, 0.0001)))
			r[3] = int(r[3]) + 1
			r[4] = bm.uv1_triplanar
			surfaces += 1

	print("texel_density: %d kit surface(s) over %d skin(s)"
		% [surfaces, per_skin.size()])
	print("%-26s %6s %9s %9s %9s %9s" % ["skin", "surfs", "min d", "max d",
		"mismatch", "stretch"])
	var names: Array = per_skin.keys()
	names.sort()
	var worst: float = 1.0
	for skin in names:
		var r: Array = per_skin[skin]
		var mismatch: float = float(r[1]) / maxf(float(r[0]), 0.0001)
		worst = maxf(worst, mismatch)
		var tri: String = "  world-triplanar" if bool(r[4]) else ""
		print("%-26s %6d %9.3f %9.3f %8.1fx %8.1fx%s"
			% [skin, int(r[3]), float(r[0]), float(r[1]), mismatch,
				float(r[2]), tri])
	print("worst mismatch on any skin: %.1fx" % worst)
	quit(0)
