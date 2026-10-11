"""Roadmap 231 CLOSED: both levers landed, proven and priced on 9233's lot (cold runs 9236 and
9237), and both gates held. Replaces 231's status block (asserted once) and appends one body
paragraph after the item's last paragraph. The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_231_close.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = ("*STATUS: NARROWED 2026-10-11 -- the first lever is LANDED, PROVEN and PRICED, and it tripped "
                   "its own gate; the second is landed with the answer and in flight.")
STATUS_NEW = (
    "*STATUS: CLOSED 2026-10-11 -- both levers LANDED, PROVEN and PRICED on 9233's lot, and both gates held. "
    "Lever 1 (Lot 0.114.0, Level Factory 0.177.1-0.177.3; cold run 9236 against 9233's package): the road "
    "paint as one OBJ mesh a colour beside the scene, lightmapped; the site scene's pool from 795 box meshes "
    "and 178 materials to 568 and 55; -107 draws and -0.36 ms p95 a heading median on a 6.14 ms frame (noise "
    "0.08 ms; 39 of 53 headings faster beyond it, 4 slower by at most 0.41); the same seven stations in both "
    "packages read alike, the wear in the same places. Its paired census put each level-wide paint mesh under "
    "21 live lights against the cap of 8, so lever 2 took the cells with it. Lever 2 (Lot 0.115.0, Level "
    "Factory 0.178.0; cold run 9237 against 9236's package): the plate families on the 32 m baked tile where "
    "the spec says the lights bake and the paint one mesh a colour a 32 m cell; the pool from 568 box meshes "
    "to 112 and 570 nodes to 131, materials 55 still; -255 draws (every heading fewer, -48 to -557) and -0.39 "
    "ms p95 a heading median on a 5.65 ms frame (noise 0.27 ms this time, the second control 0.29 ms slower "
    "than the first; 46 of 53 faster beyond 0.08, none slower beyond the spread); the lot's one heading over "
    "16.7 ms from 18.3 and 19.7 to 16.8. Together, about -360 draws and -0.75 ms a heading median against "
    "9233's package: the second street's +107 draws and +0.55 ms paid back three times over. THE GATE HELD: "
    "9237's paired census reads no plate tile, slab, band or paint cell over 8 live lights (three at exactly "
    "8); the two meshes over the cap -- the horizon glow ring at 240 and one roof at 10 -- 9233's package "
    "carried before this item, the glow's material unlit and the roof's tubes under it, nil to the eye, "
    "recorded below as an observation. What this item leaves to its owners: Zoo's `PLATE_TILE` and Deli "
    "Counter's `SLAB_TILE`, the same law indoors, each its own decision; and a lot with poles left live and "
    "cycling along a street, the case the 32 m number has not been read against (every run here left 29 "
    "failing tubes live and no pole). Owner: Lot, with Level Factory's perf census as the gate.*")

BODY_TAIL = ("Zoo's `PLATE_TILE` and Deli Counter's `SLAB_TILE` are the same law indoors and have not moved; "
             "each is its own decision, after this one is measured.")
BODY_ADD = """

**LEVER 2 PRICED AND BOTH GATES HELD, 2026-10-11** (`docs/cold_runs/cold_9237/NOTES.md`). Cold run 9237, 9233's brief on Lot 0.115.0 + Level Factory 0.178.0, 0 interventions, every Lot job printing `plate tile 32 m: the site spec's render says the lights bake`; the bake 491 models (9236's 474 less two paint meshes plus 19 cells, every sidecar `generate_lightmap_uv2=true`) and 224 primitives where 9236 had 1,136. The pool (`draw_census_9236_9237.txt`): the plate's bands and tiles 377 to 50, road slabs 78 to 13, sidewalk bands 66 to 22, frontages 25 to 8, 568 boxes to 112 and 570 nodes to 131, the 55 materials untouched; across the three runs, 795 boxes and 795 nodes to 112 and 131, 178 materials to 55. The price against 9236's package: -255 draws a heading median and every heading fewer, -0.39 ms p95 median on a 5.65 ms frame, the worst heading (player_start_19 yaw 90) from 18.28 and 19.70 ms to 16.78 with 548 fewer draws, longest_sightline and patrol_point_13 at yaw 270 -1.7 to -1.8 ms; 46 of 53 headings faster beyond 0.08 ms, one slower by 0.09, none beyond the controls' spread -- which was 0.27 ms this time, the second control run 0.29 ms slower than the first at the median and 2.16 ms on one heading, the harness's own variance on the night, so the draws (which do not vary) are the cleaner reading and the time is read against it. The frame time is the tile's and the cells' together; the pool separates them (the cells add 17 nodes, the tile removes 456 boxes) and 17 draws are below the noise. The paired census on 9237's package: no plate tile, slab, band or paint cell over 8 live lights -- a tile four times the side sits under the same failing tubes, which are indoors -- and the histogram's tail is three meshes at exactly 8, the roof at 10, the glow at 240, as 9236's was without its two 21s.

**AN OBSERVATION, NOT THIS ITEM'S DEFECT:** two meshes in every package of this lot since 9233 pair with more than 8 live lights -- `LuxHorizonGlow` (235-240; its box is the sky and its material unlit, so the pairs light nothing) and `b0/roof_footprint/Roof_brick_delco_1997` (10; a building's roof mesh under the failing tubes inside it, which cannot light a roof from below). The cap drops lights on both and the eye sees neither. The count is cited here so that a future census reading "2 over" on a street lot is recognised as these two and not read as a regression; a roof under a live rooftop fixture would be a different reading, and the census would say so.

**WHAT IT LEAVES, AND TO WHOM.** Zoo's `PLATE_TILE` and Deli Counter's `SLAB_TILE` are the same 8 m law indoors, priced against live lights before the bake; under the bake they cost draws the same way (9233's 1,136 primitives lightmapped were mostly theirs and Lot's), and each is its owner's decision with the same census as its gate -- roadmap 54's half that this item did not take. A lot with poles left live and cycling along a street is the case the 32 m number has not been read against: every run on this brief left 29 failing tubes live indoors and no pole, so the census here could not have tripped on a pole; `Lux`'s cycling poles over a 32 m tile or a paint cell is the reading to take when such a lot is next priced."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF count means something changed"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "231's status block not found once"
    j = text.find("\n", i)
    old_status = text[i:j]
    assert old_status.endswith("*") and old_status.count("*STATUS:") == 1, old_status[-80:]
    assert text.count(BODY_TAIL) == 1, ("231's last paragraph not found once", text.count(BODY_TAIL))
    assert "LEVER 2 PRICED AND BOTH GATES HELD" not in text, "already applied"
    new = text[:i] + STATUS_NEW + text[j:]
    k = new.find(BODY_TAIL) + len(BODY_TAIL)
    assert new[k:].strip() == "", "231 is no longer the last item: re-anchor the body addition"
    new = new[:k] + BODY_ADD + "\n"
    assert "\n\n**231. " in new[new.find(STATUS_NEW):new.find(STATUS_NEW) + len(STATUS_NEW) + 40]
    RM.write_bytes(new.encode("utf-8"))
    print("roadmap 231: CLOSED, three paragraphs appended; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
