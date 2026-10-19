"""Level Factory 0.217.0: a vault ledge is skinned -- the building's drywall, then any wall, then its floor.

FOUND re-measuring roadmap 169 on cold run 9321's package (`greybox_skin_scan.json`): with the ladders skinned,
the only greybox left in the themed package was three `VAULTLEDGE_n` surfaces on `gb_floor`, 49.7 m2 -- two on
deli_a01's ground floor and one beside the office's reception desk. Deli Counter builds a waist-height ledge
inside a floor (`deli_counter.py` `_vault_ledges`) as a box in the FLOOR role, so it arrives in `gb_floor`, and
no kit module stands in for it: like a slab, a flight and a ladder, it is the base's own geometry, and
`zoo_worldskin.gd` dresses those with one pass each. Nothing dressed a ledge. 204 of Deli Counter's 446 specs
declare one, so most levels ship them grey; the greybox census reports them and does not refuse, because it
refuses on slabs only.

WHAT IT WEARS IS A CALL, made 2026-10-19 under the walker's standing instruction to make decisions that can be
changed later: a ledge inside a floor reads as a short partition, so it takes the building's interior DRYWALL
wall first (`wall_*_mdrywall*`; deli_a01, office and pharmacy_a01 on 9321 each ship
`wall_delco_1997_02_w200_mdrywall.glb`), then any wall module, then the floor family the slabs take, so it is
never left grey while the building has a kit. The list, `VAULT_LEDGE_FAMILIES`, is the dial.

What it changes (anchored; each file pinned by hash; nothing written on a miss; LF-safe):
  * assets/godot/zoo_worldskin.gd -- the constants; `_family_material` takes an optional `contains` filter on
    the file name (default "", so the stair and slab passes are untouched); `_skin_vault_ledges`,
    `_is_visual_vault_ledge`, `_assign_vault_ledges` on the slab pass's shape (one definition counts and
    dresses); one log line after the ladders'.
  * tests/unit/test_worldskin_crt_motion.py -- `_assign_vault_ledges` joins MATERIAL_REPLACERS, with its reason.
  * tests/unit/test_worldskin_vault_ledges.py (new, 8; through a real Godot import): drywall first, any wall
    without it, the floor family without a wall, the collider untouched, a base with no ledge says so, no art
    and no family are errors, and the call is recorded as one that can change.
  * VERSION 0.216.1 -> 0.217.0, CHANGELOG.

NOT HERE: platform decks (`PLATFORM_<id>`, also the floor role) are the same shape of defect in the one spec
that has one (warehouse.json); no package carrying one has been measured, so the pass does not claim them.

    python patches/patch_lf_vault_ledge_skin.py --tests   # the new test file only (prove it fails first)
    python patches/patch_lf_vault_ledge_skin.py           # everything
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LF = ROOT / "level_factory"
SKIN = LF / "assets" / "godot" / "zoo_worldskin.gd"
CRT = LF / "tests" / "unit" / "test_worldskin_crt_motion.py"
SHA = {SKIN: "c83929f35949fcb3", CRT: "e32b8719f4bab978"}

CONST_OLD = r'''const SLAB_REVEAL_FAMILY: Array = ["floor_", "roof_"]
'''
CONST_NEW = r'''const SLAB_REVEAL_FAMILY: Array = ["floor_", "roof_"]

## VAULT LEDGES (0.217.0). Deli Counter builds a waist-height ledge inside a
## floor (`_vault_ledges`: `VAULTLEDGE_<n>`) as a box in the FLOOR role, so it
## arrived in `gb_floor`. No kit module stands in for it -- it is the base's
## own geometry, as a slab, a flight and a ladder are -- and on cold run 9321's
## package three of them, 49.7 m2, were the only greybox left in a themed
## build. 204 of Deli Counter's 446 specs declare one.
##
## WHAT IT WEARS IS A CALL, made 2026-10-19 and meant to be changed: a ledge
## inside a floor reads as a short partition, so it takes the building's
## interior DRYWALL wall first (`wall_*_mdrywall*`, which each mission building
## on cold run 9321 ships), then any wall module, then the floor family the
## slabs take, so it is never left grey while the building has a kit. The list
## is the dial: each row is [file prefix, a substring the file name carries].
const VAULT_LEDGE_PREFIX: String = "VAULTLEDGE_"
const VAULT_LEDGE_FAMILIES: Array = [["wall_", "_mdrywall"], ["wall_", ""], ["floor_", ""]]
'''

FAMILY_OLD = r'''func _family_material(art: String, dir: DirAccess, families: Array,
		part: String) -> Array:
	var files: PackedStringArray = dir.get_files()
	files.sort()
	for fam in families:
		for f in files:
			if not f.ends_with(".glb") or not f.begins_with(String(fam)):
				continue
'''
FAMILY_NEW = r'''func _family_material(art: String, dir: DirAccess, families: Array,
		part: String, contains: String = "") -> Array:
	var files: PackedStringArray = dir.get_files()
	files.sort()
	for fam in families:
		for f in files:
			if not f.ends_with(".glb") or not f.begins_with(String(fam)):
				continue
			# a family narrowed by a substring of the file's name (0.217.0: the
			# vault ledge's drywall, `wall_*_mdrywall*`); "" narrows nothing
			if contains != "" and not f.contains(contains):
				continue
'''

LOG_OLD = r'''				% [base, int(ld["ladder_surfaces"]), int(ld["ladder_meshes"]),
					int(ld["exterior_meshes"]), int(ld["unskinned_meshes"]),
					String(ld["note"])])
			return scene
'''
LOG_NEW = r'''				% [base, int(ld["ladder_surfaces"]), int(ld["ladder_meshes"]),
					int(ld["exterior_meshes"]), int(ld["unskinned_meshes"]),
					String(ld["note"])])
			var vl: Dictionary = _skin_vault_ledges(scene, get_source_file().get_base_dir())
			print("[worldskin] %s  vault ledges: %d surface(s) skinned on %d mesh(es), %d mesh(es) left flat%s"
				% [base, int(vl["ledge_surfaces"]), int(vl["ledge_meshes"]),
					int(vl["unskinned_meshes"]), String(vl["note"])])
			return scene
'''

TAIL_OLD = r'''	return [fs, fm, seen, flat, ext_n]
'''
TAIL_NEW = r'''	return [fs, fm, seen, flat, ext_n]


## Skin every vault ledge in the base (0.217.0; see VAULT_LEDGE_FAMILIES).
func _skin_vault_ledges(scene: Node, base_dir: String) -> Dictionary:
	var out: Dictionary = {"ledge_surfaces": 0, "ledge_meshes": 0,
		"unskinned_meshes": 0, "note": ""}
	# One definition of a visual ledge for the census and the work, as the
	# slab pass has: a null material counts instead of assigning.
	var present: Array = _assign_vault_ledges(scene, null)
	var ledges: int = int(present[2])
	if ledges == 0:
		out["note"] = "; no vault ledge in this base, nothing to skin"
		return out
	var art: String = base_dir.path_join("art").path_join("zoo")
	var dir := DirAccess.open(art)
	if dir == null:
		out["unskinned_meshes"] = ledges
		out["note"] = "; NO art/zoo BESIDE THE BASE -- %d vault ledge mesh(es) left in the greybox material" % ledges
		push_error("[worldskin] %s%s" % [get_source_file(), String(out["note"])])
		return out
	var found: Array = []
	for row in VAULT_LEDGE_FAMILIES:
		found = _family_material(art, dir, [String(row[0])], "vault_ledge", String(row[1]))
		if not found.is_empty():
			break
	if found.is_empty():
		out["unskinned_meshes"] = ledges
		# `%` binds tighter than `+`, so the formatted piece is built whole.
		out["note"] = ("; NO MODULE UNDER art/zoo IN FAMILIES %s -- %d vault ledge mesh(es) left in the greybox material"
			% [str(VAULT_LEDGE_FAMILIES), ledges])
		push_error("[worldskin] %s%s" % [get_source_file(), String(out["note"])])
		return out
	var counts: Array = _assign_vault_ledges(scene, found[0] as Material)
	out["ledge_surfaces"] = int(counts[0])
	out["ledge_meshes"] = int(counts[1])
	out["unskinned_meshes"] = int(counts[3])
	out["note"] = "; from %s" % String(found[1])
	return out


## A mesh named for a vault ledge that is DRAWN rather than collided with.
## Godot's `-convcolonly` import deletes the collider's visual, so a collider
## never reaches the pass; the `col` test is a second line over that.
func _is_visual_vault_ledge(nm: String) -> bool:
	return nm.begins_with(VAULT_LEDGE_PREFIX) and not nm.contains(SLAB_COLLISION_MARK)


## Assign the ledge material; a null `mat` counts instead (see `_assign_slabs`).
##
## Returns [ledge_surfaces, ledge_meshes, ledge_seen, unskinned_meshes].
func _assign_vault_ledges(n: Node, mat: Material) -> Array:
	var fs: int = 0
	var fm: int = 0
	var seen: int = 0
	var flat: int = 0
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi != null and mi.mesh != null and _is_visual_vault_ledge(String(mi.name)):
		seen += 1
		if mat == null:
			flat += 1
		else:
			for i in range(mi.mesh.get_surface_count()):
				mi.mesh.surface_set_material(i, mat)
				fs += 1
			fm += 1
	for c in n.get_children():
		var sub: Array = _assign_vault_ledges(c, mat)
		fs += int(sub[0])
		fm += int(sub[1])
		seen += int(sub[2])
		flat += int(sub[3])
	return [fs, fm, seen, flat]
'''

CRT_OLD = r'''#: building's own metal on a ladder's rails and rungs as the stairs and slabs
#: passes put its floor on theirs.
MATERIAL_REPLACERS = {"_assign_stairs", "_assign_slabs", "_shutters", "_turning_parts", "_sway_crowns",
                      "_assign_ladders", "_signal_lenses"}
'''
CRT_NEW = r'''#: building's own metal on a ladder's rails and rungs as the stairs and slabs
#: passes put its floor on theirs.
#: 0.217.0: `_assign_vault_ledges`, the vault ledge skin, chosen for the slab
#: pass's reason: Deli Counter's ledge is a greybox box with no UVs, so its
#: `gb_floor` is swapped for the building's drywall, world-triplanar
#: (`test_worldskin_vault_ledges.py`).
MATERIAL_REPLACERS = {"_assign_stairs", "_assign_slabs", "_shutters", "_turning_parts", "_sway_crowns",
                      "_assign_ladders", "_signal_lenses", "_assign_vault_ledges"}
'''

TEST = r'''"""A vault ledge is skinned: the building's drywall, then any wall, then its floor (0.217.0).

