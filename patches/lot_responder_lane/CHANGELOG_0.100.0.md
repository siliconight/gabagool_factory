## 0.100.0 - the responders' cruiser is Zoo's, and its lane steers round what stands in it

**Roadmap 212.** Zoo 1.86.0 built the cruiser the walker asked for, a 1990s
Crown Victoria lettered DELCO COUNTY POLICE. Two changes here had to land
together.

### The vehicle is Zoo's

`site_responders.VEHICLE` is the `cruiser` genome's defaults:

| | 0.99.x | 0.100.0 |
|---|---|---|
| width | 2.0 | 2.196, to the mirror heads |
| length | 5.4 | 5.545, push bar to rear bumper |
| height | 1.5 | 1.578, to the light bar's top |

- **Pinned, because Lot does not import Zoo.**
  `test_the_vehicle_is_zoos_cruiser` reads the genome and
  `car_forms.CRUISER` whenever Zoo stands beside this repo, and fails when
  they disagree.
- **`MIRROR_OUT`** (0.105, Zoo's `mirror_out`) separates the body from the
  mirrors.
  - **A door opens from the body,** so the stop's door room is measured from
    its 1.986 m: the stop is 3.986 m across, where 0.99 had 4.0.
  - **A lane passes the mirrors,** so it is measured from them: 3.196 m
    with `LANE_MARGIN` each side, where 0.99 had 3.0.
- **`ENTRY_RUN`** stays twice the length: 11.09 m.
- *As 0.99.0 wrote it:* the 2.0 m was a width "to the mirrors". Wrong. The
  published 1.99-2.0 m it cited is a Crown Victoria's body.

### Why the lane had to steer in the same change

Cold run 9204 lost one arrival of three to the getaway van: its mirrors
stand 0.45 m out of the parking lane into road 0's eastern driving half
(`docs/findings/responder_entry_no_stop/` at the factory root). Measured on
that road, against the van's edge at -21.80:

| what is centred in the lane | across, plan y | over the van |
|---|---|---|
| 0.99's lane box, 3.0 m | -24.25 .. -21.25 | 0.55 m |
| 0.100's lane box, 3.196 m | -24.348 .. -21.152 | 0.648 m |
| the cruiser alone, 2.196 m | -23.848 .. -21.652 | 0.148 m |

So the cruiser's real width alone makes the van case worse, and so does
the box built round it. No vehicle passes that van without moving over.

### The lane steers

A driver meeting a van parked out of its bay moves toward the centre line,
and across it, rather than stopping. Now the lane does too:
- **Slices.** The lane from the entry to the stop's rear is cut into
  `STATION_STEP` (1 m) slices.
- **The shift each needs.** A slice moves toward and across the centre line
  by the least shift at which its box clears every standing rect and every
  other arrival's stop (`_needs`).
  - Each rect beside the slice forbids an open interval of shifts.
  - The least allowed shift is 0, or the top of the chain of intervals that
    holds 0.
  - It is computed once an entry, for every stop tried along it.
- **The bound.** A lane may shift until its far edge meets the oncoming
  driving half's outer edge (`shift_limit`). The far parking lane is the
  other kerb's, where cars stand.
- **The taper** (`steer`). A shift ramps up before what it passes and down
  after it, at `SHIFT_RATE`.
  - The rate is MUTCD (2009) section 6C.08's shifting taper, L/2 with
    L = W * S^2 / 60 below 40 mph. A shift of W so takes W * S^2 / 120
    along the road, a rate of 120 / S^2: 0.192 across per metre along at
    `SHIFT_SPEED_MPH` 25.
  - That speed is STATED: a residential street's posted speed.
- **Back in its own half by the stop.** A lane that cannot taper back to 0
  before the stop's rear is refused for that stop.
- **Read back.** Every box is checked against standing ground and other
  stops before the lane is kept.

**What a record carries.** `lane_boxes`, each a run of slices at one shift,
in order from the entry, and `lane_shift`, the largest. They replace
`lane_box`, because one box drawn round a steered lane covers the van the
lane goes round.
- `keep_out` and `blocked` read every box.
- Level Factory 0.161.0 ships them. An older Level Factory cannot read this
  Lot's arrivals, so the two go together.

### Measured

**Cold run 9204's seed_9181**, as its assemble planned it: the new fixture
`club_block_014_seed_9181.site.json`, the input site with its cover as
drawn, cut back to the van.

| | 0.99.1 | 0.100.0 |
|---|---|---|
| arrivals | 2 | 3 |
| `LOT_RESPONDER_ENTRY_NO_STOP` | 1 (road 0's east end) | 0 |

- **The east end's stop** is (62.637, -22.75).
- **Its lane is nine boxes.** It shifts 0.648 m, exactly what the van's
  edge needs, ramping 0.072, 0.264, 0.456, holding past the van from x 79.5
  to 71.5, and ramping back to 0 by x 65.41.
- **The road's other arrival moved** from x 64.0 to 56.4. A stop with its
  doors open cannot stand in another arrival's lane, and the two lanes now
  share the road.

**Cold run 9198's seed_9256:** three arrivals, as before. Each stop moved
0.36-0.64 m on the new station grid, and no lane needed to shift.

**The control moved.** It used to be cold run 9198's car at (21.1, 14.8) on
seed_9256, in a stop. Now that stop misses it by about 4 cm, so on 9256
nothing lands in a stop either way, and that ground controls nothing. On
9204's site:
- **The record.** Cold run 9204 parked a `simple_car` at (66.5, -20.25), in
  what is now the steered arrival's stop, and the read-back names it.
- **Unreserved,** `plan_parking` parks it there again (37 cars).
- **Reserved,** no car lands in a stop or a lane (36).

**Tests.** `tests/test_site_responders.py` has 12, four of them new:
- the steering on 9204;
- the taper, and a need too close to the stop;
- a lane nothing can pass;
- the Zoo pin.

Run on 0.99.1, the file fails 6, the steering test on
`LOT_RESPONDER_ENTRY_NO_STOP` itself.

**Suite:** 705 passed (701 + 4), `python -m pytest -q`.

### Not proven

- **No cold run yet.** One on club_block_014 follows.
- **Rotated roads.** `_box` is a bounding box there. The steering's
  projection is exact and the read-back uses the bounding boxes, so such a
  lane may be refused where it would pass.
- **A shift toward the kerb.** Not built. What stands in a lane before the
  responders are planned is the van, at the kerb.
