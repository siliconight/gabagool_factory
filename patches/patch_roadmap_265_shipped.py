"""Roadmap 265 NARROWED: Zoo 1.114.0 and Deli Counter 0.236.0 shipped (every hole in a floor has a cause).

Anchored: the item's whole OPEN status line and the last 160 characters of its body, read verbatim from the roadmap
when this was written, must each be there exactly once, the body followed by item 266's status; nothing is written
otherwise. Every line LF. Then `python tools/roadmap_status.py --write` and `--check` regenerate and verify the index.

    python patches/patch_roadmap_265_shipped.py
"""
import pathlib
import sys

ROADMAP = pathlib.Path(__file__).resolve().parents[1] / "PIPELINE_ROADMAP.md"
OLD_STATUS = "*STATUS: OPEN 2026-10-19 -- the walker's call; in progress (Zoo species drawn and previewed in a clone, nothing shipped).*"
NEW_STATUS = "*STATUS: NARROWED 2026-10-20 -- SHIPPED: Zoo 1.114.0 (5cedc35) builds the torn edge, the spoil, the crew's kit and the floor hatch; Deli Counter 0.236.0 (9e720516) gives every drop in a floor a cause and stands them round it (`hole_causes.py`; layout_lint L28 names a hole that ships bare) -- 21 drops in 12 library specs, 30 slots, the tests failing without them, the library rebuilt, `check.py` passed. Left: a cold run with frames from above and below and the draws at its stations; the walker's eye; L28's uncaused holes -- foundry_heist_vertical's catwalk over its machine floor and lf_county_hospital_001's atriums and light well, where a guard rail or a curb, not damage, is the walker's call. Earlier status kept: OPEN 2026-10-19 -- the walker's call; in progress (Zoo species drawn and previewed in a clone, nothing shipped).*"
BODY_END = " fail without them, the library rebuilt, a cold run per cause with frames from above and below, the hole's price in draws at its stations, and the walker's eye.\n"
BODY_ADD = "\n**SHIPPED, 2026-10-20.** Zoo 1.114.0 (5cedc35, `patches/patch_zoo_hole_causes.py`) and Deli Counter 0.236.0 (9e720516, `patches/patch_dc_hole_causes.py`); the investigation `docs/findings/hole_causes_265/`. A drop's cause is its link's own `cause`, else `stair` where its hole opens into a stair's well, else `hatch` for a hatch link, else a row of `hole_causes.RULES` by its rooms. Measured on the library: 21 drops in 12 specs -- `cut` 6 (the delis, `cut_slab`: a concrete floor over a drop ceiling), `broken` 2 (the walk-ups, the spoil on tile), `hatch` 8, `stair` 4, uncaused 1 -- 30 slots; Level Factory's `lf_` transients 40 drops more, 9 uncaused, every one lf_county_hospital_001's atriums and light well. **This item's body, corrected:** 12 specs carry a drop, not 13 (the first count does not reproduce; bank's atrium is a slab hole, not a drop); foundry's skylight room over its archive is a `hatch` link and ships as a floor hatch, not `cut`; a deli's cut hole is 9 draw submissions (edge 3, spoil 3, kit 3, `cut_slab`), not seven materials. **Found on the way, kept:** deli_a01-a03's drop to the stairwell and rowhouse_raid's hatch are cut inside a stair's own well -- the first build stood a floor hatch over each and Deli Counter's circulation gate read its frame 0.03 m inside the stair's column; now `stair`, nothing round it, and the twelve specs built on 0.235.0 and on 0.236.0 show no new conflict. A slot outside its species' sizes would be built as a plain box over the hole, so it is left out. Two float tie-breaks (a kit's side, a spoil's cut-back) and three Zoo spoil defects (a bar set askew onto a fragment, the ceiling's pieces crowded out of a small slot, the floor's finish riding only the sawn panels), each with its numbers in the CHANGELOGs. Tests that fail without them: Deli Counter's 17 (the file does not collect on 0.235.0; with the module alone beside it 8 fail) and Zoo's 601 (the every-kind case 23 of 64 on row-order placement). The rebuild moved the 12 specs' records and no other's; the suites 1,635 and 5,976 passed; `check.py` passed.\n"
NEXT = "\n*STATUS: OPEN 2026-10-19 -- measured, not started.*"


def main():
    raw = ROADMAP.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: the roadmap has CRLF lines; nothing written")
    text = raw.decode("utf-8")
    if text.count(OLD_STATUS) != 1:
        raise SystemExit("REFUSED: roadmap 265's OPEN status is there %d times, not once; nothing written"
                         % text.count(OLD_STATUS))
    if text.count(BODY_END + NEXT) != 1:
        raise SystemExit("REFUSED: roadmap 265's body does not end where it did, before 266's status; nothing written")
    text = text.replace(OLD_STATUS, NEW_STATUS).replace(BODY_END + NEXT, BODY_END + BODY_ADD + NEXT)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 265 NARROWED; now tools/roadmap_status.py --write and --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
