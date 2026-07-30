extends SceneTree
## navmesh_solid_probe.gd -- is the baked navmesh inside solid geometry?
##
##   godot4 --headless --path <site>_proj --script res://navmesh_solid_probe.gd
##
## The walktest walkers stop on three sites pressed against a stair ramp with a
## HORIZONTAL contact normal, on a path the navmesh handed them. The ramp's foot
## sits exactly on the slab (slab top -3.20, ramp base -3.20) and it rises
## 3.40 m over a 4.16 m run -- 39.2 deg, legal by every number in
## agent_contract.json.
##
## The first hypothesis was that the bake had produced walkable surface inside
## the stair hull. The polygon test said no: 132 polygons near the stuck point,
## ONE solid, and that one buried in `cover_13` -- a prop, not the stairs. That
## refutation was recorded here and it was WRONG, because the test was weaker
## than the defect. A polygon CENTRE can sit in clear air while most of the
## polygon is swallowed; testing centres answers a question nobody asked.
## Swept with the walker's own body at the height the walker actually stands,
## `stair0ramp_-1` obstructs 39 of 41 samples across the 0.73 m -- the first at
## the walker's own position. So there IS navmesh where a body cannot stand,
## and the centre test could not see it. Both results are kept above each other
## on purpose: the lesson is not the ramp, it is that the instrument was cheap
## in the same way the thing it was auditing was cheap.
##
## Two questions now, in order. Which polygons cannot hold a body -- that is the
## bake's honesty, and one stray polygon in a cover block is item 12 in
## miniature rather than the blockage. And then: what is physically between the
## walker and the waypoint it could not reach, swept with the walker's own
## capsule, because polygon CENTRES coming back clear says nothing about the
## space between them.
##
## WHERE IS THE FEET LINE? The sweep first reported the whole segment CLEAR,
## which cannot be reconciled with the walker reporting on_wall against
## `stair0ramp_-1` at the same coordinate. The two are only both true if the
## probe put the body somewhere the walker is not. The stuck y is -2.30; the
## slab top is -3.20; AGENT_HEIGHT * 0.5 is 0.90; -3.20 + 0.90 = -2.30 exactly.
## The reported coordinate is the body's CENTRE standing on the slab, and the
## first sweep added another half-height on top of it, floating a capsule a
## metre up where the ramp's lower steps could not reach it. A polygon centre
## IS a floor point and does need lifting; a body position does not. So the
## sweep now runs both readings and labels them, because guessing which one a
## coordinate means is how the last three hours were spent.

#: Where the walkers give up. Override per site with DC_PROBE_AT="x,y,z".
const DEFAULT_AT := Vector3(35.8, -2.3, -14.9)
const RADIUS_M := 12.0          # how far around that point to look
#: The walker's own body, from the director: AGENT_RADIUS * 0.7, AGENT_HEIGHT.
const CAPSULE_RADIUS := 0.28
const CAPSULE_HEIGHT := 1.8

var _scene: Node
var _done := false
var _frames := 0


func _at() -> Vector3:
	var raw := OS.get_environment("DC_PROBE_AT")
	if raw == "":
		return DEFAULT_AT
	var p := raw.split(",")
	if p.size() != 3:
		return DEFAULT_AT
	return Vector3(float(p[0]), float(p[1]), float(p[2]))


func _initialize() -> void:
	var found := ""
	var dir := DirAccess.open("res://")
	if dir != null:
		for f in dir.get_files():
			if f.ends_with("_navqa.tscn"):
				found = f
				break
	if found == "":
		print("[probe] no *_navqa.tscn in this project")
		quit(2)
		return
	var packed: PackedScene = load("res://" + found)
	if packed == null:
		print("[probe] cannot load ", found)
		quit(2)
		return
	print("[probe] scene: ", found)
	_scene = packed.instantiate()
	var setup: Node = _scene.get_node_or_null("NavQASetup")
	if setup != null:
		setup.set("run_on_ready", false)   # bake yes, the walker sim no
	get_root().add_child(_scene)


