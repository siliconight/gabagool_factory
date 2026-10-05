"""Deli Counter 0.184.0: twelve rowhome Empties, not six -- so a 26-house terrace
repeats each about twice instead of up to seven times. See
`dc_more_rowhomes/CHANGELOG_0.184.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  presets.py             EMPTY_ROWHOMES g..l after f
  navgate_baseline.json  the six new shells unjudged, counts 15->21, 14->20
  test_empties.py        VARIANTS lists the twelve
  test_front_doors.py    the family's doors: each finish at most twice
  test_house_bricks.py   the family's bricks: each worn
Rewrites the twelve rowhome specs from the preset; copies the test;
CHANGELOG and VERSION. Rebuild after: `python build.py --all` (presets.py is
a geometry source, so every shell goes stale).

    python patch_dc_more_rowhomes.py
"""
import importlib
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "deli_counter"
SRC = HERE / "dc_more_rowhomes"
NEW = "ghijkl"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


FAM_OLD = '''    "gs_empty_rowhome_f": dict(width=6.0, floors=3, wall="brick", door_side="E", cornice=0.7, seed=1916,
                               door_finish="stained"),
}
'''
FAM_NEW = '''    "gs_empty_rowhome_f": dict(width=6.0, floors=3, wall="brick", door_side="E", cornice=0.7, seed=1916,
                               door_finish="stained"),
    # SIX MORE (0.184.0): a 26-house terrace drawn from six showed one house
    # seven times (cold run 9159). Across the twelve every wall kind and every
    # door finish is worn exactly twice, and no two houses share both.
    "gs_empty_rowhome_g": dict(width=5.8, floors=3, wall="brick_brown", door_side="W", cornice=0.9, seed=1917,
                               door_finish="green"),
    "gs_empty_rowhome_h": dict(width=6.3, floors=2, wall="brick_orange", door_side="E", cornice=0.7, seed=1918,
                               door_finish="white", security_door=True),
    "gs_empty_rowhome_i": dict(width=6.1, floors=3, wall="siding", door_side="W", cornice=0.8, seed=1919,
                               door_finish="oxblood"),
    "gs_empty_rowhome_j": dict(width=6.2, floors=3, wall="brick", door_side="W", cornice=0.6, seed=1920,
                               door_finish="black"),
    "gs_empty_rowhome_k": dict(width=5.6, floors=3, wall="paint_block", door_side="E", cornice=1.0, seed=1921,
                               door_finish="navy"),
    "gs_empty_rowhome_l": dict(width=6.4, floors=2, wall="stone_ext", door_side="E", cornice=0.8, seed=1922,
                               door_finish="stained", security_door=True),
}
'''

REASON = ("an Empty (Deli Counter 0.174.0, roadmap 106): facade-only, sealed, no interior for a "
          "spawn marker to stand in, so zero markers checked is the correct outcome -- the same "
          "call as gs_facade_rowhome")
BASE_OLD = '''      "shell": "gs_empty_rowhome_f",
      "checked": 0,
      "navigable": null,
      "stairs_ok": true,
      "reason": "%s"
    }
''' % REASON
BASE_NEW = BASE_OLD.rstrip("\n") + "".join(''',
    {
      "shell": "gs_empty_rowhome_%s",
      "checked": 0,
      "navigable": null,
      "stairs_ok": true,
      "reason": "%s (0.184.0, one of the six added)"
    }''' % (c, REASON) for c in NEW) + "\n"
COUNT_OLD = '''    "unjudged": 15,
'''
COUNT_NEW = '''    "unjudged": 21,
'''
NULL_OLD = '''    "navigable_null": 14
'''
NULL_NEW = '''    "navigable_null": 20
'''

VAR_OLD = '''VARIANTS = ["gs_empty_rowhome_a", "gs_empty_rowhome_b", "gs_empty_rowhome_c",
            "gs_empty_rowhome_d", "gs_empty_rowhome_e", "gs_empty_rowhome_f"]
'''
VAR_NEW = '''VARIANTS = ["gs_empty_rowhome_%s" % c for c in "abcdefghijkl"]   # twelve since 0.184.0
'''

DOORS_OLD = '''def test_the_family_authors_a_different_door_on_every_house_and_two_iron():
    doors = [a.get("door_finish") for a in presets.EMPTY_ROWHOMES.values()]
    assert None not in doors and len(set(doors)) == len(doors) == 6
    assert set(doors) <= set(empty_panes.DOOR_FINISHES)
    assert sum(1 for a in presets.EMPTY_ROWHOMES.values() if a.get("security_door")) == 2
'''
DOORS_NEW = '''def test_the_family_authors_every_finish_at_most_twice_and_a_few_iron():
    """Six houses wore six different doors; twelve (0.184.0) wear each finish
    at most twice."""
    doors = [a.get("door_finish") for a in presets.EMPTY_ROWHOMES.values()]
    assert None not in doors and set(doors) == set(empty_panes.DOOR_FINISHES)
    assert max(doors.count(f) for f in set(doors)) <= 2
    assert 2 <= sum(1 for a in presets.EMPTY_ROWHOMES.values() if a.get("security_door")) <= 4
'''

BRICKS_OLD = '''def test_the_brick_houses_are_three_different_bricks():
    bricks = sorted(a["wall"] for a in presets.EMPTY_ROWHOMES.values() if a["wall"].startswith("brick"))
    assert bricks == ["brick", "brick_brown", "brick_orange"]
'''
BRICKS_NEW = '''def test_the_brick_houses_wear_all_three_bricks():
    bricks = [a["wall"] for a in presets.EMPTY_ROWHOMES.values() if a["wall"].startswith("brick")]
    assert set(bricks) == {"brick", "brick_brown", "brick_orange"}
'''


def main():
    assert (DC / "VERSION").read_text(encoding="utf-8").strip() == "Deli Counter 0.183.0"
    _edit(DC / "presets.py", [(FAM_OLD, FAM_NEW)])
    _edit(DC / "navgate_baseline.json", [(BASE_OLD, BASE_NEW), (COUNT_OLD, COUNT_NEW), (NULL_OLD, NULL_NEW)])
    json.loads((DC / "navgate_baseline.json").read_text(encoding="utf-8"))   # still JSON
    _edit(DC / "test_empties.py", [(VAR_OLD, VAR_NEW)])
    _edit(DC / "test_front_doors.py", [(DOORS_OLD, DOORS_NEW)])
    _edit(DC / "test_house_bricks.py", [(BRICKS_OLD, BRICKS_NEW)])
    sys.path.insert(0, str(DC))
    presets = importlib.import_module("presets")
    assert len(presets.EMPTY_ROWHOMES) == 12
    for name, args in presets.EMPTY_ROWHOMES.items():
        with open(DC / "specs" / f"{name}.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(presets.empty_rowhome(name=name, **args), f, indent=2)
    shutil.copyfile(SRC / "test_more_rowhomes.py", DC / "test_more_rowhomes.py")
    ch = DC / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.184.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (DC / "VERSION").write_text("Deli Counter 0.184.0", encoding="utf-8", newline="\n")
    print("applied Deli Counter 0.184.0 -- now rebuild: python build.py --all")


if __name__ == "__main__":
    main()
