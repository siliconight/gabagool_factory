"""Level Factory 0.127.0: screens that run -- the import gives Zoo's shutters a clock.

The walker, 2026-10-02: the lit screens are "just fixed with nothing
dynamic/alive about them", and of four steps toward levels that feel alive,
the first: "screens that run". Zoo 1.45.0 ships SHUTTERS on the ATM's and
the video poker's screens -- black quads a hair proud of the picture, each
over one part of it, each with a schedule in its two UV sets -- on a
material named `M_Shutter_Screen` that is exported fully transparent. This
is the clock.

  * `_shutters` in `zoo_worldskin.gd`, for every GLB: a surface wearing
    `M_Shutter_Screen` gets one shared ShaderMaterial. It is black where a
    shutter is closed and absent where it is open: open while
    `fract((TIME + UV2.y) / UV2.x + phase)` is in `[UV.x, UV.y)`. The phase
    is per INSTANCE (`NODE_POSITION_WORLD`), so two machines side by side do
    not deal in step, and every shutter of one machine shares it, so a hand
    is dealt in order.
  * `_vfd_motion`: the cash register's customer display, which is its own
    `M_Register_*_Face` material, gets the CRT pass's darkening overlay with
    a display's numbers -- a flicker and no roll, no snow. The register's
    picture is a price; a price does not animate, a tube display shimmers.

Both are import-time and both run off the shader's clock: no script runs in
the level, no light is added. Each costs one draw where it is seen.

Every edit asserts its anchor once and refuses to write on a miss.
"""
from __future__ import annotations

import os
import pathlib

LF = pathlib.Path(os.environ.get("LF_ROOT") or pathlib.Path(__file__).resolve().parents[1] / "level_factory")