func _process(_delta: float) -> bool:
	if _done:
		return true
	var map: RID = get_root().get_world_3d().navigation_map
	NavigationServer3D.map_force_update(map)
	_frames += 1
	# The NavigationServer commits a baked region on its own schedule; querying
	# before it settles answers about the world origin instead of the map.
	var probe := NavigationServer3D.map_get_closest_point(map, Vector3(0, 100, 0))
	if (NavigationServer3D.map_get_iteration_id(map) == 0 or probe == Vector3.ZERO) \
			and _frames < 900:
		return false
	_done = true
	print("[probe] map settled after %d frame(s), %d region(s)"
		% [_frames, NavigationServer3D.map_get_regions(map).size()])

	var region: NavigationRegion3D = _scene.get_node_or_null("Nav") as NavigationRegion3D
	if region == null:
		print("[probe] no Nav region")
		return true
	var nm: NavigationMesh = region.navigation_mesh
	if nm == null:
		print("[probe] region has no navigation_mesh")
		return true
	var verts := nm.get_vertices()
	var xform := region.global_transform
	var at := _at()
	print("[probe] %d polygons in the bake; testing those within %.1f m of (%.1f, %.1f, %.1f)"
		% [nm.get_polygon_count(), RADIUS_M, at.x, at.y, at.z])

	var space := get_root().get_world_3d().direct_space_state
	var shape := CapsuleShape3D.new()
	shape.radius = CAPSULE_RADIUS
	shape.height = CAPSULE_HEIGHT
	var params := PhysicsShapeQueryParameters3D.new()
	params.shape = shape
	params.collide_with_areas = false
	params.collide_with_bodies = true

	var tested := 0
	var solid := 0
	var offenders := {}
	for i in nm.get_polygon_count():
		var poly := nm.get_polygon(i)
		var c := Vector3.ZERO
		for idx in poly:
			c += verts[idx]
		c /= float(poly.size())
		c = xform * c
		if c.distance_to(at) > RADIUS_M:
			continue
		tested += 1
		# Stand the walker's capsule on this polygon, feet on the surface.
		params.transform = Transform3D(Basis(), c + Vector3(0, CAPSULE_HEIGHT * 0.5 + 0.02, 0))
		var hits := space.intersect_shape(params, 8)
		if hits.is_empty():
			continue
		solid += 1
		var names: Array = []
		for h in hits:
			var o = h.get("collider")
			var nm2 := String((o as Node).name) if o is Node else "<?>"
			names.append(nm2)
			offenders[nm2] = int(offenders.get(nm2, 0)) + 1
		print("[probe] SOLID  poly %4d at (%7.2f, %6.2f, %7.2f)  inside: %s"
			% [i, c.x, c.y, c.z, ", ".join(names)])

	print("\n[probe] %d polygon(s) near the point; %d of them cannot hold a body"
		% [tested, solid])
	if offenders.is_empty():
		print("[probe] every polygon here is CLEAR -- the bake is not the problem "
			+ "and the route is blocked by something else")
	else:
		var keys := offenders.keys()
		keys.sort()
		for k in keys:
			print("[probe]   %-40s %d polygon(s) buried in it" % [k, int(offenders[k])])
		# Names what was found and stops there. The first version of this ended
		# with a fixed sentence blaming the stair hull, and printed it on a run
		# whose single offender was a cover block -- an instrument asserting a
		# cause its own data did not support, in the probe written to settle
		# exactly that kind of claim.
		print("[probe] Those polygons cannot hold a body and should not have "
			+ "baked. What that means depends on what they are buried in: a "
			+ "prop is one defect, a wall or a stair hull is a different one.")
	_headroom(space, nm, xform, at)
	_path(space, params, map)
	_nav_vs_floor(space, map, at, "stuck point")
	_nav_vs_floor(space, map, _to(), "waypoint")
	_sweep(space, params)
	return true


