"""Roadmap 179 and 244, 2026-10-12 night: the street's drains placed and drawn (Lot 0.120.0, cold run 9269)
and their grates stepped past the paint (Lot 0.120.1, cold run 9270); and the kerb the same printout
found, filed as 244 -- a marked crosswalk that lands on a raised kerb.

Replaces 179's status (asserted once, and still directly above its heading), appends one paragraph to
179's body (before 180's status), and appends item 244 at the end of the file, after 243. The index is
NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_179_244_drains.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S179_OLD = ("*STATUS: OPEN 2026-10-04 -- FILED FOR LATER by the walker, with five photographs. Nothing places "
            "either today: no species, no placement rule, no skin.*")
S179_NEW = ("*STATUS: NARROWED 2026-10-12 -- placed and drawn by Lot: 0.120.0 (a manhole cover at every junction "
            "and along a run past 121.9 m, a storm inlet a corner, a lid in the sidewalk behind one; floaters, with "
            "the art only) and 0.120.1 (a grate steps past the paint: 0.120.0 stood four of cold run 9269's eight "
            "over a crosswalk bar). Cold runs 9269 and 9270, 0 interventions each; priced on 9269 at +1.2 draws a "
            "heading (0 to +5) and p95 +0.03 ms against a 0.05 ms floor. Left: inlets between corners (they need "
            "a grade and a design storm); the walker's eye on the frames; and, if that eye asks more of the iron "
            "than a flat colour, the Zoo species and Pixelcoat iron this item first assigned.*")

BODY_179 = """

**PLACED AND DRAWN, 2026-10-12 night** (`docs/reference/STREET_DRAINS.md`; `docs/cold_runs/cold_9269/`, `cold_9270/`). The rules were read at source first, as the hydrant's were: Ten States' 400 ft (121.9 m) between sanitary manholes on sewers of 15 in and under; TxDOT's storm inlet upstream of a crosswalk; a 24 in sewer frame and cover (the lid 25 5/16 in, the frame 32 3/16 in) and a 2 x 3 ft curb inlet grate from standards and catalogues. Lot 0.120.0 (`site_drains`, `patches/patch_lot_drains.py`) stands a cover at every road-road junction's centre and along a run, an inlet a corner by the hydrant's `corner_key`, and a lid in the sidewalk a step behind an inlet, no two lids nearer than the hydrant's 45.7 m. Each piece is a floater by 234's rule (a 4 mm skirt, 3 mm proud of the paint). They are drawn as one mesh a material a 32 m cell, in an OBJ beside the scene as the paint and the wires are, lightmapped, casting no shadow, with no collision, and with the art only: the graded lots carry none (242). **WHO OWNS WHAT, AS BUILT -- not as assigned above:** the covers and grates are Lot's generated meshes, as the paint and wires are, and their iron is a flat colour, not a Zoo species in a Pixelcoat skin; flush pieces merged by cell are 8 meshes a site, at most 5 drawn at a heading. Cold run 9269 (0 interventions): 4 covers, 8 inlets, 4 lids, 4,184 triangles in 8 OBJs; +1.2 draws a heading, p95 +0.03 ms against a 0.05 ms floor. **FOUND BY LOOKING, NOT BY AN INSTRUMENT:** 9269's corner frame showed a grate against a crosswalk's bar. Read off the package (`cold_9269/drain_paint.py`: each piece's footprint from the shipped OBJs against the job's `site.markings.json`), four of the eight grates lay over a bar, 0.155 m^2 each (27.8 % of the grate), all on the main road at its two T's. A through road's crosswalks lie in line with the side street's sidewalks, outside the kerb's dropped stretch the grate was placed against. Lot 0.120.1 (`patches/patch_lot_drains_paint.py`) steps a grate along the kerb past any marking nearer than a hand, the lines along a road excepted; on that lot the four move 2.15 m. Cold run 9270 (0 interventions): all eight grates clear of the paint, the four moved ones exactly 0.300 m from the bar each passed, with their two lids. Two covers lie on a bar at the lane's junctions and are kept: the walker's photograph has a cover out in a crosswalk. **THE WHOLE-FRAME DIFF COULD NOT SEE THEM:** at 9269 a control station moved 2.7 % of its pixels past 8 codes, as much as the drain stations did; a map of the pixels past 32 codes separated them. Measured (`cold_9269/lm_users.gd`): adding the 8 meshes repacked the lightmap atlas -- of the 3,338 users both bakes carry, 127 kept their rect and slice. 9270, which added none, kept all 3,346, and its controls stayed quiet (0.187 % and 0.000 %). A change that adds a bake user re-bakes the whole level's light in a new layout, and a frame comparison across it has to read its controls. The same printout of the kerbs found roadmap 244."""