def _edit(rel, pairs):
    p = LF / rel
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    s = raw.replace(b"\r\n", b"\n").decode("utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, f"{rel}: anchor found {n} times: {old[:60]!r}"
        s = s.replace(old, new)
    b = s.encode("utf-8")
    p.write_bytes(b.replace(b"\n", b"\r\n") if crlf else b)
    print("patched", rel)


SKIN = [
    ('''## One Shader per imported GLB rather than one per material: the five club
## materials would otherwise compile five identical pipelines.
var _motion_shader: Shader = null
''', '''## One Shader per imported GLB rather than one per material: the five club
## materials would otherwise compile five identical pipelines.
var _motion_shader: Shader = null

## SHUTTERS (0.127.0) -- screens that run. The walker, 2026-10-02: the lit
## screens are "just fixed with nothing dynamic/alive about them". Zoo 1.45.0
## stands black quads a hair proud of a lit screen, each over one part of its
## picture -- a dealt card, a line that takes its turn -- on a material of this
## name, exported fully transparent, with a schedule in the quad's UV sets:
##
##     UV  = (open_from, open_to)   fractions of the period
##     UV2 = (period_s, phase_s)
##
## The shutter is ABSENT while fract((TIME + phase_s) / period_s + instance)
## is in [open_from, open_to) and its CLOSED COLOUR otherwise: the base colour
## of the placeholder material Zoo exports, which is the screen's own
## background -- a hidden card is empty screen. (Black was the first cut and
## read as holes in the poker's blue tube.) The name BEGINS `SHUTTER_MATERIAL`
## and ends in that colour.
##
## THE INSTANCE TERM IS PER NODE, from NODE_POSITION_WORLD, as the CRT pass's
## is: two cabinets side by side do not deal in step, and every shutter of one
## cabinet is one mesh on one node, so one cabinet's cards still come up in
## order.
const SHUTTER_MATERIAL: String = "M_Shutter_Screen"

const SHUTTER_SHADER: String = """
shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, cull_back,
	shadows_disabled, fog_disabled;

uniform vec3 closed_color : source_color = vec3(0.0);

float shutter_hash(float x) {
	return fract(sin(x) * 43758.5453123);
}

void fragment() {
	float inst = shutter_hash(dot(NODE_POSITION_WORLD, vec3(12.9898, 78.233, 37.719)));
	float t = fract((TIME + UV2.y) / max(UV2.x, 0.001) + inst);
	float open = step(UV.x, t) * (1.0 - step(UV.y, t));
	ALBEDO = closed_color;
	ALPHA = 1.0 - open;
}
"""

## One Shader per imported GLB and one ShaderMaterial per placeholder: every
## shutter reads its own schedule off its own vertices, and the only thing
## set per material is the closed colour.
var _shutter_shader: Shader = null
var _shutter_materials: Dictionary = {}

## THE REGISTER'S DISPLAY (0.127.0). Zoo's cash register lights its customer
## display on a material of its own, `M_Register_<art>_Face`, and its picture
## is a price -- which does not animate. A vacuum-fluorescent display does
## shimmer, so it takes the CRT pass's overlay with a display's numbers: a
## two-rate flicker, no sync bar, no snow. Darkening only, for the CRT pass's
## reason.
const VFD_FACE_MARK: String = "Register_"
const VFD_FLICKER_DEPTH: float = 0.07
const VFD_FLICKER_HZ_A: float = 3.1
const VFD_FLICKER_HZ_B: float = 4.7
'''),
    ('''	var crt: int = _crt_motion(scene, {})
	if crt > 0:
		print("[worldskin] %s  %d CRT face(s) given a motion pass" % [base, crt])
''', '''	var crt: int = _crt_motion(scene, {})
	if crt > 0:
		print("[worldskin] %s  %d CRT face(s) given a motion pass" % [base, crt])
	# EVERY GLB, and before the kit branch for the CRT pass's reason: a
	# shutter arrives in a prop GLB.
	var shut: int = _shutters(scene)
	if shut > 0:
		print("[worldskin] %s  %d shutter surface(s) given their clock" % [base, shut])
	var vfd: int = _vfd_motion(scene, {})
	if vfd > 0:
		print("[worldskin] %s  %d register display(s) given a flicker" % [base, vfd])
'''),
    ('''func _is_tiled(base: String) -> bool:''', '''## Every surface wearing Zoo's shutter material gets the one shader that reads
## its schedule. The surface's own material is REPLACED, which the CRT pass
## must not do and this may: a shutter is not a lit face, Lux's power cut has
## no business with it, and its exported material is a transparent
## placeholder with nothing to keep.
##
## IDEMPOTENT on a re-import: a surface already wearing the shader is left.
func _shutters(n: Node) -> int:
	var count: int = 0
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi != null and mi.mesh != null:
		for i in range(mi.mesh.get_surface_count()):
			var mat: Material = mi.mesh.surface_get_material(i)
			if mat == null or not String(mat.resource_name).begins_with(SHUTTER_MATERIAL):
				continue
			var bm: BaseMaterial3D = mat as BaseMaterial3D
			if bm == null:
				continue                      # already the shader: a re-import
			mi.mesh.surface_set_material(i, _shutter_shader_material(bm))
			count += 1
	for c in n.get_children():
		count += _shutters(c)
	return count


func _shutter_shader_material(bm: BaseMaterial3D) -> ShaderMaterial:
	var key: int = bm.get_instance_id()
	if _shutter_materials.has(key):
		return _shutter_materials[key] as ShaderMaterial
	if _shutter_shader == null:
		_shutter_shader = Shader.new()
		_shutter_shader.code = SHUTTER_SHADER
	var sm: ShaderMaterial = ShaderMaterial.new()
	sm.shader = _shutter_shader
	sm.resource_name = String(bm.resource_name)
	var c: Color = bm.albedo_color
	sm.set_shader_parameter("closed_color", Color(c.r, c.g, c.b, 1.0))
	_shutter_materials[key] = sm
	return sm


## The register's lit display: the CRT pass's shape exactly -- the display's
## own StandardMaterial3D untouched, a darkening ShaderMaterial under it as
## `next_pass` -- with the roll and the snow at zero.
func _vfd_motion(n: Node, seen: Dictionary) -> int:
	var count: int = 0
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi != null and mi.mesh != null:
		for i in range(mi.mesh.get_surface_count()):
			var bm: BaseMaterial3D = mi.mesh.surface_get_material(i) as BaseMaterial3D
			if bm == null or seen.has(bm.get_instance_id()):
				continue
			seen[bm.get_instance_id()] = true
			if not _is_vfd_face(String(bm.resource_name)):
				continue
			if bm.next_pass != null:
				continue
			var sm: ShaderMaterial = _motion_material(bm)
			sm.set_shader_parameter("roll_depth", 0.0)
			sm.set_shader_parameter("noise_depth", 0.0)
			sm.set_shader_parameter("flicker_depth", VFD_FLICKER_DEPTH)
			sm.set_shader_parameter("flicker_hz_a", VFD_FLICKER_HZ_A)
			sm.set_shader_parameter("flicker_hz_b", VFD_FLICKER_HZ_B)
			bm.next_pass = sm
			count += 1
	for c in n.get_children():
		count += _vfd_motion(c, seen)
	return count


## `M_Register_<art>_Face`: the lit-face contract's prefix and suffix, and the
## register's own mark between them.
func _is_vfd_face(nm: String) -> bool:
	return nm.begins_with(CRT_FACE_PREFIX + VFD_FACE_MARK) and nm.ends_with(CRT_FACE_SUFFIX)


func _is_tiled(base: String) -> bool:'''),
]

TEST = '''"""Zoo's shutters get their clock at import, and the register's display a flicker (0.127.0).

The walker, 2026-10-02: the lit screens are "just fixed with nothing
dynamic/alive about them". Zoo 1.45.0 ships shutters -- black quads over
parts of a lit screen, a schedule in their UV sets, on a transparent material
named `M_Shutter_Screen` -- and this import gives them the shader that reads
it. The register's display, a lit face of its own, takes the CRT pass's
darkening overlay with no roll and no snow.

These read the GDScript rather than run it -- the unit suite has no Godot --
so they hold the SHAPE: the contract with Zoo (the name, which UV is which),
that a shutter only ever darkens, that the phase is per node, that both
passes run for every GLB before the kit branch, and that the register's own
material is not replaced. What the shader DOES is measured in frames; see the
0.127.0 changelog.

Run:  python -m pytest tests/unit/test_worldskin_shutters.py
"""
import re
from pathlib import Path

import pytest

from tests.siblings import sibling_repo

SCRIPT = (Path(__file__).resolve().parents[2]
          / "assets" / "godot" / "zoo_worldskin.gd")


def _src() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    m = re.search(r"^func %s\\(.*?(?=^func |\\Z)" % re.escape(name), src,
                  re.S | re.M)
    assert m, f"no func {name} in {SCRIPT.name}"
    return m.group(0)


def _shader(src: str) -> str:
    m = re.search(r'const SHUTTER_SHADER: String = """(.*?)"""', src, re.S)
    assert m, "no SHUTTER_SHADER block"
    return m.group(1)


def test_both_passes_run_for_every_glb_before_the_kit_branch():
    post = _func(_src(), "_post_import")
    for call in ("_shutters(scene", "_vfd_motion(scene"):
        at = post.find(call)
        assert at != -1, call
        assert at < post.find("is_kit") < post.find("return scene"), call


def test_the_name_is_zoo_s_when_zoo_is_beside_this_repo():
    src = _src()
    assert 'const SHUTTER_MATERIAL: String = "M_Shutter_Screen"' in src
    zoo = sibling_repo("zoo", marker="zoo_keeper/core/shutters.py")
    if zoo is None:
        pytest.skip("no Zoo with shutters beside this repo")
    their = (zoo / "zoo_keeper" / "core" / "shutters.py").read_text(encoding="utf-8")
    assert 'MATERIAL = "M_Shutter_Screen"' in their
    # which UV is which, as Zoo's contract spells it
    assert "UV  = (open_from, open_to)" in their and "UV2 = (period_s, phase_s)" in their


def test_the_shader_reads_the_schedule_and_only_ever_darkens():
    sh = _shader(_src())
    assert "render_mode unshaded, blend_mix" in sh and "depth_draw_never" in sh
    assert "shadows_disabled" in sh
    # open from UV.x to UV.y of a period UV2.x long, offset UV2.y
    assert "(TIME + UV2.y) / max(UV2.x" in sh
    assert "step(UV.x, t) * (1.0 - step(UV.y, t))" in sh
    # the closed colour where closed, absent where open; never emission
    assert "ALBEDO = closed_color;" in sh and "ALPHA = 1.0 - open;" in sh
    assert "uniform vec3 closed_color : source_color" in sh
    assert "EMISSION" not in sh
    # the depth test stays on: a shutter must lose it to a wall in front
    assert "depth_test_disabled" not in sh


def test_the_phase_is_per_node_so_two_machines_do_not_run_in_step():
    sh = _shader(_src())
    assert "NODE_POSITION_WORLD" in sh
    # and it is added to the whole machine's clock, not to one shutter's
    assert re.search(r"fract\\(\\(TIME \\+ UV2\\.y\\) / max\\(UV2\\.x, 0\\.001\\) \\+ inst\\)", sh)


def test_only_the_shutter_material_is_replaced_and_only_once():
    body = _func(_src(), "_shutters")
    assert "begins_with(SHUTTER_MATERIAL)" in body and "continue" in body
    assert "if bm == null:" in body                          # idempotent on re-import
    assert body.count("surface_set_material") == 1
    # the closed colour is the placeholder's own base colour
    make = _func(_src(), "_shutter_shader_material")
    assert "bm.albedo_color" in make and '"closed_color"' in make


def test_the_register_keeps_its_own_material_and_gets_no_roll_and_no_snow():
    vfd = _func(_src(), "_vfd_motion")
    assigns = re.findall(r"\\bbm\\.(\\w+)\\s*=[^=]", vfd)
    assert assigns == ["next_pass"], assigns
    assert "surface_set_material" not in vfd and "emission" not in vfd
    assert "if bm.next_pass != null:" in vfd
    assert 'set_shader_parameter("roll_depth", 0.0)' in vfd
    assert 'set_shader_parameter("noise_depth", 0.0)' in vfd
    face = _func(_src(), "_is_vfd_face")
    assert "CRT_FACE_PREFIX + VFD_FACE_MARK" in face and "CRT_FACE_SUFFIX" in face
    assert 'const VFD_FACE_MARK: String = "Register_"' in _src()
    # and it does not catch the CRTs, which have their own pass
    assert "CRT_Screen" not in "M_Register_x_Face"
'''


GUARD = [
    ('MATERIAL_REPLACERS = {"_assign_stairs", "_assign_slabs"}\n',
     '#:\n#: `_shutters` (0.127.0) WAS CHOSEN: what it replaces is Zoo\'s shutter\n#: placeholder -- black, fully transparent, named for the purpose, dressed\n#: from no pack and not a lit face -- and the shader it puts there is the\n#: only thing that ever draws it. It replaces nothing else: it asks for the\n#: placeholder\'s name first (`test_worldskin_shutters.py`).\nMATERIAL_REPLACERS = {"_assign_stairs", "_assign_slabs", "_shutters"}\n'),
]


def main():
    t = LF / "tests" / "unit" / "test_worldskin_shutters.py"
    assert not t.exists(), "already applied"
    _edit("assets/godot/zoo_worldskin.gd", SKIN)
    _edit("tests/unit/test_worldskin_crt_motion.py", GUARD)
    t.write_bytes(TEST.encode("utf-8"))
    print("wrote tests/unit/test_worldskin_shutters.py")


if __name__ == "__main__":
    main()
