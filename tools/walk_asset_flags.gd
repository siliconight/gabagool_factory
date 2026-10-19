extends Node
## ASSET FLAGS FOR THE WALK COPY: G marks what the crosshair rests on as LOOKING GOOD, P as NEEDING LOVE.
##
## The walker, 2026-10-14, after the demo: "I want a way to flag assets that look good and assets that need more
## polish/love" (factory roadmap 253). Today a look is judged in chat, frame by frame, and nothing keeps the
## verdicts. Each press here writes one: the verdict, the asset, the building, the level, where the camera stood
## and looked, and a small frame -- to `asset_flags.jsonl` and `asset_flags/` beside the walk copy -- and a banner
## says what was flagged. `tools/asset_flags.py` gathers every walk copy's flags into one ledger per asset.
##
## WHAT "THE ASSET" IS, and why it is not what the physics ray hits. In these levels collision is Deli Counter's
## greybox and the thing a body SEES is a separate Zoo module instanced over it: the F3 overlay's ray names
## `slab_col_1`, never the floor tile on top of it. So the pick here is by RENDER first -- the camera's ray against
## the triangles of the visible meshes, nearest first, among those whose bounds it enters -- and the asset is the
## nearest instanced ancestor's file: `res://lot/deli_a01/art/zoo/wall_delco_1997_02_w200_mdrywall.glb` names the
## module `wall_delco_1997_02_w200_mdrywall` in the building `deli_a01`. The physics hit is recorded beside it,
## and is the pick when no mesh is hit (the record says which, as `how`). A fire escape has no collider and still
## picks; a MultiMesh (Lot's dressing) is not a MeshInstance3D and does not -- the physics hit then stands in.
##
## WHAT A FLAG LEAVES ON SCREEN. The walker, 2026-10-19, after the first walk with these keys: "we should put a red
## line around an item that is flagged", "green for looks good, red for needs more work", "and it persists for that
## session". So each asset flagged is boxed in its verdict's colour until the walk quits, and a second flag of one
## asset repaints its box rather than adding one; flags from an earlier walk are in the file, not on screen. The box
## goes round the nearest instanced ancestor when that is a MODEL -- the GLB a Zoo module or a prop was instanced
## from, as the car `cover/prop_simple_car_...glb` -- and otherwise round the node picked, which the banner names by
## its path under the scene it sits in. Otherwise means a scene: a building's own `lot/<arch>/site.tscn`, or the
## level's, `presentation/lux.applied.tscn`, which holds the whole site, so a sidewalk Lot draws into it has no file
## of its own. REFUTED, kept: the rule was first "unless the ancestor is a scene at the package's root", and on cold
## run 9334's walk copy a press on the sidewalk beside the car boxed the whole level, 760 m across, the banner
## calling it `lux.applied` -- the site is not at the root. A box and not a silhouette: a wall or floor module sits
## flush in a run of its neighbours, where a hull drawn just outside it is buried on every side. A box held off the
## bounds shows wherever its edges clear the level, and they are drawn pulled OUTLINE_PULL_M toward the eye, so an
## edge that lands just inside the slab a wall module meets still draws. The picks never take a box for an asset.
## Two draw calls a box, in a debug walk only.
##
## A mesh is picked only within RAY_LENGTH, as the physics ray is. The pick's own comment said so and its test did
## not hold it: on that walk copy a press turned toward the street's buildings picked Lux's horizon glow, 405 m off,
## a mesh whose bounds hold every camera in the level.
##
## The banner saying what was flagged hangs from the foot of the screen. At the top-left it drew under the F3
## overlay's panel, and a frame of that first walk shows it cut off between the overlay's two panels.
##
## Walk copies only, DEBUG BUILDS ONLY: a release export frees this on its first frame. The package ships no
## player and no flags; `tools/walk_export.py` copies this in as `_walk_asset_flags.gd`. Proven headless by
## `tools/walk_asset_flags_selftest.gd`.

