"""Deli Counter 0.189.0: deli_a03's `office_stair_door` widens to 2.4 m so
the way up does not turn inside its reveal.

Measured 2026-10-06 (roadmap 189, `docs/findings/stairwell_on_one_grid_in_four/`
at the factory root):
- The stairwell's only walkable way in is this door, in `int_0_1` (y 6).
- At 1.25 m centred on x -15.0, all but its east 0.2 m opens over
  `deli_stair_down`'s slab hole, which spans x -17.0 to -14.6 from y 6.2. It
  is the basement flight's own door, by design.
- A body going UP turns east inside the reveal onto the 1.6 m strip between
  that hole and `deli_stair_up` (x -14.6 to -13.0).
- That turn bakes at 4 of 8 voxel-grid origins (nav_gate 0.189.0:
  objective_A `[F, F, T, T, F, F, T, T]`). Cold run 9185 lost two candidates
  of three to it.

Widened to 2.4 m centred on x -14.5 (pos -0.38; openings snap to the spec's
0.5 m grid), the door spans -15.7 to -13.3:
- its west part still meets the basement flight's top;
- its east part opens about 0.5 m (five cells, after the 0.4 m agent erosion
  both sides) straight onto the strip.

Built to a scratch folder and gated before this patch: objective_A at 8 of 8
origins, navigable. validate.py OK; layout_lint 0 FAIL.

The reason travels with the stair it serves, beside `open_under_why`: an
opening has no `meta` in level.schema.json.

    python patch_dc_deli_a03_stair_door.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEC = ROOT / "deli_counter" / "specs" / "deli_a03.json"

DOOR_OLD = '''     "kind": "door",
     "pos": -0.4,
     "width": 1.25,
     "tag": "office_stair_door"
'''
DOOR_NEW = '''     "kind": "door",
     "pos": -0.38,
     "width": 2.4,
     "tag": "office_stair_door"
'''

META_OLD = '''    "open_under_why": "Nav gate 2026-09-13: with the underside solid, objective_A upstairs is unreachable; the only route to this flight's foot passes under its high end, because deli_stair_down's slab hole leaves 0.4 m beside it. Reachable with the underside open."
   }
'''
META_NEW = '''    "open_under_why": "Nav gate 2026-09-13: with the underside solid, objective_A upstairs is unreachable; the only route to this flight's foot passes under its high end, because deli_stair_down's slab hole leaves 0.4 m beside it. Reachable with the underside open.",
    "door_why": "Deli Counter 0.189.0: office_stair_door is 2.4 m centred on x -14.5, not 1.25 m on -15.0. At 1.25 m all but its east 0.2 m opened over deli_stair_down's slab hole, so the way to this flight turned inside the door's reveal, and that turn baked at 4 of 8 voxel-grid origins (nav_gate grid sweep; cold run 9185 lost two candidates to it). The wider door still meets the basement flight's top and opens about 0.5 m straight onto the strip beside this flight: 8 of 8."
   }
'''

EDITS = {SPEC: [(DOOR_OLD, DOOR_NEW), (META_OLD, META_NEW)]}


def main():
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
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
