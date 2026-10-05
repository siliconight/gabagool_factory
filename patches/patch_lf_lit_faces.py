"""Level Factory 0.140.0: a lit face keeps its own UVs on a kit module.

Cold run 9152: Zoo 1.66.0 put each painted pane's cell on the street side --
measured -- and from the street every pane still read as flat beige with no
glow. Read headless on the walk copy, the pane material imported with
`uv1_triplanar true, uv1_world_triplanar true, uv1_scale 0.1856`: `_apply`
world-projects every material on a kit module, so the atlas was sampled by
world position and the mesh's UVs were ignored. See
`lf_lit_faces/CHANGELOG_0.140.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  assets/godot/zoo_worldskin.gd     LIT_FACE_SUFFIXES; `_apply` skips and
                                    counts them; the report says so
  tests/unit/glb_import_fixture.py  `spread_uv`, opt-in
Copies the test; CHANGELOG and VERSION.

    python patch_lf_lit_faces.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
LF = HERE.parent / "level_factory"
SRC = HERE / "lf_lit_faces"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


CONST_OLD = '''const KIT_PREFIXES: Array = ["wall_", "wallEnd_", "window_", "doorway_",
	"breach_"]
'''
CONST_NEW = '''const KIT_PREFIXES: Array = ["wall_", "wallEnd_", "window_", "doorway_",
	"breach_"]

## A LIT FACE IS ARTWORK MAPPED BY ITS UVs (0.140.0). A material named with
## one of these suffixes -- Lux's emissive-binder contract, the same list as
## `lux_emissive_binder.gd` SUFFIXES -- is never world-projected by `_apply`.
## Every kit material was a tiling skin until Zoo 1.64.0 painted the Empties'
## window panes into one atlas whose cell is picked by the pane's UVs; world
## projection threw those UVs away, and cold run 9152 showed every pane as
## flat frame-paint beige with no glow, its material imported with
## `uv1_world_triplanar true` (`patches/lf_empties/pane_census.gd`).
const LIT_FACE_SUFFIXES: Array = ["_Lens", "_Diffuser", "_Face"]
'''

HELPER_ANCHOR = '''func _apply(n: Node, seen: Dictionary) -> Array:
	var changed: int = 0
	var no_density: int = 0
'''
HELPER_NEW = '''func _is_lit_face(bm: BaseMaterial3D) -> bool:
	var nm: String = String(bm.resource_name)
	if not nm.begins_with("M_"):
		return false
	for s in LIT_FACE_SUFFIXES:
		if nm.ends_with(String(s)):
			return true
	return false


func _apply(n: Node, seen: Dictionary) -> Array:
	var changed: int = 0
	var no_density: int = 0
	var lit_faces: int = 0
'''

SKIP_OLD = '''			var key: int = bm.get_instance_id()
			if seen.has(key):
				continue
			seen[key] = true
			var density: float = _uv_density(mesh, i)
'''
SKIP_NEW = '''			var key: int = bm.get_instance_id()
			if seen.has(key):
				continue
			seen[key] = true
			# a lit face's picture IS its UVs: left alone, and counted
			if _is_lit_face(bm):
				lit_faces += 1
				continue
			var density: float = _uv_density(mesh, i)
'''

SUM_OLD = '''	for c in n.get_children():
		var sub: Array = _apply(c, seen)
		changed += int(sub[0])
		no_density += int(sub[1])
	return [changed, no_density]
'''
SUM_NEW = '''	for c in n.get_children():
		var sub: Array = _apply(c, seen)
		changed += int(sub[0])
		no_density += int(sub[1])
		lit_faces += int(sub[2])
	return [changed, no_density, lit_faces]
'''

REPORT_OLD = '''	var counts: Array = _apply(scene, seen)
	changed = counts[0]
	no_density = counts[1]
	print("[worldskin] %s  %d material(s) world-projected, %d without a UV density"
		% [base, changed, no_density])
'''
REPORT_NEW = '''	var counts: Array = _apply(scene, seen)
	changed = counts[0]
	no_density = counts[1]
	print("[worldskin] %s  %d material(s) world-projected, %d without a UV density, %d lit face(s) left on their own UVs"
		% [base, changed, no_density, int(counts[2])])
'''

FIX_SIG_OLD = '''def build_glb(meshes, materials=()) -> bytes:
'''
FIX_SIG_NEW = '''def build_glb(meshes, materials=(), spread_uv=False) -> bytes:
'''
FIX_UV_OLD = '''    uvs = b"".join(struct.pack("<2f", *_UV) for _ in _CORNERS)
'''
FIX_UV_NEW = '''    # `spread_uv` (0.140.0): UVs that follow x and y, so `_uv_density` reads
    # 1 texel-unit a metre and `_apply`'s world projection is exercised. Off,
    # every corner shares one UV and every fixture written before is unchanged.
    uvs = b"".join(struct.pack("<2f", *((c[0] + 0.5, c[1] + 0.5) if spread_uv else _UV))
                   for c in _CORNERS)
'''
FIX_WRITE_OLD = '''def write_glb(path, meshes, materials=()):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_glb(meshes, materials))
    return path
'''
FIX_WRITE_NEW = '''def write_glb(path, meshes, materials=(), spread_uv=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_glb(meshes, materials, spread_uv=spread_uv))
    return path
'''


def main():
    assert (LF / "VERSION").read_text(encoding="utf-8").strip() == "0.139.0"
    _edit(LF / "assets" / "godot" / "zoo_worldskin.gd",
          [(CONST_OLD, CONST_NEW), (HELPER_ANCHOR, HELPER_NEW), (SKIP_OLD, SKIP_NEW),
           (SUM_OLD, SUM_NEW), (REPORT_OLD, REPORT_NEW)])
    _edit(LF / "tests" / "unit" / "glb_import_fixture.py",
          [(FIX_SIG_OLD, FIX_SIG_NEW), (FIX_UV_OLD, FIX_UV_NEW), (FIX_WRITE_OLD, FIX_WRITE_NEW)])
    shutil.copyfile(SRC / "test_worldskin_lit_faces.py",
                    LF / "tests" / "unit" / "test_worldskin_lit_faces.py")
    ch = LF / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.140.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (LF / "VERSION").write_text("0.140.0", encoding="utf-8", newline="\n")
    print("applied Level Factory 0.140.0")


if __name__ == "__main__":
    main()
