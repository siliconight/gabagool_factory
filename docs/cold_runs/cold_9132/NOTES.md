# Cold run 9132 -- the first video store

A NEW brief, `video_block_001` (archetype `video_store`), on Deli Counter
0.171.0, Zoo 1.43.0 and Level Factory 0.126.0. Night, clear, three buildings.
Zero interventions, no observations.

VACUITY: all three candidate lots drew `video_store_a01` (the brief's
archetype anchors it). The selected candidate, seed 9181, is the video store
with `arena_a03` and `mansion_a02`. It was selected by habit -- it is the
seed the club_block runs use -- and not on its merits; see below.

The art leg before export: 0 blockers, 55 findings. There is no earlier run
of this mission to compare them with.

## The store (`street.png`, `sales_floor.png`, `aisle.png`, `back_room.png`)

* From the street: MACDADE MOVIES lit over the door, the racks visible
  through the glass, the checkout inside the door on the left.
* The sales floor from inside the door: four rows of low islands, the back
  wall's racks under their genre boards, the east wall's beyond.
* The back room: ADULTS ONLY 18+ boards, the plain boxes, the two walls
  meeting at the corner.

Seen and not fixed:

* the store's wall posters are the CONVENIENCE store's -- SCRATCH & WIN,
  HOT DOGS 2/$1. `poster_wall_store` has one copy table and a video store
  draws from it;
* a bracket of the lit sign box crosses the name (it reads MACDAD6 at a
  glance);
* the sales floor is dim between its three fluorescents: the islands' near
  faces are lit and their far faces are not;
* no TV, no curtain (the back room's doorway is a door), no drop box --
  Deli Counter 0.171.0's NOT DONE list.

## What the run says about the LEVEL, as distinct from the store

* `walktest_navqa`, the gate: ok on all three candidates -- 0 proof failures,
  0 stranded anchors.
* Laser Tag, on the SELECTED candidate (9181): `LT_ROUTE_NEVER_COMPLETED` --
  the route was not completed in any of 25 runs, 19 of them with the crew
  alive at the clock; the bot walked 61% of the route on average. Candidate
  9282 finished 84% of its runs. One of this mission's three destinations
  sits 6.0 m up (`LT_STOREY_UNSEEN`), which is not in the video store: it is
  one storey. No cause is claimed; the two instruments disagree about this
  candidate and which is right has not been established. Selecting 9282
  would have been the better pick and the driver should choose on the
  walktest and the finish rate, not on a remembered seed.
* `ZOO_PARTIAL_BUILD`: one module failed, `prop_flat_top_grill_..._w160_d90
  _h105_mmetal` -- a kitchen grill in the arena or the mansion, neither of
  which a cold run had drawn before. Not the video store's.
* `PRESENTATION_ZFIGHT`: 130 coplanar pairs, the worst three the arena's
  stair against its event floor.

## Priced (`perf_9132.json`)

53 headings, 53,865 draws, worst heading 2,471 (attacker_spawn_17, yaw
270), median 1,004. 92 lights, 3,917 meshes, 19 over the 8-light cap (worst
30, a ceiling). A different lot from club_block_014's, so there is nothing
to subtract it from; the video store's own cost was not isolated.
