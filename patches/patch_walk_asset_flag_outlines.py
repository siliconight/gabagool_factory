"""A flagged asset stays boxed in its verdict's colour for the rest of the walk, and the banner moves clear of F3 (roadmap 253).

The walker, 2026-10-19, after the first walk with the asset-flag keys (cold run 9334's copy, county_hospital_001 on a
rainy night): "we should put a red line around an item that is flagged to show the user that it is flaggd for future
art pass or more work", then "green for looks good, red for needs more work" and "and it persists for that session".
Their five presses on a parked car had landed -- five records, five frames -- and nothing on screen had stayed to say
so: the banner drew at the top-left, under the F3 overlay's panel, and a frame of that walk shows it cut off between
the overlay's two panels (`_scratch/review/walk_9334/asset_flags/20261019T212551_good_004.png`).

What it changes (anchored; each file pinned by hash; nothing written on a miss):
  * tools/walk_asset_flags.gd -- every press boxes the asset the record names, green for good and red for needs love,
    until the walk quits; a second flag of one asset repaints its box and adds none; a piece of a level layer (a scene
    at the package's root, where Lot's kerbs live) is boxed itself rather than the layer; the box is held off the
    asset's bounds and drawn pulled toward the eye, so its edges show on a wall module flush in a run of neighbours;
    the picks skip the boxes. The banner hangs from the foot of the screen in the verdict's colour.
  * tools/walk_asset_flags_selftest.gd -- what a flag leaves on screen, checked headless: colours, rings, the repaint,
    the layer piece, a pick along a line only a box crosses (with its control), the boxes outlasting the banner, and
    the banner's place.

    python patches/patch_walk_asset_flag_outlines.py --stage DIR   # both files patched into DIR; tools/ untouched
    python patches/patch_walk_asset_flag_outlines.py --tests       # the selftest only (prove it fails first)
    python patches/patch_walk_asset_flag_outlines.py               # everything
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
HANDLER = ROOT / "tools" / "walk_asset_flags.gd"
SELFTEST = ROOT / "tools" / "walk_asset_flags_selftest.gd"
SHA = {HANDLER: "7ac2454ad91a3443", SELFTEST: "3f8b8d1dda247dba"}


def T(block):
    """GDScript indents with tabs; the blocks below are written with four spaces a level, at line starts only."""
    out = []
    for line in block.split("\n"):
        body = line.lstrip(" ")
        lead = len(line) - len(body)
        assert lead % 4 == 0, "indent not a whole number of levels: %r" % line
        out.append("\t" * (lead // 4) + body)
    return "\n".join(out)


# --------------------------------------------------------------------------------------------- the handler

H_HEAD_OLD = T("""## picks; a MultiMesh (Lot's dressing) is not a MeshInstance3D and does not -- the physics hit then stands in.
##
## Walk copies only, DEBUG BUILDS ONLY: a release export frees this on its first frame. The package ships no
""")
H_HEAD_NEW = T("""## picks; a MultiMesh (Lot's dressing) is not a MeshInstance3D and does not -- the physics hit then stands in.
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
""")

H_CONST_OLD = T("""const VERDICT_BY_KEY := {KEY_G: "good", KEY_P: "needs_love"}
""")
H_CONST_NEW = T('''const VERDICT_BY_KEY := {KEY_G: "good", KEY_P: "needs_love"}
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
''')

H_VARS_OLD = T("""var _banner_left: float = 0.0
var _count: int = 0
""")
H_VARS_NEW = T("""var _banner_left: float = 0.0
var _count: int = 0
## The boxes drawn this session, under one node the picks skip, each by its asset's instance id.
var _outlines: Node3D = null
var _outlined: Dictionary = {}
var _materials: Dictionary = {}
var _shader: Shader = null
""")

H_LABEL_OLD = T("""    _label = Label.new()
    _label.position = Vector2(16, 48)
    _label.add_theme_font_size_override("font_size", 20)
    _banner.add_child(_label)
""")
H_LABEL_NEW = T("""    _label = Label.new()
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
""")

H_FLAG_OLD = T("""    _append(rec)
    _show("FLAGGED %s: %s%s" % [
        "LOOKS GOOD" if verdict == "good" else "NEEDS LOVE",
        String(rec["asset"]) if String(rec["asset"]) != "" else String(rec["node"]),
        (" in " + String(rec["building"])) if String(rec["building"]) != "" else ""])
    return rec
