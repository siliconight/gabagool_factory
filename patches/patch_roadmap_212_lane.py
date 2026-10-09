"""Roadmap 212: the lane steers and the vehicle is Zoo's, proven by cold runs
9206 and 9207; what is left is the cruiser in the package.

Anchored on 212's status tail, the "let the lane steer" bullet, and the
Zoo 1.86.0 section's last line; each must match exactly once, or nothing
is written.
"""
import pathlib
import sys

ROADMAP = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory\PIPELINE_ROADMAP.md")

EDITS = [
    # the status line's open list
    ("Open: the cruiser into a level -- Lot's responder slot derived from it, the asset in the package for the "
     "gameplay layer to spawn, and a price; `S_RESPONDER_ARC` firing where a site's roads lie to one side of the "
     "objective; and the getaway van closing every lane that has to pass it, which cost cold run 9204 one arrival "
     "of three.*\n",
     "Lot 0.100.0 and 0.100.1 size the arrivals for that cruiser and steer a lane round what stands in it, and "
     "Level Factory 0.161.0 ships the steered lanes: cold runs 9206 and 9207 (club_block_014, 0 interventions "
     "each) took `LOT_RESPONDER_ENTRY_NO_STOP` 2 to 0, three arrivals on every candidate, each candidate one lane "
     "steered 0.649 m round the getaway van, every stop walked by Lot's nav QA. Open: the cruiser itself in the "
     "package for the gameplay layer to spawn, and a price; `S_RESPONDER_ARC` firing where a site's roads lie to "
     "one side of the objective.*\n"),
    # the NEXT bullet that this closes
    ("- **Lot: let the lane steer round the van.** Cold run 9204's club_block_014 lost one arrival of three to "
     "the getaway van (`docs/findings/responder_entry_no_stop/`, which replays Lot's planner on the job's inputs "
     "and reproduces its record).\n",
     "- **Lot: let the lane steer round the van.** *Done, below: Lot 0.100.0 and 0.100.1, cold runs 9206 and "
     "9207.* Cold run 9204's club_block_014 lost one arrival of three to the getaway van "
     "(`docs/findings/responder_entry_no_stop/`, which replays Lot's planner on the job's inputs and reproduces "
     "its record).\n"),
    # the new section, after the Zoo 1.86.0 section
    ("  - **The livery is the walker's to choose.** Both are shown in the finding's frames.\n",
     "  - **The livery is the walker's to choose.** Both are shown in the finding's frames.\n"
     "\n"
     "**LOT 0.100.0 AND 0.100.1, LEVEL FACTORY 0.161.0, DONE: THE VEHICLE IS ZOO'S AND THE LANE STEERS "
     "(2026-10-08)** (`patches/patch_lot_responder_lane.py`, `patch_lot_responder_precision.py`, "
     "`patch_lf_lane_boxes.py`).\n"
     "- **The vehicle.** `site_responders.VEHICLE` is the cruiser genome's defaults, 2.196 x 5.545 x 1.578, "
     "pinned with a test that reads Zoo's genome when Zoo is beside Lot. `MIRROR_OUT` (0.105) separates the two "
     "widths: the stop's door room is measured from the 1.986 m body, the lane from the mirrors.\n"
     "  - 0.99.0's 2.0 m, which it called a width \"to the mirrors\", was the body's published width.\n"
     "- **Why the lane had to steer in the same change.** The mirror width widens the lane box to 3.196 m. On "
     "9204's site that box would overlap the van by 0.648 m, where the 3.0 m box overlapped it by 0.55.\n"
     "- **How it steers.** The lane is 1 m slices.\n"
     "  - **The shift.** Each slice moves toward and across the centre line by the least shift that clears what "
     "stands there.\n"
     "  - **The bound.** It may go as far as the oncoming driving half's outer edge.\n"
     "  - **The taper.** MUTCD 6C.08's shifting-taper rate: 120/S^2 across per metre along, 0.192 at a stated "
     "25 mph.\n"
     "  - **The return.** It is back in its own half by the stop.\n"
     "  - **The record.** `lane_boxes` with `lane_shift`; Level Factory 0.161.0 ships them as "
     "`responder_arrivals.json` schema v2.\n"
     "- **Cold run 9206** (`docs/cold_runs/cold_9206/NOTES.md`, 0 interventions):\n"
     "  - `LOT_RESPONDER_ENTRY_NO_STOP` 2 to 0;\n"
     "  - three arrivals in the package, the east end's lane steered 0.648 m in nine boxes;\n"
     "  - six bot spawns in Lot's nav QA, the three stops among them, and all 20 walkers `ok`.\n"
     "- **Found by 9206, a phantom.** It carried a new major on seed_9080, `LOT_RESPONDER_BLOCKED`: the van in "
     "a lane.\n"
     "  - **What happened.** The planner had cleared the van by 1e-6 m and checked the unrounded box. The record "
     "rounded the box's edge onto the van's: -28.22 against -26.92 - 1.3 = -28.220000000000002.\n"
     "  - **What the read-back saw.** It checks recorded boxes, and found 3.6e-15 m of overlap.\n"
     "  - **The fix, Lot 0.100.1.** The planner rounds each box once, checks it and records it, and clears by "
     "1 mm.\n"
     "- **Cold run 9207** (`docs/cold_runs/cold_9207/NOTES.md`, 0 interventions): `LOT_RESPONDER_BLOCKED` 1 to "
     "0. Every candidate gets three arrivals and no responder finding, and each steers one lane, 0.649 m round "
     "its van.\n"
     "- **The van's lane is the same on every site.** The van's 0.45 m overhang is fixed by design, so each "
     "site's van lane needs the same shift.\n"
     "- **Not done: the cruiser in the package.** The gameplay layer spawns responders, so the car must ship "
     "beside `responder_arrivals.json`, not stand in the scene.\n"
     "  - **The route.** Lot gives the arrivals kit slots, so Zoo's site kit builds the car. The themed "
     "assembly copies the module to a new `vehicles/` sibling without standing it, and writes which file it "
     "is. Level Factory adds `vehicles` to its sibling list and names the car in `responder_arrivals.json`.\n"
     "  - **Not built yet.** Then a price.\n"),
]


def main():
    data = ROADMAP.read_bytes()
    if b"\r\n" in data:
        sys.exit("refusing: the roadmap has CRLF endings; it is LF")
    text = data.decode("utf-8")
    for old, _new in EDITS:
        n = text.count(old)
        if n != 1:
            sys.exit("refusing: an anchor matches %d times:\n%s" % (n, old[:120]))
    for old, new in EDITS:
        text = text.replace(old, new)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 212 updated; %d -> %d bytes" % (len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
