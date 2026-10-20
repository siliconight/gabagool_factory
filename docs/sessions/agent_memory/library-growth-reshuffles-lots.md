---
name: library-growth-reshuffles-lots
description: "Adding a building family to Deli Counter's library changes what every existing brief+seed draws (pick_lot pops from the pool by index). club_block_014 seed 9181 lost its gas station at DC 0.171.0."
metadata:
  type: project
---

Cold run 9134 (2026-10-02): club_block_014 seed 9181, which had drawn gas_station_a02 + airport_terminal_a02 + strip_club_a01 in every run 9121-9131, drew arena_a03 + mansion_a02 + strip_club_a01. The only library change was Deli Counter 0.171.0 adding `video_store_a01`. `level_factory/packages/pipeline/building_library.py` `pick_lot` draws non-anchor buildings as `pool.pop(next(rng) % len(pool))` and its own comment says a pool change "reshuffles every existing draw". Not isolated by re-running without the video store.

**Why:** the comparison baseline every cold run used is gone, and a batch note saying "Expected: the same lot" was wrong.

**How to apply:** never predict "the same lot" across a library change; a brief's ARCHETYPE anchors one building in every candidate (video_block_001 anchors the video store), so a baseline that must survive library growth needs an anchored brief -- a `gas_station` brief for the store's machines. The 9131 gas-station walk copy was rebuilt at `_runs/walk_9131_gas_station` (the default `_runs/walk_export_club_block_014` now holds 9134's lot). Pick candidates with the scratch `pick_candidate.py` rule (walktest ok, no major LT route/pathing finding), not seed 9181 by habit.

**Update 2026-10-02:** the anchored brief exists: `gas_block_001` (archetype gas_station), first run cold 9135 (seed 9080: bank tower, freight terminal, gas_station_a03), walk copy `_runs/walk_export_gas_block_001`. It is the baseline for the store machines from here on.
