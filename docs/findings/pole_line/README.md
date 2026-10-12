# The pole line (roadmap 240)

The walker's Philly comps (`docs/reference/PHILLY_STREET_COMPS.md`) put the
overhead network in two of three frames; the factory stood a steel lamp on
both kerbs every 25 m and not one pole. The walker's calls of 2026-10-12
(`docs/proposals/POLE_LINE_DESIGN.md`): one side of every street; the full
wire set without house drops; a transformer can every third or fourth pole; a
cobra-head on every pole.

Built in three steps, each its own release:

1. **Zoo 1.104.0, the pole** (`patches/patch_zoo_utility_pole.py`): a 40 ft
   wood pole, its crossarm and insulators, the cobra-head on a 6 ft arm, a
   `transformer` form; four materials, so four draws a pole (Blender 5.1.1:
   census 3 builds 0 coincident pairs; both forms PASS through the kit path).
2. **Lot 0.118.0, the line** (`patches/patch_lot_pole_line.py`): one kerb of
   every street, poles at the kerb no more than 36 m apart, every pole's light
   at its lens, a can every third or fourth pole by the buildings it serves.
3. **The wires**, between the poles -- next.

## The census (`pole_census.py`, `pole_census.out.txt`)

Each Lot checkout's planner on the four stored site fixtures of cold runs,
their cover dropped first:

    fixture                         0.117.0 lamps   0.118.0 poles / cans   lights      trees   hydrants
    bank_block_001 seed 9256        18              8 / 3                  18 -> 8     16      3
    club_block_014 seed 9080        20              9 / 3                  20 -> 9     21      3
    club_block_014 seed 9181        15              9 / 3                  15 -> 9     18      2
    restaurant_row_001 seed 9205    16              9 / 3                  16 -> 9     14      2

The street lights about halve, as the walker's option said they would (pools
with dark between); whether a street reads too dark is for frames, not this
table. The trees and hydrants did not move on these four. On Lot's kerb probe
they did: its first kerb now takes every corner hydrant the site's spacing
allows, its lamps having refused two of them (four across both kerbs became
three on one) -- the hydrant rule working alone, recorded rather than undone.

## In a real drive: cold run 9262 (`docs/cold_runs/cold_9262/`)

0 interventions; the picked lot stands 11 poles (4 with cans), every pole a
module and its light at the lens. Its Laser Tag route read 0.64 where 9261's
read 1.00 -- and `lt_pole_ab.py` (`lt_pole_ab.out.txt`), the job's command on
copies of both runs' staged projects, says the poles are not the snag:

    9262 as built (poles, no lamps)        route 0.64   player stuck 29   76
    9262 with its 11 poles removed         route 0.72   player stuck 45   78
    9261 as built (lamps on both kerbs)    route 1.00   player stuck  9   80
    9261 with its 19 lamps removed         route 0.88   player stuck 50   79

Both controls read their jobs in every field. No stuck event stood within
1.5 m of a pole; they stand at a kerb face (-66, -5) and beside a meter
between two parked cars (35, -17), where 9261's bot stuck too. The route on
this lot swings with any change to its furniture -- the navmesh it reshapes
decides which way the bot walks into two snags that were already there --
filed as roadmap 242.

## Found on the way (Lot 0.118.0's drafts)

- **A lost station doubles a span.** The first draft stepped a pole only up to
  6 m and lost one inside the probe's 20 m footpath cut: a 75 m gap. A pole
  now also tries a cut's or a shop band's ends (`site_poles._steps`).
- **Along-only spacing is wrong across two lines.** `site_furniture._free`
  compares stations along the road, right for pieces on one line. The
  corner's bin and blade stand on the furniture line 1.9 m across the band
  from the pole line, and read along-only they refused both ends of that cut.
  The pole reads plan boxes instead (`site_poles._room`); a tree keeps its
  crown's spread and a signal 5 m.
- **A band on one kerb moves the whole line.** `pole_kerb` takes the kerb with
  less to dodge, so the band tests put a matching band behind both kerbs.

## Found by the first cold run (Lot 0.118.1)

Cold run 9262's west side street stood 2 poles for 3 stations: no corner pole
at its T, so its first pole stood 35.7 m from the main road's nearest -- past
the reach a junction's wires take. Re-planned from the run's drawn spec, step
by step: `_runs` trimmed a road crossing by the cut's WIDTH where the kerb's
span reaches `site_streets.CUT_MARGIN` (0.6 m) further, so every run's first
station stood in the cut's clearance; and 0.118.0's 5 m circle round a signal
refused every step off it, though the signal stands on the furniture line and a
pole on its own line clears its arms by 1.63 m (REFUTED, KEPT in `site_poles`).
Lot 0.118.1 breaks runs at the kerb's spans, asks a signal's arm box, and reads
every road's pieces at a corner: the west street stands 3 poles, the first 7.05
from the crossing, and the fixtures' census 8/9/9/9 poles became 9/10/9/9.

## Frames (`docs/cold_runs/cold_9262/poles.png`, `pole_frames.sh`)

The same three stations in 9261's package and 9262's, at the level's evening
light: the line along the kerb, a can's pole from across the street, the
corner. For the walker's eye: the darker gaps between the pools (the "every
pole" call) and the wood's colour under sodium light.
