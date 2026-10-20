---
name: stairs-and-ladders-are-primary
description: Walker 2026-10-20 -- stairs and ladders primary; holes in floors rare. SHIPPED LF 0.221.0 (per-level rate 0.25, brief floor_holes) + DC 0.237.0 (--holes off, deli_a01 hole-free); roadmap 269 CLOSED
metadata:
  type: feedback
---

The walker, 2026-10-20 (mid-run, while the floor-hole causes were being proven): "stairs and ladders should be the primary way to get between floors in this game...with the holes in floors being somewhat rare...but still at our disposal to use if needed/desired to add some more ways to navigate levels".

**Why:** a hole is a one-way drop route and a strong visual signal; levels where every building has one stop reading as designed circulation. Before this, deli missions drew a cut drop in every level (restaurant_row_001's lot always places a deli with the 2.2 m `vertical_attack_angle`).

**How to apply:** every storey reachable by stairs or a ladder; a floor hole (cut / broken / hatch, roadmap 265) is an optional extra route, rare by default and asked for on purpose (a brief or spec dial), never a default every building of a family carries. Measure frequency per LEVEL, not per spec. See [[floor-holes-get-a-cause]], [[open-work-2026-10-09]].

**Shipped 2026-10-20:** Level Factory 0.221.0 decides per level (`building_library.holes_wanted`, SHA-256 of the candidate id -- crc32 correlated missions; `FLOOR_HOLE_RATE` 0.25; brief `floor_holes` 0..1 overrides) and swaps a drawn family's VARIANT through `draw_lot` (the one place for planner, compose and the site spec's own draw); the mission's own building gets `--holes off`. Deli Counter 0.237.0: `hole_causes.without_holes`, `presets.make(holes=False)`, `new_level.py --holes`, deli_a01 hole-free. Replay: 54 -> 17 of 300 lot levels. A family needs a hole-free variant for the swap to work -- add one when a new family gets a drop.
