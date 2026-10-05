"""Deli Counter 0.183.0: a house's own brick -- `brick_brown` and `brick_orange`
are skin kinds, outside-only like brick, and two rowhome Empties wear them.
See `dc_house_bricks/CHANGELOG_0.183.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  material_kind.py   SKIN_KINDS, KIND_BY_MATERIAL
  deli_counter.py    OUTSIDE_ONLY
  presets.py         rowhome a orange, c brown; the family's comment
Rewrites the six rowhome specs from the preset; copies the test; CHANGELOG
and VERSION. Rebuild after: `python build.py --all`.

    python patch_dc_house_bricks.py
"""
import importlib
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "deli_counter"
SRC = HERE / "dc_house_bricks"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


SKIN_OLD = '''    "wood_panel", "slatwall",
)
'''
SKIN_NEW = '''    "wood_panel", "slatwall",
    # A HOUSE'S OWN BRICK (0.183.0, Pixelcoat 0.57.0, Zoo 1.73.0): the comp's
    # row is brown, red and orange, one brick a house, and a theme holds one
    # grammar per kind
    "brick_brown", "brick_orange",
)
'''

KIND_OLD = '''    # already kinds
    "brick": "brick",
'''
KIND_NEW = '''    # already kinds
    "brick": "brick",
    "brick_brown": "brick_brown",
    "brick_orange": "brick_orange",
'''

OUT_OLD = '''    OUTSIDE_ONLY = frozenset({"brick", "stone", "wood", "siding"})
'''
OUT_NEW = '''    OUTSIDE_ONLY = frozenset({"brick", "brick_brown", "brick_orange", "stone", "wood", "siding"})
'''

FAM_DOC_OLD = '''#: storeys, wall, door side, cornice height (m), seed. Brick dominates as it
#: does on the comp's street; siding and Formstone (`stone_ext`) are the
'''
FAM_DOC_NEW = '''#: storeys, wall, door side, cornice height (m), seed. Brick dominates as it
#: does on the comp's street -- three bricks, red, brown and orange, one a
#: house (0.183.0), as the comp has; siding and Formstone (`stone_ext`) are the
'''

A_OLD = '''    "gs_empty_rowhome_a": dict(width=6.0, floors=3, wall="brick", door_side="W", cornice=0.8, seed=1911,
'''
A_NEW = '''    "gs_empty_rowhome_a": dict(width=6.0, floors=3, wall="brick_orange", door_side="W", cornice=0.8, seed=1911,
'''
C_OLD = '''    "gs_empty_rowhome_c": dict(width=6.5, floors=3, wall="brick", door_side="E", cornice=1.0, seed=1913,
'''
C_NEW = '''    "gs_empty_rowhome_c": dict(width=6.5, floors=3, wall="brick_brown", door_side="E", cornice=1.0, seed=1913,
'''


def main():
    assert (DC / "VERSION").read_text(encoding="utf-8").strip() == "Deli Counter 0.182.0"
    _edit(DC / "material_kind.py", [(SKIN_OLD, SKIN_NEW), (KIND_OLD, KIND_NEW)])
    _edit(DC / "deli_counter.py", [(OUT_OLD, OUT_NEW)])
    _edit(DC / "presets.py", [(FAM_DOC_OLD, FAM_DOC_NEW), (A_OLD, A_NEW), (C_OLD, C_NEW)])
    sys.path.insert(0, str(DC))
    presets = importlib.import_module("presets")
    for name, args in presets.EMPTY_ROWHOMES.items():
        with open(DC / "specs" / f"{name}.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(presets.empty_rowhome(name=name, **args), f, indent=2)
    shutil.copyfile(SRC / "test_house_bricks.py", DC / "test_house_bricks.py")
    ch = DC / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.183.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (DC / "VERSION").write_text("Deli Counter 0.183.0", encoding="utf-8", newline="\n")
    print("applied Deli Counter 0.183.0 -- now rebuild: python build.py --all")


if __name__ == "__main__":
    main()
