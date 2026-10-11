# Cold run 9233 -- 0 interventions, 0 retries: the first level with a return loop

restaurant_row_001 (`corner_deli`, a `strip` site), evening and clear,
seed auto, 9232's batch and brief (`cluster: auto`) with one field ADDED:
`"road_grammar": "block"`. The first level laid on Level Factory 0.177.0's
`block` grammar -- the T as it was, a second side street past the row's
far end, and a 5 m service lane behind the row between the two streets --
and audited by Lot 0.113.0, which stops the lane at the streets and counts
it (roadmap 199 and 230 step 3; the ground was measured first in
`docs/findings/rear_lane/`).

Tool versions hashed at `--begin` (`_runs/cold/cold_9233/before.json`):
Deli Counter 0.207.0, Dispatch 0.5.2, Laser Tag 0.25.0, Level Factory
0.177.0, Lot 0.113.0, Lux 0.74.0, Patina 0.30.0, Pipeline 0.6.0, Pixelcoat
0.62.0, Zoo 1.97.0. Against 9232: Level Factory 0.176.1 to 0.177.0, Lot
0.112.0 to 0.113.0; the lot is 9232's (deli_a01 at x -51, pharmacy_a01 at
4, office at 48, drawn by `C03_station_neighborhood`), so the two runs
differ by the street form alone.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 0,
driver exit 0.**
- **The shell leg:** 3 candidates built, all distinct, 0 blockers of 86;
  picked seed_9104 (0 major, route completion 1.00; 9003: 1 major, 1.00;
  9205: 1 major, 0.48).