func _path(space: PhysicsDirectSpaceState3D,
		params: PhysicsShapeQueryParameters3D, map: RID) -> void:
	## Ask the navmesh for the route, then walk it with a body.
	##
	## The walktest says four walkers press against `ext_col_0_N_seg27` -- an
	## EXTERIOR WALL SEGMENT -- with a horizontal contact normal and a waypoint
	## 17 m away. Every probe so far has interrogated a single point. The
	## question this asks is different: does the navmesh's own path cross solid
	## geometry, and if so, on which leg?
	##
	## Path points sit ON the navmesh, so they are floor points and the capsule
	## is lifted onto them. That is the opposite of the stuck coordinate, which
	## is a body centre, and confusing the two cost this investigation an hour.
	var a := _at()
	var b := _to()
	var pts := NavigationServer3D.map_get_path(map, a, b, true)
	var head := ("\n[probe] the navmesh's own path from the stuck point to "
		+ "the waypoint: %d point(s)")
	print(head % [pts.size()])
	if pts.size() < 2:
		print("[probe]   NO PATH -- the navmesh does not join these two points, "
			+ "so the walker was steering at a waypoint it could not reach")
		return
	for i in pts.size():
		var q: Vector3 = pts[i]
		print("[probe]   %2d  (%8.2f, %6.2f, %8.2f)" % [i, q.x, q.y, q.z])
	var blocked := 0
	for i in pts.size() - 1:
		var p0: Vector3 = pts[i]
		var p1: Vector3 = pts[i + 1]
		var span := p0.distance_to(p1)
		var steps := maxi(4, int(span / 0.1))
		for j in steps + 1:
			var t := float(j) / float(steps)
			var q := p0.lerp(p1, t)
			params.transform = Transform3D(Basis(),
				q + Vector3(0, CAPSULE_HEIGHT * 0.5 + 0.02, 0))
			var hits := space.intersect_shape(params, 4)
			if hits.is_empty():
				continue
			var o = hits[0].get("collider")
			var n2 := String((o as Node).name) if o is Node else "<?>"
			var line := ("[probe]   leg %d->%d (%.2f m) BLOCKED %.0f%% along at "
				+ "(%.2f, %.2f, %.2f) by %s")
			print(line % [i, i + 1, span, t * 100.0, q.x, q.y, q.z, n2])
			blocked += 1
			break
	if blocked == 0:
		print("[probe]   every leg of the navmesh's own path is clear for a "
			+ "body -- the route is walkable and the walker's steering is what "
			+ "failed")
	else:
		var verdict := ("[probe]   %d of %d leg(s) cross solid geometry -- "
			+ "the navmesh handed out a route through something")
		print(verdict % [blocked, pts.size() - 1])


func _nav_vs_floor(space: PhysicsDirectSpaceState3D, map: RID, p: Vector3,
		label: String) -> void:
	## Does the navmesh think the floor is where the floor is?
	##
	## Every probe so far has interrogated the geometry, and the geometry keeps
	## coming back innocent: the ramp is a legal 38.7 deg slope, no polygon is
	## buried, nothing is roofed under agent height. But the walker is not
	## steered by the geometry. It is steered by the navmesh, and nothing has
	## yet asked whether the two agree. If the navmesh puts a waypoint 0.58
	## below the surface a body would actually stand on there, the walker
	## spends its whole budget trying to walk down into solid ramp, and every
	## measurement of the ramp will keep saying the ramp is fine -- because it
	## is.
	var np := NavigationServer3D.map_get_closest_point(map, p)
	var nn := NavigationServer3D.map_get_closest_point_normal(map, p)
	var rq := PhysicsRayQueryParameters3D.create(
		Vector3(p.x, p.y + 0.2, p.z), Vector3(p.x, p.y - 6.0, p.z))
	rq.collide_with_areas = false
	rq.collide_with_bodies = true
	var hit := space.intersect_ray(rq)
	print("\n[probe] navmesh vs geometry at the %s:" % [label])
	var nav_line := ("[probe]   navmesh nearest point (%.2f, %.2f, %.2f), "
		+ "normal (%+.2f, %+.2f, %+.2f), %.3f m from the query")
	print(nav_line % [np.x, np.y, np.z, nn.x, nn.y, nn.z, np.distance_to(p)])
	if hit.is_empty():
		print("[probe]   no floor under this point at all")
		return
	var o = hit.get("collider")
	var n2 := String((o as Node).name) if o is Node else "<?>"
	var fy: float = (hit["position"] as Vector3).y
	print("[probe]   physical floor  y=%+.3f  on %s" % [fy, n2])
	var feet := p.y - CAPSULE_HEIGHT * 0.5
	var gap := feet - fy
	var gap_line := ("[probe]   a body centred here has its feet at %+.3f, "
		+ "which is %+.3f from that floor")
	print(gap_line % [feet, gap])
	if absf(gap) > 0.05:
		print("[probe]   ^^ the walker is not standing on the surface under it")


