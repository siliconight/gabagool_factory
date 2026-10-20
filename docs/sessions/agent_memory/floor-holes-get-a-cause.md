---
name: floor-holes-get-a-cause
description: "Walker 2026-10-19: 'give them a reason to exist' -- SHIPPED Zoo 1.114.0 + DC 0.236.0/.1; all three causes seen in packages (cut 9341, broken + hatch 9343); hatch frame yellow reads brown (Zoo fix next)"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-20T04:30:23.626Z
---

The walker asked "why are there holes in the floor?" and chose to keep the drops and give each a reason to exist, "clear to the player ... some reason other than a perfectly cut square".

**Shipped 2026-10-20:** Zoo 1.114.0 (5cedc35): `hole_edge` (torn edge, forms cause x `_slab` x `_plaster`), `hole_spoil` (what came down; one of each kind first; the floor's finish on panels and boards), `hole_kit` (the crew's tarp, saw, bag, work light), `roof_hatch` form `floor`. Deli Counter 0.236.0 (9e720516): `hole_causes.py` -- cause = the link's own `cause`, else `stair` (hole in a stair's well: nothing built), else `hatch` (hatch link), else `RULES` by rooms (hideout>kitchen cut, bedroom>kitchen broken, armory>garage and mezz_south>main_floor hatch); slots mirror Zoo's genome sizes (`GENOME_DIMS`: out of size = left out, Zoo would build a box); layout_lint L28 (bare holes). Library: 21 drops / 12 specs / 30 slots; lf_ transients 40 more, 9 uncaused (county hospital atriums). Records: docs/findings/hole_causes_265/, patches/{dc,zoo}_hole_causes/.

**Cold run 9340** (restaurant_row_001, seed 9003): 0 interventions, findings +8 WALKTEST_WALKER_STUCK -- the greybox box over the hole was baked into the walk navmesh ([[greybox-is-in-the-walk-navmesh]]); DC 0.236.1 draws a ring. Also measured: the kit 0.35 m off the south rim takes 2 declared drop edges (a walker's call); deli hole = 9 draws; lightmap users +9.

**Proven:** 9341 (cut; stuck 8 -> 0; +9 draws where seen, p95 in floor) and 9343 (broken + hatch on apartment_walkup_a01, precinct_yard_001 seed 9708; docs/cold_runs/cold_9343/holes_9343.jpg). The hatch's safety-yellow 3 cm frame reads dark brown: the theme skin's metal_rusted_street multiplies the vertex-colour yellow -- paint the floor form on metal_bare.

**Open:** the hatch frame fix, the walker's eye (broken hole square in plan behind its teeth; spoil sparse); foundry's catwalk drop and the hospital atriums uncaused (L28). See [[open-floors-255-awaiting-walker]], [[authorship-guide]].
