"""Level Factory 0.138.0: an Empty's roof slab takes the roof family.

Cold run 9146's export was refused by `GREYBOX_SLAB_IN_A_THEMED_PACKAGE`:
588 slab surfaces in `gb_floor`, all of them the rowhome Empties'. Deli
Counter 0.175.0 leaves an Empty one slab -- its roof -- and records it a roof
slot; this is the half that lets the worldskin dress that slab from the
`roof_` module Zoo then builds, since an Empty has no `floor_` module.

Anchored edits (every anchor once; refuses on a miss):
  assets/godot/zoo_worldskin.gd     SLAB_REVEAL_FAMILY gains "roof_" after "floor_"
  tests/unit/test_worldskin_slabs.py  two real-import tests; the source shape
CHANGELOG and VERSION from `lf_slab_roof/CHANGELOG_0.138.0.md`.

    python patch_lf_slab_roof.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LF = HERE.parent / "level_factory"
SRC = HERE / "lf_slab_roof"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


GD_OLD = '''## it would match a seam that is not there. Same value as
## `STAIR_FLIGHT_FAMILY` and written out rather than aliased to it, so the two
## can diverge later without one silently moving the other.
const SLAB_REVEAL_FAMILY: Array = ["floor_"]
'''
GD_NEW = '''## it would match a seam that is not there. Same value as
## `STAIR_FLIGHT_FAMILY` and written out rather than aliased to it, so the two
## can diverge later without one silently moving the other.
##
## `roof_` IS THE FALLBACK, BY THE SAME RULE (0.138.0). An Empty (Deli Counter
## 0.175.0) keeps one slab, its roof, and has no room to record a floor slot
## from, so Zoo builds it a `roof_` module and no `floor_`. The surface that
## slab meets is the roof. Families are tried in order, so a building -- which
## always carries a `floor_` module -- takes exactly the material it took
## before. Without this, cold run 9146 was refused at export with 588 Empty
## slabs in `gb_floor`.
const SLAB_REVEAL_FAMILY: Array = ["floor_", "roof_"]
'''

T_SHAPE_OLD = '''    assert 'const SLAB_REVEAL_FAMILY: Array = ["floor_"]' in src
'''
T_SHAPE_NEW = '''    assert 'const SLAB_REVEAL_FAMILY: Array = ["floor_", "roof_"]' in src
'''

T_RULE_OLD = '''@godot_required
def test_a_collision_slab_is_not_skinned(tmp_path):
'''
T_RULE_NEW = '''@godot_required
def test_an_empty_s_roof_slab_takes_the_roof_family(tmp_path):
    """FAILS BEFORE 0.138.0: an Empty has a `roof_` module and no `floor_`,
    and cold run 9146 shipped 588 of its slabs in `gb_floor`."""
    roof = "roof_delco_1997_01_w600_d1200_mconcrete.glb"
    proj = _project(tmp_path, base_meshes=[("slab_3_t0_0", 0)], art_modules=(roof,))
    line = _slab_line(_import(proj))
    assert "1 surface(s) skinned on 1 mesh(es)" in line, line
    assert "0 mesh(es) left flat" in line, line
    assert f"reveal from {roof}" in line, line


@godot_required
def test_a_building_with_both_still_takes_the_floor_family(tmp_path):
    """The control: the fallback must not move a building, which always has a
    `floor_` module, off the material it took before."""
    floor = "floor_delco_1997_05_w1000_d700.glb"
    roof = "roof_delco_1997_01_w600_d1200_mconcrete.glb"
    proj = _project(tmp_path, base_meshes=[(SLAB, 0)], art_modules=(roof, floor))
    line = _slab_line(_import(proj))
    assert f"reveal from {floor}" in line, line


@godot_required
def test_a_collision_slab_is_not_skinned(tmp_path):
'''


def main():
    assert (LF / "VERSION").read_text(encoding="utf-8").strip() == "0.137.0"
    _edit(LF / "assets" / "godot" / "zoo_worldskin.gd", [(GD_OLD, GD_NEW)])
    _edit(LF / "tests" / "unit" / "test_worldskin_slabs.py",
          [(T_SHAPE_OLD, T_SHAPE_NEW), (T_RULE_OLD, T_RULE_NEW)])
    ch = LF / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.138.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (LF / "VERSION").write_text("0.138.0", encoding="utf-8", newline="\n")
    print("applied Level Factory 0.138.0")


if __name__ == "__main__":
    main()
