extends Node
## Renders a generated level from cameras derived from its own mission spine and
## reports the exposure of each frame.
##
## Loaded as an autoload by tools/look_shots.py into a MIRROR of the project
## under test. It prints one fenced JSON block and quits.
##
## It reports what it measured and stops. "Washed out" and "correctly bright for
## noon" are the same histogram, and this file cannot tell them apart.
##
## FRAME AND UNITS, because a number here without them has been wrong before:
## luminance is Rec.709 on the 8-bit sRGB values the swap chain received, after
## tonemapping and after Lux's post stack, 0-255. It is NOT scene-referred light.
## The rendering driver and adapter are reported alongside every run, because the
## same scene grades differently under Compatibility and Forward+ and comparing
## across them is comparing two instruments.

const MARK_BEGIN := "<<<LOOK_SHOTS_JSON"
const MARK_END := "LOOK_SHOTS_JSON>>>"

## The dispatch handoff's anchor list, shipped at the root of every portable
## export. It carries the mission spine as data when the entry scene carries it
## as nothing.
const ANCHORS_PATH := "res://gameplay_anchors.json"

## anchor_type -> the spine key the scene exports would have used, so both
## sources produce identically-shaped shots and a reader can compare runs.
const ANCHOR_KEYS := {
	"player_start": "spawn_pos",
	"objective": "objective_pos",
	"extraction": "extraction_pos",
}

## Rec.709 luma weights, the coefficients the sRGB primaries are defined with.
const LUMA_R := 0.2126
const LUMA_G := 0.7152
const LUMA_B := 0.0722

var _out_dir: String = ""
var _shots: Array = []
var _hidden_layers: Array = []
var _centre_frac: float = 0.0
var _notes: Array = []


func _ready() -> void:
	_out_dir = String(ProjectSettings.get_setting("look_shots/out_dir", ""))
	var settle: int = int(ProjectSettings.get_setting(
		"look_shots/settle_frames", 10))
	var per_shot: int = int(ProjectSettings.get_setting(
		"look_shots/frames_per_shot", 6))
	var hide_hud: bool = bool(ProjectSettings.get_setting(
		"look_shots/hide_non_lux_canvas", true))
	# Linear fraction of the frame that counts as "what the shot is aimed at".
	# 1/3 by width and height, so a ninth of the pixels. This number is a
	# CHOICE, not a derivation -- nothing in the scene says how wide attention
	# is -- so every shot reports the fraction and the pixel rect it produced,
	# and the whole-frame figures stay beside it. A reader who disagrees with
	# the third can set look_shots/centre_fraction and get a labelled answer.
	_centre_frac = clampf(float(ProjectSettings.get_setting(
		"look_shots/centre_fraction", 1.0 / 3.0)), 0.05, 1.0)

	for _i in range(settle):
		await get_tree().process_frame

	var scene: Node = get_tree().current_scene
	if scene == null:
		_emit({"error": "current_scene is null"})
		return
	if _out_dir == "":
		_emit({"error": "look_shots/out_dir was not set by the driver"})
		return

	if hide_hud:
		_hide_non_lux_canvas(scene)

	var cams: Array = _derive_cameras(scene)
	if cams.is_empty():
		_emit({"error": "no cameras could be derived from this scene"})
		return

	var cam := Camera3D.new()
	cam.far = 2000.0
	scene.add_child(cam)
	cam.make_current()

	for spec in cams:
		var d: Dictionary = spec
		cam.global_position = d["eye"]
		var target: Vector3 = d["target"]
		if not target.is_equal_approx(cam.global_position):
			cam.look_at(target, Vector3.UP)
		for _i in range(per_shot):
			await RenderingServer.frame_post_draw
		_shots.append(_capture(String(d["name"]), d))

	# Both, deliberately. rendering_method is what the PROJECT asks for and is
	# what a reader assumes they got; the API version is what the process
	# actually bound, and a --rendering-driver on the command line moves the
	# second without touching the first. Reporting only the setting is how a
	# run under OpenGL gets filed as a Forward+ measurement.
	_emit({
		"engine": String(Engine.get_version_info().get("string", "")),
		"rendering_method": String(
			ProjectSettings.get_setting("rendering/renderer/rendering_method", "")),
		"adapter_api": RenderingServer.get_video_adapter_api_version(),
		"adapter": RenderingServer.get_video_adapter_name(),
		"adapter_vendor": RenderingServer.get_video_adapter_vendor(),
		"viewport": [get_viewport().size.x, get_viewport().size.y],
		"hidden_canvas_layers": _hidden_layers,
		"notes": _notes,
		"shots": _shots,
	})


