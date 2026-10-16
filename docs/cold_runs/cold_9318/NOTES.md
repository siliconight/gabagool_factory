# Cold run 9318 -- urban_row_001 on Deli Counter 0.225.0 (2026-10-16)

Staged from 9317 (`batch.json`, `briefs/`); the only tool change between them is Deli Counter 0.225.0
(f7bbcea9): a multi-storey switchback's top leg cuts and reserves only its own run, a thin seam wall with its
underside a body's height above the floor, and a rail at the seam. The run exists to re-measure roadmap 173's
first findings that were not the instrument's own.

**Run:** 0 interventions (journal 0, unattributed files 0). Three candidates, all distinct; the pick is seed
9104 again, PASS 100, route completion 1.00, 0 major -- the same pick and grade as 9317, so the stair change
moved nothing the grader scores. `driver.log`, `art.log`, `export.log` beside this file.

**The drop-edge instrument** (`tools/walkable_edge.gd`, seeded from the package's `player_start` at
(44.85, 0, 15.47) with the package's `navigation_hints.json` as links; the session's `edge_9318.sh`; outputs in
`docs/findings/drop_edges_173/edges_9318.*`, `sort_9318.out.txt`):

    standable 115,022 (occupied 22,976, steep 4,184)   reached 84,399   into things 8,725
    drop edges 921: guarded 872, blocked 3, UNGUARDED 46, all 46 indoors        (9317 on 0.224.1: 59)

    class        9317   9318   what they are
    stair          23     10   the first metre of three flights' open sides, drops 0.52-1.30 m (deliberate)
    hatch          13     13   the two ladder hatches (declared)
    floor_hole     16     16   the deli's floor_hole link (declared)
    slab_cut        4      4   recorded cuts (declared)
    prop_top        3      3   a guard rail's top the flood steps onto from the ramp beside it

The 13 stair rows that left are the office's pit: the five at the storey-2 landing's edge over the well, the
seven along the upper flight's inner side, and one at the lower flight's foot that the old two-run cut had
left open. Nothing new appeared. Links: 0 used, 2 unresolved -- both ladders' endpoints sit on occupied cells
(a ladder's foot, a hatch's hole), so no roof was reached; the instrument's lookup now searches the ring of
cells around an endpoint (the next run's).

**`body_names.gd`** named the anonymous colliders the earlier runs' owner table carried: deli_a01's
`@StaticBody3D@19803` / `@19804` and the office's `@19802` are the VAULT LEDGES (`VAULTLEDGE_0/1`, Deli
Counter 0.215.0's routed vault): convex boxes 0.35-0.4 m thick, 1.05-1.2 m tall, 5-6 m long, each beside a
marker empty of the same base name -- which is why Godot auto-named the body. Standing on one is a prop top,
as the sort already classed them. `blocker_0/KitCollision/@StaticBody3D@2` is an Empty's blocker mesh.
