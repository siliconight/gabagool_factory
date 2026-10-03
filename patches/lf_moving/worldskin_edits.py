"""Level Factory 0.129.0: the anchored edits to zoo_worldskin.gd, run by
`patches/patch_lf_moving_parts.py` (which checks the version first). Every
anchor must match exactly once; a miss refuses the whole file."""
import pathlib

import os

LF = pathlib.Path(os.environ.get("LF_ROOT") or pathlib.Path(__file__).resolve().parents[2] / "level_factory")
GD = LF / "assets" / "godot" / "zoo_worldskin.gd"

raw = GD.read_bytes()
crlf = b"\r\n" in raw
s = raw.decode("utf-8").replace("\r\n", "\n")


def edit(old, new):
    global s
    assert s.count(old) == 1, (old[:60], s.count(old))
    s = s.replace(old, new)


# --- constants and shaders, after the shutter block's state -----------------------------
edit('''var _shutter_shader: Shader = null
var _shutter_materials: Dictionary = {}
''', '''var _shutter_shader: Shader = null
var _shutter_materials: Dictionary = {}


## TURNING PARTS (0.129.0) -- small things that move. The walker, 2026-10-02:
## "start with the roller grill". Zoo 1.55.0 builds a part that turns (the
## grill's rollers, its dogs) as a surface of its own, every vertex carrying
## the AXLE in its second UV set, in this engine's axes, and names the
## material for its axis and rate:
##
##     M_<species>_<kind>_turn_x36      36 degrees a second about +X
##     M_<species>_<kind>_turn_xn36     the other way
##
## The surface's own material is REPLACED by a shader that reproduces a flat
## material -- albedo times the vertex colour, roughness, metallic; Zoo keeps
## a turning kind off the skin library for exactly this, so there is no
## texture to carry -- and turns the vertices and their normals about the
## axle on the shader clock. No node moves, no script ticks, no draw is
## added here: the surface was one draw as a standard material and is one
## as a shader. The phase is per node from NODE_POSITION_WORLD, as the CRT
## pass's and the shutters' are, so two grills do not turn in step. A part
## whose name names no rate is left alone: only `_turn_` names are read.
const TURN_MARK: String = "_turn_"
const TURN_PATTERN: String = "_turn_([xyz])(n?)(\\\\d+)$"

const TURN_SHADER: String = """
shader_type spatial;
render_mode cull_back, depth_draw_opaque;

uniform vec4 albedo : source_color = vec4(1.0);
uniform float roughness : hint_range(0.0, 1.0) = 0.5;
uniform float metallic : hint_range(0.0, 1.0) = 0.0;
uniform float rate_rad_s = 0.0;
uniform int axis = 0;

float turn_hash(float x) {
	return fract(sin(x) * 43758.5453123);
}

vec2 turn_about(vec2 v, vec2 pivot, float c, float s) {
	vec2 q = v - pivot;
	return pivot + vec2(c * q.x - s * q.y, s * q.x + c * q.y);
}

void vertex() {
	// ONE PHASE PER PROP: two grills side by side are not in step, and every
	// roller of one grill shares its node and so its phase.
	float inst = turn_hash(dot(NODE_POSITION_WORLD, vec3(12.9898, 78.233, 37.719)));
	float a = rate_rad_s * TIME + inst * 6.2831853;
	float c = cos(a);
	float s = sin(a);
	// the axle, in model space, from the second UV set: the two coordinates
	// of the axis in the plane the part turns in
	vec2 pivot = UV2;
	if (axis == 0) {
		VERTEX.yz = turn_about(VERTEX.yz, pivot, c, s);
		NORMAL.yz = turn_about(NORMAL.yz, vec2(0.0), c, s);
	} else if (axis == 1) {
		VERTEX.zx = turn_about(VERTEX.zx, pivot, c, s);
		NORMAL.zx = turn_about(NORMAL.zx, vec2(0.0), c, s);
	} else {
		VERTEX.xy = turn_about(VERTEX.xy, pivot, c, s);
		NORMAL.xy = turn_about(NORMAL.xy, vec2(0.0), c, s);
	}
}

void fragment() {
	ALBEDO = albedo.rgb * COLOR.rgb;
	ROUGHNESS = roughness;
	METALLIC = metallic;
}
"""

var _turn_shader: Shader = null
var _turn_materials: Dictionary = {}
var _turn_re: RegEx = null

## THE CHURN (0.129.0). The walker, 2026-10-02: "i want some motion on the
## slurpee stuff too". Zoo 1.55.0's slush tile is the flavour and its ice;
## the diagonal bands it used to paint are drawn HERE, moving: a pass over
## the barrel's glow surface, a hair proud like the CRT pass, that darkens
## the same diagonal (three bands round, one and a half up; 1.15.0's
## `(x // 2 + y // 4) % 16`, the dark band two steps of sixteen) and walks it
## round the barrel once every CHURN_PERIOD_S. The facets say where they are
## round the barrel in their second UV set -- (u round, v up), both 0..1 --
## and every other corner of the glow surface carries v = 2, which this
## pass reads as "not slush" and discards.
##
## DARKENS ONLY, for the CRT pass's reason: ALBEDO is black and the blend is
## mix, so the barrel is multiplied by (1 - ALPHA), and a barrel Lux has cut
## the power to -- emission zero, black -- stays black under it. The light
## band the tile used to paint is what that costs; a pass that could lighten
## would glow on a dead machine. The base material is NOT replaced, so Lux's
## binder still finds the `_Face` it cuts. Cost: one draw a slush machine,
## the pass over its one glow surface, priced in this version's changelog.
const CHURN_PREFIX: String = "M_Slush_"
const CHURN_SUFFIX: String = "_Face"
const CHURN_PERIOD_S: float = 6.0
const CHURN_BAND_DARK: float = 0.42
## 2/16 painted; 3/16 moving, because a band two steps wide at 96 texels
## is four pixels and vanishes under motion at a metre.
const CHURN_BAND_FRAC: float = 3.0 / 16.0

const CHURN_SHADER: String = """
shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, cull_back,
	shadows_disabled, fog_disabled;

uniform float period_s = 6.0;
uniform float band_dark = 0.42;
uniform float band_frac = 0.1875;
uniform float proud_m = 0.002;

void vertex() {
	VERTEX += NORMAL * proud_m;
}

float churn_hash(float x) {
	return fract(sin(x) * 43758.5453123);
}

void fragment() {
	// not a churn facet: the cap, the topper, the panels
	if (UV2.y > 1.5) {
		discard;
	}
	float inst = churn_hash(dot(NODE_POSITION_WORLD, vec3(12.9898, 78.233, 37.719)));
	// three bands round and one and a half up, walking once round a period
	float b = fract(3.0 * UV2.x + 1.5 * UV2.y - 3.0 * TIME / period_s + inst);
	float band = step(0.5, b) * (1.0 - step(0.5 + band_frac, b));
	ALBEDO = vec3(0.0);
	ALPHA = band * band_dark;
}
"""

var _churn_shader: Shader = null
''')

