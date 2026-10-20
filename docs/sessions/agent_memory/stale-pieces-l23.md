---
name: stale-pieces-l23
description: "DC 0.192.0 (6bce1a1d): L23 flags pieces over an opening or in a stair's walk; 17 moved (deli islands, twin wardrobes MY 0.190.0 regression), 47 frozen; furnish can't see AUTHORED slab_holes (next fix); any piece move needs a refurnish"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-06T22:19:27.308Z
---

Found 2026-10-06 via the restored circulation gate: deli_a01's counter
island stood over its up-stair's hole. Census: 64 pieces in 18 shells.

**Two causes:**
- **Stale.** The placement passes clear stairs only when they place a
  piece, and are idempotent by name. A stair change leaves old pieces in
  place.
  - **My 0.190.0 width change put twin_a01's wardrobes over the hole**, and
    the gate passed it.
- **Unseen.** `furnish` and `seed_cover` check stairs
  (`_stair_reserved_rects`), not authored `slab_holes`.
  - apartment_walkup_a01's dining set comes back on every refurnish.
  - This is the NEXT generator fix, and it will refurnish cbp_town_finale,
    final_stand and apartment.

**Shipped in DC 0.192.0:**
- L23 (WARN);
- `level_design.reseat_piece`;
- `migrate_stale_pieces.py`;
- `stale_pieces_baseline.json`, with 47 pieces frozen;
- `test_stale_pieces.py`.

**How to apply:**
- After ANY change to a stair's size or position, run L23 on that spec.
- **Any edit to a spec's pieces must be followed by
  `migrate_furnish_recipes.migrate`**, or `test_club_fixtures`' fixed point
  fails. furnish lays rooms around existing pieces. Learned twice: deli_a03
  in 0.189.0, the delis here.
- Moving a furnish piece by hand is pointless: the refurnish re-derives it.
  Fix the rule instead.

Related: [[presentation-gates-were-unread]], [[stairwell-on-one-grid-in-four]].