func _headroom(space: PhysicsDirectSpaceState3D, nm: NavigationMesh,
		xform: Transform3D, at: Vector3) -> void:
	## How much room is ABOVE each polygon?
	##
	## This is the question the first two probes kept missing. "Can a capsule
	## stand here" conflates two different failures and answers neither well:
	## resting on a floor reads as a collision, and a body held at the wrong
	## height sails over the obstruction entirely. Headroom does not conflate
	## anything. Fire a ray straight up from the polygon to the height the agent
	## needs; if it hits, the bake has produced walkable surface a body cannot
	## stand upright on, and the ray says by how much and under what.
	##
	## The vertical sections are why this exists. At the stuck point the column
	## is slab, slab, slab -- no ramp. At the waypoint 0.73 m away the ramp
	## surface is already at -2.620, 0.58 above the slab the walker stands on,
	## with the slab STILL under it at -3.200. So the two ends are not on the
	## same floor, and a horizontal sweep between them was never the route.
	var verts := nm.get_vertices()
	var need := CAPSULE_HEIGHT
	var tested := 0
	var cramped := 0
	var by_name := {}
	var lowest := 1e9
	var lowest_name := ""
	var lowest_at := Vector3.ZERO
	for i in nm.get_polygon_count():
		var poly := nm.get_polygon(i)
		var c := Vector3.ZERO
		for idx in poly:
			c += verts[idx]
		c /= float(poly.size())
		c = xform * c
		if c.distance_to(at) > RADIUS_M:
			continue
		tested += 1
		# Not just the centre. A polygon can be mostly under an overhang with
		# its centroid poking out into clear air, which is exactly how the
		# first probe cleared the stairs and the second cleared this. Sample
		# the centre and a point drawn most of the way toward each vertex.
		var probes: Array[Vector3] = [c]
		for idx in poly:
			probes.append(c.lerp(xform * verts[idx], 0.8))
		var hit_here := false
		for q in probes:
			var rq := PhysicsRayQueryParameters3D.create(
				q + Vector3(0, 0.05, 0), q + Vector3(0, need, 0))
			rq.collide_with_areas = false
			rq.collide_with_bodies = true
			var hit := space.intersect_ray(rq)
			if hit.is_empty():
				continue
			hit_here = true
			var o = hit.get("collider")
			var n2 := String((o as Node).name) if o is Node else "<?>"
			var head: float = (hit["position"] as Vector3).y - q.y
			by_name[n2] = int(by_name.get(n2, 0)) + 1
			if head < lowest:
				lowest = head
				lowest_name = n2
				lowest_at = q
		if hit_here:
			cramped += 1
	var head_line := ("\n[probe] headroom: %d of %d polygon(s) here have less "
		+ "than %.2f m of clear space above them")
	print(head_line % [cramped, tested, need])
	if cramped == 0:
		print("[probe]   every polygon here can hold an upright body")
		return
	var keys := by_name.keys()
	keys.sort()
	for k in keys:
		print("[probe]   %-28s roofs %d polygon(s)" % [k, int(by_name[k])])
	var worst := ("[probe]   worst is %.2f m under %s at (%.2f, %.2f, %.2f) "
		+ "-- a %.2f m body does not fit there and it should not have baked")
	print(worst % [lowest, lowest_name, lowest_at.x, lowest_at.y, lowest_at.z,
		need])


func _to() -> Vector3:
	## The waypoint the walker could not reach. Default is walkup_siege's 2/18.
	var raw := OS.get_environment("DC_PROBE_TO")
	if raw == "":
		return Vector3(35.6, -2.3, -15.6)
	var p := raw.split(",")
	if p.size() != 3:
		return Vector3(35.6, -2.3, -15.6)
	return Vector3(float(p[0]), float(p[1]), float(p[2]))