""")
H_FLAG_NEW = T("""    _append(rec)
    outline(node, verdict)
    _show("FLAGGED %s: %s%s" % [
        "LOOKS GOOD" if verdict == "good" else "NEEDS LOVE",
        _shown_name(node, rec),
        (" in " + String(rec["building"])) if String(rec["building"]) != "" else ""],
        OUTLINE_COLOR.get(verdict, Color.WHITE))
    return rec
""")

H_REACH_OLD = T("""        var t: float = _triangle_t(mi, from, dir)
        if t < best_t:
""")
H_REACH_NEW = T("""        var t: float = _triangle_t(mi, from, dir)
        if t < best_t and t <= RAY_LENGTH:
""")

H_COLLECT_OLD = T("""## Every visible MeshInstance3D whose world bounds the ray enters within RAY_LENGTH, as [entry distance, node].
func _collect(n: Node, from: Vector3, dir: Vector3, out: Array) -> void:
    var mi := n as MeshInstance3D
""")
H_COLLECT_NEW = T("""## Every visible MeshInstance3D whose world bounds the ray enters within RAY_LENGTH, as [entry distance, node]; the
## boxes drawn round flagged assets are not among them.
func _collect(n: Node, from: Vector3, dir: Vector3, out: Array) -> void:
    if n == _outlines:
        return
    var mi := n as MeshInstance3D
""")

H_SHOW_OLD = T("""func _show(text: String) -> void:
    if _label == null:
        return
    _label.text = text
    _banner.visible = true
    _banner_left = BANNER_SECS
""")
H_SHOW_NEW = T("""func _show(text: String, color: Color) -> void:
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
""")

HANDLER_EDITS = [
    ("the header says what a flag leaves on screen", H_HEAD_OLD, H_HEAD_NEW),
    ("the outline constants and shader", H_CONST_OLD, H_CONST_NEW),
    ("the session's boxes", H_VARS_OLD, H_VARS_NEW),
    ("the banner at the foot of the screen; the boxes' node", H_LABEL_OLD, H_LABEL_NEW),
    ("a press boxes what it flagged", H_FLAG_OLD, H_FLAG_NEW),
    ("a mesh is picked only within reach", H_REACH_OLD, H_REACH_NEW),
    ("the picks skip the boxes", H_COLLECT_OLD, H_COLLECT_NEW),
    ("the banner's colour; the box itself", H_SHOW_OLD, H_SHOW_NEW),
]

# --------------------------------------------------------------------------------------------- the selftest

S_HEAD_OLD = T("""## checks the collider stands in, said as `how: physics`. An echo and a release must write nothing.

const SUBJECT := "res://_walk_asset_flags.gd"
const FLAGS := "res://asset_flags.jsonl"
const MODULE := "res://lot/deli_a01/art/zoo/prop_bench_delco_1997_01_w180.glb"
const BUILDING := "res://lot/deli_a01/site.tscn"

var _fails: int = 0
""")
S_HEAD_NEW = T("""## checks the collider stands in, said as `how: physics`. An echo and a release must write nothing.
##
## And what a flag leaves on screen (the walker, 2026-10-19): each thing flagged is boxed, green for good and red for
## needs love, and the box is held off its bounds. The box goes round the module when the pick is under a model (the
## GLB the module came from), and round the node picked when it is under a scene: the building's collider, and a kerb
## in the level's own scene -- `res://presentation/lux.applied.tscn`, where a walk copy's site lives, with a second
## piece 30 m off that a box round the level would take in -- which the banner names by its path, not the level's
## file. A second flag of one asset repaints its box and adds none; a pick along a line that meets only a box finds
## nothing, beside its control, that the line does meet the box; a mesh round the whole level, its faces 450 m off as
## Lux's horizon glow's are, is never picked, and a press at the open sky boxes nothing; the boxes outlast the banner;
## and the banner hangs from the foot of the screen in its verdict's colour.

