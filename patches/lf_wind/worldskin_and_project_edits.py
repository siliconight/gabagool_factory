"""Level Factory 0.130.0: the anchored edits to the worldskin, the project
writer, the export and the preview, run by `patches/patch_lf_wind.py` (which
checks the version first). Every anchor must match exactly once."""
import os
import pathlib

LF = pathlib.Path(os.environ.get("LF_ROOT") or pathlib.Path(__file__).resolve().parents[2] / "level_factory")


def edit(rel, pairs):
    p = LF / rel
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in pairs:
        assert s.count(old) == 1, (rel, old[:60], s.count(old))
        s = s.replace(old, new)
    p.write_bytes((s.replace("\n", "\r\n") if crlf else s).encode("utf-8"))
    print("edited", rel)


# --- the worldskin -------------------------------------------------------------------------
edit("assets/godot/zoo_worldskin.gd", [
('''var _churn_shader: Shader = null
''',
'''var _churn_shader: Shader = null


## THE WIND (0.130.0) -- a crown sways. The walker, 2026-10-03: "start with
## the crowns" (`docs/proposals/WIND_DESIGN.md` at the factory root). Zoo
## 1.56.0 writes every corner of a street tree's crown with a WEIGHT (its
## height over the crown's, squared) and a PHASE of its own leaf cluster in
## its second UV set; the crown is the MeshInstance3D named for it. Its
## material is a textured skin, so the shader that replaces it reproduces
## exactly what Zoo's skins use -- the albedo texture at its UV1 scale, the
## metallic-roughness texture by channel, the vertex colour where the
## surface is tinted, the two factors, alpha scissor where the skin is a
## cutout -- and a material carrying anything outside that set (a normal
## map, an emission, a blend) is REFUSED: left still and named, never drawn
## wrong. Before any motion, the crown is shot with the wind at zero and
## compared with its old self pixel for pixel.
##
## The wind is one global uniform, `lf_wind` (direction times metres a
## second), declared by the shipped project.godot from the brief's weather
## (`packages/core/godot_project.py`). Gusts are computed in the shader from
## TIME and the vertex's world position -- a swell over a slower swell,
## phased by the distance downwind so the front walks across the lot -- and
## a per-node offset keeps two trees apart. No node moves, no script ticks,
## no draw is added: the crown was one surface and is one surface.
const CROWN_NODE_PREFIX: String = "StreetTree_Crown"
## Tip displacement per metre a second of wind, and its cap: a breath
## (1.5 m/s) moves the top of a crown 3 cm, a storm (9) 18 cm.
const SWAY_M_PER_MS: float = 0.02
const SWAY_CAP_M: float = 0.4
const SWAY_SWELL_S: float = 7.0
const SWAY_GUST_FRONT_MS: float = 10.0
const SWAY_FLUTTER_HZ: float = 2.0
const SWAY_FLUTTER_M_PER_MS: float = 0.002

const SWAY_SHADER: String = """
shader_type spatial;
render_mode cull_back, depth_draw_opaque, world_vertex_coords;

global uniform vec3 lf_wind;

uniform vec4 albedo : source_color = vec4(1.0);
uniform sampler2D albedo_tex : source_color, filter_nearest_mipmap, repeat_enable;
uniform bool has_albedo_tex = false;
uniform sampler2D rm_tex : hint_default_white, filter_nearest_mipmap, repeat_enable;
uniform bool has_rough_tex = false;
uniform int rough_channel = 1;
uniform bool has_metal_tex = false;
uniform int metal_channel = 2;
uniform float roughness : hint_range(0.0, 1.0) = 1.0;
uniform float metallic : hint_range(0.0, 1.0) = 0.0;
uniform vec3 uv1_scale = vec3(1.0);
uniform vec3 uv1_offset = vec3(0.0);
uniform bool use_vertex_colour = false;
uniform float alpha_scissor = -1.0;
uniform float m_per_ms = 0.02;
uniform float cap_m = 0.4;
uniform float swell_s = 7.0;
uniform float front_ms = 10.0;
uniform float flutter_hz = 2.0;
uniform float flutter_m_per_ms = 0.002;

const float TAU_ = 6.2831853;

float sway_hash(float x) {
	return fract(sin(x) * 43758.5453123);
}

float channel(vec4 c, int i) {
	if (i == 0) { return c.r; }
	if (i == 1) { return c.g; }
	if (i == 2) { return c.b; }
	return c.a;
}

void vertex() {
	// VERTEX is in world space here (world_vertex_coords), so the wind,
	// which is a world direction, is added as it is
	float speed = length(lf_wind);
	if (speed > 0.0001) {
		vec3 dir = lf_wind / speed;
		float weight = UV2.x;
		float phase = UV2.y;
		float inst = sway_hash(dot(NODE_POSITION_WORLD, vec3(12.9898, 78.233, 37.719)));
		// the gust front: a swell over a slower swell, delayed by the
		// distance downwind, so the front walks across the lot
		float down = dot(VERTEX, dir) / front_ms;
		float t = TIME - down + inst * swell_s;
		float gust = 0.6 + 0.25 * sin(t * TAU_ / swell_s) + 0.15 * sin(t * TAU_ / (swell_s * 2.7) + 1.3);
		// the lee lean: a crown bends away from the wind and does not
		// swing back past upright
		float lean = weight * weight * min(speed * m_per_ms, cap_m) * gust;
		// the flutter: each cluster its own, across the wind
		vec3 across = normalize(cross(dir, vec3(0.0, 1.0, 0.0)));
		float flutter = weight * speed * flutter_m_per_ms * sin(TIME * TAU_ * flutter_hz + phase * TAU_ + inst * 3.0);
		VERTEX += dir * lean + across * flutter;
	}
}

void fragment() {
	vec2 uv = UV * uv1_scale.xy + uv1_offset.xy;
	vec4 base = albedo;
	if (has_albedo_tex) {
		base *= texture(albedo_tex, uv);
	}
	if (use_vertex_colour) {
		base.rgb *= COLOR.rgb;
	}
	if (alpha_scissor >= 0.0 && base.a < alpha_scissor) {
		discard;
	}
	vec4 rm = texture(rm_tex, uv);
	ALBEDO = base.rgb;
	ROUGHNESS = roughness * (has_rough_tex ? channel(rm, rough_channel) : 1.0);
	METALLIC = metallic * (has_metal_tex ? channel(rm, metal_channel) : 1.0);
}
"""

var _sway_shader: Shader = null
var _sway_materials: Dictionary = {}
'''),
('''	var churned: int = _churn_passes(scene, {})
	if churned > 0:
		print("[worldskin] %s  %d churn surface(s) given their bands" % [base, churned])
''',
'''	var churned: int = _churn_passes(scene, {})
	if churned > 0:
		print("[worldskin] %s  %d churn surface(s) given their bands" % [base, churned])
	# EVERY GLB, before the kit branch: a crown arrives in a prop GLB.
	var swayed: Array = _sway_crowns(scene)
	if int(swayed[0]) + int(swayed[1]) > 0:
		print("[worldskin] %s  %d crown surface(s) given the wind, %d refused" % [base, int(swayed[0]), int(swayed[1])])
'''),
('''func _is_tiled(base: String) -> bool:
''',
'''## Every surface of a crown node whose mesh carries a second UV set gets
## the sway shader in place of its skin, carrying the skin's own numbers.
## ``[given, refused]``. IDEMPOTENT: a surface already wearing the shader
## is left. A skin outside the shader's support set is refused by name.
func _sway_crowns(n: Node) -> Array:
	var given: int = 0
	var refused: int = 0
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi != null and mi.mesh != null and String(mi.name).begins_with(CROWN_NODE_PREFIX):
		for i in range(mi.mesh.get_surface_count()):
			var arrays: Array = mi.mesh.surface_get_arrays(i)
			var uv2: Variant = arrays[Mesh.ARRAY_TEX_UV2] if arrays.size() > Mesh.ARRAY_TEX_UV2 else null
			if uv2 == null or (uv2 as PackedVector2Array).is_empty():
				continue                      # no sway layer: an older Zoo's crown
			var mat: Material = mi.mesh.surface_get_material(i)
			var bm: BaseMaterial3D = mat as BaseMaterial3D
			if bm == null:
				continue                      # already the shader: a re-import
			var why: String = _sway_unsupported(bm)
			if why != "":
				push_warning("[worldskin] %s on %s left still: %s" % [bm.resource_name, mi.name, why])
				refused += 1
				continue
			var cols: PackedColorArray = PackedColorArray()
			if arrays[Mesh.ARRAY_COLOR] != null:
				cols = arrays[Mesh.ARRAY_COLOR]
			mi.mesh.surface_set_material(i, _sway_material(bm, not cols.is_empty() and _has_tint(cols)))
			given += 1
	for c in n.get_children():
		var r: Array = _sway_crowns(c)
		given += int(r[0])
		refused += int(r[1])
	return [given, refused]


## Why a skin cannot be reproduced by the sway shader, or "" when it can.
func _sway_unsupported(bm: BaseMaterial3D) -> String:
	if bm.normal_enabled:
		return "a normal map"
	if bm.emission_enabled:
		return "an emission"
	if bm.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED \\
			and bm.transparency != BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR:
		return "a blended transparency"
	if bm.shading_mode != BaseMaterial3D.SHADING_MODE_PER_PIXEL:
		return "a shading mode other than per-pixel"
	if bm.ao_enabled or bm.heightmap_enabled or bm.rim_enabled or bm.clearcoat_enabled \\
			or bm.anisotropy_enabled or bm.subsurf_scatter_enabled or bm.backlight_enabled \\
			or bm.refraction_enabled or bm.detail_enabled:
		return "a feature the sway shader does not carry"
	if bm.uv1_triplanar:
		return "triplanar UV1"
	return ""


func _sway_material(bm: BaseMaterial3D, tinted: bool) -> ShaderMaterial:
	var key: int = bm.get_instance_id()
	if _sway_materials.has(key):
		return _sway_materials[key] as ShaderMaterial
	if _sway_shader == null:
		_sway_shader = Shader.new()
		_sway_shader.code = SWAY_SHADER
	var sm: ShaderMaterial = ShaderMaterial.new()
	sm.shader = _sway_shader
	sm.resource_name = String(bm.resource_name)
	sm.set_shader_parameter("albedo", Color(bm.albedo_color.r, bm.albedo_color.g, bm.albedo_color.b, bm.albedo_color.a))
	if bm.albedo_texture != null:
		sm.set_shader_parameter("albedo_tex", bm.albedo_texture)
		sm.set_shader_parameter("has_albedo_tex", true)
	var rm: Texture2D = bm.roughness_texture if bm.roughness_texture != null else bm.metallic_texture
	if rm != null:
		sm.set_shader_parameter("rm_tex", rm)
	sm.set_shader_parameter("has_rough_tex", bm.roughness_texture != null)
	sm.set_shader_parameter("rough_channel", int(bm.roughness_texture_channel))
	sm.set_shader_parameter("has_metal_tex", bm.metallic_texture != null)
	sm.set_shader_parameter("metal_channel", int(bm.metallic_texture_channel))
	sm.set_shader_parameter("roughness", bm.roughness)
	sm.set_shader_parameter("metallic", bm.metallic)
	sm.set_shader_parameter("uv1_scale", bm.uv1_scale)
	sm.set_shader_parameter("uv1_offset", bm.uv1_offset)
	sm.set_shader_parameter("use_vertex_colour", tinted or bm.vertex_color_use_as_albedo)
	sm.set_shader_parameter("alpha_scissor",
		bm.alpha_scissor_threshold if bm.transparency == BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR else -1.0)
	sm.set_shader_parameter("m_per_ms", SWAY_M_PER_MS)
	sm.set_shader_parameter("cap_m", SWAY_CAP_M)
	sm.set_shader_parameter("swell_s", SWAY_SWELL_S)
	sm.set_shader_parameter("front_ms", SWAY_GUST_FRONT_MS)
	sm.set_shader_parameter("flutter_hz", SWAY_FLUTTER_HZ)
	sm.set_shader_parameter("flutter_m_per_ms", SWAY_FLUTTER_M_PER_MS)
	_sway_materials[key] = sm
	return sm


func _is_tiled(base: String) -> bool:
'''),
])