- **The art leg:** 0 blockers of 122.
- **The export:** `closure verdict: ok=true, 0 issue(s) over 81
  resource(s) in a package of 2959 file(s)`; the light bake ran (472
  models and 1,590 primitive meshes lightmapped, 206 steady rigs baked, 29
  failing left live, 215 room fills, 100.4 s); `backdrop: 269 instances of
  7 module(s) on their sides, 25 draw calls`; surface dressing 4,285
  instances of 4 meshes in 4 draws (9232: 3,642 -- the lane's and the
  second street's surfaces take dressing too).

## The block, stage by stage

- **The spec** (`themed_site_assemble/1/out/site.site.drawn.json`):
  `road_grammar_resolved` asked `block`, got `block`, known. Four roads:
  the main street at y -21.7 across the 171 m plate; the first side street
  at x -20 from the main street to y 32; the second at x 75.2, the same
  run, half a band past the office's east edge; the lane at y 27.2 from
  x -20 to 75.2, 5 m wide, no sidewalk, `kind: service_lane`, `serves`
  b0, b1, b2 -- 8 m and half its width past the deli's rear face at 16.7,
  past the dumpster yards (6 m) and the road margin (2 m). The plate is
  171 x 96 (9232: 177 x 99; the second street replaced the T's westward
  widening).
- **The doors:** 14 paths. The front spurs and the office's rear spur are
  walks; five spurs are recorded undrawn by `LOT_PATH_END_OFF_DOOR` (the
  deli's and the pharmacy's rear spurs, and three side spurs toward the
  streets): the shells have no ground door on those faces. The lane
  serves the office's rear door and the dumpsters; the deli's and the
  pharmacy's rear doors are Deli Counter's to add (roadmap 199, left).
- **Lot's streets** (`site_streets.roads` and `approaches` run on the
  spec): the lane's two junctions resolved as T stems -- the lane's slab
  clipped to 8.0..87.1 of its 95.1 m, `terminal` recorded on each street
  at t 48.8 -- and the control is Lot 0.113.0's: the lane's legs `stop`
  and `minor` at both streets, the streets' legs `through`, the two
  street-to-main junctions `signal` as the one was. In the furniture, 2
  traffic signals where 9232 had 1 and 7 sign posts where it had 3 (the
  lane's stop signs among them), 3 bus shelters, 17 streetlights and 47
  parking meters along the kerbs (9232: 2, 15, 46).
  `LOT_RESPONDERS_PLACED: 3 arrival(s)`: road 1 from the first street's
  north end, road 0 from the west end, road 2 from the second street's
  north end at (73.8, 32), a new entry the T did not have;
  `S_RESPONDER_ARC` still reads a 21 degree arc, as it did in 9232.
  `LOT_PERIMETER_FENCED: 6 run(s), 569.7 m` (9232: 589.7).
- **What the lane cost on this plate:** `0 parking field(s)` where 9232
  had one of six bays beside the first side street: the lane's band at y
  24.7 to 29.7 took the field's room. The guide's parking strategy by use
  is roadmap 199's and 230's to keep beside a lane.
- **The audit** (`S_TARGETS`, every line INFO): `1 loop(s) in the road
  graph over 4 junction(s)` where every level before read 0; `1 service
  lane(s) behind the row serving 3 building(s): the guide's connector
  with an owner and users`; `2 road end(s) reach the plate's edge` (the
  streets' north ends stop 16 m short of it, as the T's stem always did);
  the focal stretch 55 m on each leg as 9232; 3 enterable; 96 % ordinary
  fabric. No `S_ADJACENCY` line, as 9232.
- **Laser Tag on the picked candidate** (25 crew runs): route completion
  1.00 and progress 1.00 where 9232's same lot read 0.92 and 0.95; 19
  stuck events where 9232 had 65; 9 player deaths where 9232 had 35. The
  loop is the one thing that changed between the two levels; the sim's
  crew had a way round, and it shows in every number. An observation on
  one seed, not a measurement over many.

## Seen

`lane.png`: two stations on the lane's centre line, 6 m in from each end,
looking along it (`tools/lane_stations.py`), in the evening light.
- **From the first street's end, looking east** (`lane3_a`): the lane runs
  ahead as a dark carriageway between the row's rear elevations on the
  right -- the pharmacy's pale rear box, the office's brick beyond it, the
  deli's dumpster and its pad in the foreground throwing a long shadow
  across the lane -- and, on the left, the backdrop's rowhomes with their
  lit windows beyond the plate's north edge, a parked car and the second
  street's lamps far ahead. It reads as what it is: a service lane behind
  a row, with the borough beyond it.
- **From the second street's end, looking west** (`lane3_b`): the office's
  rear wall tall at the left with its windows lit, the lane dark to the
  far street, the rowhomes' windows on the right.
- **For the walker's eye:** the lane carries no light of its own. Lux's
  poles stand on sidewalks and the lane has none, so at dusk it is lit by
  the rear windows and the backdrop's glow alone, and the crew's way back
  would be a dark alley. That may be the right alley; if not, the lever
  is a wall pack over each rear door that opens onto it, or a pole at
  each mouth, in Lux. And the rear elevations are blank brick with a few
  windows: the rear doors the lane is for are two of three shells short.

## Priced

`price/price.txt`, 9232's package as the control and 9233's as the
subject through `docs/findings/horizon_glow/price_glow.py` (control,
subject, control; the harness calls the subject `glow`): 53 headings a run
at the package's anchors on this heavy level, the frame 5.67 ms p95 at the
controls' median. The two packages hold the same lot and the same tool set
but for the street form, so this is the price of the second side street
and the lane together.

| run | draws +mean | +min | +max | p95 +median ms | +max ms |
|---|---|---|---|---|---|
| control_1 | 0.0 | 0 | 0 | -0.00 | 0.27 |
| subject | 133.4 | -206 | 538 | 0.55 | 3.53 |
| control_2 | 0.0 | 0 | 0 | 0.00 | 0.24 |

Against the controls' mean, heading by heading (`price_vs_mean.py`,
`price/vs_mean.txt`; matched by station and yaw, no pass flipped): **the
block costs +107 draws a heading median (-206 to +538) and p95 +0.55 ms
median (-0.33 to +3.53)**, over the controls' 0.07 ms spread on 44 of 53
headings: a tenth of the frame on the heaviest level in the set. The cost
is where the second street is in view -- `player_start_19` yaw 90 +538
draws, `extraction_15` yaw 270 +483, `highest_vantage` and
`defender_spawn_9` yaw 90 +437, `camera_socket_1` yaw 270 +404 -- and the
headings that look away from it read within a few draws of 9232. A
street is not a slab: its kerbs split at every cut, its crosswalk bars,
stop bars and centre line, its meters, lamps, trees, signs, a shelter and
a signal are each their own submission, and this plate gained a street's
worth (`LOT_FURNITURE_PLACED`: 7 sign posts where 3, 2 signals where 1,
17 lamps where 15, 4 litter bins where 1, 15 trees where 14) and nine
backdrop pieces and one Empty besides. The lane itself is a slab, two
clipped mouths and their stop signs.

**The lever, recorded and not taken:** Lot's street markings and kerb
furniture are per-piece draws, and the T's one cross street has always
been paid for without being priced; a merge per road per material, the
pattern Zoo 1.68.0's cover merge priced (roadmap 180), would buy back
most of the +107 on every level, not only on a block. Priced the way the
merge was: draws and frame time at fixed stations, before and after.

## What this run does not prove

The look from a player's eye on the lane in daylight (this level is an
evening one); the lane with rear doors to serve (two of three shells have
none); a lane on a plate that keeps its parking field; the gate with a
state, the rear passage and the shared court the guide also names; and
whether the Laser Tag numbers hold over many seeds.

## Instruments

- `lane_frames.sh`: `tools/lane_stations.py` on the themed spec, two
  stations along the lane, shot in the package; the sheet `lane.png`.
- The price: `docs/findings/horizon_glow/price_glow.py` with 9232's
  package as the control and 9233's as the subject (the same lot, the
  street form the only difference), `price/`.
