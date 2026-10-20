# Cold run 9354 -- 0 interventions; restaurant_row_001, seed 9003: the first level set at high noon

**What it was for.** The noon beside cold run 9353's morning: Lux 0.79.0's Delco High Noon, which Level Factory
0.225.0 asks for at `time_of_day: noon`. This is 9353's level and brief with that one word changed
(`briefs/restaurant_row_001.json`, morning -> noon).

**Tools:** Lux 0.79.0 (9132d32), Level Factory 0.225.0 (af75c5e), Deli Counter 0.239.0, Lot 0.126.0, Zoo 1.116.0.
Staged from 9353; seed 9003 named.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0), read after `cold_run.py --end`; 9 min.
Shell 0 blockers of 79 findings; art 0 of 108; **findings 108 -> 108** against 9353. The Lux apply's own record:
`preset` Delco High Noon, `preset_applied` Delco High Noon.

## Three times of one level (`tod_evening_morning_noon.jpg`)

The same derived cameras in 9351 (evening, Blue Hour), 9353 (morning) and this run (noon): the spawn, the extraction,
the objective. Against the morning, the noon's sky is a deeper, clearer blue with no warm haze and no sun in frame,
the brick wall at the extraction lit evenly from high overhead, and the street a little cooler. The two days are
nearer each other than either is to the evening, which is what an hour's difference in the sun should be.

## The price (`_runs/perf_inner/run.py`, 53 station-headings)

The morning (9353) and the noon (this run) in turn, twice each (`price_morning_vs_noon_a.out.txt`, `_b`), and
against this level's evening -- 9351's package, priced twice earlier the same day -- in 9353's
`price_evening_vs_morning.out.txt`.

| | evening (9351) A | evening B | morning A | morning B | noon A | noon B |
|---|---|---|---|---|---|---|
| draws, all headings | 34,731 | 34,731 | 23,609 | 23,609 | 23,609 | 23,609 |
| p95, mean a heading | 3.949 ms | 3.777 ms | 3.080 ms | 3.091 ms | 3.069 ms | 3.073 ms |
| the worst heading | 10.54 ms | 9.21 ms | 7.01 ms | 7.03 ms | 7.19 ms | 6.97 ms |
| meshes over the 8-light cap, paired | 9 | 9 | 5 | 5 | 5 | 5 |

- **The morning and the noon cost the same:** the same draws at every heading, the frame time 0.013 to 0.017 ms a
  heading apart against the mornings' own 0.099 ms floor.
- **A day draws a third less than this level's evening:** 210 fewer draws a heading (median 164, most 562), p95 0.78
  ms a heading under it against the evenings' 0.223 floor, the worst heading 10.5 -> 7.0 ms, the meshes over the
  light cap 9 -> 5, the same mesh instances and video memory. Attributed, not measured apart: the street lamps are
  dark by day (Lux 0.71.0), and the lamps and the shadow maps they cast are what the evening adds.