# --- the project writer: the wind as a shader global ------------------------------------
edit("packages/core/godot_project.py", [
('''def rendering_block(light_count: int, occluders: int) -> str:
''',
'''#: THE WIND (0.130.0). One global shader uniform, `lf_wind`, a direction
#: times metres a second, declared here so every shader that moves with the
#: weather (`zoo_worldskin.gd`'s sway) reads one value. Strength by the
#: brief's weather word; a word nobody knows gets the calm. The direction is
#: from the west (+X) until a brief says otherwise. Lux owns weather and is
#: where a wind that changes while a level runs would be set from.
WIND_BY_WEATHER = {"clear": 1.5, "rain": 4.0, "storm": 9.0, "hurricane": 15.0}
WIND_DEFAULT_M_S = 1.5
WIND_DIRECTION = (1.0, 0.0, 0.0)
WIND_KEY = "lf_wind"


def wind_for_weather(weather: str | None) -> tuple[float, float, float]:
    """The `lf_wind` vector for a brief's weather word."""
    speed = WIND_BY_WEATHER.get(str(weather or "").strip().lower(), WIND_DEFAULT_M_S)
    dx, dy, dz = WIND_DIRECTION
    return (dx * speed, dy * speed, dz * speed)


def shader_globals_block(weather: str | None) -> str:
    """The `[shader_globals]` section, ending with a blank line. One line a
    global, because the agreement test reads settings a line at a time."""
    x, y, z = wind_for_weather(weather)
    return ("[shader_globals]\\n"
            f'{WIND_KEY}={{"type": "vec3", "value": Vector3({x:g}, {y:g}, {z:g})}}\\n\\n')


def rendering_block(light_count: int, occluders: int) -> str:
'''),
])

