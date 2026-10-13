# The breadth sweep, 2026-10-13: paused after one mission, on the disk

**Why.** Every cold run since 9264 has built restaurant_row_001. Since each other mission last ran cold --
from cold run 9169 (video_block_001) to 9246 (deli_001) -- the factory has shipped:

- the stoops and railings (Deli Counter 0.211.0-0.212.0, Zoo 1.105.0);
- the tar roofs (Deli Counter 0.210.0);
- the reflection atlas sized to the package (Level Factory 0.198.0);
- the price's memory (Level Factory 0.199.0);
- four grader releases (Laser Tag 0.28.0-0.31.0);
- the mid-rise family (Deli Counter 0.213.0).

None of it has been through a cold run on another mission. The zeros on one level are one level's zeros
-- the 2026-10-06 sweep's reason (`docs/findings/breadth_sweep_2026-10-06/`).

**How.** `tools/cold_drive/sweep_one.sh`, one cold run a call, each mission staged from its own last cold
run, the seed picked by the driver. The plan was the seven missions longest without one: video_block_001,
precinct_yard_001, convenience_001, gas_block_001, bank_block_001, card_block_001 and club_block_014.
`sweep_table.py` reads each run's row off its driver log and its picked candidate's Laser Tag report.

## The result so far

    run=9278  mission=video_block_001  interventions=0  outcome=DONE (15:04:44)  seed=seed_9080  grade=PASS 90
              stuck=enemy 0, blocked 0, crew 0  findings=66 / 96  bake_users=2161  drive=8.5 min

**1 of 1 at 0 interventions:** video_block_001, staged from cold run 9169, on today's tools.

## Why it stopped

`sweep_one.sh` refuses a run below 8 GB free on C:, the rule since cold run 9163 died on a full disk. It
started 9278 at 8 GB, and after it C: had 4.3 GB free. That is about 0.75 GB a cold-run workspace.

`tools/factory_retire.py` finds nothing retirable. Every cold workspace is among the newest it keeps or
is named by a record.

The largest things on C: that no rule retires:

- Godot's shader cache in `AppData/Roaming/Godot`, 4.2 GB. The walker cleared it once, at 13.25 GB, with
  a yes.
- `_scratch/`, 5.7 GB, mostly earlier sessions' folders.

Whether to clear either is the walker's. The sweep resumes from precinct_yard_001 (cold run 9172) when
there is room.