const SUBJECT := "res://_walk_asset_flags.gd"
const FLAGS := "res://asset_flags.jsonl"
const MODULE := "res://lot/deli_a01/art/zoo/prop_bench_delco_1997_01_w180.glb"
const BUILDING := "res://lot/deli_a01/site.tscn"
const SITE := "res://presentation/lux.applied.tscn"
## What each box must ring, worked by hand from the sizes and places the scene below is built with.
const BENCH := AABB(Vector3(-0.5, -0.5, -5.5), Vector3(1, 1, 1))
const SLAB := AABB(Vector3(-2, -2, -8.5), Vector3(4, 4, 1))
const KERB := AABB(Vector3(5.5, -0.1, -0.5), Vector3(1, 0.2, 1))

var _fails: int = 0
var _consts: Dictionary = {}
""")

S_HELPERS_OLD = T("""func _lines() -> Array:
    if not FileAccess.file_exists(FLAGS):
        return []
    var out: Array = []
    for ln in FileAccess.get_file_as_string(FLAGS).split("\\n", false):
        out.append(JSON.parse_string(ln))
    return out
""")
S_HELPERS_NEW = T("""func _lines() -> Array:
    if not FileAccess.file_exists(FLAGS):
        return []
    var out: Array = []
    for ln in FileAccess.get_file_as_string(FLAGS).split("\\n", false):
        out.append(JSON.parse_string(ln))
    return out


## The boxes the handler has drawn this session.
func _boxes(flags: Node) -> Array:
    var holder: Node = flags.get_node_or_null(^"AssetFlagOutlines")
    return [] if holder == null else holder.get_children()


## The box drawn round `target`, or null.
func _box_for(flags: Node, target: Node) -> MeshInstance3D:
    for b in _boxes(flags):
        var n: Node = b
        if n.get_meta(&"target", NodePath()) == target.get_path():
            return n as MeshInstance3D
    return null


func _color(box: MeshInstance3D) -> Color:
    if box == null or not (box.material_override is ShaderMaterial):
        return Color.BLACK
    var m: ShaderMaterial = box.material_override as ShaderMaterial
    var c: Color = m.get_shader_parameter(&"color")
    return c


func _green(c: Color) -> bool:
    return c.g > 0.6 and c.r < 0.5 and c.b < 0.5


func _red(c: Color) -> bool:
    return c.r > 0.8 and c.g < 0.4 and c.b < 0.4


## True when `box` rings `inner`: its bounds grown by the handler's pad and half an edge's thickness, to float error.
func _rings(box: MeshInstance3D, inner: AABB) -> bool:
    if box == null or box.mesh == null:
        return false
    var grow: float = float(_consts.get("OUTLINE_PAD_M", NAN)) + 0.5 * float(_consts.get("OUTLINE_EDGE_M", NAN))
    var want: AABB = inner.grow(grow)
    var got: AABB = box.global_transform * box.mesh.get_aabb()
    return got.position.is_equal_approx(want.position) and got.size.is_equal_approx(want.size)
""")

S_CONSTS_OLD = T("""        quit(2)
        return
    if FileAccess.file_exists(FLAGS):
""")
S_CONSTS_NEW = T("""        quit(2)
        return
    _consts = (load(SUBJECT) as GDScript).get_script_constant_map()
    if FileAccess.file_exists(FLAGS):
""")

S_SITE_OLD = T("""    mi.position = Vector3(0, 0, -5)
    var flags: Node = (load(SUBJECT) as GDScript).new()
""")
S_SITE_NEW = T("""    mi.position = Vector3(0, 0, -5)
    # the level's own scene, as a walk copy instances it, with a kerb 6 m to the camera's right, a second piece of it
    # 30 m beyond, which a box round the whole level would take in, and a mesh round all of it with its faces 450 m
    # off, as Lux's horizon glow is
    var site := Node3D.new()
    site.name = &"Site"
    site.scene_file_path = SITE
    scene.add_child(site)
    var slab_mesh := BoxMesh.new()
    slab_mesh.size = Vector3(1, 0.2, 1)
    var kerb := MeshInstance3D.new()
    kerb.name = &"kerb"
    kerb.mesh = slab_mesh
    site.add_child(kerb)
    kerb.position = Vector3(6, 0, 0)
    var far_piece := MeshInstance3D.new()
    far_piece.name = &"far_piece"
    far_piece.mesh = slab_mesh
    site.add_child(far_piece)
    far_piece.position = Vector3(36, 0, 0)
    var horizon := MeshInstance3D.new()
    horizon.name = &"horizon"
    var hm := BoxMesh.new()
    hm.size = Vector3(900, 900, 900)
    horizon.mesh = hm
    site.add_child(horizon)
    var flags: Node = (load(SUBJECT) as GDScript).new()
