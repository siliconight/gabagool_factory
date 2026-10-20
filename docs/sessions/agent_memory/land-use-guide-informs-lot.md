---
name: land-use-guide-informs-lot
description: "Land-use guide informs Lot: steps 2 and 4 shipped 2026-10-03 (LF 0.132 doors face the street; Lot 0.93 pads, 0.94 parking fields); remainder still ~55-64 %; step 3 (one building line) and verges/vacant lots next; walker's eye owed"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-04T10:08:19.885Z
---

The walker filed the land-use guide with "this should directly inform Lot",
and on 2026-10-03 agreed the order: doors to the street, then parking fields
and service yards.

Shipped 2026-10-03, each measured on the same nine candidates (3 briefs x 3
seeds) with `tools/landuse_census.py`:
- LF 0.132.0: yaw from the front door. Through-road facing 15/27 -> 27/27;
  corner buildings now show a side to the cross street (12 misses).
- Lot 0.93.0: a concrete pad under each dumpster, 27/27; remainder -0.3 pt.
- Lot 0.94.0: parking fields in gaps (7.3 m aisle, 2.7 x 5.5 m bays,
  driveway crosser kind). 23 fields; remainder down 1.5-6.1 pt.

The first field build hurt Laser Tag on seed 9181 (cars beside Enemy_0).
It was fixed by `ENEMY_CLEAR` = 4.0 m/s x 3.0 s = 12 m. The residue is
recorded in Lot's CHANGELOG.

Follow-ups, same day (cold runs 9142-9144, all at zero interventions):
- Zoo 1.59.0 put car paint in vertex colour, taking a car from 9-11
  materials to 4. Cost: -78 draws a heading, more than the fields added.
- Patina 0.23.0 makes a zone dress only the ground it owns.
- Lot 0.95.0 plans the dressing on the drawn site. Lot 0.96.0 makes a cover
  piece exclude only its own footprint.
- Field aisles went from 0.29 to 0.08 dressing pieces per m².
- Laser Tag 0.23.2: stuck events always had positions in their metadata.
  Seed 9181's crew sticks 6 m up inside arena_a03. That's a Deli Counter
  question, not yet asked.

Still open:
- Remainder is still ~55-64 %, against the design's under-15 % band. Verges
  and vacant lots (rest of step 4) are what move it.
- Step 3 SHIPPED 2026-10-04 as LF 0.135.0. Street edges come from per-side
  collider extents, so a station's store stands back behind its canopy.
  Spread went from 10-24 m to 0 on 7 of 9 candidates. Cold run 9145 needed
  zero interventions.
- On the shipped seed (gas_block_001 9080) the encounter is now trivial: an
  enemy is pinned at the store's NE corner. Not yet investigated.
- Corner buildings face the cross street with a side.
- The walker hasn't seen pads or fields in a frame yet.

**Why:** this is the first measurement of roadmap 18's "good" gate.

**How to apply:**
- Judge each step by the census before/after and by the walker's eye.
- Placement lives in Level Factory; ground roles live in Lot.
- A new solid on the ground (cars) must respect `site_cover`'s
  crew-end bias.

Related: [[walk-feedback-2026-10-03]], [[dumpsters-beside-buildings]].
