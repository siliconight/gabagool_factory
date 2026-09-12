"""Roadmap batch 20, 2026-09-11: item 143 narrowed by Deli Counter 0.116.0.
REPLACE mode; the old status block is kept verbatim inside the new one.
Asserts the anchor matches exactly once.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

OLD = """*STATUS: OPEN 2026-09-11 -- FOUND BY A PERSON, MEASURED, AND THE INSTRUMENT
ALREADY EXISTED*

**143. Ceiling lamps sit inside partitions on this shell.**"""

NEW = """*STATUS: NARROWED 2026-09-11 -- FIXED IN DELI COUNTER 0.116.0 AND MEASURED
BACK WITH THE SAME PROBE: 9 LAMP POINTS INSIDE A WALL -> 0; NOT YET
RE-WALKED, AND THE PROBE IS STILL NOT A GATE. `lights.partition_rects` hands
the rows the spec's partitions (the builder's trimmed pieces, at the wall
thickness the emitters build to) the way it hands them ceiling voids;
`_row_runs` nudges a lamp whose centre falls within `wall_clearance` of a
band to the band's edge along the row -- as its own run, since a run's
points are equally spaced by contract -- and drops one with no landing
inside half a spacing; `_colinear_shift` moves a row lying ALONG a
partition (the roof's five bulbs in the y = 0 spine, every one of them) to
the centre of the larger side. The clearance is derived: half the wall +
half Zoo's troffer (`depth` 0.3 in `fluorescent_fixture`'s genome) + the
row's own 0.1 m ceiling gap = 0.40 m from the centreline, 0.25 from the
face. Rebuilt `lf_county_hospital_001_9005` and probed: 35 lamp points, 0
inside a wall (was 9), 6 at exactly 0.250 m from a face -- the two lobby
and two ward lamps nudged to x = +-8.4 / 7.6, and two roof bulbs that,
once the row moved to y = 7.5, met the ward partitions at x = +-8 and were
nudged in turn; 6 nudged, 0 dropped, 1 row moved, printed by
`write_light_manifest` beside the void count. RESIDUE: the roof's south
half has no bulbs now (one row, one side, on purpose -- whether that
space wanted its own row is a room-splitting question for the spec); the
probe's 0.30 m band still lists the six, which is the band being a
reporting threshold and not a defect threshold; and item 85's ask -- the
probe run as a gate over the deli job's outputs -- is still open. EARLIER
STATUS, KEPT VERBATIM: OPEN 2026-09-11 -- FOUND BY A PERSON, MEASURED, AND
THE INSTRUMENT ALREADY EXISTED*

**143. Ceiling lamps sit inside partitions on this shell.**"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    n = text.count(OLD)
    if n != 1:
        print(f"anchor matched {n} times; refusing", file=sys.stderr)
        return 1
    out = text.replace(OLD, NEW, 1).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); item 143 narrowed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
