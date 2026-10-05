"""Deli Counter 0.183.0, second half: the two existing tests that held their own
copy of the brick vocabulary move with it.

`patch_dc_house_bricks.py` made `brick_brown` and `brick_orange` skin kinds,
outside-only like brick, and built two rowhomes in them. `check.py` then
failed two tests that each keep a literal of the old set -- correctly: each
pins a rule, and the rule's vocabulary changed. Applied on top of that patch
rather than folded into it, because re-applying it from a clean tree would
rewrite the builder's sources after `build.py --all` and make every built
shell look older than its code. Test files only; no build input changes.

Anchored edits (every anchor once; refuses on a miss):
  test_empties.py     the family's wall kinds include the house bricks
  test_inner_face.py  its OUTSIDE_ONLY mirror includes them

    python patch_dc_house_bricks_tests.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "deli_counter"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


EMPTIES_OLD = '''        assert material_kind.kind_for(s["default_material"]) in ("brick", "siding", "stone", "paint_block")
'''
EMPTIES_NEW = '''        # three bricks since 0.183.0: the comp's row is brown, red and orange
        assert material_kind.kind_for(s["default_material"]) in (
            "brick", "brick_brown", "brick_orange", "siding", "stone", "paint_block")
'''

INNER_DOC_OLD = '''its exterior walls. Held here: every exterior wall slot in brick, stone, wood
or siding names its building's interior finish as `material_in`, no other
'''
INNER_DOC_NEW = '''its exterior walls. Held here: every exterior wall slot in a brick (red, and
since 0.183.0 brown or orange), stone, wood or siding names its building's
interior finish as `material_in`, no other
'''
INNER_SET_OLD = '''OUTSIDE_ONLY = {"brick", "stone", "wood", "siding"}
'''
INNER_SET_NEW = '''OUTSIDE_ONLY = {"brick", "brick_brown", "brick_orange", "stone", "wood", "siding"}
'''


def main():
    assert (DC / "VERSION").read_text(encoding="utf-8").strip() == "Deli Counter 0.183.0"
    _edit(DC / "test_empties.py", [(EMPTIES_OLD, EMPTIES_NEW)])
    _edit(DC / "test_inner_face.py", [(INNER_DOC_OLD, INNER_DOC_NEW), (INNER_SET_OLD, INNER_SET_NEW)])
    print("applied: the two vocabulary tests move with the house bricks")


if __name__ == "__main__":
    main()