# --- the export: the brief's weather into the profile and the project ---------------------
edit("packages/exporting/export.py", [
('''    require_no_autoloads: bool = True
    require_resource_closure: bool = True

    def as_dict(self) -> dict:
''',
'''    require_no_autoloads: bool = True
    require_resource_closure: bool = True
    #: The brief's weather word (0.130.0): what the shipped project's wind is
    #: written from. "clear" when the caller has no brief in hand.
    weather: str = "clear"

    def as_dict(self) -> dict:
'''),
('''def _write_project_godot(export_dir: Path, entry_scene: str, mission_id: str,
                         godot_version: str) -> None:
''',
'''def _write_project_godot(export_dir: Path, entry_scene: str, mission_id: str,
                         godot_version: str, weather: str = "clear") -> None:
'''),
('''        + rendering_block(package_light_budget(export_dir), 0)
        + _importer_defaults_block(export_dir) +
''',
'''        + rendering_block(package_light_budget(export_dir), 0)
        # the wind (0.130.0): one global the sway shaders read
        + shader_globals_block(weather)
        + _importer_defaults_block(export_dir) +
'''),
('''    _write_project_godot(export_dir, profile.entry_scene, mission_id,
                         profile.godot_version)
''',
'''    _write_project_godot(export_dir, profile.entry_scene, mission_id,
                         profile.godot_version, profile.weather)
'''),
])

s = (LF / "packages" / "exporting" / "export.py").read_text(encoding="utf-8")
assert "shader_globals_block" in s
import re
m = re.search(r"from packages\.core\.godot_project import \(([^)]*)\)", s, re.S) or re.search(r"from packages\.core\.godot_project import ([^\n]*)", s)
assert m, "no godot_project import in export.py"
old = m.group(0)
if "shader_globals_block" not in old:
    if old.rstrip().endswith(")"):
        new = old.rstrip()[:-1].rstrip() + ", shader_globals_block)"
    else:
        new = old + ", shader_globals_block"
    s = s.replace(old, new, 1)
    (LF / "packages" / "exporting" / "export.py").write_text(s, encoding="utf-8", newline="\n")
    print("import extended:", new.replace("\n", " ")[:120])

# --- the preview's project text carries the same global (the calm) ------------------------
edit("packages/preview/walk_preview.py", [
('''{rendering}[debug]
; Verbatim from export.py::_write_project_godot, and it must stay verbatim:
''',
'''{rendering}[shader_globals]
lf_wind={{"type": "vec3", "value": Vector3(1.5, 0, 0)}}

[debug]
; Verbatim from export.py::_write_project_godot, and it must stay verbatim:
'''),
])
print("lf sway applied")
