"""Roadmap 266 NARROWED: the enterable buildings' merge shipped as Level Factory 0.223.0 and 0.224.0, priced four
times against two controls each (docs/findings/interior_merge_266/, docs/cold_runs/cold_9349/).

Anchored: the item's status block with its heading, and the end of its body with the next item's status, read
verbatim from the roadmap when this was written, must each be there exactly once; nothing is written otherwise.
Every line LF. Then `python tools/roadmap_status.py --write` and `--check` regenerate and verify the index.

    python patches/patch_roadmap_266_merge.py
"""
import pathlib
import sys

ROADMAP = pathlib.Path(__file__).resolve().parents[1] / "PIPELINE_ROADMAP.md"
HEADING = "**266. Enterable buildings' interiors merge per room and material.**"
STATUS_OLD = "*STATUS: OPEN 2026-10-19 -- measured, not started.*\n\n" + HEADING
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-20 -- SHIPPED AND PRICED: Level Factory 0.223.0 (4174d64, "
    "`patches/patch_lf_merge_buildings.py`) merges every enterable building's static modules in the export, after the "
    "Empties' merge and before the light bake, per material within a unit -- a wall side of a storey, a partition run, "
    "a parapet side, the roof, or a 6 m cell of the room a piece stands in, the rooms read off Lot's site record into "
    "each building's frame -- its colliders copied whole, the module GLBs no file names dropped; interactive slots, "
    "openings, light fixtures, anything animated, scripted or shader-driven, the greybox base and the covers left as "
    "they are; on by default, `export --no-merge-buildings` ships one module a slot. 0.224.0 (f754562, "
    "`patches/patch_lf_lit_face_split.py`) gives a lit face that is not a fixture's (`M_*_Face`, a sign, a screen) a "
    "mesh of its own per instance where it stood and merges the rest of its module. Priced at 53 station-headings, two "
    "controls each (`docs/findings/interior_merge_266/`): cold run 9349's package (restaurant_row_001, 0 "
    "interventions, 1,643 surfaces -> 789 meshes) against itself exported unmerged, draws 38,938 -> 34,531 and 34,439 "
    "(-83 and -85 a heading, 11 %, 418 at most); 0.224.0 on a copy, -85 and -81; p95 frame time -0.18 to -0.25 ms a "
    "heading in four of the five runs of the shipped path (9347's copies once, 9349 four times) against floors of "
    "0.097 and 0.131, +0.156 in one; the worst heading 9.95 / 10.33 -> 9.13 / 9.96 ms on 9349; the meshes over the "
    "8-light cap the control's 9 in every shipped arm. The cost: a 2048 x 1024 "
    "lightmap where the control's is 1024 x 1024, about 4 MiB of video memory. REFUSED ON THE LIGHT CAP and kept: one "
    "unit a storey (19 meshes over the cap), whole rooms (11), and 0.224.0's first cut, the fixtures' housings merged "
    "per cell (11, two cells pairing 10 lights), though it was the fastest arm. Left: frames of a shipped package "
    "against its control (the prototype's were compared; a merge changes the lightmap's users, 3,524 -> 2,880, so "
    "they cannot be compared user by user), the low-end target's frame time, a unit that lets a fixture's housing "
    "merge, and the 6 m cell's derivation (measured on one level).*\n\n" + HEADING)
BODY_OLD = ("and the walker told what it cost and bought.\n\n*STATUS: OPEN 2026-10-20 -- measured "
            "(`docs/findings/asset_wishlist_2026-10-19/box_slots.py`), not started.*\n")
BODY_NEW = (
    "and the walker told what it cost and bought.\n\n"
    "**SHIPPED, 2026-10-20** (`docs/findings/interior_merge_266/`; Level Factory 0.223.0 and 0.224.0; cold run 9349). "
    "The prototype was priced in three versions on copies of cold run 9347's package, each arm re-baked by Level "
    "Factory's own bake, and WHAT THE UNIT IS decided it: a storey-wide unit cut 87.6 draws a heading and paired 14 "
    "lights on one mesh; whole rooms paired 11 meshes over the cap; rooms cut into 6 m cells kept the control's 9 and "
    "cut 79.6; the export's path is the third. The census that counted the merge's keys first read the buildings' "
    "transforms straight after `add_child`, got the identity and put every unnamed piece on one storey (refuted, "
    "kept); made to wait a frame, it agrees with the merge to the key. On this desktop GPU, at about 4 ms a frame, submission is not what a frame waits "
    "on, so the draws fall every time and the frame time by less than a third of a millisecond and not every time; "
    "the merge is bought for the low-end target the packages ship for. 0.224.0's lit-face split changes nothing on "
    "a level without lit screens (9349's 6 lit faces, the same 2,953 mesh instances); it is what keeps Zoo 1.115.0's "
    "desks, whose screens are lit (roadmap 148), in their rooms' meshes.\n\n"
    "*STATUS: OPEN 2026-10-20 -- measured (`docs/findings/asset_wishlist_2026-10-19/box_slots.py`), not started.*\n")
EDITS = [("roadmap 266's status", STATUS_OLD, STATUS_NEW), ("the end of roadmap 266's body", BODY_OLD, BODY_NEW)]


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
    if text.count(HEADING) != 1:
        raise SystemExit("REFUSED: the heading is not there once after the edit; nothing written")
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 266 updated; now tools/roadmap_status.py --write and --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
