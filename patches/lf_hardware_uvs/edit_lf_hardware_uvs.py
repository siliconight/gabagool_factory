"""Level Factory 0.242.0 on a clone: a door's hardware keeps its own UVs on a kit module, so it keys like the stoop
railing it is painted to match and the Empties' per-side merge makes the two one mesh.

    python edit_lf_hardware_uvs.py <clone>

Anchored; refuses on a miss. Edits assets/godot/zoo_worldskin.gd; writes tests/unit/test_worldskin_hardware.py.
VERSION and CHANGELOG are the generator's.
"""
import pathlib
import sys

C = pathlib.Path(sys.argv[1])
p = C / "assets" / "godot" / "zoo_worldskin.gd"
raw = p.read_bytes()
assert b"\r\n" not in raw, "the clone's worldskin is LF"
t = raw.decode("utf-8")
assert "AUTHORED_UV_PARTS" not in t

EDITS = [
    ('const LIT_FACE_SUFFIXES: Array = ["_Lens", "_Diffuser", "_Face"]\n',
     'const LIT_FACE_SUFFIXES: Array = ["_Lens", "_Diffuser", "_Face"]\n'
     '\n'
     '## A DOOR\'S HARDWARE KEEPS ITS OWN UVs (0.242.0). A mesh whose node name ends\n'
     '## with one of these is never world-projected by `_apply`. Zoo 1.127.0 paints\n'
     '## a door\'s knob and plate (`{root}_LeafHardware`, `_arch.py`) the stoop\n'
     '## railing\'s black iron so that on a front the two are one material -- but the\n'
     '## knob arrives inside a `doorway_` kit module and the railing in a `prop_`, so\n'
     '## this pass projected the one and left the other, and `merge_empties.gd`, whose\n'
     '## key reads `uv1_scale` and both triplanar flags, kept them apart: cold run\n'
     '## 9392\'s `blocker_0` carried two meshes of `M_Skin_metal_painted_delco_1997_\n'
     '## 0f0f11` on its street side, `uv1_scale (0.833, 0.833, 0.833) triplanar true`\n'
     '## and `(0.833, 0.833, 1.0) triplanar false` (the factory\'s\n'
     '## `docs/cold_runs/cold_9392/meshes_blocker0_9392.out.txt`). A 6 cm knob shows\n'
     '## no tile period to keep continuous. A part whose material another mesh in the\n'
     '## same module also wears follows whichever mesh `_apply` meets first.\n'
     'const AUTHORED_UV_PARTS: Array = ["_LeafHardware"]\n'),
    ('\tvar mi: MeshInstance3D = n as MeshInstance3D\n'
     '\tif mi != null and mi.mesh != null:\n'
     '\t\tvar mesh: Mesh = mi.mesh\n',
     '\tvar mi: MeshInstance3D = n as MeshInstance3D\n'
     '\tvar authored_part: bool = false\n'
     '\tif mi != null:\n'
     '\t\tfor s in AUTHORED_UV_PARTS:\n'
     '\t\t\tif String(mi.name).ends_with(String(s)):\n'
     '\t\t\t\tauthored_part = true\n'
     '\tif authored_part and mi.mesh != null:\n'
     '\t\thardware += 1\n'
     '\telif mi != null and mi.mesh != null:\n'
     '\t\tvar mesh: Mesh = mi.mesh\n'),
    ('\tvar lit_faces: int = 0\n'
     '\tvar mi: MeshInstance3D = n as MeshInstance3D\n',
     '\tvar lit_faces: int = 0\n'
     '\tvar hardware: int = 0\n'
     '\tvar mi: MeshInstance3D = n as MeshInstance3D\n'),
    ('\t\tlit_faces += int(sub[2])\n'
     '\treturn [changed, no_density, lit_faces]\n',
     '\t\tlit_faces += int(sub[2])\n'
     '\t\thardware += int(sub[3])\n'
     '\treturn [changed, no_density, lit_faces, hardware]\n'),
    ('\tprint("[worldskin] %s  %d material(s) world-projected, %d without a UV density, %d lit face(s) left on their own UVs"\n'
     '\t\t% [base, changed, no_density, int(counts[2])])\n',
     '\tprint(("[worldskin] %s  %d material(s) world-projected, %d without a UV density, %d lit face(s) left on their own UVs"\n'
     '\t\t+ ", %d hardware part(s) left on their own UVs")\n'
     '\t\t% [base, changed, no_density, int(counts[2]), int(counts[3])])\n'),
]
for old, new in EDITS:
    assert t.count(old) == 1, ("anchor", t.count(old), old[:80])
    t = t.replace(old, new)
