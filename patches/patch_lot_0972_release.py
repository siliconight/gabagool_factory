"""Lot 0.97.2: VERSION and CHANGELOG for `patch_lot_vertical_access.py` and
`patch_lot_vertical_access_column.py`.

    python patch_lot_0972_release.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOT = ROOT / "lot"

ENTRY = '''## 0.97.2 - the walk test decides ladder access from the anchor, not from where Godot's path stopped

**Cold run 9185, roadmap 189 at the factory root**
(`docs/findings/stairwell_on_one_grid_in_four/`). One anchor in one navmesh
got two verdicts.
- The anchor is deli_a03's objective, upstairs and off the main network.
- From `proxy_1` it passed as "VERTICAL access (ladder/drop)". From `home`
  it failed as "path stops 60.99 m short (disjoint islands)".
- 9179 had passed it from both starts, on identical islands.
- Two candidates of three were lost to it.

**The mechanism.** `_prove_path` asks Godot for a path to the anchor.
- For an unreachable target, Godot returns a path to the nearest point it
  reached. The leg passed when that point lay under or over the anchor.
- In 4.7 that fallback can fail inside the engine: "It's not expect to not
  find the most reachable polygons" (`nav_mesh_queries_3d.cpp:404`).
- It then returns a path that stops beside the START: 2.9 m from home in
  seed_9003 and 4.2 m in seed_9205.
- In both, the job log shows the engine's error on the call immediately
  before each FAIL.

**Now `_vertical_access` asks the question of the anchor.** It samples the
anchor's column height by height, nearest first, from 1.5 m out to
`VERTICAL_REACH_M`. That reach is the library's longest ladder (8.0 m,
measured over deli_counter's gameplay files) plus a storey band. A surface
counts when:
- it lies inside the old concession's window: within 1.5 x `SNAP_MAX`
  across, and more than 1 m up or down;
- and a strict route from the start reaches it.

`_prove_path` and the non-strict `_reaches` both use it. Neither reads the
end of a failed path any more.

**Superseded, kept** (`patch_lot_vertical_access.py`, then
`_column.py`). The first version asked for the single point closest to the
whole column.
- That is the floor under the anchor's own foot every time.
- So it failed `proxy_2 -> proxy_3`: a drop from the deli's upstairs edge to
  the street, 2.7 m out and 3.3 m down, which the old rule passed in both
  9179 and 9185.
- The second version keeps the old window, and passes it.

**Proven on a copy of 9185's staged seed_9003:**
- `home->proxy_2` and `proxy_1->proxy_2` agree: both walk to (-54.0, 0.3,
  12.5), the floor under the objective.
- `proxy_2->proxy_3` passes as before.
- `ok: true`, 0 proof failures. The anchor is still reported stranded, as
  information.
- The engine still logs its error 10 times, from the census's strict
  queries. No verdict reads it now.

**Tests:** `tests/test_nav_qa_vertical_access.py`, 3. The director is
engine-bound, so it is read as source:
- `_vertical_access` samples the column inside the old window and reaches
  strictly;
- neither verdict reads a failed path's end;
- the reach is derived, and says from what.

All three fail on 0.97.1.

**Suite:** 664 passed (0.97.1's 661 and these 3).

'''


def main():
    v = LOT / "VERSION"
    assert v.read_bytes() == b"Lot 0.97.1", v.read_bytes()
    cl = LOT / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## 0.97.1 - a fence does not grow the plate"), text[:60]
    cl.write_bytes((ENTRY + text).encode("utf-8"))
    v.write_bytes(b"Lot 0.97.2")
    print("Lot 0.97.2: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
