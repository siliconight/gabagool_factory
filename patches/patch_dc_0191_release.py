"""Deli Counter 0.191.0: VERSION and CHANGELOG for
`patch_dc_circulation_parts_tests.py` and `patch_dc_circulation_parts.py`.

    python patch_dc_0191_release.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

ENTRY = '''## [0.191.0] - the circulation gate reads a dressing's parts, and excuses a stair's own guards

Found 2026-10-06, measuring roadmap 177's successor at the factory root
(`docs/findings/presentation_gates/`).

### A gate that could not pass

**Every cold run from 9164 to 9187 failed the circulation gate on every
building with covers**, and every one was counted clean. The compose driver's
exit is advisory, and Level Factory had no branch that read the result.
- Zoo merges a building's covers per side per material (1.68.0).
  `check_dressing` boxed each NODE, so one box carried dozens of strips.
- On 9187's gs_empty_rowhome_l, 9 nodes carry 109 covers, and each concrete
  node's box is the building's, about 6.7 x 7.1 x 12 m. Every doorway lay
  inside one.
- The four buildings measured read 9, 48, 28 and 27 conflicts.
- The dressing layer is non-collision by construction (Zoo's build record:
  `"collision": "none"`).

**`circulation.dressing_part_boxes`** splits each node into its parts: the
position-welded, index-connected pieces of its mesh. A part is a strip, which
is what `DOOR_TRIM_PEN` was written against. `check_dressing` boxes parts and
reports `nodes` beside `props`.
- On all 15 buildings 9187 shipped: 123 to 249 parts each, 0 conflicts.
- **The positive control:** a 1 m crate planted in a doorway is caught at
  0.95 m.

**Refuted first, kept.** Index connectivity without welding returns one
component per FACE, because faces carry their own vertices for split normals
and UVs. That gave 1,452 planes on gs_empty_rowhome_l. A plane has zero
thickness, so `_pen` can never flag it: 0 conflicts, for the wrong reason.

### A stair's guards inside its own stair

Every volume is role `prop`, so the shell arm read a stair's fall guards as
props in its column. office's `stair_guard_back_10` stood 0.26 m inside
`office_stair_0`, a storey above the flight's foot.
- **`GUARD_PREFIX`**, the builder's `stair_guard_{kind}_{k}`, is excused from
  STAIR volumes only, and returned as `excused`. In a doorway or a ladder's
  climb volume a guard is a prop like any other.
- Not linked to its own stair: a guard inside another stair's column would
  be excused too.

**What the gate says now about 9187's 15 buildings:** one thing, and it is
real. deli_a01's `counter_island_upper_hall_2` stands 0.8 m inside
`deli_stair_up`, a counter partly over the stairwell. That is the next
release.

### Tests

`test_circulation.py`, 7 new:
- a merged node's box spans its parts;
- parts are welded boxes, not faces;
- a merged frame passes its doorway, and a crate in the doorway is still
  caught;
- the guard prefix is the builder's;
- a stair's guard is excused from its stair, and not from a doorway.

The GLBs are written in the test the way a real export writes them: 24
vertices a box, four a face. Five fail on 0.190.0. The defect statement and
the positive control pass on both by design.

**Suite:** 1,257 passed, 2 skipped. That is 0.190.0's 1,250 and these 7.

'''


def main():
    v = DC / "VERSION"
    assert v.read_bytes() == b"Deli Counter 0.190.0", v.read_bytes()
    cl = DC / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## [0.190.0] - stairs a body can walk"), text[:60]
    cl.write_bytes((ENTRY + text).encode("utf-8"))
    v.write_bytes(b"Deli Counter 0.191.0")
    print("Deli Counter 0.191.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
