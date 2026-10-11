# Cold run 9247 -- three graders at once, and the enemy as the contract's body, on the big lot

**What it tested:** two releases measured where 9245 had already run:
Level Factory 0.179.1 (roadmap 239: `scheduler.godot_cap` lets three Godot
graders run at once where 9245 ran two) and Laser Tag 0.26.0 (roadmap 197:
enemies built as the contract's body, steering with the crew's arrival
radius), with Deli Counter 0.209.1's bounded stair column beside them.
restaurant_row_001 on 9245's lot and seeds; Lot 0.116.0, Zoo 1.101.0, Lux
0.75.0, Pixelcoat 0.62.0, Patina 0.30.0 as in 9245.

**Result: 0 interventions, 0 tool files changed; the package baked on its
first attempt** (3,501 lightmap users, as 9245). seed_9104 picked, as in
9241 to 9245 (route completion 1.00). Findings 125 -> 122, every item
accounted for:

    LT_MAP_ENEMY_STUCK         1 -> 0   seed_9104's enemies no longer jam (below)
    PRESENTATION_CIRCULATION   2 -> 0   Deli Counter 0.209.1, as regate_9245.py predicted (8 conflicts -> 0)

## Same build first

The comparisons below are between two runs of the same lots, proven, not
assumed: every `lot_assemble` output of the three candidates is
byte-identical to 9245's (46 of 46 files a seed), and so is every walk
test's report. What changed between the two runs' graders is Laser Tag's
version and how many ran at once.

## The shell leg: 15.7 -> 10.4 minutes

From each job's own `duration=` and log time (minutes from the leg's start):

    9245 (two at a time)                     9247 (three at a time)
    0.4 ->  6.8  Laser Tag seed_9003         0.4 ->  7.0  Laser Tag seed_9003
    2.9 -> 13.2  Laser Tag seed_9104         0.5 -> 10.4  Laser Tag seed_9104
    9.1 -> 13.1  Laser Tag seed_9205         5.1 ->  9.4  Laser Tag seed_9205
    13.2 -> 15.7 walk test seed_9205         7.1 ->  9.7  walk test seed_9205

    shell leg   15.7 min -> 10.4 min
    art leg      4.4 min ->  4.2 min
    export       7.6 min ->  7.6 min (bake 92.6 s -> 101.7 s in the editor)
    the drive   30.4 min -> 24.3 min (from --begin to the driver's last line)
    job-minutes 31.6     -> 31.5     (the same work, side by side)

Roadmap 239 predicted "about 10.5, the longest evaluation's length". The leg
now ends when seed_9104's evaluation does (9.89 minutes of it), so on this
lot three is the floor: only a shorter evaluation shortens the leg.

## Every evaluation waits on the clock

Simulated time (the sum of each report's 25 run durations) against the job's
wall time:

    run   seed   simulated   job wall   ratio
    9245  9003   25.15 min    6.40 min   3.93
    9245  9104   40.70 min   10.26 min   3.97
    9245  9205   15.61 min    3.99 min   3.91
    9247  9003   26.17 min    6.65 min   3.94
    9247  9104   39.20 min    9.89 min   3.96
    9247  9205   16.75 min    4.28 min   3.92

Two at a time and three at a time alike, each evaluation runs at its 4x
clock less the import and the nav bake: it is paced by real seconds, not by
the processor. `run_map_eval.gd`'s comment says "Headless evaluation
shouldn't wait on real-world seconds"; measured, it does. This is why three
side by side ran no slower. Whether an unsynchronised clock (Godot's
`--fixed-fps`) computes the same reports faster is
`docs/findings/grader_speed/fixedfps_ab.sh`, run after this one.

**What followed (the same evening, on this run's staged projects):** alone,
`--fixed-fps 60` computed seed_9104's evaluation in 21 s against the job's
593 s but moved its crew stuck count 9 -> 21; with the navigation map
updating on the evaluation's thread it read identical to the job in every
field, under either clock and three at once. Shipped as Laser Tag 0.27.0 and
Level Factory 0.180.0 (`docs/findings/grader_speed/README.md`, Lever 4).

## Laser Tag 0.26.0 on the big lot

    seed   run   grade              score  enemy stuck  crew deaths  runs with a crew death  first crew death (median)
    9003   9245  PASS_WITH_TUNING   79      0            3            3                       3.73 s
    9003   9247  PASS_WITH_TUNING   80      0            5            5                       6.13 s
    9104   9245  PASS_WITH_TUNING   75     36           11           10                      14.10 s
    9104   9247  PASS_WITH_TUNING   80      3           29           23                       9.87 s
    9205   9245  WARN               74      0            2            2                       5.77 s
    9205   9247  PASS_WITH_TUNING   75      0            8            6                       5.94 s

- **seed_9104's enemies stopped jamming: 36 -> 3**, and its `ENEMY_STUCK`
  WARN is gone, which is the art leg's `LT_MAP_ENEMY_STUCK` 1 -> 0.
- **The enemies that used to jam now arrive and fight.** Crew deaths rose on
  every seed, most on the one whose enemies had jammed: seed_9104 11 -> 29,
  a crew death in 23 of 25 runs against 10. The grader reads this lot as
  more contested than it did, and a reading where the enemies reach the
  crew is the truer one. Every run still ends with all six enemies down
  (150 enemy deaths a seed, both runs) and seed_9104's route completion is
  1.00 in both.
- `avg_player_survival_seconds` is the time of a run's FIRST crew death, or
  the run's whole length when nobody died (`LT_MetricsCollector.end_run`), so
  its fall on seed_9104 (64.65 -> 16.20 s) is mostly more runs having a death
  at all (10 -> 23 of 25); among the runs with one, the median first death
  came at 9.87 s against 14.10.
- The crew's own figures moved by one or two (player stuck 2 -> 1, 10 -> 9,
  14 -> 15). Which part is the enemies' changed fights and which the 0.01 m
  noise three-wide can show (roadmap 239), this run cannot separate.
- **Jams did not cost wall time here.** No run reached the 180 s limit in
  either run; seed_9104's simulated time fell 40.70 -> 39.20 minutes and its
  wall 10.26 -> 9.89.

## What is evidence of what

- 0 interventions, the bake, the findings, the grades and stuck counts, the
  job timings: this run and 9245, each from its own job logs and reports.
- Same build: hashes of both runs' `lot_assemble` and `walktest_navqa`
  outputs.
- The drive's length: `--begin`'s journal time to `driver.log`'s last write;
  9245's to its last write the same way.
- The clock reading is a measurement (the ratio); that Godot keeps physics in
  step with real seconds is the explanation it suggests, which
  `fixedfps_ab.sh` tests.
