extends Node
## Is non-collision dressing standing in space a body can walk through?
##
## Loaded as an autoload by tools/dressing_in_nav.py into a MIRROR of the
## project under test. Prints one fenced JSON block and quits.
##
## WHY THE NAVMESH AND NOT ROOM BOUNDS. Patina's keep-out rules read one
## building's slots.json and gameplay.json, so they can see a doorway lane and
## a room interior and nothing else. A pilaster 5 cm proud is legal on its own
## facade and becomes an obstruction the moment Lot places another building
## 1.2 m away and the gap between them becomes a route. That gap is a SITE
## fact; no per-building rule can reach it, however good its arithmetic.
##
## The baked NavigationRegion3D is the answer to "where can a body go", it is
## baked from the real assembled site, and it already carries the agent radius
## the rest of the pipeline quotes. So the test is: does a cover's volume
## intersect the space above walkable surface, between step height and head
## height. Anything that does is dressing you walk through.
##
## It reports and stops. A cover in the walk volume may be a placement bug or a
## deliberate prop you are meant to brush past, and this file cannot tell which.

const MARK_BEGIN := "<<<DRESSING_NAV_JSON"
const MARK_END := "DRESSING_NAV_JSON>>>"


func _ready() -> void:
	var frames: int = int(ProjectSettings.get_setting(
		"dressing_nav/settle_frames", 5))
	for _i in range(frames):
		await get_tree().process_frame

	var scene: Node = get_tree().current_scene
	if scene == null:
		_emit({"error": "current_scene is null"})
		return

	var agent_radius: float = float(ProjectSettings.get_setting(
		"dressing_nav/agent_radius", 0.4))
	var step_clear: float = float(ProjectSettings.get_setting(
		"dressing_nav/step_clear", 0.15))
	var body_height: float = float(ProjectSettings.get_setting(
		"dressing_nav/body_height", 1.8))
	var prefix: String = String(ProjectSettings.get_setting(
		"dressing_nav/prefix", "Cover_"))

	var samples: Array = []
	var regions: Array = []
	var baked := await _bake_empty_regions(scene)
	_collect_nav(scene, samples, regions)

	var covers: Array = scene.find_children("*", "MeshInstance3D", true, false)
	var by_family: Dictionary = {}
	var offenders: Array = []
	var considered := 0

	for c in covers:
		var mi := c as MeshInstance3D
		if not String(mi.name).begins_with(prefix):
			continue
		considered += 1
		var fam := _family(String(mi.name))
		if not by_family.has(fam):
			by_family[fam] = [0, 0]
		by_family[fam][0] += 1
		var box: AABB = mi.global_transform * mi.get_aabb()
		var n := _samples_inside(box, samples, agent_radius,
			step_clear, body_height)
		if n > 0:
			by_family[fam][1] += 1
			if offenders.size() < 40:
				offenders.append({
					"name": String(mi.name),
					"family": fam,
					"pos": [snappedf(box.get_center().x, 0.001),
						snappedf(box.get_center().y, 0.001),
						snappedf(box.get_center().z, 0.001)],
					"size": [snappedf(box.size.x, 0.001),
						snappedf(box.size.y, 0.001),
						snappedf(box.size.z, 0.001)],
					"nav_samples": n,
				})

	var flagged := 0
	for fam in by_family:
		flagged += int(by_family[fam][1])

	_emit({
		"scene": String(scene.name),
		"engine": Engine.get_version_info().get("string", "?"),
		"agent_radius": agent_radius,
		"step_clear": step_clear,
		"body_height": body_height,
		"prefix": prefix,
		"nav_regions": regions,
		"nav_samples": samples.size(),
		"baked_here": baked,
		"covers": considered,
		"flagged": flagged,
		"by_family": by_family,
		"offenders": offenders,
	})


func _emit(report: Dictionary) -> void:
	print(MARK_BEGIN)
	print(JSON.stringify(report, "  "))
	print(MARK_END)
	get_tree().quit()


