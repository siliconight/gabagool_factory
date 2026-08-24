extends Node
## Per-MESH light census: how many positional lights actually reach each mesh
## in a running scene.
##
## Loaded as an autoload by tools/mesh_light_census.py into a MIRROR of the
## project under test, never into the project itself. It prints one fenced
## JSON block and quits.
##
## WHY PER MESH. GL Compatibility budgets positional lights per mesh
## (`rendering/limits/opengl/max_lights_per_object`, engine default 8). A mesh
## over the budget silently drops lights, which reads as a hard brightness
## step where two slabs meet. The only numbers this repo had for that were
## filename-based estimates; this walks the tree the level actually runs and
## counts, per visible MeshInstance3D, the visible OmniLight3D / SpotLight3D
## whose range reaches its world AABB -- the engine's own question, asked
## directly. Spot cones are ignored on purpose: range is a sphere here, so the
## count is an upper bound on what the engine will bind. A mesh that passes
## this cannot fail in the renderer.
##
## It reports what it found and stops. Whether 9 lights on one mesh is a
## defect belongs in the reply, where it can be argued with.

const MARK_BEGIN := "<<<MESH_LIGHT_CENSUS_JSON"
const MARK_END := "MESH_LIGHT_CENSUS_JSON>>>"

## Meshes with more lights than this are listed individually in the payload.
## The report's HISTOGRAM is complete either way; this only bounds the detail
## rows so a 5000-mesh site does not print 5000 lines.
const WORST_ROWS := 40


func _ready() -> void:
	var frames: int = int(ProjectSettings.get_setting(
		"mesh_light_census/settle_frames", 5))
	for _i in range(frames):
		await get_tree().process_frame

	var scene: Node = get_tree().current_scene
	if scene == null:
		_emit({"error": "current_scene is null"})
		return

	# The positional lights that can claim a slot in a mesh's budget.
	# `warm` (red channel over blue) rides along because it is the cheapest
	# honest TYPE tag this tree offers: the pendant is deliberately the
	# fluorescent rig in an incandescent costume, so paths and lamp names
	# ("Fluoro_N") cannot tell them apart -- census #7's b1 verdict hinged
	# on exactly that ambiguity. Color temperature can: every warm source
	# here is a pendant / sodium / halogen, every cool one a tube or window.
	var lights: Array = []
	for n in scene.find_children("*", "OmniLight3D", true, false):
		var l: OmniLight3D = n
		if l.is_visible_in_tree():
			lights.append({"pos": l.global_transform.origin,
							"range": l.omni_range, "kind": "omni",
							"warm": l.light_color.r > l.light_color.b,
							"path": String(scene.get_path_to(l))})
	for n in scene.find_children("*", "SpotLight3D", true, false):
		var l: SpotLight3D = n
		if l.is_visible_in_tree():
			lights.append({"pos": l.global_transform.origin,
							"range": l.spot_range, "kind": "spot",
							"warm": l.light_color.r > l.light_color.b,
							"path": String(scene.get_path_to(l))})
	var directional := 0
	for n in scene.find_children("*", "DirectionalLight3D", true, false):
		if (n as Light3D).is_visible_in_tree():
			directional += 1

	var meshes := 0
	var histogram := {}          # light count -> mesh count
	var over: Array = []         # every mesh over the engine default of 8
	var worst_count := 0
	var worst_path := ""
	for n in scene.find_children("*", "MeshInstance3D", true, false):
		var mi: MeshInstance3D = n
		if mi.mesh == null or not mi.is_visible_in_tree():
			continue
		meshes += 1
		var aabb: AABB = mi.global_transform * mi.get_aabb()
		var count := 0
		for l in lights:
			if _sphere_touches_aabb(l["pos"], l["range"], aabb):
				count += 1
		histogram[count] = int(histogram.get(count, 0)) + 1
		if count > worst_count:
			worst_count = count
			worst_path = String(scene.get_path_to(mi))
		if count > 8:
			# Second pass, offenders only: WHO binds, and by what MARGIN
			# (range minus distance-to-AABB). Census #6 forced this: 14
			# plates at 9-10 with the geometry exonerated left range trims
			# as the only knob, and a trim is a guess unless the census
			# says how much range each claimant would have to lose. Sorted
			# slimmest first, so the (count - 8)th margin IS the trim that
			# frees the mesh.
			var binders: Array = []
			for l in lights:
				var dist := _dist_to_aabb(l["pos"], aabb)
				if dist <= float(l["range"]):
					binders.append({
						"path": l["path"],
						"range": snappedf(float(l["range"]), 0.01),
						"margin": snappedf(float(l["range"]) - dist, 0.01),
						"warm": bool(l["warm"]),
					})
			binders.sort_custom(func(a, b): return a["margin"] < b["margin"])
			over.append({
				"path": String(scene.get_path_to(mi)),
				"lights": count,
				"size": [snappedf(aabb.size.x, 0.01),
							snappedf(aabb.size.y, 0.01),
							snappedf(aabb.size.z, 0.01)],
				"binders": binders,
			})

	over.sort_custom(func(a, b): return a["lights"] > b["lights"])
	var truncated := over.size() > WORST_ROWS
	_emit({
		"light_population": _light_population(lights),
		"scene": String(scene.name),
		"settle_frames": frames,
		"engine": String(Engine.get_version_info().get("string", "")),
		"positional_lights": lights.size(),
		"directional_visible": directional,
		"meshes": meshes,
		"histogram": histogram,
		"over_8": over.size(),
		"worst": worst_count,
		"worst_path": worst_path,
		"over_rows": over.slice(0, WORST_ROWS),
		"over_rows_truncated": truncated,
		"cap_per_object": int(ProjectSettings.get_setting(
			"rendering/limits/opengl/max_lights_per_object", 8)),
		"cap_renderable": int(ProjectSettings.get_setting(
			"rendering/limits/opengl/max_renderable_lights", 32)),
	})


