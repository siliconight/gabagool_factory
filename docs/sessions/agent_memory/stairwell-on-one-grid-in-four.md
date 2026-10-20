---
name: stairwell-on-one-grid-in-four
description: "Roadmap 189 NARROWED: navmesh connectivity can depend on the voxel grid origin; DC 0.189.0's gate sweeps 8 origins (fragile = unfit for themed lots), proven in cold 9186; DC 0.190.0 flights >= 1.2 m fixed twin_a01 (not its fridge); 6 frozen; next 3 neck rules; stand-point patch HELD; registers are a walker call"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-06T21:09:03.934Z
---

Found 2026-10-06, closing cold run 9185. The record is
`docs/findings/stairwell_on_one_grid_in_four/` (README, probes, census,
neck finder, outputs).

**Mechanism.** Recast's grid starts at the corner of whatever is baked.
- A connection through a neck a few cells wide holds on some origins and
  not others.
- deli_a03's stair door turned inside its reveal past a slab hole, and
  connected at 4 of 8 origins.
- Deli Counter's gate baked one origin and passed it.

**Shipped 2026-10-06:**
- **Deli Counter 0.189.0:**
  - `_grid_sweep` makes a fragile stair, or a fragile reached marker, not
    navigable.
  - Level Factory's `themed_fitness` reads that, so fit went 102 to 101
    (twin_a01 left).
  - deli_a03's `office_stair_door` is now 2.4 m and connects at 8 of 8.
- **Lot 0.97.2:** `_vertical_access` samples the anchor's column inside the
  old window. It no longer reads Godot's fallback, which fails with "It's
  not expect to not find the most reachable polygons".
- **Cold run 9186 proved both:**
  - both deli_a03 candidates passed the walk test;
  - the engine error fired 0 times, against 19 in 9185.
- **Deli Counter 0.190.0:** `presets.STAIR_FLIGHT_WIDTH` is 1.2 m, the
  contract's 1.1 corridor plus one bake cell.
  - twin_a01's 0.9 m flight was one cell wide after erosion; widened, it
    connects at 8 of 8.
  - **Refuted, kept:** the fridge that stood beside the tear. Moved, it was
    still 7 of 8.
  - Fit is back to 102, and 6 shells are frozen in `navgate_baseline.json`
    `grid_fragile`.

**Still open, in order.** Fix each by a RULE, not a spec edit.
1. **Stair heads facing a wall.** foundry_heist_vertical and primos_pizza
   leave 1.08 and 1.05 m before the wall. Rule: a corridor (1.2 m) at a
   flight's head, a lint sibling of L21.
2. **A door running past its wall's end.** cbp_town_finale's
   `third_vomitory` door. L18 doesn't cover this case.
3. **Auto cover leaves a corridor.** bank_job's crate stack is 0.99 m from
   a desk.

**Not doing:** the stand-point patch (`patch_dc_grid_stand_point.py`) is
HELD, decided 2026-10-06. The gate's re-snap is what a level's bake does,
so a marker on a counter is a hazard that is real in play.

**The register markers** sit at z 0.9 on the counter (`presets.py:730`,
`:1784`). Where the crew stands to take a register is a gameplay-layer
call; ask the walker.

**How to apply:**
- Before trusting any navmesh connectivity verdict from one bake, ask
  whether it survives a grid shift. `filter_baking_aabb` moves the origin
  without moving the geometry.
- Instruments here were wrong three times first (loose snap, closest
  approach, single closest point), and a cause was wrong once (the fridge).
  Check each new one against a known positive, and build the fix in scratch
  before believing it.

**Why:** a random walk-test verdict can drop every candidate, which is an
intervention.

Related: [[stair-head-ledge]], [[never-edit-tool-repos-during-a-cold-run]], [[library-growth-reshuffles-lots]].
