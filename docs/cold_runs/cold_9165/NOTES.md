# Cold run 9165 -- 0 interventions; the Empties merged one mesh a side per material in the export

gas_block_001, seed 9080, `empties: "across"`, `--bake-lights`.

**Stack.** Level Factory 0.143.0 (roadmap 182, the walker's "then optimise
them for runtime"). The export merges each Empty's kit modules into one mesh
per side per material.
- **Where:** after the occluder bake and before the light bake.
- **What it keeps:** every collider, and a copy of every material.
- **What it adds:** a lightmap unwrap for every merged mesh.
- **What it trusts:** its report, not its exit code.

**Result:** every leg ran, `INTERVENTIONS: 0`.
- Shell: 3 candidates, all distinct; 0 blockers.
- Art exited 1 on 55 findings, as before.
- No `STEM COLLISION`.
- The walk copy is this run's.

## The export, as it printed

    [export] 1358 occluder(s) from 1364 solid module(s); 51 glass, 248 porous and 826 filler left open
    [export] Empties merged: 12 scene(s), 1061 mesh(es) of 1660 surface(s) -> 236 merged mesh(es), 962 collider(s) kept
    [export] light bake: 383 model(s) and 1650 primitive mesh(es) lightmapped, 7 kept dynamic; ... 3309 users, 75.6 s in the editor

- **The bake:** `light_bake.json` is `ok`, with 3,309 users (about 5,000
  before the merge).
- **The report:** `merge_empties.json` ships in the package, `ok`, at 14 to
  22 merged meshes a design.

**Not what the pre-flight showed.** On 9164's walk copy, already imported for
its lightmap, the same merge made 12 or 13 meshes a design. In the export it
runs before the light bake's re-import, and the groups split further.
- **The untested candidate:** module surfaces differing in format (UV2 or
  not), which is part of the group key.
- **Worth unifying:** every merged mesh is unwrapped afresh, so the format
  split buys nothing.

## Checked

- **Collision survived the merge.** `door_collision_probe.gd` on
  `gs_empty_rowhome_f`: every ray across the doorway stops at the face, and
  the walk capsule stops at the wall, exactly as in 9164.
- **The look.** `docs/findings/empties_merged_9165/` against 9164's frames
  from the same cameras shows the same street: brick and stone, the lit and
  dark windows, the AC units, grilles, antennas and lamp pools. The merged
  meshes are in the baked lightmap.

## Before the run

- **Level Factory's suite** exited 0: 1,904 passed, 14 skipped, 1 xfail.
- **The new file's 15 tests** failed at collection on 0.142.0.
- **The Godot half** passed gdcheck.
- **Pre-flight** (`patches/lf_empty_merge/preflight_merge.py`, on a clone of
  9164's walk copy):
  - all 12 designs merged, every merged mesh unwrapped, every collider
    kept;
  - the editor bake took the merged meshes as users (5,032 to 3,124);
  - its entry retarget refused a walk copy already baked once. That is a
    property of re-baking, and the real export bakes once.

## The price

A = 9164's package, B = 9165's, A2 = 9164's again, with the two-pass
harness and 60 s cool-downs (`price_merge.txt`, `price_merge_robust.txt`).
The control had 0 headings more than 1 ms apart, median +0.058 ms.

| a view | the merge (9165) | prototype (9162) | ceiling: every Empty hidden (9161) |
|---|---|---|---|
| draws, median / mean / most | -643 / -875 / -2,914 | -686 / -913 / -3,015 | -816 / -1,212 / -3,951 |
| median frame, median | -1.11 ms | -0.88 ms | -1.87 ms |
| median frame, mean / most | -1.59 / -7.10 ms | -1.53 / -6.94 ms | -2.85 / -11.6 ms |
| p95, median | -1.08 ms | -1.07 ms | -2.23 ms |

- **Better than the prototype on frame time, a little worse on draws.**
  - The merged meshes are in the baked lightmap here, and the prototype's
    drew without it. That is a candidate for the frame, not tested.
  - The groups split to 14-22 a design, against 12-13.
- **Light census:** 61 meshes over the cap, unchanged, out of 3,363 (5,086
  in 9164).
