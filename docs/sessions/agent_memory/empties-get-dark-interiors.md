---
name: empties-get-dark-interiors
description: "Empties (roadmap 106): look, variety, doors shut, and the per-side merge (LF 0.143.0, -643 draws/-1.11 ms median) all shipped and pushed 2026-10-05; next session: merge follow-ups, then awning, porch-front row, fence, backdrops"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-06T08:47:24.134Z
---

**What an Empty is:** a non-enterable shell (roadmap item 106). Spec flag
`facade: true`; the rename to `empty` is deferred. Placed across the
through road by `empties: "across"` on the brief, as Lot `blockers`. LF
`empties.terrace` picks a variant per house uniformly (no immediate repeat)
from every `gs_empty_*` DC built.

**Shipped 2026-10-04/05, every one verified in a cold run at 0 interventions:**
- Rowhome family: DC 0.174.0, placed by LF 0.137.0; roof only, full-storey
  walls (DC 0.175.x); Patina 0.24.0 reads the up axis off the file.
- One module name per geometry (DC 0.176.0, Zoo 1.60/1.63). A stem collision
  fails the kit and blocks the run (Zoo 1.62.0, LF 0.139.0).
- Parapets are wall slots (DC 0.177.0); doors shut (DC 0.178.0, Zoo 1.61.0).
- Painted windows (9153): 16-state atlas (Zoo 1.64-1.66), state per window
  (DC 0.179/0.180); LF 0.140.0 lit faces keep their own UVs.
- Gutters + downspouts (9154, Patina 0.25.x, Zoo 1.67.0): +160 draws.
- Cover merge per building side (9155, Zoo 1.68.0, roadmap 180 CLOSED):
  -673 draws, -1.86 ms median view.
- AC units + window bars (9156, DC 0.181, Patina 0.26, Zoo 1.69): +4 draws.
- Storey seams (Zoo 1.70.0) + stone lintels/sills (9157, Patina 0.27, Zoo
  1.71): +14 draws.
- Front doors (9158, DC 0.182, Zoo 1.72, Patina 0.28): authored per house
  (`door_finish`; a seeded draw gave 3 finishes and no iron), stem
  `_e<finish>`, iron security doors. 0 draws. GOTCHA: preset `empty_rowhome`
  has a local `door` (the door's POSITION); the param is `door_finish`.
- Per-house brick (9159, Pixelcoat 0.57, Zoo 1.73, DC 0.183): kinds
  `brick_brown`/`brick_orange`. A profile's `kind` must equal its theme slot;
  Zoo `KNOWN_KINDS` and `ROUGHNESS` share keys. 0 draws.

- Twelve rowhomes (9160, DC 0.184.0): the row shows 10-12 of 12 designs,
  one up to 5-6 times -- LF's terrace DRAWS uniformly (`empties.py:97`),
  so "each about twice" was wrong; fix written as LF 0.142.0 (a shuffled
  deal, `patches/patch_lf_terrace_deal.py`), run it alone.
- TV antennas + dishes (9161; Zoo 1.74.0, Patina 0.29.0, DC 0.185.0): 14
  antennas + 2 dishes in the level, 0 new meshes (gutters' white metal);
  dish raised to 0.6 m over the parapet after a pre-flight render.
- Perf harness: LF 0.141.0 measures each heading twice, keeps lower p95;
  control gaps max 0.24 ms median (were 1.5-3.5). Price with it from 9161 on.
- Roadmap 181 filed: Zoo's `--roof-props` path can never fire.

- Terrace DEALT (LF 0.142.0, 9162): every row shows all 12, none > 3 times.
- Doors shut + no party-wall gutters (DC 0.186.0, Patina 0.29.1, 9164).
- MERGED (LF 0.143.0, 9165; roadmap 182 CLOSED): the export merges each
  Empty's kit modules one mesh a side per material, after the occluder bake
  and before the light bake. -643 draws, -1.11 ms at the median view (up to
  -2,914 / -7.1 ms); the ceiling (all hidden) was -816 / -1.87 ms.
- ON BY DEFAULT (LF 0.144.0, walker 2026-10-05): `empties` defaults to
  "across" and "none" turns it off. It needs a lot_library and 2+ buildings
  (`models.empties_effective`), so 3 of the 10 sweep missions get none.
  Roadmap 106 CLOSED after the breadth sweep stood all 12 designs on 7
  missions ([[breadth-sweep-ten-missions]]).

**State at the pause (2026-10-05 evening): everything committed and PUSHED**
(root + 8 tool repos). Cold runs 9153-9165 at 0 interventions; 9163 died on
a full disk ([[perf-copies-fill-the-disk]]).

**Open follow-ups on the merge:**
- 14-22 merged meshes a design, against 12-13 in the prototype. The
  untested candidate is the format split in the group key (UV2 or not).
- The Empties' module GLBs still ship and are re-imported though nothing
  instances them.
- The Empties' occluders are still one per wall module (about 1,000).

**Before a cold run:** `python patches/dc_more_rowhomes/plan_stems.py` plans
every built building through Zoo (`plan_kit`): 0 collisions / 145 buildings
at 0.184.0. Cold runs: `tools/cold_drive/` (`docs/COMMANDS.md`), about 33
minutes on gas_block_001.

**Queue after the optimise pass:** an aluminium awning; the next family
(porch-front row); the fence at the playable edge
([[fence-marks-the-playable-edge]]); backdrops; roadmap 179 (manholes and
drain grates on the hydrant's spacing rule).

**Comps and plan:** `docs/reference/EMPTIES_COMPS.md` -- rowhome, industrial
and taproom comps; the eleven window photographs; feature-to-tool tables.
It may also suit the first dive bar ([[first-dive-bar-the-wooder-hole]]).

**Period:** 1990s. Invented brands only.

**Families, in order:** rowhome (done), porch-front row, main-street
storefront, corner store or taproom, brick factory or loft, cinder-block
garage; then landmarks, mural end walls, and the fence at every playable edge.

**How to apply:**
- Every row is DIFFERENT houses.
- Colour variation is key (the walker): never a material per colour --
  atlas cells, instance tint, vertex colour.
- Doors are SHUT, collision included: the walker, 2026-10-05, "Emptys can
  have closed doors because they are buildings that are never meant to go
  inside as a player". DC 0.186.0 fills a facade's door full-thickness, as
  its window's pane (roadmap 183; cold run 9164 measured rays stopping at
  the face). Never reopen an Empty's door for any reason.
- Price every look A/B/A2 ([[performance-beats-graphics]]).