func _emit(report: Dictionary) -> void:
	print(MARK_BEGIN)
	print(JSON.stringify(report, "  "))
	print(MARK_END)
	get_tree().quit()


## Hides CanvasLayers that are not part of a Lux post stack.
##
## The walk harness draws its own briefing HUD over the frame, and those pixels
## are pure white text: on a 1600x900 capture they were 1.4% of the frame and
## every one of them clipped, which is a measurable bias in exactly the statistic
## this tool exists to report. Lux's post stack is ALSO a CanvasLayer and must
## stay -- it is the grade. The distinction is ancestry, not name.
func _hide_non_lux_canvas(scene: Node) -> void:
	for n in scene.find_children("*", "CanvasLayer", true, false):
		var layer: CanvasLayer = n
		if _under_lux_root(layer):
			continue
		if not layer.visible:
			continue
		layer.visible = false
		_hidden_layers.append(String(scene.get_path_to(layer)))


func _under_lux_root(node: Node) -> bool:
	var p: Node = node
	while p != null:
		if p.is_in_group(&"lux_root"):
			return true
		p = p.get_parent()
	return false


## Cameras derived from the scene rather than chosen.
##
## Lot's walk scene root exports the mission spine -- spawn_pos, objective_pos,
## extraction_pos -- so the eye-level shots are the three places the level is
## actually about, looking the way the crew will be looking. Eye height comes
## from the Player's own Camera3D when there is one, so it tracks the body the
## contract describes instead of a number typed here. The overview is framed
## from the site's visual AABB and the camera's own FOV, so a bigger site backs
## the camera off by exactly as much as it needs.
func _derive_cameras(scene: Node) -> Array:
	var out := []
	var aabb := _visual_aabb(scene)
	if aabb.size.length() > 0.0:
		var centre: Vector3 = aabb.get_center()
		# Distance that fits the largest extent in the vertical FOV, with a
		# quarter-extent of air around it.
		var extent: float = maxf(aabb.size.x, maxf(aabb.size.y, aabb.size.z))
		var fov_rad: float = deg_to_rad(75.0)
		var dist: float = (extent * 0.5) / tan(fov_rad * 0.5) * 1.25
		var dir := Vector3(-1.0, 0.9, -1.0).normalized()
		out.append({
			"name": "overview",
			"eye": centre + dir * dist,
			"target": centre,
			"derivation": "site visual AABB, framed to 75 deg vertical FOV",
		})

	var eye_h: float = _eye_height(scene)
	var spine := []
	for key in ["spawn_pos", "objective_pos", "extraction_pos"]:
		var v: Variant = scene.get(StringName(key))
		if v is Vector3:
			spine.append({"key": key, "pos": v})

	# A Level Factory presentation scene carries no mission spine: the exports
	# above live on Lot's walk-scene root, and the portable shell's entry is a
	# bare Node3D. The spine is still IN the package, as data -- the dispatch
	# handoff writes gameplay_anchors.json to the export root with a
	# player_start, an objective and an extraction point. Read those.
	var spine_source := "scene exports"
	if spine.is_empty():
		spine = _anchor_spine()
		if not spine.is_empty():
			spine_source = ANCHORS_PATH

	# THREE REFUTED FALLBACKS, kept above the thing that replaced them, because
	# each produced a clean-looking histogram of somewhere no player stands and
	# the third was only caught by printing the y.
	#
	#   aabb.position.y + eye_h     -- lowest visible geometry in the whole
	#                                  site: a sunk ground plate. In a basement.
	#   first hit casting down      -- highest surface in the column: the ROOF.
	#                                  Reported eye y=9.60 on a site whose
	#                                  ground is y=0, and read as daylight.
	#   lowest hit in the column    -- the UNDERSIDE of the ground plate.
	#                                  Reported eye y=-2.40 against a floor at
	#                                  y=-4.00, and read as a dark interior.
	#
	# The pattern is the finding: the geometry does not say where a player
	# stands, and every attempt to infer it invented a plausible number. So no
	# fourth guess. With no spine and no anchors this returns the overview alone
	# and says why, because one honest shot beats four confident wrong ones.
	if spine.is_empty():
		_notes.append(
			("no mission spine on the scene and no usable anchors in %s; "
			+ "eye-level shots omitted rather than guessed") % ANCHORS_PATH)
		return out
	for i in range(spine.size()):
		var here: Dictionary = spine[i]
		var next: Dictionary = spine[(i + 1) % spine.size()] if spine.size() > 1 else here
		var eye: Vector3 = (here["pos"] as Vector3) + Vector3(0.0, eye_h, 0.0)
		var target: Vector3 = (next["pos"] as Vector3) + Vector3(0.0, eye_h, 0.0)
		var label: String = String(here["key"]).replace("_pos", "")
		out.append({
			"name": label,
			"eye": eye,
			"target": target,
			"derivation": "%s: %s at eye height %.2f m, facing the next leg" % [
				spine_source, String(here["key"]), eye_h],
		})
	return out


