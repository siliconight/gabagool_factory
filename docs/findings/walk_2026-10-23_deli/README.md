# The walker's walk of cold run 9383, 2026-10-23: four findings in deli_a03

The walker played `_runs/walk_9383_restaurant_row_001` (Level Factory 0.236.1, Deli Counter 0.260.0; restaurant_row_001
at seed 9003; deli_a03 standing as `b0` at world (-51, 0, -2.51), identity rotation -- spec metres (x east, y north,
z up) are local Godot (x, z, -y)). Their words and the overlay's figures, as they reported them; each is investigated
in its own section below as it is measured. Screenshots are the walker's, not kept here.

| # | the walker | where (overlay) | spec | state |
|---|---|---|---|---|
| 1 | "this shouldn't look pitch black" -- a wood-guarded opening in a tiled floor, nothing visible below | not given; tiled floor, plaster walls, a stair rising beside it | a stair opening (storey 0 or 1) | cause found: basement MOODY, light check ungated |
| 2 | "im stuck trying to get up the ladder to the roof" | pos -43.0, 5.5, 9.1; look ladder0_plane 0.84 m; sky through an opening above | ladder night_deli_ladder_0, x 8.0 y -12.0, storey 0 -> 2 (the roof) | investigating |
| 3 | "layout of these tables doesn't seem to have a rhyme or reason" | pos -60.9, 4.9, -5.1; storey 1 | x -9.9, y 2.6: upper_hall / manager_office | investigating |
| 4 | "this stair has unexpected space below it" | pos -59.7, 1.6, -11.9; look int_col_0_1_seg2 5.11 m | x -8.7, y 9.4: the stairwell, storey 0 | investigating |

## 1. The pitch-black opening

`hole_probe.gd` (beside this) photographs a hole from above, below and straight down in the walk copy, after the
level's warm-up. Its first target was the apartment's broken-floor hole (storey 1, x 7.4..9.6, y -5.1..-2.9): NOT
the walker's -- carpeted, no wood guard -- and NOT black straight down (`hole_down.png`: the kitchen floor lit, its
debris); kept as the control that the instrument can show a lit floor through a hole. Its second target, the ground
floor's stair opening to the basement: the camera from the basement (`hole_sw_basement.png`) reads the basement near
black -- one dim red-lit brick wall -- which is what an opening onto it would show from above. The above-camera
(`hole_sw_above.png`) landed inside a wall and shows nothing of the opening: its position is wrong, not the scene.

