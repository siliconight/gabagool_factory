# Cold run 9262 -- the pole line in a real drive

**What it tested:** roadmap 240's first two builds in a real drive of
restaurant_row_001: Zoo 1.104.0's utility pole and Lot 0.118.0's line (one
kerb of every street, a cobra-head on every pole, a can every third or fourth
pole, no steel lamps on the band roads), everything else as in 9261.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked, as in
9241 to 9261. The picked lot stands 11 poles -- 7 `auto`, 4 `transformer` --
and its lane keeps its 2 steel lamps (0.116.0); the site's 13 streetlight
anchors hang at 7.498 m (the sidewalk's 0.097 and the lens's 7.401) and the
lane's at 5.825. Zoo's site kit built both forms, PASS
(`prop_utility_pole_delco_1997_01_w30_d367_h1040` x7 and the `_ftransformer`
x4), and every pole stood as its module.

## Against 9261

- **The export:** 494 -> 497 models, 3,320 -> 3,333 lightmap users, 224
  primitives and 6 dynamic as before; 213 -> 210 steady rigs and 29 -> 26
  failing -- six fewer street lights on the picked lot, as the line puts one
  on each of 11 poles where 0.117.0 stood a lamp every 25 m on both kerbs.
- **Findings 122 -> 120, every item Laser Tag's** (the validation reports,
  candidate by code): seed_9104 `LT_MAP_BLIND_MAP` 1 -> 0 and
  `LT_MAP_TRAVERSAL` 0 -> 1; seed_9205 `LT_MAP_PLAYER_STUCK` 1 -> 0 and
  `LT_MAP_TRAVERSAL` 1 -> 0.

## The picked candidate's route: the furniture moves the dice, the poles are not the snag

Laser Tag read seed_9104 at route completion 0.64 and 29 player-stuck events
(PASS_WITH_TUNING 76) where 9261 read 1.00 and 9 (80). Measured, in order:

- **No stuck event within 1.5 m of a pole**: the nearest 16.6 m. They stand at
  two places -- (-66, -5), a kerb face, 18 events where 9261 had 6 there, and
  (35, -17), beside a parking meter between two parked cars, 5 -- and the
  cover within 5 m of each is the same in both runs.
- **`docs/findings/pole_line/lt_pole_ab.py`**, the job's own command on copies
  of the staged evaluation projects (both controls read their jobs in every
  field):

      9262 as built (poles, no lamps)        route 0.64   player stuck 29   76
      9262 with its 11 poles removed         route 0.72   player stuck 45   78
      9261 as built (lamps on both kerbs)    route 1.00   player stuck  9   80
      9261 with its 19 lamps removed         route 0.88   player stuck 50   79

  Taking the poles out does not give 9261's reading back, and taking 9261's
  lamps out moves it as far; the two arms with neither still read 0.72 and
  0.88. On this lot the route Laser Tag reads swings with ANY change to the
  street's furniture -- by the navmesh it reshapes, and with it which way the
  bot walks into two snags that were already there. 9261's 1.00 was one roll
  of those dice; the snags are the defect.

## The time

    run    shell   art     export   walk   retire   the drive
    9261   79 s    165 s   183 s    11 s    4 s     7.5 min (449 s)
    9262   77 s    160 s   175 s    10 s    4 s     7.4 min (443 s)

## What is evidence of what

- The time: the step stamps in `driver.log`.
- The poles and their light: the picked lot's `site.slots.json` and
  `site.site.lights.json` in the run's workspace; the kit build's log.
- The findings and the route: the validation reports and Laser Tag's reports
  of 9261 and 9262; `docs/findings/pole_line/lt_pole_ab.out.txt`.
- The result: `cold_run.py --end`.