## Every walkable sample point, in world space: each polygon's vertices AND its
## centroid. Vertices alone miss a wide polygon's middle; centroids alone miss
## its edges, and an alley is exactly an edge case -- the dressing stands at
## the boundary of the walkable strip, not in the middle of it.
func _collect_nav(scene: Node, out_samples: Array, out_regions: Array) -> void:
	for n in scene.find_children("*", "NavigationRegion3D", true, false):
		var region := n as NavigationRegion3D
		var nm: NavigationMesh = region.navigation_mesh
		if nm == null:
			out_regions.append({"path": String(scene.get_path_to(region)),
				"polygons": 0, "note": "no navigation_mesh resource"})
			continue
		var verts: PackedVector3Array = nm.get_vertices()
		var xf := region.global_transform
		var polys := nm.get_polygon_count()
		for i in range(polys):
			var idx: PackedInt32Array = nm.get_polygon(i)
			var centroid := Vector3.ZERO
			for j in idx:
				var w: Vector3 = xf * verts[j]
				out_samples.append(w)
				centroid += w
			if idx.size() > 0:
				out_samples.append(centroid / float(idx.size()))
		# WHAT THE BAKE PARSED decides whether a zero here means anything.
		# parsed_geometry_type MESH_INSTANCES (0) carves the walkable surface
		# around every visual mesh -- including the dressing -- so no cover can
		# overlap nav by construction and "0 in the way" is circular.
		# STATIC_COLLIDERS (1) ignores geometry with no collider, which covers
		# are by contract, and only then is the zero a finding.
		out_regions.append({"path": String(scene.get_path_to(region)),
			"polygons": polys, "vertices": verts.size(),
			"parsed_geometry_type": nm.geometry_parsed_geometry_type,
			"source_geometry_mode": nm.geometry_source_geometry_mode,
			"bake_agent_radius": nm.agent_radius,
			"bake_agent_height": nm.agent_height,
			"bake_cell_size": nm.cell_size})


## Walkable samples that fall inside this cover's swept volume.
##
## Horizontally the box is grown by the agent radius, because a body does not
## have to share a coordinate with the geometry to collide with it -- it has to
## come within its own radius. Vertically the test is between step height and
## head height above the walkable surface: a curb you step over is not an
## obstruction, and a gutter three metres up is not either.
func _samples_inside(box: AABB, samples: Array, radius: float,
		step_clear: float, body_height: float) -> int:
	var lo := box.position
	var hi := box.position + box.size
	var hits := 0
	for p in samples:
		var q: Vector3 = p
		if q.x < lo.x - radius or q.x > hi.x + radius:
			continue
		if q.z < lo.z - radius or q.z > hi.z + radius:
			continue
		# Godot is Y-up: q.y is the floor the body stands on.
		if hi.y < q.y + step_clear or lo.y > q.y + body_height:
			continue
		hits += 1
	return hits


## The stem shared by every instance of one cover kind. Blender dedupes with
## `.001` and Godot's importer turns the dot into an underscore, so neither
## survives into the name.
func _family(name: String) -> String:
	var s := name.split(".")[0]
	while s.length() > 0 and (s[s.length() - 1] in "0123456789_-"):
		s = s.substr(0, s.length() - 1)
	return s if s.length() > 0 else "(unnamed)"

## Bake any NavigationRegion3D that arrived empty, and say how many.
##
## Lot's walk scene ships the region with an EMPTY NavigationMesh -- measured:
## one region, zero polygons, zero walkable samples. Nothing to test dressing
## against, and a probe that shrugged at that would report a clean level.
## The source geometry is already in the scene, so the honest move is to bake
## it here and SAY SO, rather than either failing or quietly measuring nothing.
## A bake done here is this tool's own answer to "where can a body go", not
## Lot's, and the report says which one you are reading.
func _bake_empty_regions(scene: Node) -> int:
	var baked := 0
	for n in scene.find_children("*", "NavigationRegion3D", true, false):
		var region := n as NavigationRegion3D
		var nm: NavigationMesh = region.navigation_mesh
		if nm == null or nm.get_polygon_count() > 0:
			continue
		# PARSE COLLIDERS ONLY, or the measurement answers itself. The default
		# parses mesh instances too, which carves the walkable surface around
		# every visual mesh INCLUDING the dressing -- measured: parsed BOTH,
		# 5868 covers, 0 in the way, a zero that could not have come out any
		# other way. Covers carry no collision by contract and the DC greybox
		# does, so a collider-only bake sees the building and ignores the
		# dressing, which is the question being asked.
		nm.geometry_parsed_geometry_type = \
			NavigationMesh.PARSED_GEOMETRY_STATIC_COLLIDERS
		region.bake_navigation_mesh(false)
		baked += 1
	if baked > 0:
		for _i in range(10):
			await get_tree().process_frame
	return baked