## Forensics on the LIGHTS themselves, added after the first AFTER census:
## every offender was a budget-sized tile, so the residue is the light
## population, not the meshes. Three questions this answers without another
## rebuild: what RANGES the lights carry (range decides how many tiles each
## light claims a slot on), whether lights are DUPLICATED in place (272
## visible against an authored 136 is exactly x2 -- the sun-link bug's shape:
## the file says one, the running level has two), and WHERE they live in the
## tree (a baked copy and a runtime-spawned copy group under different
## parents, so the grouping names the mechanism).
func _light_population(lights: Array) -> Dictionary:
	var ranges: Array = []
	for l in lights:
		ranges.append(float(l["range"]))
	ranges.sort()
	var hist := {}
	for r in ranges:
		var bucket := str(int(floor(r)))
		hist[bucket] = int(hist.get(bucket, 0)) + 1

	# In-place duplicates: two lights within 10 cm of each other. O(n^2) is
	# fine at a few hundred lights; a real dedup would not be measured here.
	var twin := 0
	var pairs: Array = []
	for i in range(lights.size()):
		var has_twin := false
		for j in range(lights.size()):
			if i == j:
				continue
			var d: Vector3 = lights[i]["pos"] - lights[j]["pos"]
			if d.length() < 0.1:
				has_twin = true
				if i < j and pairs.size() < 12:
					pairs.append([lights[i]["path"], lights[j]["path"]])
		if has_twin:
			twin += 1

	# Group by the first two path segments, so baked-vs-spawned reads off.
	var groups := {}
	for l in lights:
		var parts: PackedStringArray = String(l["path"]).split("/")
		var key := parts[0] if parts.size() == 1 else parts[0] + "/" + parts[1]
		groups[key] = int(groups.get(key, 0)) + 1

	var mid := ranges.size() / 2
	return {
		"range_min": ranges[0] if ranges.size() > 0 else 0.0,
		"range_median": ranges[mid] if ranges.size() > 0 else 0.0,
		"range_max": ranges[ranges.size() - 1] if ranges.size() > 0 else 0.0,
		"range_histogram": hist,
		"lights_with_twin": twin,
		"twin_pairs": pairs,
		"groups": groups,
	}


## Closest-point test: does the sphere at `pos` with `radius` touch `aabb`?
## This is the same containment question the engine's light culling answers
## when it assigns lights to an instance.
func _sphere_touches_aabb(pos: Vector3, radius: float, aabb: AABB) -> bool:
	var d := _dist_to_aabb(pos, aabb)
	return d <= radius


## Distance from `pos` to the closest point of `aabb` (0.0 inside it).
func _dist_to_aabb(pos: Vector3, aabb: AABB) -> float:
	var lo: Vector3 = aabb.position
	var hi: Vector3 = aabb.position + aabb.size
	var d := 0.0
	for i in range(3):
		var v: float = pos[i]
		if v < lo[i]:
			d += (lo[i] - v) * (lo[i] - v)
		elif v > hi[i]:
			d += (v - hi[i]) * (v - hi[i])
	return sqrt(d)


func _emit(report: Dictionary) -> void:
	print(MARK_BEGIN)
	print(JSON.stringify(report, "  "))
	print(MARK_END)
	get_tree().quit()
