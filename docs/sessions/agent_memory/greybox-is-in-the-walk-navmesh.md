---
name: greybox-is-in-the-walk-navmesh
description: "Lot bakes the walk test's (and Laser Tag's) navmesh from the greybox lot WITH visual meshes, so a visual-only greybox box over a void becomes floor; cold 9340's 8 stuck walkers."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-20T04:30:14.905Z
---

Lot's walk navmeshes parse visual meshes too (`geometry_parsed_geometry_type = 2`, lot.py), and the walk test and Laser Tag grade the candidate's GREYBOX lot. So a greybox box with no collider is still floor to the bake. Deli Counter 0.236.0 drew a hole_edge's (and a floor hatch's) greybox as one box over the hole, its top 12 mm above the floor: cold run 9340 sent all four walkers on both deli_a03 candidates to a target inside the drop, stuck in its corner on the slab's cut (WALKTEST_WALKER_STUCK 0 -> 8). Fixed in DC 0.236.1: a ring of four boxes round the hole (`hole_causes._ring`), their union still the slot's footprint for the placement gate.

**Why:** "it has no collision, so it cannot affect traversal" is false here; a greybox VISUAL box is navigation data.

**How to apply:** never draw a slot's greybox over a void (hole, shaft, stair well, gap) -- draw round it; the roof hatch's box over its roof hole (`roof_hatch.py`, 0.224.0) is the same shape, unexamined. Before shipping any new visual-only slot, ask what its greybox box does to the walk bake. See [[floor-holes-get-a-cause]], [[claim-shipping-only-from-a-package]].
