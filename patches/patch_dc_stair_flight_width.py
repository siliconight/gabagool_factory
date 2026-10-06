"""Deli Counter 0.190.0: a generator draws a stair flight at the contract's
corridor minimum plus one bake cell, never 0.9 m.

Measured 2026-10-06 (roadmap 189, `docs/findings/stairwell_on_one_grid_in_four/`
at the factory root): twin_a01's 0.9 m flights traversed at 7 of 8 voxel-grid
origins under the nav gate's sweep, and its upstairs objective was reached at
7 of 8. The route-walking neck finder put the tear on the flight itself.
- **Refuted first, kept:** moving the fridges and wardrobes against the end
  walls, because a fridge stood nearest the tear. Built and gated in scratch:
  still 7 of 8.
- **Measured:** the same frozen spec with 1.2 m flights, furniture untouched,
  connected at 8 of 8. Gate and census agree.

A flight is a corridor to the nav bake, and `min_corridor_width_m` (1.1) is
the contract's corridor minimum: 2 x the bake radius + 0.3. One bake cell
over it is 1.2. Both generators that drew 0.9 m flights take it from the
contract now: `twin` and `rowhome`. No library shell takes its stairs from
`rowhome` today; the Empties have none.

    python patch_dc_stair_flight_width.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"
PRESETS = DC / "presets.py"
SPEC = DC / "specs" / "twin_a01.json"

HELPER_OLD = '''import migrate_window_sign


# common acoustic palette'''
HELPER_NEW = '''import migrate_window_sign


def _stair_flight_width():
    """A stair flight is a corridor to the nav bake, so a generator draws it
    at the contract's corridor minimum and one bake cell over: a flight AT the
    minimum keeps a strip a few cells wide after erosion, and whether that
    strip joins up depends on where the voxel grid falls.

    Measured 2026-10-06 (Deli Counter 0.190.0, roadmap 189): twin_a01's
    0.9 m flights traversed at 7 of 8 grid origins; at this width, 1.2 m, at 8
    of 8, under the nav gate's sweep and the factory census both. The
    library's 1.0 m (cr_pawn, night_pawn) and 1.1 m (card_shop_a01) flights
    connect at 8 of 8 as they stand. This is what a generator draws, not a
    floor those specs are held to.
    """
    import agent_contract
    c = agent_contract.contract()
    return round(float(c["clearances"]["min_corridor_width_m"])
                 + float(c["nav_bake"]["cell_size_m"]), 3)


STAIR_FLIGHT_WIDTH = _stair_flight_width()


# common acoustic palette'''

ROW_OLD = '''"to_story": 2, "width": 0.9, "run": 3.0, "style": "switchback", "cut_slabs": True}]
'''
ROW_NEW = '''"to_story": 2, "width": STAIR_FLIGHT_WIDTH, "run": 3.0, "style": "switchback", "cut_slabs": True}]
'''

TWIN_OLD = '''        {"x": -qx, "y": hy - 3.2, "from_story": stair_lo, "to_story": 1,
         "width": 0.9, "run": 3.0, "style": "switchback", "cut_slabs": True},
        {"x": qx, "y": hy - 3.2, "from_story": stair_lo, "to_story": 1,
         "width": 0.9, "run": 3.0, "style": "switchback", "cut_slabs": True},
'''
TWIN_NEW = '''        {"x": -qx, "y": hy - 3.2, "from_story": stair_lo, "to_story": 1,
         "width": STAIR_FLIGHT_WIDTH, "run": 3.0, "style": "switchback",
         "cut_slabs": True},
        {"x": qx, "y": hy - 3.2, "from_story": stair_lo, "to_story": 1,
         "width": STAIR_FLIGHT_WIDTH, "run": 3.0, "style": "switchback",
         "cut_slabs": True},
'''

WHY = ("Deli Counter 0.190.0: 1.2 m, presets.STAIR_FLIGHT_WIDTH (the contract's "
       "corridor minimum and one bake cell), not 0.9. At 0.9 m this flight "
       "traversed at 7 of 8 voxel-grid origins and objective_UPSTAIRS was reached "
       "at 7 of 8 (nav gate sweep, roadmap 189); at 1.2 m, 8 of 8.")


def _stair(x, sid, role, width):
    return '''  {
   "x": %s,
   "y": 3.3,
   "from_story": -1,
   "to_story": 1,
   "width": %s,
   "run": 3.8,
   "style": "switchback",
   "cut_slabs": true,
   "facing": "N",
   "id": "%s",
   "meta": {
    "generated_by": "presets"%s
   },
   "role": "%s"
  }''' % (x, width, sid, "" if width == "0.9" else ',\n    "width_why": ' + json.dumps(WHY), role)


EDITS = {
    PRESETS: [(HELPER_OLD, HELPER_NEW), (ROW_OLD, ROW_NEW), (TWIN_OLD, TWIN_NEW)],
    SPEC: [(_stair("-4.0", "twin_a01_stair_0", "primary_egress", "0.9"),
            _stair("-4.0", "twin_a01_stair_0", "primary_egress", "1.2")),
           (_stair("4.0", "twin_a01_stair_1", "secondary_egress", "0.9"),
            _stair("4.0", "twin_a01_stair_1", "secondary_egress", "1.2"))],
}


def main():
    sys.path.insert(0, str(DC))
    import agent_contract
    c = agent_contract.contract()
    width = round(float(c["clearances"]["min_corridor_width_m"])
                  + float(c["nav_bake"]["cell_size_m"]), 3)
    assert width == 1.2, ("the spec is written at 1.2; the contract now gives", width)
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        crlf = data.count(b"\r\n")
        assert crlf in (0, data.count(b"\n")), f"{path}: mixed line endings"
        eol = "\r\n" if crlf else "\n"
        text = data.decode("utf-8")
        for old, new in pairs:
            old, new = old.replace("\n", eol), new.replace("\n", eol)
            n = text.count(old)
            assert n == 1, f"{path.name}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        staged[path] = text
    json.loads(staged[SPEC])
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