## The mission spine out of the dispatch handoff's anchor list.
##
## Positions only -- the anchors carry `pos` and `rot_y_deg`, and the shots aim
## at the next leg rather than at a stored heading, so the two sources frame the
## same way. First anchor of each type wins: a mission has one start and one
## extraction, and where it has several objectives the first is the one the
## beat graph opens on.
##
## Returns [] on anything unreadable -- absent file, bad JSON, no `anchors`, no
## recognised type. Callers treat that as "no spine", never as "spine at the
## origin", because a silent Vector3.ZERO is a camera in the ground.
func _anchor_spine() -> Array:
	if not FileAccess.file_exists(ANCHORS_PATH):
		return []
	var parsed: Variant = JSON.parse_string(
		FileAccess.get_file_as_string(ANCHORS_PATH))
	if typeof(parsed) != TYPE_DICTIONARY:
		_notes.append("%s did not parse as JSON" % ANCHORS_PATH)
		return []
	var doc: Dictionary = parsed
	if typeof(doc.get("anchors")) != TYPE_ARRAY:
		_notes.append("%s has no 'anchors' array" % ANCHORS_PATH)
		return []
	var found := {}
	for entry in doc["anchors"]:
		if typeof(entry) != TYPE_DICTIONARY:
			continue
		var a: Dictionary = entry
		var key: String = String(ANCHOR_KEYS.get(String(a.get("anchor_type", "")), ""))
		if key == "" or found.has(key):
			continue
		if typeof(a.get("transform")) != TYPE_DICTIONARY:
			continue
		var xform: Dictionary = a.get("transform")
		if typeof(xform.get("pos")) != TYPE_ARRAY:
			continue
		var pos: Array = xform.get("pos")
		if pos.size() < 3:
			continue
		found[key] = {"key": key, "pos": Vector3(
			float(pos[0]), float(pos[1]), float(pos[2]))}
	var spine := []
	# Fixed order, not dictionary order, so shot names and the leg each camera
	# faces are the same on every run and two runs can be diffed line by line.
	for key in ["spawn_pos", "objective_pos", "extraction_pos"]:
		if found.has(key):
			spine.append(found[key])
	return spine


