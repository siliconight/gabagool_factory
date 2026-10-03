"""Level Factory 0.129.0: the import turns Zoo's turning parts and walks the
slush's churn -- small things that move, items 1 and 2 of
`docs/proposals/MOVING_PARTS_DESIGN.md`. The walker, 2026-10-02: "start with
the roller grill, and i want some motion on the slurpee stuff too".

WHAT THIS DOES (every edit anchored once; refuses on a miss):

  * `zoo_worldskin.gd` (`lf_moving/worldskin_edits.py`): `_turning_parts`
    replaces a surface whose material is named `..._turn_x36` /
    `..._turn_xn36` (Zoo 1.55.0) with a shader that reproduces the flat
    material and turns VERTEX and NORMAL about the axle in UV2 on the shader
    clock, phase per node; `_churn_passes` hangs a darkening next_pass off
    every `M_Slush_*_Face` that walks the churn's diagonal bands round the
    barrel's UV2 (u round, v up), skipping v = 2. Both run for every GLB
    before the kit branch.
  * `tests/unit/test_worldskin_moving_parts.py` (new, from `lf_moving/`), and
    `test_worldskin_crt_motion.py` admits `_turning_parts` to the set of
    material replacers.
  * CHANGELOG and VERSION, from `lf_moving/CHANGELOG_0.129.0.md`.

    python patch_lf_moving_parts.py
    LF_ROOT=<copy> python patch_lf_moving_parts.py
"""
import os
import pathlib
import runpy

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")


def main():
    v = (LF / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "0.128.0", v
    gd = LF / "assets" / "godot" / "zoo_worldskin.gd"
    assert "_turning_parts" not in gd.read_text(encoding="utf-8"), "already applied"
    os.environ["LF_ROOT"] = str(LF)
    runpy.run_path(str(HERE / "lf_moving" / "worldskin_edits.py"), run_name="__main__")
    # the tests
    t = LF / "tests" / "unit" / "test_worldskin_moving_parts.py"
    t.write_bytes((HERE / "lf_moving" / "test_worldskin_moving_parts.py").read_bytes())
    c = LF / "tests" / "unit" / "test_worldskin_crt_motion.py"
    cs = c.read_text(encoding="utf-8")
    old = 'MATERIAL_REPLACERS = {"_assign_stairs", "_assign_slabs", "_shutters"}\n'
    new = ("#: 0.129.0: a TURNING part's material is replaced too -- a second pass cannot\n"
           "#: move the first -- by a shader carrying the flat material's own numbers,\n"
           "#: and only on a name that names a rate (`test_worldskin_moving_parts.py`).\n"
           'MATERIAL_REPLACERS = {"_assign_stairs", "_assign_slabs", "_shutters", "_turning_parts"}\n')
    assert cs.count(old) == 1
    c.write_text(cs.replace(old, new), encoding="utf-8", newline="\n")
    # the changelog and the version
    entry = (HERE / "lf_moving" / "CHANGELOG_0.129.0.md").read_text(encoding="utf-8")
    cl = LF / "CHANGELOG.md"
    d = cl.read_bytes()
    assert d.startswith(b"## [0.128.0]") and b"## [0.129.0]" not in d
    cl.write_bytes(entry.replace("\r\n", "\n").encode("utf-8") + d)
    (LF / "VERSION").write_bytes(b"0.129.0")
    print("0.128.0 -> 0.129.0")


if __name__ == "__main__":
    main()
