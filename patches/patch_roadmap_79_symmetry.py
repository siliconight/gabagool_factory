"""Roadmap 79 stays OPEN: its status and body take predict.py's full table -- moving the upper storeys goes part of
the way, symmetry is what it costs -- with the same-day refutation of the first reading kept
(docs/findings/facade_census_79/).

Anchored: two passages read verbatim from the roadmap when this was written must each be there exactly once; nothing
is written otherwise. Every line LF. Then `python tools/roadmap_status.py --write` and `--check`.

    python patches/patch_roadmap_79_symmetry.py
"""
import pathlib
import sys

ROADMAP = pathlib.Path(__file__).resolve().parents[1] / "PIPELINE_ROADMAP.md"
EDITS = [("roadmap 79's status sentence", "Moving only the 170 untagged upper windows cannot compose a face (`predict.py`): equal centred bays drop stacking over the ground floor to 5, and the best grid through the ground floor's own openings reaches 139 by moving windows a median 2.5 m and up to 22 m, 8 into another room. So the grid has to be chosen where the openings are first chosen, the spec's authoring, and the proposal puts the planner there:", "The upper storeys were authored mirrored about their face's centre (167 of 177 openings) and the ground floors for the rooms behind them (135 of 321), so while the ground floor holds, stacking and symmetry trade (`predict.py`, the 170 untagged upper windows): onto the opening below within a bay, 99 stacked and 44 openings lose their mirrored partner; the same move in mirrored pairs only (`over sym`), 74 stacked with every mirrored opening kept, 46 windows moved in 22 buildings, none into another room; equal centred bays, 5; the best grid through the ground floor's own openings, 139, by moves up to 22 m. REFUTED THE SAME DAY and kept: this status first said moving the upper windows cannot compose a face, read off the half-bay row alone (17 moved). A face both stacked and symmetric needs its ground floor laid out with the grid, the spec's authoring, and the proposal puts the planner there:"), ("roadmap 79's measured paragraph", "\n**MEASURED, 2026-10-20** (`docs/findings/facade_census_79/`: `census.py` reads the built library's slots, `predict.py` prices four candidate grammars before anything is built). The critique's first bullet has a number now -- 28 of 169 first-storey openings over a ground-floor one, against the Empties' 92.9 % -- and so does the reason an emitter-side fix cannot reach it: holding the ground floor where gameplay put it, equal bays upstairs move windows under a metre and stack 5; a grid through the ground floor's openings stacks 139 and moves windows up to 22 m. The two were laid out independently. Within one storey the openings are already evenly spaced (43 of 62 runs). `docs/proposals/FACADE_PLANNER.md` owns the mechanism this item asks for and leaves the grammar to its rows' sources.\n", "\n**MEASURED, 2026-10-20** (`docs/findings/facade_census_79/`: `census.py` reads the built library's slots, `predict.py` prices candidate grammars before anything is built). The critique's first bullet has a number now -- 28 of 169 first-storey openings over a ground-floor one, against the Empties' 92.9 % -- and so does why: the upper storeys were authored to one rule, mirrored about the face's centre (167 of 177 openings), and the ground floors to another, the rooms behind them (135 of 321 mirrored). Within one storey the openings are already evenly spaced (43 of 62 runs). Holding the ground floor where gameplay put it, the upper windows can be moved part of the way: in mirrored pairs onto mirrored openings below, within a bay, 46 windows in 22 buildings, stacking 28 to 74 and keeping every mirrored opening; a plain move within a bay stacks 99 and breaks 44. Refuted the same day and kept in the finding: the first reading priced that move at half a bay only (17 windows) and concluded the upper storeys could not be moved toward a composition at all. `docs/proposals/FACADE_PLANNER.md` owns the mechanism this item asks for and leaves the grammar to its rows' sources; its third step is the mirrored-pairs migration.\n")]


def main():
    raw = ROADMAP.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: the roadmap has CRLF lines; nothing written")
    text = raw.decode("utf-8")
    for what, old, new in EDITS:
        if text.count(old) != 1:
            raise SystemExit("REFUSED: %s is there %d times, not once; nothing written" % (what, text.count(old)))
    for what, old, new in EDITS:
        text = text.replace(old, new)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 79 updated; now tools/roadmap_status.py --write and --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