p.write_bytes(t.encode("utf-8"))

test = C / "tests" / "unit" / "test_worldskin_hardware.py"
assert not test.exists()
src = (C / "tests" / "unit" / "test_worldskin_lit_faces.py").read_text(encoding="utf-8")
head_end = src.index("MODULE = ")
helpers = src[src.index("from __future__"):head_end]
helpers = helpers.replace('config/name="worldskin lit-face fixture"', 'config/name="worldskin hardware fixture"')
assert 'config/name="worldskin hardware fixture"' in helpers
test.write_text('''"""A door's hardware keeps its own UVs on a kit module (0.242.0).

Zoo 1.127.0 paints a door's knob and plate (`<root>_LeafHardware`) the stoop
railing's black iron so that on a front the two are one material and one mesh.
They were not: the knob arrives in a `doorway_` kit module, which `_apply`
world-projects, and the railing in a `prop_`, which it leaves alone, and the
Empties' per-side merge keys on `uv1_scale` and both triplanar flags -- cold
run 9392's `blocker_0` carried the iron twice on its street side (the
factory's `docs/cold_runs/cold_9392/meshes_blocker0_9392.out.txt`). A mesh
named for one of `AUTHORED_UV_PARTS` is never projected, and the report
counts it.

These run the real script through a real Godot import over a generated
module, as `test_worldskin_lit_faces.py` does. Skipped where no Godot is
installed.
"""
''' + helpers + '''MODULE = "doorway_delco_1997_01_w100_mbrick_orange_enavy_o1d20e5.glb"


def _import(tmp_path: Path, meshes, materials) -> str:
    proj = tmp_path / "pkg"
    proj.mkdir()
    (proj / "project.godot").write_text(_PROJECT, encoding="utf-8")
    (proj / "zoo_worldskin.gd").write_text(WORLDSKIN.read_text(encoding="utf-8"), encoding="utf-8")
    write_glb(proj / MODULE, meshes, materials, spread_uv=True)
    out = subprocess.run([_godot(), "--headless", "--path", str(proj), "--import"],
                         capture_output=True, text=True, timeout=300)
    log = out.stdout + out.stderr
    lines = [ln for ln in log.splitlines()
             if ln.startswith(f"[worldskin] {MODULE}") and "world-projected" in ln]
    # an unrecognised shape FAILS: a missing line means the pass did not run
    assert len(lines) == 1, f"expected one report line, got {lines!r}\\n{log}"
    return lines[0]


def _counts(line: str) -> tuple:
    projected = int(re.search(r"(\\d+) material\\(s\\) world-projected", line).group(1))
    m = re.search(r"(\\d+) hardware part\\(s\\) left on their own UVs", line)
    assert m, f"no hardware count in the report: {line}"
    return projected, int(m.group(1))


@godot_required
def test_the_knob_keeps_its_uvs_and_the_leaf_is_still_projected(tmp_path):
    """FAILS ON 0.241.0: both world-projected, and no hardware count."""
    line = _import(tmp_path, [("Doorway_Leaf", 0), ("Doorway_LeafHardware", 1)],
                   [("M_Skin_wood_panel_delco_1997", True), ("M_Skin_metal_painted_delco_1997_0f0f11", True)])
    assert _counts(line) == (1, 1), line


@godot_required
def test_a_doorway_with_no_hardware_is_projected_as_before(tmp_path):
    """The control: a leaf alone is world-projected exactly as it was."""
    line = _import(tmp_path, [("Doorway_Leaf", 0)], [("M_Skin_wood_panel_delco_1997", True)])
    assert _counts(line) == (1, 0), line


def test_the_part_is_zoo_s_knob():
    """One name, two readers: the node Zoo builds a door's hardware as is the
    one this leaves on its UVs. Renamed on one side and not the other, the knob
    is projected again and the front is two meshes of one iron."""
    src = WORLDSKIN.read_text(encoding="utf-8")
    assert 'const AUTHORED_UV_PARTS: Array = ["_LeafHardware"]' in src
    arch = "zoo_keeper/recipes/_arch.py"
    zoo = sibling_repo("zoo", marker=arch)
    if zoo is not None:
        assert 'f"{root}_LeafHardware"' in (zoo / arch).read_text(encoding="utf-8")
''', encoding="utf-8", newline="\n")
print("edited zoo_worldskin.gd (%d edits); wrote %s" % (len(EDITS), test.name))
