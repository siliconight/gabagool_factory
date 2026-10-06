"""Deli Counter 0.189.0: `navgate_baseline.json` freezes the shells whose
connections the gate's grid sweep found on some voxel grids and not others.

The list is nav_gate 0.189.0's first library run (2026-10-06): eight shells
flagged, of which deli_a03 is fixed in the same release
(`patch_dc_deli_a03_stair_door.py`) and so is not frozen. Each reason says
what was measured; none names a neck that has not been located.

Six of the seven were unfit for a themed lot before the sweep too: each one's
pre-0.189.0 verdict, re-scoped from the same files with the grid lists removed,
is not navigable. twin_a01 was fit and is the only shell of its family, so the
twin family leaves themed lots with it. No brief names that family.

    python patch_dc_grid_baseline.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = ROOT / "deli_counter" / "navgate_baseline.json"

_REG = ("objective_REGISTER is reached from spawn at {k} of 8 voxel-grid "
        "origins (nav_gate 0.189.0). It stands inside its register counter and "
        "snaps about 1.1 m to the floor beside it (nav_gate.gd MARKER_MAX_ABOVE); "
        "which side of the counter it resolves to, and whether that side joins "
        "the floor, is not yet located. Not fit for a themed lot before the "
        "sweep either.")

ENTRIES = [
    {"shell": "corner_deli_heist_01", "stairs": [],
     "markers": ["objective_REGISTER (2/8 grid origins)"], "reason": _REG.format(k=2)},
    {"shell": "cr_deli", "stairs": [],
     "markers": ["objective_REGISTER (2/8 grid origins)"], "reason": _REG.format(k=2)},
    {"shell": "foundry_heist_vertical",
     "stairs": ["foundry_heist_vertical_stair_0", "foundry_heist_vertical_stair_1"],
     "markers": [],
     "reason": ("both stairs traverse at only some of 8 voxel-grid origins "
                "(nav_gate 0.189.0); the necks are not yet located. Not fit for "
                "a themed lot before the sweep either.")},
    {"shell": "fuel_stop_heist", "stairs": [],
     "markers": ["objective_REGISTER (4/8 grid origins)"], "reason": _REG.format(k=4)},
    {"shell": "night_deli", "stairs": [],
     "markers": ["objective_REGISTER (2/8 grid origins)"], "reason": _REG.format(k=2)},
    {"shell": "primos_pizza", "stairs": ["primos_pizza_stair_0"],
     "markers": ["objective_COUNT_SAFE (6/8 grid origins)", "loot_STASH (6/8 grid origins)"],
     "reason": ("primos_pizza_stair_0 traverses at only some of 8 voxel-grid "
                "origins, and the safe and the stash are reached at 6 of 8 "
                "(nav_gate 0.189.0). The stair is already in stair_failures from "
                "an older run. Not fit for a themed lot before the sweep either.")},
    {"shell": "twin_a01", "stairs": ["twin_a01_stair_1"],
     "markers": ["objective_UPSTAIRS (7/8 grid origins)"],
     "reason": ("twin_a01_stair_1 traverses at only some of 8 voxel-grid "
                "origins and objective_UPSTAIRS is reached at 7 of 8 (nav_gate "
                "0.189.0); level_factory's spawn_placement.py records cold run "
                "9058 meeting trouble with the same objective. Fit for a themed "
                "lot before the sweep, and the only shell of the twin family, "
                "which leaves themed lots with it.")},
]

COUNTS_OLD = '''    "navigable_null": 20
  },
'''
COUNTS_NEW = '''    "navigable_null": 20,
    "grid_fragile": %d
  },
''' % len(ENTRIES)

TAIL_OLD = '''      "shell": "primos_pizza",
      "stairs": [
        "primos_pizza_stair_0"
      ],
      "reason": "stair(s) reported not traversable by the Godot bake; a geometry fix, not a marker one"
    }
  ]
}'''


def _tail_new():
    body = json.dumps({"grid_fragile": ENTRIES}, indent=2)
    inner = body[body.index("\n") + 1: body.rindex("\n")]   # drop the outer braces
    return TAIL_OLD[:-2] + ",\n" + inner + "\n}"


def main():
    data = BASE.read_bytes()
    assert b"\r\n" not in data, "navgate_baseline.json is LF"
    text = data.decode("utf-8")
    for old, new in ((COUNTS_OLD, COUNTS_NEW), (TAIL_OLD, _tail_new())):
        n = text.count(old)
        assert n == 1, f"anchor matched {n} times: {old[:70]!r}"
        text = text.replace(old, new)
    parsed = json.loads(text)
    assert parsed["counts"]["grid_fragile"] == len(parsed["grid_fragile"]) == 7
    BASE.write_bytes(text.encode("utf-8"))
    print("patched", BASE.relative_to(ROOT), "-- grid_fragile:", len(ENTRIES))


if __name__ == "__main__":
    main()