Deli Counter builds a waist-height ledge inside a floor (`_vault_ledges`, `VAULTLEDGE_<n>`) as a box in the
FLOOR role, so it shipped in `gb_floor`: on the factory's cold run 9321 the only greybox left in the themed
package was three of them, 49.7 m2. No kit module stands in for one, so -- like a slab, a flight and a
ladder -- the base's own pass has to dress it.

WHAT IT WEARS IS A CALL, made 2026-10-19 and meant to be changed (`VAULT_LEDGE_FAMILIES`): a ledge inside a
floor reads as a short partition, so the building's interior drywall wall first, then any wall, then the floor
family the slabs take.

These run the real script through a real Godot import, as `test_worldskin_ladders.py` does, and are skipped
where no Godot is installed. `LF_GODOT` overrides, then `DC_GODOT`, then `LOT_GODOT`, then the usual Windows
install path, then PATH.

Run:  python -m pytest tests/unit/test_worldskin_vault_ledges.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from glb_import_fixture import write_glb  # noqa: E402

WORLDSKIN = ROOT / "assets" / "godot" / "zoo_worldskin.gd"

#: The names Deli Counter emits (`deli_counter.py` `_vault_ledges`): the visual box, and its convex collider,
#: whose visual Godot's `-convcolonly` convention deletes on import.
LEDGE = "VAULTLEDGE_0"
LEDGE_2 = "VAULTLEDGE_1"
COLLIDER = "VAULTLEDGE_0-convcolonly"
#: The modules a mission building ships beside its base (on cold run 9321, deli_a01, office and pharmacy_a01
#: each carry `wall_delco_1997_02_w200_mdrywall.glb`).
DRYWALL = ("wall_delco_1997_02_w200_mdrywall.glb", "M_Skin_drywall_delco_1997")
BRICK = ("wall_delco_1997_01_w200_mbrick.glb", "M_Skin_brick_delco_1997")
FLOOR = ("floor_delco_1997_05_w1000_d700.glb", "M_Skin_concrete_delco_1997")
PROP = ("prop_bench_delco_1997_01_w180.glb", "M_Skin_wood_delco_1997")