const RAY_LENGTH := 60.0
## Of the meshes whose bounds the ray enters, the nearest this many are tested triangle by triangle -- a key
## press, not a frame, so the cost is a pause the walker does not see.
const MAX_CANDIDATES := 24
const FLAGS_FILE := "res://asset_flags.jsonl"
const FRAMES_DIR := "res://asset_flags"
## A frame is stored this wide; enough to see what was meant, small enough to keep beside the ledger.
const FRAME_WIDTH := 640
const BANNER_SECS := 3.0
const VERDICT_BY_KEY := {KEY_G: "good", KEY_P: "needs_love"}
## The banner's foot above the bottom of the screen; the F3 overlay's two panels hold the top corners.
const BANNER_FROM_BOTTOM_PX := 40.0
## Each verdict's box, in the walker's colours: green for looks good, red for needs more work.
const OUTLINE_COLOR := {"good": Color(0.2, 0.95, 0.3), "needs_love": Color(1.0, 0.12, 0.1)}
## How far the box stands off the asset's bounds, so an edge clears the face of a flush neighbour.
const OUTLINE_PAD_M := 0.03
## How thick an edge is drawn: about 5 px at 2 m on the walk's 648-high window with its 75-degree view, the distance
## the first flags were given from, and 1 px at 10 m. A line one pixel wide runs down each edge as well, so a box
## farther off still reads.
const OUTLINE_EDGE_M := 0.025
## How far toward the eye the box is drawn: an edge less than this inside a surface still shows.
const OUTLINE_PULL_M := 0.10
## The files a model is instanced from, by extension: an ancestor from one of these is the asset a box goes round.
const MODEL_FILES := ["glb", "gltf", "blend", "fbx", "dae", "obj"]
## Unshaded and unfogged, so a box reads the same at the far end of a rainy night as under a lamp; two-sided, so a
## beam's winding does not matter; pulled toward the eye in view space, never more than half the way to it.
const OUTLINE_SHADER := """shader_type spatial;
render_mode unshaded, cull_disabled, shadows_disabled, fog_disabled;

uniform vec4 color : source_color = vec4(1.0, 0.0, 0.0, 1.0);
uniform float pull_m = 0.1;

void vertex() {
	vec4 v = MODELVIEW_MATRIX * vec4(VERTEX, 1.0);
	float d = length(v.xyz);
	if (d > 0.001) {
		v.xyz *= (d - min(pull_m, 0.5 * d)) / d;
	}
	POSITION = PROJECTION_MATRIX * v;
}

void fragment() {
	ALBEDO = color.rgb;
}
"""

var _banner: CanvasLayer = null
var _label: Label = null
var _banner_left: float = 0.0
var _count: int = 0
## The boxes drawn this session, under one node the picks skip, each by its asset's instance id.
var _outlines: Node3D = null
var _outlined: Dictionary = {}
var _materials: Dictionary = {}
var _shader: Shader = null


func _ready() -> void:
	if not OS.is_debug_build():
		queue_free()
		return
	_banner = CanvasLayer.new()
	_banner.name = &"AssetFlagBanner"
	_banner.layer = 121
	_banner.visible = false
	add_child(_banner)
	_label = Label.new()
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_label.add_theme_font_size_override("font_size", 22)
	_label.add_theme_color_override("font_outline_color", Color(0.0, 0.0, 0.0))
	_label.add_theme_constant_override("outline_size", 8)
	_banner.add_child(_label)
	_label.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	_label.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_label.offset_top = -BANNER_FROM_BOTTOM_PX - 32.0
	_label.offset_bottom = -BANNER_FROM_BOTTOM_PX
	_outlines = Node3D.new()
	_outlines.name = &"AssetFlagOutlines"
	add_child(_outlines)


func _unhandled_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k == null or not k.pressed or k.echo:
		return
	if VERDICT_BY_KEY.has(k.keycode):
		flag(String(VERDICT_BY_KEY[k.keycode]))


func _process(delta: float) -> void:
	if _banner_left > 0.0:
		_banner_left -= delta
		if _banner_left <= 0.0 and _banner != null:
			_banner.visible = false


