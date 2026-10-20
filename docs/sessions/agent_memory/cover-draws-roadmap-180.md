---
name: cover-draws-roadmap-180
description: "CLOSED 2026-10-05: Zoo 1.68.0 merges covers per building side per material (3,370 -> 232); cold run 9155: draws -673 median a view, median frame -1.86 ms (89% of hiding them), no live light lost; 12 of 14 stations still over budget"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-05T11:03:18.393Z
---

Measured 2026-10-05 on cold run 9154's package (notes:
`docs/cold_runs/cold_9154/NOTES.md`, roadmap item 180).

- Zoo `build_dressing` exports covers with `merge_parts=False`; its comment
  claims LF merges them downstream -- false. Each cover = one MeshInstance3D,
  one surface. Each building's dressing GLB is instanced per placement, so
  gas_block_001 carries 3,370 cover instances (26 rowhome Empties x ~100).
- Hiding every `Dressing` node (`patches/lf_empties/make_nocov.py`):
  median view -850 draws / -2.06 ms; worst view 8,690 -> 5,571 draws,
  27.33 -> 17.74 ms p95; over-budget stations 13 -> 11 of 14. Control 0
  draws / +0.05 ms.
- The gutters themselves (9152 -> 9154): +160 draws, +0.37 ms a view
  (mean), up to +418 / +1.26 ms.

**Why:** the biggest single draw lever measured in a level so far, and every
queued Empty detail (AC units, bars, sills) multiplies covers by placements.

**How to apply:** merge per building SIDE per material (NOT by normal alone:
curbs and roof edges face up and would weld into one building-sized mesh),
at most 8 meshes a building -- NOT per building, because
occlusion culling is on (1,407 box occluders) and a whole-building merge
keeps back-side covers drawn. After merging, re-read the lights-per-object
census, the lightmap bake and the worldskin tiling, and price it A/B/A2.

**2026-10-05, the walker: "do the merge first"** (before the window-photo
features). Shipped Zoo 1.68.0 (zoo 3ebf2d4, root 03da651):
- side = N/E/S/W (DC facings, +y = N); wall covers by normal, UP-facing ones
  (curbs, roof edge strips -- 60 of a rowhome's 103) by position against the
  footprint half-size; covers built in place (merge refuses transforms);
  name `Cover<side>_<kind>` so `partnames.family` IS the side;
- rebuilt from 9154's own manifests: rowhome 103 -> 8 meshes, freight 273
  -> 8, every vertex within 1.3 um (`patches/zoo_cover_merge/glb_geometry.py
  --exact`; control house: 3,624 of 3,648 vertices unpartnered);
- `tools/dressing_in_nav` default prefix `Cover`, refuses a zero match.
**Verified, cold run 9155 (0 interventions), roadmap 180 CLOSED:** every
dressing GLB 8 meshes; bake users 8,263 -> 5,125, 88.5 -> 84.4 s; against
the mean of two 9154 runs (50 stable headings): median frame -1.86 ms (89%
of the hidden ceiling), p95 -2.32 ms (99%), draws -673 median; worst view
8,690 -> 5,904 draws. Harness light census 46 -> 61 over cap BUT it counts
baked lights; live-only census (`patches/zoo_cover_merge/cover_light_census.gd`)
finds max 5 live on a merged mesh. Frames: <= 0.33% of pixels differ by >16.
Still 12 of 14 stations over budget -- not the covers' doing (11 with none).
Gotcha: a control run can hitch (camera_socket_6 43 ms p95 once); compare
against the MEAN of two controls and list unstable headings
(`patches/zoo_cover_merge/price_robust.py`). See
[[empties-get-dark-interiors]], [[performance-beats-graphics]].