_PROJECT = """\
config_version=5

[application]
config/name="worldskin vault ledge fixture"

[rendering]
renderer/rendering_method="gl_compatibility"

[importer_defaults]

scene={
"import_script/path": "res://zoo_worldskin.gd"
}
"""


def _godot() -> str | None:
    for env in ("LF_GODOT", "DC_GODOT", "LOT_GODOT"):
        p = os.environ.get(env)
        if p and Path(p).is_file():
            return p
    usual = Path("C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe")
    if usual.is_file():
        return str(usual)
    return shutil.which("godot")


godot_required = pytest.mark.skipif(
    _godot() is None, reason="no Godot binary; this test imports a real package")


def _project(tmp_path: Path, *, base_meshes, modules=(DRYWALL, BRICK, FLOOR), art=True) -> Path:
    proj = tmp_path / "pkg"
    proj.mkdir()
    (proj / "project.godot").write_text(_PROJECT, encoding="utf-8")
    (proj / "zoo_worldskin.gd").write_text(WORLDSKIN.read_text(encoding="utf-8"), encoding="utf-8")
    write_glb(proj / "site_base.glb", base_meshes, [("gb_floor", False)])
    if art:
        for fname, mat in modules:
            write_glb(proj / "art" / "zoo" / fname, [("part", 0)], [(mat, True)])
    return proj


