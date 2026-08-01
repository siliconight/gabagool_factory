extends Node
## Runtime census of every light and environment in a running scene.
##
## Loaded as an autoload by tools/light_census.py into a MIRROR of the project
## under test, never into the project itself. It prints one fenced JSON block
## and quits.
##
## It reports what it found and stops. It names no cause: two directional lights
## may be a defect or a deliberate fill, and this file is not in a position to
## know which. The argument belongs in the reply, where it can be argued with.

const MARK_BEGIN := "<<<LIGHT_CENSUS_JSON"
const MARK_END := "LIGHT_CENSUS_JSON>>>"


func _ready() -> void:
	# Settling matters: LuxRoot builds its modules in _ready and applies the
	# preset in the same frame, but a light created there is not measurable
	# until the tree has processed it. Frames rather than seconds, because a
	# headless run has no wall clock worth trusting.
	var frames: int = int(ProjectSettings.get_setting(
		"light_census/settle_frames", 5))
	for _i in range(frames):
		await get_tree().process_frame

	var scene: Node = get_tree().current_scene
	if scene == null:
		_emit({"error": "current_scene is null"})
		return

	var report := {
		"scene": String(scene.name),
		"settle_frames": frames,
		"engine": String(Engine.get_version_info().get("string", "")),
		"directional": _directional(scene),
		"positional": _positional(scene),
		"environments": _environments(scene),
		"lux_roots": _lux_roots(scene),
		"duplicate_names": _duplicate_names(scene),
	}
	_emit(report)


func _emit(report: Dictionary) -> void:
	print(MARK_BEGIN)
	print(JSON.stringify(report, "  "))
	print(MARK_END)
	get_tree().quit()


## Every DirectionalLight3D, with the numbers that decide whether two of them
## fight: where each one points, how hard it drives, and whether it casts.
func _directional(scene: Node) -> Array:
	var out := []
	for n in scene.find_children("*", "DirectionalLight3D", true, false):
		var l: DirectionalLight3D = n
		# A DirectionalLight3D emits along -Z; the direction TO the light is +Z
		# of its basis. Same convention lux_root._track_sun_light() uses, so the
		# two can be compared without a sign hunt.
		var to_light: Vector3 = l.global_transform.basis.z.normalized()
		out.append({
			"path": String(scene.get_path_to(l)),
			"energy": l.light_energy,
			"color": [l.light_color.r, l.light_color.g, l.light_color.b],
			"shadow_enabled": l.shadow_enabled,
			"visible_in_tree": l.is_visible_in_tree(),
			"to_light_dir": [to_light.x, to_light.y, to_light.z],
			"elevation_deg": rad_to_deg(asin(clampf(to_light.y, -1.0, 1.0))),
		})
	return out


## Omni and spot counts only. They are here because a level that reads as
## over-lit is sometimes over-lit by fixtures rather than by suns, and a census
## that answers only the question you thought to ask sends you round again.
func _positional(scene: Node) -> Dictionary:
	var omni: Array = scene.find_children("*", "OmniLight3D", true, false)
	var spot: Array = scene.find_children("*", "SpotLight3D", true, false)
	var omni_on := 0
	for n in omni:
		if (n as Light3D).is_visible_in_tree():
			omni_on += 1
	var spot_on := 0
	for n in spot:
		if (n as Light3D).is_visible_in_tree():
			spot_on += 1
	return {
		"omni_total": omni.size(), "omni_visible": omni_on,
		"spot_total": spot.size(), "spot_visible": spot_on,
	}


## Every WorldEnvironment and the grade fields that move exposure. Two of these
## in one scene is a silent fight -- the last one to enter the tree wins and
## nothing says so.
func _environments(scene: Node) -> Array:
	var out := []
	for n in scene.find_children("*", "WorldEnvironment", true, false):
		var we: WorldEnvironment = n
		var row := {
			"path": String(scene.get_path_to(we)),
			"has_environment": we.environment != null,
		}
		if we.environment != null:
			var e: Environment = we.environment
			row["tonemap_mode"] = int(e.tonemap_mode)
			row["tonemap_exposure"] = e.tonemap_exposure
			row["tonemap_white"] = e.tonemap_white
			row["ambient_light_energy"] = e.ambient_light_energy
			row["ambient_light_source"] = int(e.ambient_light_source)
			row["background_mode"] = int(e.background_mode)
			row["glow_enabled"] = e.glow_enabled
			row["fog_enabled"] = e.fog_enabled
		out.append(row)
	return out


## Anything in the "lux_root" group, with the state that decides whether Sun
## Link took: the resolved sun_light, and what Lux parented onto itself.
func _lux_roots(scene: Node) -> Array:
	var out := []
	for n in get_tree().get_nodes_in_group(&"lux_root"):
		var kids := []
		var child_dir := 0
		var child_canvas := 0
		for c in (n as Node).get_children():
			kids.append({"name": String(c.name), "class": c.get_class()})
			if c is DirectionalLight3D:
				child_dir += 1
			if c is CanvasLayer:
				child_canvas += 1
		var sun_path := ""
		var sun: Variant = (n as Node).get(&"sun_light")
		if sun is DirectionalLight3D and is_instance_valid(sun):
			sun_path = String(scene.get_path_to(sun))
		out.append({
			"path": String(scene.get_path_to(n)),
			"sun_light": sun_path,
			"sun_link_resolved": sun_path != "",
			"child_directional_lights": child_dir,
			"child_canvas_layers": child_canvas,
			"children": kids,
		})
	return out


## Sibling nodes sharing a name. Godot renames on collision, so a scene that
## accumulated a second copy of a module shows up here as @Name@nnnnn beside
## Name -- which is what editor scaffolding looked like when it was baked into a
## saved scene.
func _duplicate_names(scene: Node) -> Array:
	var out := []
	var stack: Array[Node] = [scene]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		var seen := {}
		for c in n.get_children():
			# Godot's collision suffix: @Type@12345 beside Type.
			var base := String(c.name)
			if base.begins_with("@"):
				var parts := base.split("@", false)
				if parts.size() >= 1:
					base = parts[0]
			seen[base] = int(seen.get(base, 0)) + 1
			stack.append(c)
		for key in seen:
			if int(seen[key]) > 1:
				out.append({
					"parent": String(scene.get_path_to(n)),
					"base_name": String(key),
					"count": int(seen[key]),
				})
	return out