""")

S_ECHO_OLD = T("""        _check("the collider is recorded beside it", String(r.get("collider")).ends_with("slab_col_1"))

    _press(KEY_G, true, true)
    _press(KEY_G, false, false)
    await process_frame
    _check("an echo and a release write nothing", _lines().size() == 1)
""")
S_ECHO_NEW = T("""        _check("the collider is recorded beside it", String(r.get("collider")).ends_with("slab_col_1"))
    _check("G boxes the module", _boxes(flags).size() == 1 and _box_for(flags, module) != null)
    _check("in green", _green(_color(_box_for(flags, module))))
    _check("round the module's bounds, held off them", _rings(_box_for(flags, module), BENCH))

    _press(KEY_G, true, true)
    _press(KEY_G, false, false)
    await process_frame
    _check("an echo and a release write nothing", _lines().size() == 1)
    _check("and draw nothing", _boxes(flags).size() == 1)
""")

S_TAIL_OLD = T("""        _check("and names its building's scene", String(r2.get("asset_file")) == BUILDING)
        _check("the building is still deli_a01", String(r2.get("building")) == "deli_a01")

    DirAccess.remove_absolute(ProjectSettings.globalize_path(FLAGS))
    print("selftest: %d check(s) failed" % _fails)
    quit(1 if _fails > 0 else 0)
""")
S_TAIL_NEW = T("""        _check("and names its building's scene", String(r2.get("asset_file")) == BUILDING)
        _check("the building is still deli_a01", String(r2.get("building")) == "deli_a01")
    _check("P boxes the collider itself, the building being a scene and not a model", _boxes(flags).size() == 2
        and _box_for(flags, body) != null and _box_for(flags, bldg) == null)
    _check("in red", _red(_color(_box_for(flags, body))))
    _check("round its shape, nothing under it being drawn", _rings(_box_for(flags, body), SLAB))

    mi.visible = true
    await process_frame
    _press(KEY_P, true, false)
    await process_frame
    recs = _lines()
    _check("P on the module writes a third record", recs.size() == 3)
    if recs.size() >= 3:
        var r3: Dictionary = recs[2]
        _check("needs_love, picked by render", String(r3.get("verdict")) == "needs_love"
            and String(r3.get("how")) == "render")
    _check("and repaints the module's box rather than adding one", _boxes(flags).size() == 2)
    _check("red now", _red(_color(_box_for(flags, module))))
    _check("still round the module", _rings(_box_for(flags, module), BENCH))

    cam.look_at(kerb.global_position, Vector3.UP)
    await process_frame
    _press(KEY_P, true, false)
    await process_frame
    recs = _lines()
    _check("P on the kerb writes a fourth record", recs.size() == 4)
    if recs.size() >= 4:
        var r4: Dictionary = recs[3]
        _check("which names the layer, as it always has", String(r4.get("asset_file")) == SITE)
    _check("the kerb is boxed itself, not the level", _rings(_box_for(flags, kerb), KERB)
        and _box_for(flags, site) == null)
    _check("in red", _red(_color(_box_for(flags, kerb))))
    _check("three boxes now", _boxes(flags).size() == 3)
    var shown: Label = flags.get("_label")
    _check("the banner names the kerb by its path, not the level's file", shown != null
        and shown.text.contains("kerb") and not shown.text.contains("lux.applied"))

    # a line from the camera's place to the module box's lower front edge passes under the bench and meets nothing
    # else in the scene: the box is all a pick along it could find
    var pad: float = float(_consts.get("OUTLINE_PAD_M", NAN))
    var dir: Vector3 = Vector3(0.0, BENCH.position.y - pad, BENCH.end.z + pad).normalized()
    var mbox: MeshInstance3D = _box_for(flags, module)
    _check("control: that line meets the box", mbox != null
        and float(flags.call("_triangle_t", mbox, Vector3.ZERO, dir)) < INF)
    var hit: Dictionary = flags.call("_render_hit", Vector3.ZERO, dir)
    _check("and a pick along it takes no box for an asset, nor the mesh 450 m off", hit.is_empty())

    # the open sky: nothing within reach but the mesh round the level, whose faces are 450 m off
    cam.look_at(Vector3(0, 50, -1), Vector3.UP)
    await process_frame
    _check("control: the line up meets the mesh round the level, out of reach", float(flags.call("_triangle_t",
        horizon, Vector3.ZERO, Vector3(0, 50, -1).normalized())) > float(_consts.get("RAY_LENGTH", INF)))
    _press(KEY_P, true, false)
    await process_frame
    recs = _lines()
    _check("P at the open sky writes a fifth record", recs.size() == 5)
    if recs.size() >= 5:
        var r5: Dictionary = recs[4]
        _check("which names nothing", String(r5.get("how")) == "none" and String(r5.get("node")) == "")
    _check("and boxes nothing", _boxes(flags).size() == 3)
    _check("the banner says nothing was in reach", shown != null and shown.text.contains("nothing within"))

    await create_timer(float(_consts.get("BANNER_SECS", 3.0)) + 0.5).timeout
    var banner: CanvasLayer = flags.get("_banner")
    _check("the banner goes after its seconds", banner != null and not banner.visible)
    _check("and the boxes stay", _boxes(flags).size() == 3)
    var label: Label = flags.get("_label")
    _check("the banner hangs from the foot of the screen, clear of F3's panels at the top", label != null
        and label.anchor_top == 1.0 and label.anchor_bottom == 1.0)
    _check("in the last verdict's colour", label != null and _red(label.get_theme_color(&"font_color")))

    DirAccess.remove_absolute(ProjectSettings.globalize_path(FLAGS))
    print("selftest: %d check(s) failed" % _fails)
    quit(1 if _fails > 0 else 0)
