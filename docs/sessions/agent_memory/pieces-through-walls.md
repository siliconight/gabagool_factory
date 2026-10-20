---
name: pieces-through-walls
description: "Roadmap 195: DC 0.199.0's L25 names pieces through walls (19 in 15 specs); presets.make trims the THROUGH ones; 12 ALONG a wall frozen; casino_tower's generated vault block open"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-07T03:38:45.075Z
---

Found 2026-10-06, sizing the deli case: every deli's `deli_case_cover` ran
0.825 m through its own partition into the market aisles. `presets.corner_deli`
authored it that way (7.0 m from x -14.0, the wall at x -8.0).
Finding: `docs/findings/pieces_through_walls/`.

**What shipped (Deli Counter 0.199.0, roadmap 195 NARROWED):**
- **layout_lint L25 (WARN), `wall_crossings`.** It measures the builder's own
  walls: partition spans, setbacks, stair voids, and all four exterior sides
  under `auto_exterior`. It reports two shapes:
  - THROUGH: the piece's centre is off the wall;
  - ALONG: the piece is centred on the wall's line.
- **`migrate_wall_crossing.trim`.** It pulls a THROUGH piece's far end back
  to the wall's face, less `_WALL_PIECE_AIR`.
  - It refuses a piece ALONG a wall, a turned piece, a cut of more than half
    the piece, and a cut from under a marker.
  - `presets.make` runs it on every recipe, before enrich.
- **The library:** 7 pieces trimmed (six deli cases, warehouse's shelving
  run). 12 ALONG pieces are frozen in `wall_crossing_baseline.json`.

**In a level:** cold runs 9190 and 9191 stand the trimmed case. 9190
priced the deli case at +1.0 draw a station, within noise.

**Open:**
- the 12 ALONG pieces, which are racks, forklift bays, vomitory covers, a
  rollgate, a vault door and four columns;
- `casino_tower`'s generated basement vault block, centred on a partition.

**How to apply:**
- When a gate never asked a question, measure the whole library before
  fixing the one instance. One deli case became 19 pieces.
- Generators, not only the library: run every recipe through `presets.make`
  too. The hospital's seats through a wall showed only there.

Related: [[detail-lives-in-generator-logic]], [[stale-pieces-l23]].
