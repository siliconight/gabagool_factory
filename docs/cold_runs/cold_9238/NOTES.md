# Cold run 9238 -- Lot 0.116.0 on 9233's lot: the lane lights its own length

**What it tested:** the dark lane's design call (2026-10-11, made after the
walker asked for the calls): Lot 0.116.0 stands the street's own lamp
along a road without a sidewalk -- the `block` grammar's service lane --
on the side the buildings it runs behind stand, evenly spread no farther
apart than 40 m (further than two of the lamp's 14 m reaches: pools with
dark between), 0.6 m beyond the paved edge, clear of the path corridors,
footprints, parking fields, mouths and markers. On 9233's brief and lot
(restaurant_row_001, seed auto), priced against 9237's package, the same
lot one Lot release earlier.

**Result: 0 interventions, 0 stops.** Three candidates, seed_9104 picked
as before, 0 blockers on both legs. The bake: 491 models and 224
primitives lightmapped as 9237's, 212 steady rigs baked and 30 failing left
live where 9237 had 211 and 29 -- the two lane lamps, one steady and one in
Lux's failing set. The closure clean.

**The lamps:** two on 9104's lane, `Lamp_55` at plan (7.8, 24.1) and
`Lamp_56` at (47.4, 24.1), on the row's (south) side, both in the site's
lights manifest as streetlights at the lens height. The lane's slab is 79 m,
so two at its 40 m spacing, each half a spacing in from its mouths;
b1's rear spur at x = 4 is 3.8 m from the first, its corridor and the pole
clear by the planner's keep-out.

## One more finding, and it is not the lamps

`findings 122 -> 123`: `LT_MAP_PLAYER_STUCK` on a third candidate. Read off
the Laser Tag reports: seed_9003 (not picked) reported 2 player stuck
events where 9237's run of it reported none, both at plan (-10.4, -13.6),
the main street's north sidewalk -- 38 m from that candidate's nearest lane
lamp at (-5.3, 24.1). The picked seed_9104 went from 19 stuck events to 10,
its enemy events clustered at the same sidewalk (plan y = -11). Two poles on
a lane change where the bots' runs go, and the run's own variance put one
more candidate over the reporting line. Recorded, not counted against the
lamps.

## The price (`price/`, 9237's package the control)

    measured control_1  53 headings  draws mean 2522 worst 5253  p95 median 5.30 ms
    measured glow       53 headings  draws mean 2524 worst 5257  p95 median 5.30 ms
    measured control_2  53 headings  draws mean 2522 worst 5253  p95 median 5.17 ms
    controls' spread, median over 53 headings: p95 0.10 ms, draws 0.0 (the noise floor)
    draws vs controls' mean: median 2.0  min 0.0  max 8.0
    p95 ms vs controls' mean: median +0.04  min -0.62  max +1.13

- **+2 draws a heading median, 8 at most, where a lane lamp is in view;**
  27 of 53 headings see one. The frame time is inside the noise: +0.04 ms
  at the median against a 0.10 ms spread between the two control runs,
  which themselves disagreed by up to 1.15 ms on one heading.
- **The paired census:** no mesh over 8 live lights but the two 9233's
  package already carried (the horizon glow, 240 to 242 as the lamps reach
  its sky-sized box, and one roof at 10). The 32 m tiles and paint cells
  under the lane are not among them.

## Seen (`lane.png`; `lane_frames.sh`, `tools/lane_stations.py`, `tools/lane_lamp_stations.py`)

The lane from both ends, and on the lane 12 m short of each lamp looking
past it, at dusk: 9237 left, 9238 right. 9237's lane is black from end to
end between the rear yards and the plate's edge. In 9238 each pole stands
at the lane's right edge with a warm pool on the asphalt around its foot,
the centre and edge lines picked out in it, and the lane dark again
between the pools -- pools, not a lit street, which is the call. The pools
are modest at this hour: a lamp's light on dark asphalt at dusk, the same
as the main street's under its own lamps.

## What is evidence of what

- The price and the frames are the lamps' and nothing else's: the same
  lot, brief and seed, and Lot 0.115.0 to 0.116.0 the only change.
- One lot, one time of day. A lane whose row backs onto it with rear doors
  on both sides would test `lane_side`'s vote; this one has its row on one
  side and the plate's edge on the other.
- The lane's stop control is still never stood -- `LOT_TRAFFIC_CONTROL_NO_BAND`
  twice in the furniture findings, as since 9233: a lane has no sidewalk
  band to stand a sign on. A real alley mouth often has none; recorded,
  not called.

## Instruments

- `price/`: the three perf reports, `price.txt`, `vs_mean.txt`, `price_vs_mean.py`.
- `lane_frames.sh`, `tools/lane_stations.py`, `tools/lane_lamp_stations.py`:
  the eight frames; the sheet `lane.png`; the frames in `_scratch/frames_9238_lane/`.