""")

SELFTEST_EDITS = [
    ("the header, the new places and their bounds", S_HEAD_OLD, S_HEAD_NEW),
    ("the box helpers", S_HELPERS_OLD, S_HELPERS_NEW),
    ("the subject's constants", S_CONSTS_OLD, S_CONSTS_NEW),
    ("a level layer with a kerb in it", S_SITE_OLD, S_SITE_NEW),
    ("G's box; an echo draws nothing", S_ECHO_OLD, S_ECHO_NEW),
    ("P's box, the repaint, the kerb, the skip, the banner", S_TAIL_OLD, S_TAIL_NEW),
]


def _sha(data):
    return hashlib.sha256(data).hexdigest()[:16]


def _patched(path, edits):
    """``(new text, state)``: the file with its edits applied, or ``(None, "applied")`` when every edit's NEW text is
    already there once. Refuses on a hash it was not written against, or an anchor that is not there exactly once."""
    data = path.read_bytes()
    assert b"\r\n" not in data, "%s has CRLF endings; these edits are LF" % path
    text = data.decode("utf-8")
    if _sha(data) != SHA[path]:
        if all(text.count(new) == 1 for _, _, new in edits):
            return None, "applied"
        raise SystemExit("REFUSED: %s is %s, not the %s this patch was written against; nothing written"
                         % (path.relative_to(ROOT), _sha(data), SHA[path]))
    for what, old, new in edits:
        n = text.count(old)
        if n != 1:
            raise SystemExit("REFUSED: %s: the anchor for %r is there %d times, not once; nothing written"
                             % (path.relative_to(ROOT), what, n))
        text = text.replace(old, new)
    return text, "patched"


def main(argv):
    stage = None
    if "--stage" in argv:
        stage = pathlib.Path(argv[argv.index("--stage") + 1]).resolve()
    jobs = [(SELFTEST, SELFTEST_EDITS)] if "--tests" in argv else [(HANDLER, HANDLER_EDITS), (SELFTEST, SELFTEST_EDITS)]
    # every file worked out before any is written: a refusal on the second leaves the first untouched
    results = [(path, *_patched(path, edits)) for path, edits in jobs]
    for path, text, state in results:
        if text is None:
            print("%-40s already applied" % path.relative_to(ROOT))
            continue
        dest = path if stage is None else stage / path.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(text.encode("utf-8"))
        print("%-40s %s -> %s (%d bytes, sha %s)" % (path.relative_to(ROOT), state, dest, len(text.encode("utf-8")),
                                                     _sha(text.encode("utf-8"))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
