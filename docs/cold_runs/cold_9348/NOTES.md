# Cold run 9348 -- 0 interventions; bank_block_001, seed 9054: the first composed fronts in a package

**What it was for.** Deli Counter 0.238.0 (the factory's roadmap 79, `docs/proposals/FACADE_PLANNER.md` steps 1 and
3) moved 69 untagged upper-storey windows in 32 library specs onto the openings below them, mirrored pairs together,
within a bay. Level Factory's own lot draw replayed over the staged briefs found seed 9054 of bank_block_001 placing
two of them with a moved FRONT: bank_branch_a04 (its first-storey pair 10 -> 12 m off centre, over the ground floor's
windows either side of its centred main door) and casino_a03 (12.5 -> 10.5 m). Cold run 9282 is the same mission and
seed on earlier tools, so its package is the "before".

**Tools:** Deli Counter 0.238.0 (ac5f2135), Level Factory 0.222.0, Lot 0.125.0, Zoo 1.114.1, Lux 0.78.0. Staged from
9282; seed 9054 named.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0), read after `cold_run.py --end`; 8 min
09:12-09:20.
- **Shell:** 0 blockers of 73 findings; seed_9054 placed bank_branch_a04, casino_a03 and strip_retail_a02 with the
  terrace's Empties -- 9282's lot, building for building.
- **Art:** 0 blockers of 101 findings.
- **Export:** passed; the greybox census 0; the drop-edge gate 21 unguarded, 0 undeclared indoors; the light bake
  288 models and 94 primitive meshes lightmapped, 3,063 users, 19 failing fixtures left live.
- **Findings 102 -> 101** against 9282: `LT_MAP_TRAVERSAL` 1 -> 0.

## The fronts (`fronts_9282_vs_9348.jpg`; `front_station.py`)

A station square on each S face, 14 m out at 1.7 m, aimed at the face's centre 4.5 m up, computed from each package's
own placement (the two place both buildings identically): bank_branch_a04 at x -62, casino_a03 at x 6, both faces at
z 11. 9282 left, 9348 right; the inspection light (`look_shots.py --inspect studio`) and the level's own.
- **bank_branch_a04:** the two first-storey windows now stand over the ground floor's two, either side of the main
  door, and the front is still mirrored about the door.
- **casino_a03:** the first-storey pair moved 2 m in each, over the ground floor's pair; the truck and the cars stand
  in front of most of its ground floor from this station.
- **What else differs between the two frames is not this change:** 9282 is on tools from before 2026-10-13 -- the
  bank's small sign reads FIRST DELCO SAVINGS there and BANK here, among others.

Left for the walker: whether a stacked front reads better than the mirrored-but-unstacked one, and whether symmetry or
stacking wins where a face cannot have both (the proposal's question).
