"""Roadmap 265 stays NARROWED: its `cut` cause proven by cold runs 9340 and 9341 (the walk test's navmesh floored the
hole over; Deli Counter 0.236.1 drew a ring; priced).

Anchored: the item's whole NARROWED status line and the end of its SHIPPED paragraph, read verbatim from the roadmap
when this was written, must each be there exactly once; nothing is written otherwise. Every line LF. Then
`python tools/roadmap_status.py --write` and `--check` regenerate and verify the index.

    python patches/patch_roadmap_265_proven.py
"""
import pathlib
import sys

ROADMAP = pathlib.Path(__file__).resolve().parents[1] / "PIPELINE_ROADMAP.md"
OLD_STATUS = "*STATUS: NARROWED 2026-10-20 -- SHIPPED: Zoo 1.114.0 (5cedc35) builds the torn edge, the spoil, the crew's kit and the floor hatch; Deli Counter 0.236.0 (9e720516) gives every drop in a floor a cause and stands them round it (`hole_causes.py`; layout_lint L28 names a hole that ships bare) -- 21 drops in 12 library specs, 30 slots, the tests failing without them, the library rebuilt, `check.py` passed. Left: a cold run with frames from above and below and the draws at its stations; the walker's eye; L28's uncaused holes -- foundry_heist_vertical's catwalk over its machine floor and lf_county_hospital_001's atriums and light well, where a guard rail or a curb, not damage, is the walker's call. Earlier status kept: OPEN 2026-10-19 -- the walker's call; in progress (Zoo species drawn and previewed in a clone, nothing shipped).*"
NEW_STATUS = "*STATUS: NARROWED 2026-10-20 -- THE CUT CAUSE PROVEN by cold runs 9340 and 9341 (restaurant_row_001, seed 9003, 0 interventions each): deli_a03's drop stands behind a torn concrete edge with the crew's kit beside it and the spoil below (`docs/cold_runs/cold_9340/holes_9339_vs_9340.jpg`, the same stations as 9339's). 9340 found the walk test's navmesh floored the hole over -- 0.236.0 drew the edge's greybox as one box over it and Lot bakes visual meshes too -- WALKTEST_WALKER_STUCK 0 -> 8; Deli Counter 0.236.1 (46a39afa) draws a ring round the hole (16 holes, 56.76 m2 covered on 0.236.0, none now) and 9341 read 8 -> 0, every other finding 9339's. Priced on 9341 against 9339 twice: +9 draws where a station sees the hole, p95 inside the 0.05 ms floor in two runs, +0.3 MiB. Left: the walker's eye on the frames (the spoil reads sparse; the kit's 0.35 m off the rim takes two of the hole's declared drop edges); a cold run on a `broken` and a `hatch` hole; L28's uncaused holes -- foundry_heist_vertical's catwalk and lf_county_hospital_001's atriums and light well, a guard or a curb the walker's call. Earlier status kept: NARROWED 2026-10-20 -- SHIPPED: Zoo 1.114.0 (5cedc35) builds the torn edge, the spoil, the crew's kit and the floor hatch; Deli Counter 0.236.0 (9e720516) gives every drop in a floor a cause and stands them round it (`hole_causes.py`; layout_lint L28 names a hole that ships bare) -- 21 drops in 12 library specs, 30 slots, the tests failing without them, the library rebuilt, `check.py` passed. Left: a cold run with frames from above and below and the draws at its stations; the walker's eye; L28's uncaused holes -- foundry_heist_vertical's catwalk over its machine floor and lf_county_hospital_001's atriums and light well, where a guard rail or a curb, not damage, is the walker's call. Earlier status kept: OPEN 2026-10-19 -- the walker's call; in progress (Zoo species drawn and previewed in a clone, nothing shipped).*"
BODY_END = "row-order placement). The rebuild moved the 12 specs' records and no other's; the suites 1,635 and 5,976 passed; `check.py` passed.\n"
BODY_ADD = '\n**THE FIRST COLD RUNS, 2026-10-20** (`docs/cold_runs/cold_9340/`, `cold_9341/`; `docs/findings/hole_causes_265/`, "The first cold run"). 9340 (Deli Counter 0.236.0, Zoo 1.114.0): 0 interventions, findings 110 -> 118, all eight WALKTEST_WALKER_STUCK -- every walker on both of deli_a03\'s candidates sent to a target inside the drop and stuck in its north-west corner against the slab\'s cut faces. One cause, attributed before the fix: the edge\'s greybox, one box over the hole with its top 12 mm above the floor, and Lot\'s walk navmesh parsing visual meshes (`geometry_parsed_geometry_type = 2`); `greybox_over_holes.py` measured every dressed hole in the library covered the same way. Deli Counter 0.236.1 (`patches/patch_dc_hole_ring.py`): a ring of four boxes outside the hole, its union the slot\'s footprint; 9341: 0 interventions, findings 110, WALKTEST_WALKER_STUCK 8 -> 0, the drop-edge gate as 9340\'s (0 undeclared; declared 20 -> 18, the kit\'s rim). The package strips the greybox\'s meshes and keeps the nodes, so the look is 9340\'s. **The price:** +1.4 draws a heading on average over 53, +9 where a station sees the hole (its nine submissions), the p95 median -0.02 and -0.00 ms in two runs of the subject against a 0.05 ms floor; the first run\'s +1.13 ms max (camera_socket_0 / 90) did not repeat (9.10 ms against the controls\' 9.04 and 9.23), and the same run read +1.05 ms on a heading whose draws did not move. **What the frames show:** from above, a ragged opening in a dark room with the kitchen\'s light coming up through it, the crew\'s tarp, saw, bag, cord and work light beside it, the light aimed in; from the kitchen, the ceiling broken back round a dark band of plenum, the slab\'s cut face and two tile shards hanging. The spoil reads sparse at play distance: left for the walker.\n'


def main():
    raw = ROADMAP.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: the roadmap has CRLF lines; nothing written")
    text = raw.decode("utf-8")
    if text.count(OLD_STATUS) != 1:
        raise SystemExit("REFUSED: roadmap 265's status is there %d times, not once; nothing written"
                         % text.count(OLD_STATUS))
    if text.count(BODY_END) != 1:
        raise SystemExit("REFUSED: roadmap 265's SHIPPED paragraph does not end where it did; nothing written")
    text = text.replace(OLD_STATUS, NEW_STATUS).replace(BODY_END, BODY_END + BODY_ADD)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 265 updated; now tools/roadmap_status.py --write and --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