## The parameters are typed because the body relies on inference: `var hits :=
## space.intersect_shape(...)` has no type to infer from if `space` arrives
## untyped, and that is a parse error rather than a warning.
func _sweep(space: PhysicsDirectSpaceState3D,
		params: PhysicsShapeQueryParameters3D) -> void:
	## What is between the walker and the waypoint it never reached?
	##
	## Polygon centres coming back clear does not mean the route is walkable:
	## a body travels the space BETWEEN them. Sample the capsule along the
	## segment and name the first thing it touches.
	##
	## Run twice, because the first version silently assumed the stuck
	## coordinate was a FLOOR point and lifted the capsule half a height onto
	## it. If the coordinate is already the body's centre -- which the -3.20
	## slab top plus 0.90 says it is -- that lift floats the capsule a metre
	## above where the walker actually stands, and a sweep that misses the
	## obstruction reports CLEAR just as confidently as one that is right.
	var a := _at()
	var b := _to()
	# GDScript has no implicit adjacent-string concatenation: a format string
	# split across lines needs an explicit `+`, and the `%` has to apply to the
	# whole joined string, so the join is parenthesised.
	var fmt := ("\n[probe] sweeping the walker capsule from (%.2f, %.2f, %.2f) "
		+ "to (%.2f, %.2f, %.2f) -- %.2f m")
	print(fmt % [a.x, a.y, a.z, b.x, b.y, b.z, a.distance_to(b)])
	var note := ("[probe] half a capsule is %.2f, so a body CENTRED on y=%.2f "
		+ "has its feet at %.2f -- the slab top is -3.20")
	print(note % [CAPSULE_HEIGHT * 0.5, a.y, a.y - CAPSULE_HEIGHT * 0.5])
	_sweep_at(space, params, a, b, 0.0,
		"CENTRE  (coordinate is the body origin, feet at %.2f)"
		% [a.y - CAPSULE_HEIGHT * 0.5])
	_sweep_at(space, params, a, b, CAPSULE_HEIGHT * 0.5 + 0.02,
		"FEET    (coordinate is a floor point, feet at %.2f)" % [a.y])
	_sweep_floor(space, params, a, b)
	_section(space, a, "stuck point")
	_section(space, b, "waypoint")


func _sweep_floor(space: PhysicsDirectSpaceState3D,
		params: PhysicsShapeQueryParameters3D, a: Vector3, b: Vector3) -> void:
	## The only honest sweep: stand the body on whatever floor is actually
	## under each sample rather than on a straight line between the ends.
	##
	## The sections showed the two ends are not on the same surface -- slab at
	## the stuck point, ramp 0.58 higher at the waypoint -- so a level segment
	## between them is not a route anything walks. This finds the floor in each
	## column, puts the feet on it, and reports two things: the largest jump
	## between one column's floor and the next, which is the step the body is
	## being asked to take, and anything the body still intersects while
	## standing correctly.
	var steps := 40
	var prev := 1e9
	var worst := 0.0
	var worst_t := 0.0
	var gone := 0
	var stuck_in := {}
	print("\n[probe] sweeping again, this time standing on the floor found in "
		+ "each column:")
	for i in steps + 1:
		var t := float(i) / float(steps)
		var p2 := a.lerp(b, t)
		# Start just above the body, NOT high above the site. The first version
		# started 6 m up and the storey slab at +3.200 is inside that, so every
		# column returned the floor of the storey above -- 41 identical answers,
		# a jump of exactly 0.000, and a capsule standing in open air being
		# reported clear. A floor query has to start below the next ceiling.
		var rq := PhysicsRayQueryParameters3D.create(
			Vector3(p2.x, a.y + 0.2, p2.z), Vector3(p2.x, a.y - 6.0, p2.z))
		rq.collide_with_areas = false
		rq.collide_with_bodies = true
		var hit := space.intersect_ray(rq)
		if hit.is_empty():
			gone += 1
			prev = 1e9
			continue
		var fy: float = (hit["position"] as Vector3).y
		if prev < 1e8 and absf(fy - prev) > worst:
			worst = absf(fy - prev)
			worst_t = t
		prev = fy
		params.transform = Transform3D(Basis(),
			Vector3(p2.x, fy + CAPSULE_HEIGHT * 0.5 + 0.02, p2.z))
		for h in space.intersect_shape(params, 8):
			var o = h.get("collider")
			var n2 := String((o as Node).name) if o is Node else "<?>"
			stuck_in[n2] = int(stuck_in.get(n2, 0)) + 1
	if gone > 0:
		print("[probe]   %d of %d columns have no floor at all" % [gone, steps + 1])
	var jump := ("[probe]   largest floor-to-floor jump %.3f m, %.0f%% along, "
		+ "over %.3f m of travel")
	print(jump % [worst, worst_t * 100.0, a.distance_to(b) / float(steps)])
	if stuck_in.is_empty():
		print("[probe]   a body standing on the floor is clear the whole way")
		return
	var keys := stuck_in.keys()
	keys.sort()
	for k in keys:
		var line := ("[probe]   even standing on the floor, the body is inside "
			+ "%s at %d of %d samples")
		print(line % [k, int(stuck_in[k]), steps + 1])


