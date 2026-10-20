---
name: open-floors-255-awaiting-walker
description: "Roadmap 260 CLOSED 2026-10-19 (DC 0.234.0 table + 0.235.0 hole slide, cold 9338 + 9339); the walker's eye owed on 3 stair-decided OPEN rows; 264 = L27's older walls"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-20T00:44:26.570Z
---

The walker, 2026-10-19: "go ahead with the 255 table, your defaults are good" (after answering "Wall it" on all 48 page questions while unsure; chat came later and is what was built -- one table row flips a pair back).

BUILT: Deli Counter 0.234.0 (a6cbc045; `patches/patch_dc_open_floor_table.py`, finding `docs/findings/open_floor_table_260/` with `plans/plans.html` before/after). `open_floor_rules.RULES` = 20 room-id pairs (I first told the walker 17: a miscount). WALL extends a partition or adds a piece; slides an opening a new wall's end would split (L18); a door where the pair would lose its walkable way (`DOORWAY_POLICY keep_pair_joined`); never into an objective; a pair is rolled back whole if it would leave a new lint FAIL.

FIXED AFTER THE FIRST COLD RUN: Deli Counter 0.235.0 (4fed8011, `patches/patch_dc_ceiling_holes.py`). Cold run 9338's frames showed the table's kitchen wall at x 7 under the delis' 2.2 m drop at (8, -4) in all six delis. layout_lint L27 now names a wall under a hole in its ceiling, and the table slides the hole off a wall it stands (the hole moves, not the wall; refused if it cannot). Cold run 9339 proved it: 0 interventions, the drop-edge gate's 7 lost rows back as declared drops, frames side by side in `docs/cold_runs/cold_9339/hole_9338_vs_9339.jpg`. Roadmap 260 CLOSED; 264 OPEN for L27's older walls (three library atriums, `presets.casino_tower`'s skylight).

Still the walker's: the three rows OPEN where the walker's default was WALL because a stair stands on the line -- office lobby|ground_bullpen and corner_deli_heist_01's stair well vs its two cold rooms (L21, L18).

**Lessons that cost a round:** a census of only the rules I expected to move passed walls the FULL lint refused -- run `lint_spec` before/after on every touched spec. And a plan can't show a wall under a ceiling hole; the frames did -- shoot the hole stations on the first cold run of any change that adds walls.