def _import(proj: Path) -> str:
    out = subprocess.run([_godot(), "--headless", "--path", str(proj), "--import"],
                         capture_output=True, text=True, timeout=300)
    return out.stdout + out.stderr


def _ledge_line(log: str) -> str:
    lines = [ln for ln in log.splitlines()
             if ln.startswith("[worldskin] site_base.glb") and "vault ledges:" in ln]
    # An unrecognised shape FAILS rather than passing.
    assert len(lines) == 1, f"expected one vault ledge line, got {lines!r}\n{log}"
    return lines[0]


@godot_required
def test_a_ledge_takes_the_buildings_drywall(tmp_path):
    """FAILS BEFORE THIS PASS: nothing looked at a vault ledge, so it shipped in gb_floor."""
    proj = _project(tmp_path, base_meshes=[(LEDGE, 0), (LEDGE_2, 0)])
    line = _ledge_line(_import(proj))
    assert "2 surface(s) skinned on 2 mesh(es)" in line, line
    assert "0 mesh(es) left flat" in line, line
    assert "from %s" % DRYWALL[0] in line, line


@godot_required
def test_no_drywall_takes_any_wall(tmp_path):
    proj = _project(tmp_path, base_meshes=[(LEDGE, 0)], modules=(BRICK, FLOOR))
    line = _ledge_line(_import(proj))
    assert "1 surface(s) skinned on 1 mesh(es)" in line, line
    assert "from %s" % BRICK[0] in line, line


@godot_required
def test_no_wall_takes_the_floor_family(tmp_path):
    proj = _project(tmp_path, base_meshes=[(LEDGE, 0)], modules=(FLOOR,))
    line = _ledge_line(_import(proj))
    assert "1 surface(s) skinned on 1 mesh(es)" in line, line
    assert "from %s" % FLOOR[0] in line, line


@godot_required
def test_the_collider_is_not_skinned(tmp_path):
    proj = _project(tmp_path, base_meshes=[(LEDGE, 0), (COLLIDER, 0)])
    line = _ledge_line(_import(proj))
    assert "1 surface(s) skinned on 1 mesh(es)" in line, line


@godot_required
def test_a_base_with_no_ledge_is_a_no_op_that_says_which(tmp_path):
    proj = _project(tmp_path, base_meshes=[("slab_0_t0_0", 0)])
    line = _ledge_line(_import(proj))
    assert "no vault ledge in this base, nothing to skin" in line, line
    assert "0 mesh(es) left flat" in line, line


@godot_required
def test_no_art_beside_the_base_is_an_error_not_a_note(tmp_path):
    proj = _project(tmp_path, base_meshes=[(LEDGE, 0)], art=False)
    log = _import(proj)
    line = _ledge_line(log)
    assert "NO art/zoo BESIDE THE BASE" in line, line
    assert "1 mesh(es) left flat" in line, line
    assert any("ERROR" in ln and "vault ledge" in ln and "NO art/zoo BESIDE THE BASE" in ln
               for ln in log.splitlines()), log


@godot_required
def test_no_module_in_any_family_is_an_error_not_a_note(tmp_path):
    proj = _project(tmp_path, base_meshes=[(LEDGE, 0)], modules=(PROP,))
    log = _import(proj)
    line = _ledge_line(log)
    assert "NO MODULE UNDER art/zoo IN FAMILIES" in line, line
    assert "1 mesh(es) left flat" in line, line
    assert any("ERROR" in ln and "vault ledge" in ln for ln in log.splitlines()), log


