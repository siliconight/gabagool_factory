# Cold run 9321 -- urban_row_001 on Deli Counter 0.226.0 + Lot 0.125.0 + Dispatch 0.5.3 + Level Factory 0.216.1 (2026-10-18): the declared drops reach the package, and the gate claims them

Staged from 9320, whose export the new drop-edge gate refused because the declared drops' nav links stopped at
Level Factory's own staging (`../cold_9320/NOTES.md`). The only tool change between them is Level Factory 0.216.1
(c62b873): `stage_dispatch_inputs` carries `vertical_links` verbatim on both sides.

**Run:** 0 interventions (journal 0, unattributed files 0), drive exit 0. Three candidates; the pick is seed 9104
again, PASS 100, route completion 1.00, 0 major -- the same pick and grade as 9317, 9318 and 9320. Findings 109
-> 109 against 9320. The package shipped (`export.log`), with the closure verdict clean (0 issues, 0 missing) and
`drop_edges.json` and `drop_edges_scan.json` listed in `portable_resource_manifest.json`.

**The links, read off the package** (`navigation_hints.json` `links[]`, Godot metres):

    lot:deli_a01_floor_hole_1_8_-4_navlink   drop   (-43.0, 3.3, 1.49) -> (-43.0, 0.0, 1.49)    one-way, hole (-44.1,-2.59)-(-41.9,-0.39)
    lot:deli_a01_hatch_1_-12_8_navlink       drop   (-63.0, 3.3, -10.51) -> (-63.0, 0.0, -10.51) one-way, hole (-63.7,9.81)-(-62.3,11.21)
    lot:night_deli_ladder_0_navlink          climb  (-43.0, 0.0, 9.49) <-> (-43.0, 6.6, 9.49)
    lot:night_deli_ladder_1_navlink          climb  (-58.0, -3.3, 10.49) <-> (-58.0, 0.0, 10.49)

9320's package carried the two climbs and neither drop.

**The gate** (export step 4.88, Level Factory's own copy of the instrument, bounded by the nav nodes):

    drop edges: 52130 reached of 64937 standable cells, 54 unguarded drop edge(s): 10 a flight's own side,
      20 at a declared drop, 13 at a ladder's shaft, 3 a thing's top, 8 outdoors (reported), 0 UNDECLARED indoors

The 20 are the deli's floor hole, claimed off the package's own link. They are the same rows the gate refused
on 9320.

**The cross-check** (the factory's `tools/walkable_edge.gd` unbounded on a copy of the package, the session's
`edge_9321.sh`; `docs/findings/drop_edges_173/edges_9321.*`, `sort_9321.out.txt`): 1,521 x 1,521 cells,
115,022 standable, 88,243 reached, 929 drops, 872 guarded, 54 unguarded, 46 indoors. These are the same 54 rows
as the gate's bounded run, indoors and out. The sort reads the package's links as `drop 2, climb 2`, and its
`declared_link` class claims the 20 floor-hole rows. Before the links shipped it classed those rows `floor_hole`
16 and `slab_cut` 4. `body_names_9321.log` is byte-identical to 9318's.

**Not proven here.** The flood resolves neither drop link (links used 2, unresolved 2, in both runs): a drop
link starts over its hole, and no standable surface lies within the metre the instrument searches. The floors
here are reached by their stairs, so nothing went unasked. A floor reachable only by a drop would be. The
drive's clean job took cold-9316-ws and cold-9317-ws (2.4 GB) by `tools/factory_retire.py`'s pushed-runs rule.
