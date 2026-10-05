# Cold run 9154 -- 0 interventions; one gutter the whole eave, and what the covers cost

gas_block_001, seed 9080, `empties: "across"`, `--bake-lights`.

**Stack:** Patina 0.25.1 (the top storey's openings are part of the
roofline), on 9153's Level Factory 0.140.0 and Zoo 1.67.0.

**Result:** every leg ran in 32.9 minutes (00:10:51 to 00:43:43),
`INTERVENTIONS: 0`. Art exited 1 on 55 findings, as in 9152 and 9153. No
`STEM COLLISION` in any job. The walk copy is this run's
(`glb_reference_scan.json` names `cold-9154-ws`).

## The gutters

Patina's own orders (`*.patina.dressing.json`). Each line is one facing at
one height; a gap is any break of more than 1 cm along it.

| building | gutter sections | at z | downspouts | eave lines | gaps |
|---|---|---|---|---|---|
| `gs_empty_rowhome_a`, `_d`, `_f` | 25 each | 8.92 | 2 each | 4 | 0 |
| `gs_empty_rowhome_c` | 26 | 8.92 | 2 | 4 | 0 |
| freight terminal | 90 | 5.62 | 16 | 4 | 0 |
| gas station | 49 | 3.22 | 8 | 4 | 0 |
| bank tower | 68 | 8.82 | 14 | 4 | 0 |

**Frames:** `docs/findings/empties_gutters_9154/`. `eave_9153_vs_9154.png`
crops the row from across the street, same camera both runs:
- in 9153 the pale gutter breaks over every top-floor window;
- in 9154 it runs the whole eave.

## What the covers are, counted three ways

Every Patina cover is its own mesh with one surface, and each building
GLB is instanced once per placement. The level places the six rowhome
variants 26 times: f x7, d x6, c x5, b x4, a x2, e x2.

| count | 9152 | 9154 | change |
|---|---|---|---|
| cover meshes in the nine dressing GLBs (`glb_census.py`) | 1,080 | 1,323 | +243 |
| cover instances placed in the level (`cover_census.py` x the site's placements) | 2,783 | 3,370 | +587 |
| lightmap users in the export's bake line | 7,676 | 8,263 | +587 |
| meshes in the perf harness's light census | 7,730 | 8,317 | +587 |

The last three agree, so the increase in meshes from 9152 to 9154 is the
gutters and downspouts and nothing else. That also accounts for the
package growing from 128 MB to 138 MB: 587 more lightmapped meshes. That
part is not measured file by file.

**An earlier statement here was wrong.** "1,287 cover meshes across the
level" (said during the run) was the GLB count. The level carries 3,370.

## The price of the gutters

Fixed stations (`_runs/perf_inner/run.py` + `level_factory/tools/
perf_stations_run.py`): 53 station x heading pairs in all three reports.
A = 9152's package, B = 9154's, A2 = 9152's again. The output is in
`price_gutters.txt`.

| per view | B - A (median / mean / range) | control A2 - A |
|---|---|---|
| draws | +137 / +160 / +12 .. +418 | 0 everywhere |
| ms, median frame | +0.274 / +0.367 / +0.026 .. +1.255 | +0.018 / +0.025 / -0.094 .. +0.218 |
| ms, p95 | +0.212 / +0.297 / -1.038 .. +1.619 | +0.004 / -0.010 / -0.704 .. +0.856 |

- **Every one of the 53 views got slower on its median frame.** More than
  half of them by more than the control's largest swing.
- **The worst views:** extraction_14 at yaw 90 went from 7,926 to 8,344
  draws, and its median from 25.05 to 26.22 ms. longest_sightline at 90 went
  from 8,276 to 8,690 draws, median 25.92 to 26.89 ms. Its p95 moved -0.05
  ms, inside the p95 control's spread.
- **What else changed from 9152 to 9154: LF 0.140.0's pane material.** 164
  panes lost world triplanar. It changes no draw or object count; the
  counts above match the covers exactly. It could move ms, and this
  measurement cannot separate it. Triplanar samples three times, so
  dropping it would make the panes cheaper if anything, which would hide
  part of the gutters' cost rather than add to it. That is unmeasured.

## The ceiling on merging the covers

A copy of 9154's package with every building's `Dressing` node set
`visible = false` (`patches/lf_empties/make_nocov.py`; the nodes stay, so
lightmap paths resolve). A = 9154, B = the copy with the covers hidden,
A2 = 9154 again. The output is in `price_covers_hidden.txt`.

| per view | B - A (median / mean / range) | control A2 - A |
|---|---|---|
| draws | -850 / -1,021 / -72 .. -3,119 | 0 everywhere |
| ms, median frame | -2.062 / -2.515 / -0.179 .. -9.334 | +0.054 / +0.063 / -0.065 .. +0.398 |
| ms, p95 | -2.219 / -2.625 / -0.153 .. -9.589 | +0.058 / +0.117 / -0.791 .. +0.992 |

- **Worst station, longest_sightline at yaw 90:** 8,690 draws at 27.33 ms
  p95 became 5,571 draws at 17.74 ms.
- **Over budget:** 13 of 14 stations, 11 with the covers hidden (the
  provisional 2,000 draws and 11.0 ms p95).
- **The control did not move:** 9154 twice gave the same worst station,
  8,690 draws at 27.32 ms.

Hiding the covers is not a design: the level loses its trim. It bounds what
merging them can buy. A merge keeps a few meshes a building where it has
about 100 today, so it recovers most of the figures above, not all.

**Which unit to merge is constrained.** The export runs occlusion culling
(`use_occlusion_culling=true`, 1,407 box occluders in `occluders.tscn`).
- One mesh per building per material would draw a building's back-side
  covers whenever any of the building is visible.
- One mesh per building FACE per material keeps the back sides occludable,
  and is at most 12 meshes a building.

The lights-per-object census (46 meshes over the cap of 8 in all three
reports) has to be re-read after a merge: a long merged face is touched by
more lights than one cover.

**Zoo's `build_dressing` comment is the reason this was never done.** It
says Level Factory merges covers downstream; it does not (9152 notes).

## Seen, not caused here

Short dark marks at regular spacing along a stone end wall at the storey
line, in `empties_down_the_row_night.png`. They are identical in 9153's
frame of the same view. Unexplained; queued to look at.