**The light under it** (`light_census.gd`, headless, every Light3D inside deli_a03's footprint by storey,
`light_census.out.txt`): the basement is lit, and lit weakly -- 19 pendants at energy 1.25-1.30, range 3.5 m, hung
2.3 m over its floor in two rows (two of them by the stairs' foot), against the ground floor's 57 fluorescents at
3.7, 2.7 m up. That is by rule, not by accident: a room below grade is MOODY, bare bulbs (Deli Counter's `lights.py`),
and `tools/light_check.py` holds a MOODY room to luma p50 >= 5, half an ordinary room's 10, a target it marks
PROVISIONAL for the walker's eye. "This shouldn't look pitch black" is that eye. Measured against it: see below.

**Measured** (`tools/light_check.py _runs/walk_9383_restaurant_row_001 --slots own`, `light_check_9383.out.txt`;
luma 0-255 after the grade, p50 of the room's station): the stairs land in cold_storage, p50 10 -- a PASS of the
MOODY floor of 5 that the walker, looking down into it from a stairwell at p50 74, read as pitch black; the basement
vault p50 3, a FAIL. And the check fails three rooms in this level -- the basement vault (3 under 5), the office
lobby (8 under 10), the pharmacy's retail floor (2 under 10) -- in a level that shipped with 0 interventions:
nothing in a cold run runs it (the narrowed audit's item 26: "Nothing runs it or gates on it"). Two fixes, then:
the MOODY floor raised to what the walker will read as lit -- their call, with these numbers -- and the check run by
every cold run, so a dark room is found by the factory and not by the walker.

**REFUTED, kept: "the basement is dim, so the opening reads black".** The basement IS dim by rule, and both fixes
above shipped (Deli Counter 0.261.0 lights every opening's landing; the cold drive runs the light check) -- and
neither could have made the opening the walker saw read. Cold run 9384 carried the landing lamps
(`cold_storage_landing` and `basement_corridor_landing` in `lot/deli_a03/art/fixtures/deli_a03_fixtures.glb`; a first
search that read only `.tscn` and `.json` said they were missing, and was wrong), and measured through the opening's
own rim -- the pixels a player looks through, the rim projected into the frame (`through_proto.py`, checked against
Godot: its whole-frame p50 is the engine's on all six frames) -- the ground floor's ladder hole into the basement
corridor read luma p50 0, p95 9 on 9383 and p50 0, p95 12 on 9384, a lamp lit 0.6 m beside it below. The whole-frame
p50 the light check judged it by was 41 and 42 and PASSED it: the lit floor round the hole outvoted the black inside
it. The light check's opening stations ask the wrong statistic (below).

**THE CAUSE: Level Factory's backdrop ground.** Photographed in the inspection light, which lights the scene from the
camera, the hole stayed black inside its rim with the ladder's two rail tops in it (`ladder4_inspect_down.png`);
from the basement looking up, the hole and the room above are there (`ladder4_inspect_up.png`). Every visible
instance crossing the hole's column (`hole_column.gd`, `hole_column.out.txt`) named it:
`site_backdrop/BackdropGround`, a 432 x 332 m plane at y -0.10, unshaded, albedo 0.045, facing up -- laid by Level
Factory 0.211.0 "a tenth of a metre under the plate, so the plate covers it wherever both stand". A ground slab is
-0.30..0.00: the plane runs inside every one, hidden by it everywhere but where the slab has a hole down into a
basement, and there it is a black lid at floor level, from above only. Hidden alone in a copy of 9384's walk copy,
the hole shows the ladder and the lit basement floor (`ladder4_backdrop_hidden.png`). Every level since 0.211.0 with
a basement under an opening has had it. Level Factory 0.237.0 lays the ground as a frame round the plate and every
building, never under one (the factory's `patches/lf_backdrop_frame/`).

**The instrument, then.** The light check's opening stations are held to the frame's p50, and a frame looking down an
opening is mostly the floor round it: it PASSED the black ladder hole at 42 and FAILED the broken-floor hole (p50 9,
through its rim 87) and the roof hatch (p50 0, the lit landing at the shaft's foot through-p95 129) where what each
leads to reads. An opening is judged by what is seen through its rim.

## 2. Stuck on the ladder to the roof

An investigator's headless probe on a scratch copy of the walk copy (`ladder_probe.gd`, `out_as_shipped.txt`,
`out_dc_area_in_group.txt`, `count_ladders.py`, `count_ladders.out.txt` beside this). **The walk copy's climb volume
for the roof ladder is 4.0 m tall; the climb is 6.6 m.** Past 4.0 m the body leaves it, falls, catches it again, and
bobs with the camera at 5.5-6.0 m -- the walker's 5.5 (the overlay's `pos` is the camera, 1.6 m over the body). The
volume is `WalkLadders/LADDER_0_climb`, 1.3 x 4.0 x 1.3; the package's own, `b0/Ladders/Ladder_ladder_0`, is 1.3 x
7.6 x 0.8 with `climb_height = 6.6` -- right, and unused. The roof opening is not the blocker: 1.3 x 1.3 where
`ladder_geom.through_hole` says, and a capsule cast with its feet at 6.563 m or over hits nothing. As shipped, a
simulated climb peaked at feet 4.463; with the package's volume in the `ladder` group, it cleared the opening in about
1.4 s (the step-off onto the roof not verified: the test held W and walked off the far side).

**Whose:** the factory root's `tools/walk_ladders.gd`, copied byte for byte into every walk copy
(`tools/walk_export.py:430`). `_climb_height` (:60-71) sizes a volume from a `hatch` marker within 1.0 m above the
ladder, else `DEFAULT_CLIMB = 3.0` (:22); its header (:15-17) says Deli Counter emits a hatch marker atop every roof
and slab ladder, and Deli Counter does not -- `HATCH_*` only for `vertical_links` of kind hatch
(`deli_counter.py:2991-2994`). It also ignores the package's correct Area3D, which Level Factory groups
`ladder_area3d`/`dc_ladder` (`portable_building.py:107`) while the walk player climbs group `ladder`
(`_walk_player.gd:215`). Walk copies only: a game reads the package's volume.

**How general:** 130 ladders in the library, 72 to a roof. 46 roof ladders have a hatch over them; 26 fall back to
3.0 m, 17 of them climbing 6.0-8.0 m and certainly unclimbable in a walk copy (15 at 6.6 m: night_deli,
deli_a01/02/03, cr_deli, the restaurant and urban row candidates), 9 climbing 3.2-3.6 m (0.4-0.8 m of lip, not
measured); of 58 storey ladders, 52 fall back, one at 6.8 m broken, 12 at exactly 4.0 m borderline.

## 3. Tables with no rhyme or reason

Read off `specs/deli_a03.json` and Deli Counter's `level_design.py` (an investigator's report, its instruments
`replay.py` and `census.py` beside this, `census.out.txt`). **No pass that places these pieces has a notion of
arrangement**:
- **The wrong kind of room.** `upper_hall` is the stair landing (role `connector`), but its id carries "hall", so it
  takes the "hall" kind (`level_design.py:2126`) meant for galleries, chapels and courtrooms: a service counter,
  waiting benches, vending, cigarettes, a dining table (:2430). The role is never consulted.
- **seed_cover's bare-room pass ran first**, matched "hall" in its lobby row (:372, :325) and laid lobby counters and
  planters on a jittered, shuffled grid, first fit wins (:1052), kinds alternated (:1142), facing by coin flip
  (:1144) -- the box standing alone mid-floor is most likely its planter_box_1 at (-9.01, 4.83).
- **Wall pieces**: four random positions a wall (:3290, :3310), shuffled (:3326), the walls shuffled (:4362) -- the
  uneven spacing on the back wall.
- **Floor hosts** (the manager office's three extra desks, the dining table): the first fit on a shuffled jittered
  grid (:5840, :6167), facing away from the room's middle (:6173), blind to the authored desk.

How general (the investigator's definition: a floor piece >= 0.6 m tall, > 0.6 m from its room's every edge, no
floor piece within 1.0 m; room bounds standing in for walls; gondola rows false positives), over 427 specs: seed_cover's
archetype pieces 2,047 of 3,461 isolated (59 %), its shelter pieces 781 of 813 (96 %), furnish's clusters 766 of 2,700
(28 %), floor hosts 318 of 1,763 (18 %), wall pieces 79 of 6,677 (1 %). Not verified: which box in the walker's frame
is which (inferred); and today's code replayed does NOT reproduce the shipped spec -- the library's specs are stored
artefacts furnished by older versions, so a furnishing fix reaches a level only through a refurnish.

## 4. The open space under the stair

deli_a03 stands two switchback stairs in its stairwell: `deli_stair_down` (basement to ground) and `deli_stair_up`
(ground to storey 1). Across the library's 526 stairs exactly one is open underneath -- `deli_stair_up` -- and by its
spec's own hand (`specs/deli_a03.json:409`, `open_under: true`), put there by Deli Counter 0.124.1 (cd587b9f,
2026-09-13), whose `open_under_why` reads: "Nav gate 2026-09-13: with the underside solid, objective_A upstairs is
unreachable; the only route to this flight's foot passes under its high end, because deli_stair_down's slab hole
leaves 0.4 m beside it. Reachable with the underside open." So the space the walker found is a walkway the level
needed because the stairwell was laid out so that the up-flight's foot can be reached only from under its own high
end: a hand patch in a library spec where a layout rule belongs. The rule it wants: a flight's foot reachable from
the storey's open floor without passing beneath the flight -- then every stair stands solid, as the other 525 do,
and the spec's patch goes.

**Built solid** (a scratch clone of Deli Counter 0.261.0, `open_under` removed): the nav gate traverses both stairs
and reaches objective_A upstairs and the patrol point at 8 of 8 voxel-grid origins. The patch outlived its reason:
Deli Counter 0.189.0 widened `office_stair_door` to 2.4 m, and the door has opened onto the strip beside the up-flight
since (the spec's own `door_why`). Deli Counter 0.262.0 builds it solid and holds every library stair solid unless a
named list says why (`test_library_undersides.py`), so the next hand-opened underside is a failure, not a habit. The
layout rule above is what the nav gate already proves once the underside is solid: a flight whose foot cannot be
reached from the open floor fails its traversal.