## Flag what the camera looks at with `verdict` ("good" or "needs_love") and return the record written, or an
## empty Dictionary when there is no camera to look with.
func flag(verdict: String) -> Dictionary:
	var cam: Camera3D = get_viewport().get_camera_3d()
	if cam == null:
		return {}
	var from: Vector3 = cam.global_transform.origin
	var dir: Vector3 = -cam.global_transform.basis.z.normalized()
	var phys: Dictionary = _physics_hit(from, dir)
	var seen: Dictionary = _render_hit(from, dir)
	var node: Node = null
	var point: Vector3 = from
	var how: String = "none"
	if not seen.is_empty():
		node = seen["node"] as Node
		point = seen["point"]
		how = "render"
	elif not phys.is_empty():
		node = phys.get("collider") as Node
		point = phys.get("position", from)
		how = "physics"
	_count += 1
	var rec: Dictionary = {
		"schema": "walk_asset_flag/1",
		"verdict": verdict,
		"time_utc": Time.get_datetime_string_from_system(true),
		"level": _level_name(),
		"how": how,
		"camera": [from.x, from.y, from.z],
		"looking": [dir.x, dir.y, dir.z],
		"point": [point.x, point.y, point.z],
		"distance_m": from.distance_to(point),
		"node": "" if node == null else str(node.get_path()),
		"asset_file": _asset_file(node),
		"asset": _asset_file(node).get_file().get_basename(),
		"building": _building_of(node),
		"material": _material_of(node),
		"collider": "" if phys.is_empty() or phys.get("collider") == null else str((phys.get("collider") as Node).get_path()),
		"frame": _save_frame(verdict),
	}
	_append(rec)
	outline(node, verdict)
	_show("FLAGGED %s: %s%s" % [
		"LOOKS GOOD" if verdict == "good" else "NEEDS LOVE",
		_shown_name(node, rec),
		(" in " + String(rec["building"])) if String(rec["building"]) != "" else ""],
		OUTLINE_COLOR.get(verdict, Color.WHITE))
	return rec


func _physics_hit(from: Vector3, dir: Vector3) -> Dictionary:
	var space := get_viewport().get_world_3d().direct_space_state
	var q := PhysicsRayQueryParameters3D.create(from, from + dir * RAY_LENGTH)
	q.collide_with_areas = false
	return space.intersect_ray(q)


## The nearest visible triangle the ray meets: {node, point}, or {} when none within RAY_LENGTH.
func _render_hit(from: Vector3, dir: Vector3) -> Dictionary:
	var cands: Array = []
	_collect(get_tree().root, from, dir, cands)
	cands.sort_custom(func(a: Array, b: Array) -> bool: return float(a[0]) < float(b[0]))
	var best_t: float = INF
	var best: MeshInstance3D = null
	for i in range(mini(cands.size(), MAX_CANDIDATES)):
		var mi: MeshInstance3D = cands[i][1] as MeshInstance3D
		if float(cands[i][0]) > best_t:
			break
		var t: float = _triangle_t(mi, from, dir)
		if t < best_t and t <= RAY_LENGTH:
			best_t = t
			best = mi
	if best == null:
		return {}
	return {"node": best, "point": from + dir * best_t}


## Every visible MeshInstance3D whose world bounds the ray enters within RAY_LENGTH, as [entry distance, node]; the
## boxes drawn round flagged assets are not among them.
func _collect(n: Node, from: Vector3, dir: Vector3, out: Array) -> void:
	if n == _outlines:
		return
	var mi := n as MeshInstance3D
	if mi != null and mi.mesh != null and mi.is_visible_in_tree():
		var box: AABB = mi.global_transform * mi.get_aabb()
		var t: float = _ray_box(from, dir, box)
		if t >= 0.0 and t <= RAY_LENGTH:
			out.append([t, mi])
	for c in n.get_children():
		_collect(c, from, dir, out)


## The distance at which the ray enters `box` (0 when it starts inside), or -1 when it misses.
func _ray_box(from: Vector3, dir: Vector3, box: AABB) -> float:
	var tmin: float = -INF
	var tmax: float = INF
	for k in range(3):
		var lo: float = box.position[k]
		var hi: float = box.position[k] + box.size[k]
		if absf(dir[k]) < 1e-9:
			if from[k] < lo or from[k] > hi:
				return -1.0
			continue
		var t1: float = (lo - from[k]) / dir[k]
		var t2: float = (hi - from[k]) / dir[k]
		tmin = maxf(tmin, minf(t1, t2))
		tmax = minf(tmax, maxf(t1, t2))
	if tmax < maxf(tmin, 0.0):
		return -1.0
	return maxf(tmin, 0.0)


## The distance along the ray to the mesh's nearest triangle, or INF.
func _triangle_t(mi: MeshInstance3D, from: Vector3, dir: Vector3) -> float:
	var faces: PackedVector3Array = mi.mesh.get_faces()
	var xf: Transform3D = mi.global_transform
	var best: float = INF
	var i: int = 0
	while i + 2 < faces.size():
		var hit: Variant = Geometry3D.ray_intersects_triangle(from, dir, xf * faces[i], xf * faces[i + 1], xf * faces[i + 2])
		if hit != null:
			var t: float = from.distance_to(hit as Vector3)
			if t < best:
				best = t
		i += 3
	return best


