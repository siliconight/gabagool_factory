# Cold run 9320 -- urban_row_001 on Deli Counter 0.226.0 + Lot 0.125.0 + Dispatch 0.5.3 + Level Factory 0.216.0 (2026-10-18): STOPPED at the export, by the new gate

Staged from 9318 after 9319 died on a full disk (`../cold_9319/NOTES.md`). Two jobs: the package proof that a
declared drop's nav link reaches `navigation_hints.json` (roadmap 173, step 3), and the first export through
Level Factory 0.216.0's drop-edge gate (8520801, step 4.88 of the export).

**Run:** 0 interventions (journal 0, unattributed files 0). Three candidates; the pick is seed 9104 again, PASS
100, route completion 1.00, 0 major -- the same pick and grade as 9317 and 9318. The art stage passed. The
EXPORT REFUSED (`export.log`, exit 5, `STOPPED: export`, drive exit 2), so no package shipped:

    UNDECLARED_DROP_INDOORS: 20 unguarded edge(s) a body reaches, indoors, on a floor, that nothing declares
    drop edges: 52130 reached of 64937 standable cells, 54 unguarded drop edge(s): 10 a flight's own side,
      0 at a declared drop, 13 at a ladder's shaft, 3 a thing's top, 8 outdoors (reported), 20 UNDECLARED indoors

The 20 are deli_a01's floor hole at 3.3 m, the rows the declared-drop links exist to claim. The gate's report and
verdict are kept here (`drop_edges.json`, `drop_edges_scan.json`): the same 54 rows as the gate's run on 9318's
package (`docs/findings/drop_edges_173/gate_9318_drop_edges.json`), so Deli Counter 0.226.0 moved no geometry,
and the package's links read `climb 2, drop 0`.

**Why, traced hop by hop** (the workspace's own files):

    deli_counter/build/deli_a01.gameplay.json                      floor_hole + hatch nav_link     present
    jobs/...lot_assemble.candidate.seed_9104/1/out/site.site.gameplay.json   both, in site space   present
    temp/urban_row_001/dispatch_inputs/lot/lot.gameplay.json       no `vertical_links` key at all
    jobs/urban_row_001.dispatch_handoff/1/out/navigation_hints.json   links: the two ladders' only

Level Factory's `stage_dispatch_inputs` writes Dispatch's inputs from a whitelist of keys, and the whitelist did
not name `vertical_links`. Dispatch 0.5.3's importers read it; they found nothing to read. It is the ladders'
failure on cold runs 9075 and 9076, one record over, and it means the root's 02c1b06 claim -- "the declared set
now ships in the package" -- was not true end to end. The three repos' own tests each passed. Only a package
could show it, and the gate was the first thing that read one.

**Fixed in Level Factory 0.216.1** (`patches/patch_lf_stage_vertical_links.py`): `vertical_links` verbatim on
both sides of the staging, and a test that both staged manifests carry every key Dispatch 0.5.3's importers read.
Re-staged as cold run 9321.

This run is not a level. The gate refused a package whose floor hole nothing in the package declared. That is
the refusal it was built for, and the defect was upstream of it.