def test_the_call_is_recorded_as_one_that_can_change():
    """Drywall first is a call, not a measurement. The source says so, so a reader moves the dial rather than
    'fixing' a choice whose reason they cannot find."""
    src = WORLDSKIN.read_text(encoding="utf-8")
    assert 'const VAULT_LEDGE_FAMILIES: Array = [["wall_", "_mdrywall"], ["wall_", ""], ["floor_", ""]]' in src
    assert "meant to be changed" in src
'''

CHANGELOG = '''## [0.217.0] - a vault ledge is skinned: the building's drywall, then any wall, then its floor

**Found re-measuring factory roadmap 169 on cold run 9321's package.** With the ladders skinned, the only greybox
left in the themed package was three `VAULTLEDGE_n` surfaces on `gb_floor`, 49.7 m2. Deli Counter builds a
waist-height ledge inside a floor (`_vault_ledges`) as a box in the floor role, no kit module stands in for it,
and `zoo_worldskin.gd` dresses the base's own geometry one pass per kind -- slabs, flights, ladders -- with none
for a ledge. 204 of Deli Counter's 446 specs declare one. The greybox census reported them and did not refuse.

**What it wears is a call, made 2026-10-19 and meant to be changed.** A ledge inside a floor reads as a short
partition, so `VAULT_LEDGE_FAMILIES` tries the building's interior drywall wall first (`wall_*_mdrywall*`; every
mission building on 9321 ships one), then any wall module, then the floor family the slabs take.

### Added
- `_skin_vault_ledges`, `_is_visual_vault_ledge`, `_assign_vault_ledges` on the slab pass's shape, and one
  `[worldskin] ... vault ledges:` line after the ladders'. No art, or no module in any family, is a `push_error`
  that says how many ledges stay grey.
- `_family_material` takes an optional `contains` filter on the file name; the default narrows nothing, so the
  stair and slab passes are unchanged.
- `tests/unit/test_worldskin_vault_ledges.py` (8, all fail on 0.216.1; through a real Godot import), and
  `_assign_vault_ledges` joins `test_worldskin_crt_motion`'s MATERIAL_REPLACERS with its reason.

### Not here
Platform decks (`PLATFORM_<id>`) are the same shape of defect, in the one spec that has one (warehouse.json). No
package carrying one has been measured, so the pass does not claim them.

'''


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(path):
    raw = path.read_bytes()
    assert b"\r\n" not in raw, f"{path.name} is LF"
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == SHA[path], (f"{path.name} is not the file this patch read", got)
    return raw.decode("utf-8")


def write_tests():
    p = LF / "tests" / "unit" / "test_worldskin_vault_ledges.py"
    assert not p.exists(), f"{p.name} exists"
    p.write_text(TEST, encoding="utf-8", newline="\n")
    print("wrote level_factory/tests/unit/test_worldskin_vault_ledges.py")


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    skin = _read(SKIN)
    assert "VAULT_LEDGE_PREFIX" not in skin, "already applied"
    skin = _once(skin, CONST_OLD, CONST_NEW, "the slab family constant")
    skin = _once(skin, FAMILY_OLD, FAMILY_NEW, "_family_material")
    skin = _once(skin, LOG_OLD, LOG_NEW, "the ladder log line")
    skin = _once(skin, TAIL_OLD, TAIL_NEW, "_assign_ladders' return")
    crt = _once(_read(CRT), CRT_OLD, CRT_NEW, "MATERIAL_REPLACERS")
    v = LF / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "0.216.1", v.read_text(encoding="utf-8")
    cl = LF / "CHANGELOG.md"
    rawc = cl.read_bytes()
    assert b"\r\n" not in rawc, "CHANGELOG.md is LF"
    text = rawc.decode("utf-8")
    assert text.startswith("## [0.216.1]"), text[:40]
    SKIN.write_bytes(skin.encode("utf-8"))
    CRT.write_bytes(crt.encode("utf-8"))
    v.write_text("0.217.0", encoding="utf-8")
    cl.write_bytes((CHANGELOG + text).encode("utf-8"))
    write_tests()
    print("Level Factory 0.217.0 applied: the vault ledge pass, its test, MATERIAL_REPLACERS, VERSION, CHANGELOG")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
