# Cold run 9155 -- 0 interventions; a building's covers merge one side at a time

gas_block_001, seed 9080, `empties: "across"`, `--bake-lights`.

**Stack:** Zoo 1.68.0 (covers merged per side of the building per
material, roadmap 180), on 9154's Patina 0.25.1 and Level Factory 0.140.0.

**Result:** every leg ran in 33 minutes (07:02:57 to about 07:36),
`INTERVENTIONS: 0`. Art exited 1 on 55 findings, as in 9152-9154. No
`STEM COLLISION`. The walk copy is this run's (`glb_reference_scan.json`
names `cold-9155-ws`).

## What shipped

- **Every dressing GLB holds 8 meshes: 4 sides x 2 materials.** Concrete
  and the gutters' painted metal. Each Zoo job printed `refused 0`:
  - the rowhomes merged 96-106 covers into 8 each;
  - the gas station 186 into 8;
  - the bank tower 256 into 8;
  - the freight terminal 273 into 8.
- **The bake line agrees exactly.** Lightmap users went from 8,263 to 5,125.
  That is 8,263 minus 3,370 cover instances plus 232 merged meshes (8 for
  each of 29 placed buildings). Bake time went from 88.5 s to 84.4 s.
- **Geometry, before shipping:** rebuilt from 9154's own manifests, every
  vertex sits within 1.3 um of its 1.67.0 counterpart, with matching normal
  and uv (`patches/zoo_cover_merge/glb_geometry.py --exact`). A different
  house, as the control, leaves 3,624 of 3,648 vertices without a partner
  within 1 cm.

## The price

Fixed stations, 53 station x heading pairs. A = 9154's package, B = 9155's,
A2 = 9154's again, C = 9154's with every `Dressing` node hidden (the
ceiling). Measured back to back in one session.

**The control hitched.** A and A2 differ by more than 1 ms at 3 headings:
- camera_socket_6 at yaw 270: 29.74 against 23.90 ms median, p95 43.02
  against 25.50;
- defender_spawn_22 at yaw 90: 5.02 against 3.39 ms;
- defender_spawn_22 at yaw 180: 3.23 against 2.08 ms.

So frame time is measured against the MEAN of A and A2, over the 50 stable
headings (`patches/zoo_cover_merge/price_robust.py`). The plain
`compare_price.py` output is beside it, in `price_merge.txt` and
`price_ceiling.txt`.

| per view | merged (B) | covers hidden (C) | recovered |
|---|---|---|---|
| draws (median / mean) | -673 / -901 | -850 / -1,020 | 79% / 88% |
| median frame, ms (median / mean) | -1.863 / -2.242 | -2.093 / -2.601 | 89% / 86% |
| p95 frame, ms (median / mean) | -2.323 / -2.607 | -2.344 / -2.664 | 99% / 98% |
| control, stable headings | +0.069 median | | |

- **The worst view, longest_sightline at yaw 90:**
  - 9154: 8,690 draws, 31.29 / 30.59 ms p95 (A / A2);
  - 9155: 5,904 draws, 20.56 ms p95;
  - covers hidden: 5,571 draws, 20.43 ms.

  9155's own worst is extraction_14 at yaw 90, 20.93 ms p95 and 5,704
  draws. The same view on 9154 read 27.33 ms p95 earlier the same day (the
  9154 notes). Absolute times drift between sessions on this machine; the
  deltas above are within one.
- **Over the provisional budget** (2,000 draws, 11.0 ms p95): 13 of 14
  stations on 9154, 12 on 9155, 11 with the covers hidden. **The covers are
  not the whole of the overrun.**

## Lights

The harness's light census went from 46 meshes over the 8-light cap to 61.
The worst is now a merged side, `CoverE_concrete_delco_1997` with 35 lights.
That census counts every non-directional light whose range reaches a mesh's
box, baked or not.

`patches/zoo_cover_merge/cover_light_census.gd` on this walk copy:
- the level has 94 lights: 77 baked STATIC, 17 live (bake mode 2);
- of the 232 merged cover meshes, 16 are reached by more than 8 lights,
  counting every light;
- 0 are reached by more than 8 live lights. The most any receives is 5.

A static-baked light is not drawn live on a lightmapped mesh; the light
bake's own -12 % frame time came from exactly that. **No live light is lost
on any merged cover.**

## Frames

`docs/findings/empties_merge_9155/`, the same five views as 9154, with and
without the fill light. `patches/zoo_cover_merge/frame_diff.py`:

| pair | mean abs difference | pixels > 16 levels | > 48 |
|---|---|---|---|
| 9155 shot twice (the noise floor) | 0.000-0.033 | at most 0.07% | at most 0.02% |
| 9154 against 9155 | 0.08-0.47 | 0.04-0.33% | at most 0.06% |

**The difference is real and small.** It lies on the merged gutters and
downspouts, faint over brick, and on one lit window across the street.

**The bake re-packed** (5,125 users, not 8,263). The window renders crisper
in 9155 than in 9154. Neither the window's module nor its pane changed, so
the cause is not established.

`covers_9154_vs_9155.png` crops the eave and a front by day and by night.
They read the same.
