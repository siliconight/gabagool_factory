"""Level Factory 0.218.2: the ground-contact pre-flight reads a scene's transforms as Godot does.

THE DEFECT, ONE OF A CLASS. `packages/validation/ground_contact._transform` said "Godot writes Transform3D as
the three basis columns followed by the origin" and built the transpose. Godot 4.7 writes and parses the nine
basis numbers as ROWS, measured three times: Deli Counter off the engine on cold run 9013
(`tscn_export.godot_basis`), Lot's `str_to_var` on 2026-09-13 (`lot/site_furniture.plate_facing`: at 30 degrees
local +X lands on (0.866, 0, -0.5)), and the factory's `tools/module_pose_census.py` on cold run 9324's deli_a01.
The same belief in Deli Counter's z-fight gate produced roadmap 177's last two pairs, false ones (Deli Counter
0.230.0); Lot's collision reader held it until Lot 0.72.1. Here a pure 90-degree turn read transposed turns the
other way, so a quarter-turned building's floor boxes off its own origin land mirrored about it; boxes at other
angles are reported opaque already, and a box centred on its building's origin lands the same either way.

MEASURED BEFORE WRITING (`docs/findings/zfight_rows_177/ground_contact_rows.py`, the module's own code with only
`_transform` swapped): on cold run 9324's three candidates' walk scenes, about 6,000 boxes each, 0 problems and 0
box centres moved either way -- every building there stands unturned. The fix is for the first level that turns
one; `spawn_placement` and `tactical` read scenes through the same function and inherit it.

What it changes (anchored; the file pinned by hash; nothing written on a miss; LF-safe):
  * packages/validation/ground_contact.py -- `_transform` reads rows, the refuted reading kept in its docstring.
  * tests/unit/test_ground_contact_rows.py (new, 2; both fail on 0.218.1): Lot's measured 30-degree turn read as
    Godot reads it; a floor off a quarter-turned building's origin found where Godot puts it, not mirrored.
  * VERSION 0.218.1 -> 0.218.2, CHANGELOG.

    python patches/patch_lf_ground_contact_rows.py --tests   # the test file only (prove it fails first)
    python patches/patch_lf_ground_contact_rows.py           # everything; the test again when it is this patch's
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LF = ROOT / "level_factory"
GC = LF / "packages" / "validation" / "ground_contact.py"
GC_SHA = "0936a4746d61568d"

OLD = '''def _transform(body: str):
    """The node's own transform as a 3x4 matrix; a missing one is the identity.

    Godot writes ``Transform3D`` as the three basis columns followed by the
    origin, so the row-major matrix this reader uses is a transpose away.
    """
    match = _TRANSFORM.search(body)
    if match is None:
        return _IDENTITY
    values = _floats(match.group(1))
    if len(values) != 12:
        return _IDENTITY
    return tuple(tuple(values[3 * col + row] for col in range(3))
                 + (values[9 + row],) for row in range(3))
'''
NEW = '''def _transform(body: str):
    """The node's own transform as a 3x4 matrix; a missing one is the identity.

    Godot 4.7 writes ``Transform3D`` as the basis's three ROWS followed by the
    origin, which is the row-major matrix this reader uses, number for number
    (0.218.2). Measured three times: Deli Counter off the engine on cold run
    9013 (`tscn_export.godot_basis`), Lot's `str_to_var` on 2026-09-13 (at 30
    degrees local +X lands on (0.866, 0, -0.5); `lot/site_furniture.
    plate_facing`), and the factory's `tools/module_pose_census.py` on cold
    run 9324's deli_a01.

    REFUTED, KEPT: until 0.218.1 this said "the three basis columns followed by
    the origin, so the row-major matrix this reader uses is a transpose away"
    and built the transpose. A pure 90-degree turn read that way turns the
    other way, so a quarter-turned building's floor boxes off its own origin
    landed mirrored about it. Nothing measured had met it: cold run 9324's
    candidates read about 6,000 boxes each the same either way, every building
    unturned. Deli Counter's z-fight gate held the same belief and reported
    two false pairs from it (Deli Counter 0.230.0, the factory's roadmap 177).
    """
    match = _TRANSFORM.search(body)
    if match is None:
        return _IDENTITY
    values = _floats(match.group(1))
    if len(values) != 12:
        return _IDENTITY
    return tuple(tuple(values[3 * row + col] for col in range(3))
                 + (values[9 + row],) for row in range(3))
'''

TEST = r'''"""The ground-contact pre-flight reads a `.tscn` Transform3D as Godot does: the basis's rows, then the origin
(0.218.2).

Until 0.218.1 `_transform` built the transpose, on the belief that Godot writes the basis's columns. Godot 4.7 writes
and parses rows (Lot measured `str_to_var` on 2026-09-13: at 30 degrees local +X lands on (0.866, 0, -0.5)). A pure
quarter turn read transposed turns the other way, so a floor box off a turned building's origin landed mirrored
about it; a box centred on the origin, as `test_ground_contact`'s quarter-turn test uses, lands the same either way
and could not tell.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from glb_fixture import write_glb  # noqa: E402

from packages.validation.ground_contact import _transform, read_scene, support_under  # noqa: E402

# Lot's measured case: `lot._godot_transform` at 30 degrees, `Transform3D(c, 0, s, 0, 1, 0, -s, 0, c, ...)`
THIRTY = "transform = Transform3D(0.866025, 0, 0.5, 0, 1, 0, -0.5, 0, 0.866025, 0, 0, 0)\n"

SITE = """[gd_scene load_steps=2 format=3]

[ext_resource type="PackedScene" path="res://shell.glb" id="b1"]

[node name="Site" type="Node3D"]

[node name="b0" parent="." instance=ExtResource("b1")]
transform = Transform3D(6.12323e-17, 0, 1, 0, 1, 0, -1, 0, 6.12323e-17, 6, 0, 0)
"""


def test_lots_measured_turn_reads_as_godot_reads_it():
    m = _transform(THIRTY)
    local_x = (m[0][0], m[1][0], m[2][0])   # where the basis sends local +X
    assert abs(local_x[0] - 0.866025) < 1e-6
    assert abs(local_x[1]) < 1e-9
    assert abs(local_x[2] + 0.5) < 1e-6


def test_an_offset_floor_in_a_quarter_turned_building_lands_where_godot_puts_it(tmp_path):
    # a 4 x 4 m floor 10 m along the shell's own +X, its top at y = 0
    write_glb(tmp_path / "shell.glb", [("floor_off-colonly", (10.0, -0.15, 0.0), (4.0, 0.3, 4.0))])
    (tmp_path / "site.tscn").write_text(SITE, encoding="utf-8")
    reading = read_scene(tmp_path / "site.tscn")
    # b0 turns local +X to world -Z (basis.x = (0, 0, -1)), so the floor stands at (6, -10)
    assert support_under((6.0, 0.9, -10.0), reading.boxes) is not None
    assert support_under((6.0, 0.9, 10.0), reading.boxes) is None
'''

CHANGELOG = '''## [0.218.2] - the ground-contact pre-flight reads a scene's transforms as Godot does

**One of a class, found in the factory's roadmap 177.** `ground_contact._transform` read a `.tscn` `Transform3D`'s
nine basis numbers as columns and built the transpose. Godot 4.7 writes and parses them as rows, measured three
times: Deli Counter off the engine on cold run 9013, Lot's `str_to_var` on 2026-09-13, and the factory's
`tools/module_pose_census.py` on cold run 9324's deli_a01. The same belief in Deli Counter's z-fight gate reported
roadmap 177's last two pairs, both false (Deli Counter 0.230.0), and Lot's collision reader held it until Lot
0.72.1. Here a quarter-turned building's floor boxes off its own origin landed mirrored about it; boxes at other
angles are already reported opaque, and a box centred on its building's origin lands the same either way.

### Fixed
- `_transform` reads rows; the refuted reading is kept in its docstring. `spawn_placement` and `tactical` read
  scenes through it and inherit the fix.

### Measured
- On cold run 9324's three candidates' walk scenes, about 6,000 boxes each: 0 problems and 0 box centres moved
  either way, every building unturned (the factory's `docs/findings/zfight_rows_177/ground_contact_rows.py`). The
  fix is for the first level that turns one.

### Added
- `tests/unit/test_ground_contact_rows.py` (2, both fail on 0.218.1).

'''


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _test_plan():
    p = LF / "tests" / "unit" / "test_ground_contact_rows.py"
    if p.exists():
        assert p.read_bytes() == TEST.encode("utf-8"), f"{p.name} exists and is not this patch's"
    return p


def write_tests(p=None):
    p = p or _test_plan()
    p.write_text(TEST, encoding="utf-8", newline="\n")
    print("wrote level_factory/tests/unit/test_ground_contact_rows.py")


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    raw = GC.read_bytes()
    assert b"\r\n" not in raw, "ground_contact.py is LF"
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == GC_SHA, ("ground_contact.py is not the file this patch read", got)
    text = _once(raw.decode("utf-8"), OLD, NEW, "_transform")
    v = LF / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "0.218.1", v.read_text(encoding="utf-8")
    cl = LF / "CHANGELOG.md"
    rawc = cl.read_bytes()
    eol = "\r\n" if rawc.count(b"\r\n") else "\n"
    ctext = rawc.decode("utf-8")
    assert ctext.startswith("## [0.218.1]"), ctext[:40]
    plan = _test_plan()
    GC.write_bytes(text.encode("utf-8"))
    v.write_text("0.218.2\n" if v.read_bytes().endswith(b"\n") else "0.218.2", encoding="utf-8")
    cl.write_bytes((CHANGELOG.replace("\n", eol) + ctext).encode("utf-8"))
    write_tests(plan)
    print("Level Factory 0.218.2 applied: ground_contact reads rows, the test, VERSION, CHANGELOG -- the suite, then commit")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