## The file the nearest instanced ancestor came from -- a module or species GLB, or a building's scene.
func _asset_file(node: Node) -> String:
	var n: Node = node
	while n != null:
		if n.scene_file_path != "":
			return n.scene_file_path
		n = n.get_parent()
	return ""


## `res://lot/deli_a01/...` -> `deli_a01`, from the nearest ancestor that names a lot folder.
func _building_of(node: Node) -> String:
	var n: Node = node
	while n != null:
		var p: String = n.scene_file_path
		if p.begins_with("res://lot/"):
			var parts: PackedStringArray = p.trim_prefix("res://lot/").split("/")
			if parts.size() >= 2:
				return parts[0]
		n = n.get_parent()
	return ""


func _material_of(node: Node) -> String:
	var mi := node as MeshInstance3D
	if mi == null or mi.mesh == null or mi.mesh.get_surface_count() == 0:
		return ""
	var m: Material = mi.get_active_material(0)
	return "" if m == null else m.resource_name


## The level's name: the walk scene's mission, else the project's.
func _level_name() -> String:
	var n: String = str(ProjectSettings.get_setting("application/config/name", ""))
	return n


## A small copy of the frame the verdict was given on, beside the flags file; "" when there is no image (headless).
func _save_frame(verdict: String) -> String:
	# A headless run draws nothing, and asking its viewport for an image is an
	# engine ERROR rather than a null (measured by the selftest), so it is not asked.
	if DisplayServer.get_name() == "headless":
		return ""
	var tex: ViewportTexture = get_viewport().get_texture()
	if tex == null:
		return ""
	var img: Image = tex.get_image()
	if img == null or img.is_empty():
		return ""
	if img.get_width() > FRAME_WIDTH:
		img.resize(FRAME_WIDTH, int(round(float(img.get_height()) * FRAME_WIDTH / img.get_width())))
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(FRAMES_DIR))
	var fname: String = "%s_%s_%03d.png" % [Time.get_datetime_string_from_system(true).replace(":", "").replace("-", ""), verdict, _count]
	var path: String = FRAMES_DIR.path_join(fname)
	if img.save_png(path) != OK:
		return ""
	return path


func _append(rec: Dictionary) -> void:
	var f: FileAccess = null
	if FileAccess.file_exists(FLAGS_FILE):
		f = FileAccess.open(FLAGS_FILE, FileAccess.READ_WRITE)
		if f != null:
			f.seek_end()
	else:
		f = FileAccess.open(FLAGS_FILE, FileAccess.WRITE)
	if f == null:
		push_error("[asset_flags] cannot write %s" % FLAGS_FILE)
		return
	f.store_line(JSON.stringify(rec))
	f.close()


func _show(text: String, color: Color) -> void:
	if _label == null:
		return
	_label.text = text
	_label.add_theme_color_override("font_color", color)
	_banner.visible = true
	_banner_left = BANNER_SECS


## Box the asset `node` belongs to in `verdict`'s colour for the rest of the session -- repainting its box if it was
## flagged before -- and return the box, or null when nothing there has bounds to draw one round.
func outline(node: Node, verdict: String) -> MeshInstance3D:
	if node == null or _outlines == null or not OUTLINE_COLOR.has(verdict):
		return null
	var target: Node = _outline_target(node)
	var found: Array = _bounds(target)
	if found.is_empty():
		return null
	var key: int = target.get_instance_id()
	if _outlined.has(key) and is_instance_valid(_outlined[key]):
		var old: Node = _outlined[key]
		_outlines.remove_child(old)
		old.queue_free()
	var bounds: AABB = found[0]
	var box := MeshInstance3D.new()
	box.name = "box_%d" % key
	box.mesh = _box_mesh(bounds.grow(OUTLINE_PAD_M))
	box.material_override = _material(verdict)
	box.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	box.gi_mode = GeometryInstance3D.GI_MODE_DISABLED
	box.set_meta(&"verdict", verdict)
	box.set_meta(&"target", target.get_path())
	_outlines.add_child(box)
	_outlined[key] = box
	return box


## What a flag's box goes round: the node's nearest instanced ancestor when that was instanced from a model file
## (MODEL_FILES), else the node itself -- a building's scene and the level's are not one thing to box.
func _outline_target(node: Node) -> Node:
	var root: Node = _instanced_ancestor(node)
	if root != null and MODEL_FILES.has(root.scene_file_path.get_extension().to_lower()):
		return root
	return node