func _section(space: PhysicsDirectSpaceState3D, p: Vector3, label: String) -> void:
	## Every surface stacked over this column, top down.
	##
	## The CENTRE sweep named `slab_col_-1` at all 41 samples, which is not a
	## blockage: the capsule's feet land exactly on the slab top and
	## intersect_shape has no epsilon, so resting on a floor reads the same as
	## being inside a wall. Only a shape query cannot tell those apart. A ray
	## can -- it returns the surface height and the normal -- so this prints the
	## whole column and lets the geometry say which surface is floor, which is
	## ceiling, and how much room is between them.
	var rq := PhysicsRayQueryParameters3D.create(
		p + Vector3(0, 20.0, 0), p + Vector3(0, -20.0, 0))
	rq.collide_with_areas = false
	rq.collide_with_bodies = true
	var excluded: Array[RID] = []
	print("\n[probe] vertical section at the %s (%.2f, _, %.2f):"
		% [label, p.x, p.z])
	for _i in 8:
		rq.exclude = excluded
		var hit := space.intersect_ray(rq)
		if hit.is_empty():
			break
		var o = hit.get("collider")
		var n2 := String((o as Node).name) if o is Node else "<?>"
		var pos: Vector3 = hit["position"]
		var nrm: Vector3 = hit["normal"]
		var face := "floor" if nrm.y > 0.7 else ("wall" if absf(nrm.y) < 0.3
			else "slope")
		print("[probe]     y=%+7.3f  %-26s %-6s normal (%+.2f, %+.2f, %+.2f)"
			% [pos.y, n2, face, nrm.x, nrm.y, nrm.z])
		excluded.append(hit["rid"])
	if excluded.is_empty():
		print("[probe]     nothing in this column at all")


func _sweep_at(space: PhysicsDirectSpaceState3D,
		params: PhysicsShapeQueryParameters3D,
		a: Vector3, b: Vector3, lift: float, label: String) -> void:
	## One reading of the segment. `lift` is what gets added to each sample
	## before the capsule is placed there, and it is the whole question.
	var steps := 40
	var first := -1
	var blocked := 0
	var found := {}
	for i in steps + 1:
		var t := float(i) / float(steps)
		var p2 := a.lerp(b, t)
		params.transform = Transform3D(Basis(), p2 + Vector3(0, lift, 0))
		var hits := space.intersect_shape(params, 8)
		if hits.is_empty():
			continue
		blocked += 1
		var names: Array = []
		for h in hits:
			var o = h.get("collider")
			var n2 := String((o as Node).name) if o is Node else "<?>"
			names.append(n2)
			found[n2] = int(found.get(n2, 0)) + 1
		if first < 0:
			first = i
			print("[probe]   first contact %.0f%% along at (%.2f, %.2f, %.2f): %s"
				% [t * 100.0, p2.x, p2.y + lift, p2.z, ", ".join(names)])
	if first < 0:
		print("[probe] %s -- CLEAR at all %d samples" % [label, steps + 1])
		return
	var keys := found.keys()
	keys.sort()
	var parts: Array = []
	for k in keys:
		parts.append("%s x%d" % [k, int(found[k])])
	print("[probe] %s -- OBSTRUCTED, %d of %d samples: %s"
		% [label, blocked, steps + 1, ", ".join(parts)])
