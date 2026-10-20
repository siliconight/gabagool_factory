---
name: seeded-corridor-and-entrance-gate
description: "Roadmap 194: deli_a01's upper storey was cut off by two seeded crate stacks; DC 0.194.0 server-room door + L24, 0.195.0 seeder keeps min_corridor_width, 0.196.0 nav gate asks if an entrance reaches each stair; cold 9189 is the proof run"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-07T02:06:51.404Z
---

Found 2026-10-06 measuring playable area on cold run 9188. The record is
`docs/findings/deli_a01_upper_storey_9188/` and roadmap item 194.

**Shipped, all 2026-10-06:**
- **DC 0.194.0.** deli_a01's server room gets a door: the walker's call,
  "give the server room a door". L24 (WARN) names rooms only a breach,
  window or drop reaches. 15 are frozen in `walk_reach_baseline.json` for
  the walker's call, still unasked.
- **DC 0.195.0.** `_seed_clear(..., corridor=True)`: a seeded piece keeps
  `agent_contract.min_corridor_width()` (1.1 m) from walls, stair reserves
  and volumes. `migrate_seed_corridor.py` moved 35 pieces and dropped 7 in
  13 shells.
- **DC 0.196.0.** The nav gate's `from_entry`: does a storey-0 door reach
  each stair? 148 of 149 stairs are reached. primos_pizza is frozen
  (roadmap 189's discharge neck).
- **Proof:** swap-and-bake on 9188's staging took islands 165 -> 164 -> 161.

**Lessons:**
- A stair whose ends join is not a route. Ask whether an entrance reaches
  it.
- Cover is placed first and furniture after (`enrich`), so ask the
  seeder's rule before furnish.
- A hook log is not a measurement. The L9 warnings were misattributed to
  warehouse_a02 until each spec was linted from git.
- A test that passes without the change proves nothing. The seeder test was
  re-cut in a 6 m deep building, where the old rule put a piece 0.36 m off
  a wall.

**PROVEN, cold run 9189 (0 interventions); roadmap 194 CLOSED.** deli_a01's
only own island is its roof, and the street's island grew from 16,944 to
17,728 m2. Two things are kept from that run:
- **A first bake of its site dropped every building** (1,643 polygons, no
  basements, no roofs). It was not reproduced. Always read a bake's bounds.
- **seed_9104's player stuck events went 4 -> 9**, all five new ones inside
  deli_a01 where no piece moved. Not yet explained.

**L24 was wrong about 11 of its 15 rooms (DC 0.197.0).** L12's graph had no
open floor. deli_a01's basement utility room is walked into across 7 m of
uncovered partition edge (9189's bake). The walker asked for utility-room
doors on that wrong report; none were needed or added. L12 and L24 now ask
`tactical.shared_open_edge`, lifted unchanged (build_graph identical on 128
specs).

The walker's calls:
- objective server rooms (cr_deli, deli_a02, night_deli) stay breach-only by
  design;
- deli_a03's fortifiable server room is still pending.

**Lesson:** a room-graph finding is a claim about geometry. Check one case
against the bake before reporting it as fact.

**Open:**
- furnish's 0.9 m margin (4 pieces in 2 shells);
- primos_pizza's discharge;
- item 193's authored `slab_holes`.

**How to apply:**
- To prove a shell change on a real site before shipping, run the finding
  folder's `swap_and_bake.py`.
- Never edit a tool repo while 9189's clock is ACTIVE (see
  [[never-edit-tool-repos-during-a-cold-run]]).