## The node itself or its nearest ancestor that was instanced from a file, or null.
func _instanced_ancestor(node: Node) -> Node:
	var n: Node = node
	while n != null:
		if n.scene_file_path != "":
			return n
		n = n.get_parent()
	return null


## What the banner calls the thing flagged: the asset's name when the box goes round the asset, else the node boxed by
## its path under the scene it sits in -- `sidewalk_1L_1/mesh_t0_0`, not the level's `lux.applied`.
func _shown_name(node: Node, rec: Dictionary) -> String:
	if node == null:
		return "(nothing within %d m)" % int(RAY_LENGTH)
	var target: Node = _outline_target(node)
	var root: Node = _instanced_ancestor(node)
	if root == null or target == root:
		return String(rec["asset"]) if String(rec["asset"]) != "" else String(target.name)
	return String(root.get_path_to(target))


## The world bounds of what is drawn under `target` -- its meshes, as the eye sees them -- or of its collision shapes
## when nothing under it is drawn (a physics pick); [bounds], or [] when it has neither.
func _bounds(target: Node) -> Array:
	var boxes: Array[AABB] = []
	_visual_boxes(target, boxes)
	if boxes.is_empty():
		_shape_boxes(target, boxes)
	if boxes.is_empty():
		return []
	var out: AABB = boxes[0]
	for b in boxes:
		out = out.merge(b)
	return [out]


func _visual_boxes(n: Node, out: Array[AABB]) -> void:
	if n == _outlines:
		return
	var mi := n as MeshInstance3D
	if mi != null and mi.mesh != null and mi.is_visible_in_tree():
		out.append(mi.global_transform * mi.get_aabb())
	var mm := n as MultiMeshInstance3D
	if mm != null and mm.multimesh != null and mm.multimesh.instance_count > 0 and mm.is_visible_in_tree():
		out.append(mm.global_transform * mm.get_aabb())
	for c in n.get_children():
		_visual_boxes(c, out)


func _shape_boxes(n: Node, out: Array[AABB]) -> void:
	var cs := n as CollisionShape3D
	if cs != null and cs.shape != null and not cs.disabled:
		out.append(cs.global_transform * cs.shape.get_debug_mesh().get_aabb())
	for c in n.get_children():
		_shape_boxes(c, out)


## The box's twelve edges as beams OUTLINE_EDGE_M thick, and a one-pixel line down each, as one mesh of two surfaces.
func _box_mesh(box: AABB) -> ArrayMesh:
	var c: Array[Vector3] = _corners(box.position, box.end)
	var beams := PackedVector3Array()
	var lines := PackedVector3Array()
	var h := Vector3.ONE * (OUTLINE_EDGE_M * 0.5)
	for i in range(8):
		for k in range(3):
			if (i & (1 << k)) != 0:
				continue
			var a: Vector3 = c[i]
			var b: Vector3 = c[i | (1 << k)]
			lines.append(a)
			lines.append(b)
			beams.append_array(_beam(a - h, b + h))
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, _surface(beams))
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_LINES, _surface(lines))
	return mesh


## The eight corners of the box from `lo` to `hi`: corner i takes `hi` on axis k where bit k of i is set.
func _corners(lo: Vector3, hi: Vector3) -> Array[Vector3]:
	var out: Array[Vector3] = []
	for i in range(8):
		out.append(Vector3(hi.x if (i & 1) != 0 else lo.x, hi.y if (i & 2) != 0 else lo.y,
			hi.z if (i & 4) != 0 else lo.z))
	return out


## A solid box from `lo` to `hi`, as twelve triangles.
func _beam(lo: Vector3, hi: Vector3) -> PackedVector3Array:
	var c: Array[Vector3] = _corners(lo, hi)
	var out := PackedVector3Array()
	for f in [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]:
		var q: Array = f
		out.append_array(PackedVector3Array([c[q[0]], c[q[1]], c[q[2]], c[q[0]], c[q[2]], c[q[3]]]))
	return out


func _surface(verts: PackedVector3Array) -> Array:
	var arrays: Array = []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = verts
	return arrays


func _material(verdict: String) -> ShaderMaterial:
	if _materials.has(verdict):
		return _materials[verdict]
	if _shader == null:
		_shader = Shader.new()
		_shader.code = OUTLINE_SHADER
	var m := ShaderMaterial.new()
	m.shader = _shader
	m.set_shader_parameter(&"color", OUTLINE_COLOR[verdict])
	m.set_shader_parameter(&"pull_m", OUTLINE_PULL_M)
	_materials[verdict] = m
	return m
