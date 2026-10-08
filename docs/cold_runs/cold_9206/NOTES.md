# Cold run 9206 -- 0 interventions; the lost arrival is back, and a phantom finding found

club_block_014, seed auto, staged from cold run 9205. Tests roadmap 212's
lane and vehicle:
- **Lot 0.100.0.** The responders' vehicle is Zoo 1.86.0's cruiser, and an
  arrival's lane steers round what stands in it.
- **Level Factory 0.161.0.** The package ships the steered lane as boxes,
  `responder_arrivals.json` schema v2.
- **Zoo 1.86.0** is in the run too. Its cruiser is not placed in any level;
  `simple_car`'s own cars were hashed unchanged before it shipped.

Tool versions hashed at `--begin`: Lot 0.100.0, Level Factory 0.161.0, Laser
Tag 0.25.0, Zoo 1.86.0, Deli Counter 0.203.0, Lux 0.69.0, Dispatch 0.5.2,
Patina 0.29.1, Pixelcoat 0.61.0, Pipeline 0.6.0.

**`INTERVENTIONS: 0`.** The journal holds no entries, and the run's diff is
empty. Every leg ran.

**Picked: seed_9181**, the site cold runs 9204 and 9205 lost an arrival on.

| seed | 9205 | 9206 |
|---|---|---|
| 9080 | 1 major, route completion 0.76 | 2 majors, 0.92 |
| 9181 | 0 majors, 0.84 | 0 majors, 0.96 |
| 9282 | 1 major, 0.92 | 1 major, 0.96 |

- **Why the figures moved.** The reservations changed, and so did what
  parks in each street.
- **On 9181**, the street holds one car fewer: the one at (66.5, -20.25),
  now kept out of the new stop.
- **Not attributed further.** The route figures are Laser Tag's, two runs
  apart, on streets that changed between them.

## Roadmap 212: the lost arrival is back

| | cold run 9205 | cold run 9206 |
|---|---|---|
| arrivals on seed_9181 | 2 | 3 |
| `LOT_RESPONDER_ENTRY_NO_STOP` | 2 (one road end, counted twice) | 0 |
| `responder_arrivals.json` | v1, 2 arrivals | v2, 3 arrivals |
| vehicle | 2.0 x 5.4 x 1.5 | 2.196 x 5.545 x 1.578 |

**The pipeline did what the replay predicted.** Lot's `lot_assemble` on
seed_9181 wrote, to the millimetre, the stops the fixture replay gave:

| road, travel | stop | lane |
|---|---|---|
| road 1, -1 | (40.6, -11.363) | no shift |
| road 0, -1 | (62.637, -22.75) | 0.648 m, in nine boxes |
| road 0, +1 | (56.363, -25.55) | no shift |

- **Road 0, -1 is the end 9204 lost.** Its lane steered round the getaway
  van.
- **Road 0, +1 moved 7.6 m west.** The steered lane now shares its road,
  and a stop cannot stand in another arrival's lane.

**The package carries it.** From `LF_club_block_014.portable-godot`:
- `responder_arrivals.json`: schema v2, three arrivals, each with the
  cruiser's dimensions, the steered one with its nine boxes and
  `lane_shift_m` 0.648;
- in the resource manifest;
- three `responder`-tagged anchors in `gameplay_anchors.json`.

**Every stop was walked.**
- **The spawns.** Lot's nav QA (`site_navqa.tscn`) lists six bot spawns:
  9204's three that are not stops, and all three stops.
- **The bots.** The director hands 16 bots out round-robin
  (`nav_qa_director.gd:244`, `bot_spawns[i % n]`), so every stop got at
  least two.
- **The walk.** `site_navqa.walktest.json`: all 20 walkers `ok`, none
  stranded, no proof failures. 9204 had five spawns and the same 20 `ok`.

## A new finding, and it is a phantom

Findings 60 to 59: `LOT_RESPONDER_ENTRY_NO_STOP` 2 to 0, and
`LOT_RESPONDER_BLOCKED` 0 to 1.

**What it says.** It is a major, from seed_9080, a candidate this run did
not pick: "step_van at (-9.0, -26.9) stands in responder arrival 0's lane
on road 0".

**What is true.** The van did not move: the placed and drawn records agree
at (-9.0, -26.92). Arrival 0's lane steered round it, 0.648 m as on 9204,
and the planner checked its boxes against the van. Printing the floats:

| | value |
|---|---|
| the recorded box's edge | -28.22 |
| the van's edge, by `cover_rects` | -26.92 - 1.3 = -28.220000000000002 |
| the overlap the read-back found | 3.6e-15 m |

**Why.** One number had two spellings, and a threshold was asked of each:
- the planner checked the box unrounded, 1e-6 m clear;
- the record rounded it to three decimals, onto the van's edge;
- the read-back, `blocked`, checks the recorded box.

On 9204's site the same arithmetic happened to round the other way, so the
fixture test there passed by luck.

**Fixed in Lot 0.100.1** (c31c92e). The planner rounds each box once,
checks it, and records that box. A steered lane clears what it passes by
the record's 1 mm.
- **The regression test** has a fixture from this run's seed_9080. On
  0.100.0 it fails on the phantom finding itself.
- **Cold run 9207** runs 0.100.1 on this mission.

## Other figures

- **Shell:** 3 candidates, all distinct; 0 blockers of 43 findings.
- **Art:** 0 blockers of 59. The leg exits 1, as 9204's and 9205's did; the
  driver gates on "blockers open: 0".
- **The bake:** 432 models and 1,528 primitive meshes lightmapped, 7 kept
  dynamic; 76 steady rigs baked, 13 failing and 2 cycling left live; 172
  room fills; 3,898 users; 83.2 s in the editor.