ITEM_244 = """

*STATUS: OPEN 2026-10-12 -- found, not started. On cold run 9262's lot (seed_9104) 25 % of the crosswalks' kerb ends are dropped (11.80 of 48.00 m); the rest of each walk meets a full kerb.*

**244. A marked crosswalk lands on a raised kerb.** Found reading Lot's kerbs for roadmap 179 (`docs/cold_runs/cold_9269/NOTES.md`). Lot drops a kerb where another road or a path crosses it: the crosser's carriageway and `CUT_MARGIN` (0.6 m) each side (`site_streets.split_span`). It paints the crosswalks where people walk, in line with the crossing street's sidewalks (`site_streets.crossing_walks`) -- outside the dropped stretch. Measured on seed_9104's lot, for every painted walk and each of its two kerbs (the site's own `site_streets.roads`):
  * the main road's four crosswalks, one each side of its two T's, meet its north kerb dropped for 0.35 m of the 2.50 m painted, and its south kerb -- which has no cut at all -- not at all;
  * each side street's mouth crosswalk meets its two kerbs dropped for 0.35 m each;
  * the lane-mouth crosswalks meet the lane's side dropped whole and the far kerb not at all.

In all, 11.80 of 48.00 m of crosswalk ends are dropped (25 %).

**WHAT IT IS AND IS NOT.** It is not a traversal fault: the kerb is `SIDEWALK_H` = 0.0974 m, 0.95 of the contract's unassisted step (0.1025 m), which the contract body mounts from bare ground. It is the street reading as generated -- a marked crosswalk that ends at a full kerb face is not a street anybody built. The rule a source would settle is the ADA's and PROWAG's: that a marked crosswalk ends in a curb ramp at both ends, and the ramp's width, slope and flares. Not yet read, so no number is written down here.

**WHO OWNS WHAT.** Lot, in `site_streets`' kerb model: a cut where each crosswalk lands, on both kerbs, the walk's width plus `CUT_MARGIN`. The drains' inlets (179) would step past it by the rule they already follow. **CAREFUL:** the graded greybox lots carry the kerbs, so a cut moves what Laser Tag and the walk test grade -- 242's lesson that a grade moves with any change to what stands on a lot. Price the change on the graders before judging the look."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "PLACED AND DRAWN, 2026-10-12 night" not in text and "\n**244. " not in text, "already applied"
    for key in ("RESULT_9270", "RESULT_ATLAS"):
        assert key not in BODY_179, "fill %s before applying" % key
    assert text.count(S179_OLD) == 1, "179's status not found once"
    text = text.replace(S179_OLD, S179_NEW)
    h = text.find("\n\n**179. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert h > 0 and text[s + 2:h] == S179_NEW, "179's status does not sit directly above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    # no other item's heading between 179's and the next status (a bold lead-in is not one)
    assert nxt > h and text.find("\n\n**180. ", nxt) > nxt \
        and not re.search(r"\n\n\*\*\d+\. ", text[h + 10:nxt]), "180 does not follow 179"
    text = text[:nxt] + BODY_179 + text[nxt:]
    last = text.rfind("\n\n**243. ")
    assert last > 0 and text.find("\n\n*STATUS:", last) < 0 and text.endswith("\n"), "243 is not the last item"
    text = text.rstrip("\n") + ITEM_244 + "\n"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 179: status and a paragraph; 244 filed; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
