---
name: next-lot-change-carries-docstring-fix
description: "the walker's rule for small Lot text fixes: ride the next Lot change, no release of their own; queue EMPTY since Lot 0.126.1 carried urban_tree_stations' docstring (2026-10-21)"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-14T12:04:04.383Z
---

**Queue: empty.** The one below SHIPPED in Lot 0.126.1 (dc4e2a6, 2026-10-21), its changelog's "Corrected:" line naming 0.123.0's claim.

**Shipped 2026-10-21 (was queued 2026-10-14):**
- **`site_furniture.urban_tree_stations`' docstring (Lot 0.123.0, line ~819)** says paths and driveways don't split a run and that "a tree steps clear of them where it stands (`_nudged`)". The first half is true; the second is false.
- `_nudged` returns None, before any step, when the station itself is within `CUT_CLEARANCE` (0.8 m) of any cut: road, path or driveway. Those trees are DROPPED. Only a piece already standing, a marker or a shop band steps a tree (NUDGES 2/4 m).
- **0.123.0's changelog** says the same ("steps clear of every cut, piece, marker and shop band"). The next Lot changelog should carry a "Corrected:" line.
- The root's `docs/reference/STREET_TREES.md` and `docs/findings/urban_street/README.md` were corrected in place on 2026-10-14.

**Shipped earlier:**
- `site_cover.min_passable_gap`'s docstring rode Lot 0.122.0 (030901f);
- LOT_DESTINATION_ABOVE_FLOOR's message rode Lot 0.123.0 (4e4859f).

**Why:** the walker's call, 2026-10-13, offered a Lot release for a comment alone: "leave it for the next Lot change". A message is the same.

**How to apply:** queue any further comment- or message-only Lot fix here. Add one anchored edit to the next Lot change and name it in that release's changelog. Related: [[pick-moved-name-the-seed]].