# --- _post_import: both run for every GLB, before the kit branch --------------------------
edit('''	var shut: int = _shutters(scene)
	if shut > 0:
		print("[worldskin] %s  %d shutter surface(s) given their clock" % [base, shut])
''', '''	var shut: int = _shutters(scene)
	if shut > 0:
		print("[worldskin] %s  %d shutter surface(s) given their clock" % [base, shut])
	# EVERY GLB, before the kit branch for the same reason: a turning part
	# and a churning barrel arrive in prop GLBs.
	var turned: int = _turning_parts(scene)
	if turned > 0:
		print("[worldskin] %s  %d turning surface(s) given their axle" % [base, turned])
	var churned: int = _churn_passes(scene, {})
	if churned > 0:
		print("[worldskin] %s  %d churn surface(s) given their bands" % [base, churned])
''')

# --- the installers, after the shutter material builder ---------------------------------
edit('''func _is_tiled(base: String) -> bool:
''', '''## Every surface whose material is named for a rate gets the shader that
## turns it. The surface's own material is REPLACED (a second pass cannot
## move the first) by a shader carrying the flat material's own numbers.
## IDEMPOTENT on a re-import: a surface already wearing the shader is left.
func _turning_parts(n: Node) -> int:
	var count: int = 0
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi != null and mi.mesh != null:
		for i in range(mi.mesh.get_surface_count()):
			var mat: Material = mi.mesh.surface_get_material(i)
			if mat == null or not String(mat.resource_name).contains(TURN_MARK):
				continue
			var bm: BaseMaterial3D = mat as BaseMaterial3D
			if bm == null:
				continue                      # already the shader: a re-import
			var spec: Array = _turn_spec(String(bm.resource_name))
			if spec.is_empty():
				push_warning("[worldskin] %s carries %s but names no axis and rate; left alone"
					% [bm.resource_name, TURN_MARK])
				continue
			mi.mesh.surface_set_material(i, _turn_material(bm, int(spec[0]), float(spec[1])))
			count += 1
	for c in n.get_children():
		count += _turning_parts(c)
	return count


## ``[axis, degrees a second]`` off a material name, or ``[]``: `_turn_x36`
## is 36 degrees a second about +X, `_turn_xn36` the other way.
func _turn_spec(nm: String) -> Array:
	if _turn_re == null:
		_turn_re = RegEx.new()
		_turn_re.compile(TURN_PATTERN)
	var m: RegExMatch = _turn_re.search(nm)
	if m == null:
		return []
	var axis: int = {"x": 0, "y": 1, "z": 2}[m.get_string(1)]
	var deg: float = float(m.get_string(3))
	if m.get_string(2) == "n":
		deg = -deg
	return [axis, deg]


func _turn_material(bm: BaseMaterial3D, axis: int, deg_s: float) -> ShaderMaterial:
	var key: int = bm.get_instance_id()
	if _turn_materials.has(key):
		return _turn_materials[key] as ShaderMaterial
	if _turn_shader == null:
		_turn_shader = Shader.new()
		_turn_shader.code = TURN_SHADER
	var sm: ShaderMaterial = ShaderMaterial.new()
	sm.shader = _turn_shader
	sm.resource_name = String(bm.resource_name)
	# the flat material's own numbers; the vertex colour is multiplied in
	# whatever the material said, because a roller's grease and a dog's
	# colour ride it (Zoo's `tint_wear`)
	sm.set_shader_parameter("albedo", Color(bm.albedo_color.r, bm.albedo_color.g, bm.albedo_color.b, 1.0))
	sm.set_shader_parameter("roughness", bm.roughness)
	sm.set_shader_parameter("metallic", bm.metallic)
	sm.set_shader_parameter("rate_rad_s", deg_to_rad(deg_s))
	sm.set_shader_parameter("axis", axis)
	_turn_materials[key] = sm
	return sm


## Every slush glow face gets the churn pass as its next_pass; the face's
## own material is kept (Lux cuts it). Once per material, once per import.
func _churn_passes(n: Node, seen: Dictionary) -> int:
	var count: int = 0
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi != null and mi.mesh != null:
		for i in range(mi.mesh.get_surface_count()):
			var bm: BaseMaterial3D = mi.mesh.surface_get_material(i) as BaseMaterial3D
			if bm == null or seen.has(bm.get_instance_id()):
				continue
			seen[bm.get_instance_id()] = true
			var nm: String = String(bm.resource_name)
			if not (nm.begins_with(CHURN_PREFIX) and nm.ends_with(CHURN_SUFFIX)):
				continue
			if bm.next_pass != null:
				continue
			bm.next_pass = _churn_material(bm)
			count += 1
	for c in n.get_children():
		count += _churn_passes(c, seen)
	return count


func _churn_material(bm: BaseMaterial3D) -> ShaderMaterial:
	if _churn_shader == null:
		_churn_shader = Shader.new()
		_churn_shader.code = CHURN_SHADER
	var sm: ShaderMaterial = ShaderMaterial.new()
	sm.shader = _churn_shader
	sm.resource_name = String(bm.resource_name) + "_churn"
	sm.set_shader_parameter("period_s", CHURN_PERIOD_S)
	sm.set_shader_parameter("band_dark", CHURN_BAND_DARK)
	sm.set_shader_parameter("band_frac", CHURN_BAND_FRAC)
	sm.set_shader_parameter("proud_m", SCREEN_PROUD_M)
	return sm


func _is_tiled(base: String) -> bool:
''')

out = s.replace("\n", "\r\n") if crlf else s
GD.write_bytes(out.encode("utf-8"))
print("worldskin edited", "crlf" if crlf else "lf")