## The union of every VisualInstance3D's AABB in world space.
func _visual_aabb(scene: Node) -> AABB:
	var out := AABB()
	var first := true
	for n in scene.find_children("*", "VisualInstance3D", true, false):
		var vi: VisualInstance3D = n
		if not vi.is_visible_in_tree():
			continue
		var world: AABB = vi.global_transform * vi.get_aabb()
		if first:
			out = world
			first = false
		else:
			out = out.merge(world)
	return out


## Eye height from the Player's Camera3D when the scene has one, else the
## agent-contract standing eye of 1.6 m. Reported either way, so a reader knows
## which they got.
func _eye_height(scene: Node) -> float:
	for n in scene.find_children("*", "Camera3D", true, false):
		var cam: Camera3D = n
		var parent := cam.get_parent()
		if parent != null and parent is CharacterBody3D:
			return cam.position.y
	return 1.6


func _capture(shot_name: String, spec: Dictionary) -> Dictionary:
	var img: Image = get_viewport().get_texture().get_image()
	img.convert(Image.FORMAT_RGB8)
	var path: String = _out_dir.path_join(shot_name + ".png")
	var err: int = img.save_png(path)
	var stats: Dictionary = _exposure(img)
	# The same statistics over the middle of the frame. A whole-frame mean
	# cannot separate a readable level from one whose interior sits in a hole:
	# the themed-site export read 72 outside and 20 inside, and the site average
	# showed neither. Reported ALONGSIDE the frame figures, never instead of
	# them -- two regions disagreeing is the finding.
	var w: int = img.get_width()
	var h: int = img.get_height()
	var cw: int = maxi(1, int(float(w) * _centre_frac))
	var ch: int = maxi(1, int(float(h) * _centre_frac))
	var rect := Rect2i((w - cw) / 2, (h - ch) / 2, cw, ch)
	stats["centre"] = _exposure(img.get_region(rect))
	stats["centre_fraction"] = _centre_frac
	stats["centre_rect"] = [rect.position.x, rect.position.y,
		rect.size.x, rect.size.y]
	stats["name"] = shot_name
	stats["png"] = path
	stats["png_error"] = err
	stats["eye"] = [spec["eye"].x, spec["eye"].y, spec["eye"].z]
	stats["target"] = [spec["target"].x, spec["target"].y, spec["target"].z]
	stats["derivation"] = spec["derivation"]
	return stats


## Rec.709 luminance histogram of one frame, reduced to the figures that
## distinguish a graded image from a blown one.
##
## Percentiles come out of a 256-bin histogram rather than a sort: the sort is
## 1.4 million elements per shot in GDScript, and the histogram answers the same
## question exactly, because the values are already 8-bit integers.
func _exposure(img: Image) -> Dictionary:
	var data: PackedByteArray = img.get_data()
	var hist := PackedInt32Array()
	hist.resize(256)
	var i: int = 0
	var n: int = data.size()
	while i + 2 < n:
		var lum: int = int(
			LUMA_R * float(data[i])
			+ LUMA_G * float(data[i + 1])
			+ LUMA_B * float(data[i + 2]))
		hist[lum] += 1
		i += 3
	var total: int = n / 3
	if total <= 0:
		return {"pixels": 0}
	var sum: float = 0.0
	for v in range(256):
		sum += float(v) * float(hist[v])
	return {
		"pixels": total,
		"mean": sum / float(total),
		"p05": _percentile(hist, total, 0.05),
		"p50": _percentile(hist, total, 0.50),
		"p95": _percentile(hist, total, 0.95),
		"clipped_pct": 100.0 * float(hist[255]) / float(total),
		"near_clipped_pct": 100.0 * float(
			hist[252] + hist[253] + hist[254] + hist[255]) / float(total),
		"crushed_pct": 100.0 * float(hist[0]) / float(total),
	}


func _percentile(hist: PackedInt32Array, total: int, q: float) -> int:
	var want: int = int(float(total) * q)
	var seen: int = 0
	for v in range(256):
		seen += hist[v]
		if seen >= want:
			return v
	return 255
