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
	var lights: Array = []
	for n in scene.find_children("*", "OmniLight3D", true, false):
		var l: OmniLight3D = n
		if l.is_visible_in_tree():
			lights.append({"pos": l.global_transform.origin,
							"range": l.omni_range, "kind": "omni"})
	for n in scene.find_children("*", "SpotLight3D", true, false):
		var l: SpotLight3D = n
		if l.is_visible_in_tree():
			lights.append({"pos": l.global_transform.origin,
							"range": l.spot_range, "kind": "spot"})
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
			over.append({
				"path": String(scene.get_path_to(mi)),
				"lights": count,
				"size": [snappedf(aabb.size.x, 0.01),
							snappedf(aabb.size.y, 0.01),
							snappedf(aabb.size.z, 0.01)],
			})

	over.sort_custom(func(a, b): return a["lights"] > b["lights"])
	var truncated := over.size() > WORST_ROWS
	_emit({
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


## Closest-point test: does the sphere at `pos` with `radius` touch `aabb`?
## This is the same containment question the engine's light culling answers
## when it assigns lights to an instance.
func _sphere_touches_aabb(pos: Vector3, radius: float, aabb: AABB) -> bool:
	var lo: Vector3 = aabb.position
	var hi: Vector3 = aabb.position + aabb.size
	var d := 0.0
	for i in range(3):
		var v: float = pos[i]
		if v < lo[i]:
			d += (lo[i] - v) * (lo[i] - v)
		elif v > hi[i]:
			d += (v - hi[i]) * (v - hi[i])
	return d <= radius * radius


func _emit(report: Dictionary) -> void:
	print(MARK_BEGIN)
	print(JSON.stringify(report, "  "))
	print(MARK_END)
	get_tree().quit()
