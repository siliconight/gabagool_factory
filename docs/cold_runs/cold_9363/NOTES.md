# Cold run 9363 -- 0 interventions; bank_block_001, seed 9281: a bank lobby's teller-line queue

**What it was for.** Roadmap 275, the walker's "stanchion or stanchions are likley more common for banks and indoor
common areas": Deli Counter 0.244.0's `ticket_queue` lays a teller line's queue of Zoo 1.119.0's stanchion runs, and
leaves a queue out of furnish's count. Seed 9281 draws bank_branch_a02 (`lot_for_brief` over bank_block_001's brief,
seeds 9000 to 9300: 48 of 300 draw it), one of the four library banks 0.244.0 queued. Staged from 9352 with the
batch's `seed_base` set to 9281, so the shell built the candidate the drive names -- cold run 9362 named the seed
against 9352's `seed_base` and stopped (`docs/cold_runs/cold_9362/NOTES.md`).

**Tools:** Zoo 1.119.0 (3f54314) and Deli Counter 0.244.0 (33e81109); the rest as 9361 -- Level Factory 0.227.0, Lot
0.126.0, Lux 0.79.0, Dispatch 0.5.3, Patina 0.32.0, Laser Tag 0.32.0, Pipeline 0.6.0, Pixelcoat 0.62.0.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0), read after `cold_run.py --end`; 7.5 min
(01:14:54 to 01:22:21). Shell 0 blockers of 71 findings; art 0 of 99. No earlier run made this level, so the drive's
findings line compares against nothing (0 -> 99), and the export has no line-by-line control; its bake read 131 models
and 79 primitive meshes lightmapped, 116 steady rigs, 1,871 users.

**The queue, read from the package** (`lot/bank_branch_a02/site.tscn`): four `KitCollision` bodies at the four runs --
x 3.6 / 2.4 alternately, y -4.678, -6.234, -7.79 and -9.346 in building metres -- sharing one concave shape, the posts
and belt line Zoo's module carries, and no greybox box over a run; the runs' module merged with the building's
(`merge_buildings.json`: bank_branch_a02 325 slots merged, 217 meshes, 314 colliders).

**The frames** (`docs/findings/teller_queue_275/bank_queue_9363_inspect.jpg` and `_lit.jpg`, `shots.sh` with
`stations.py`, which turns stations given in the building's frame into the package's from its placement in
`site.tscn`): six stations in the inspection light, four in the level's own. The queue reads from every station that
faces it: four lines of black posts and belts switching back in front of the wood-and-glass teller counter, letting
out at its west end, a lane a body wide, the basement stair's railed opening clear behind it. In the night light the
lobby is dim and readable, the teller windows lit and the posts standing out against the floor.
