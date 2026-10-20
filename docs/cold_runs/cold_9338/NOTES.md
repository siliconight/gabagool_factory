# Cold run 9338 -- restaurant_row_001 on Deli Counter 0.234.0 (2026-10-19): the open-floor table, proven

Staged from 9335, the mission's last run. The tool change since 9335 is Deli Counter 0.233.0 (proven by 9336 and
9337) and 0.234.0 (a6cbc045, `patches/patch_dc_open_floor_table.py`, the factory's roadmap 260): the walker's table by
room pair, each pair of rooms that met with no wall between them named one floor or walled. This lot's deli, deli_a03
(`b0`), is one of the 23 specs it moved: its kitchen walled from the market aisles along spec x 7 (y -14..6) with a
door at y -4, and its stockroom gate slid 0.5 m west to clear the new wall's end.

**Run:** 0 interventions (journal 0, unattributed files 0), DONE, drive 8.5 min. The pick is seed 9003 again, PASS 90
with nothing stuck, as every candidate graded on 9335. Findings 81 / 110, as on 9335.

**What moved against 9335**, each read off the two packages (9335's from its walk copy, `_scratch/review/walk_9335`):

- `interactives.json`: 33 interactives, 23 of them doors, against 32 and 22. The new one is `b0 int_0_6_open0`, the
  kitchen door, at plan (-44.0, -1.49): spec (7, -4) with deli_a03 placed at (-51, +2.51). `b0 int_0_1_open1`, the
  stockroom gate, moved from x -45.5 to -46.0, the 0.5 m slide. Nothing else moved.
- Lightmap users: 3,514, against 3,503. Eleven more, the new wall's pieces -- inferred, not attributed user by user.
- The drop-edge gate passed with 0 undeclared. It reached 55,454 of 63,919 standable cells, 38 fewer of each: the new
  wall's footprint, 20 m by 0.35 m on a 0.5 m lattice. It counted 45 unguarded edges against 52: 11 on flights' own
  sides, 13 at declared drops (20 before), 13 at ladders' shafts and 8 outdoors. The 7 rows gone are all on the first
  floor's slab (y 3.3) along x -44.0 to -44.25, z 0.25 to 2.75.

**Why those 7 went, and what it means.** deli_a03's first-floor hole -- the "vertical attack angle", 2.2 m square at
spec (8, -4) -- spans x 6.9 to 9.1, and the new kitchen wall at x 7, 0.35 m thick, stands under its west strip. So that
strip now looks down onto the wall's top, 0.3 m below, and the gate's column probe reads that as floor rather than a
drop. A wall top 0.35 m wide is narrower than a body (0.70 m), so it is not a floor anyone stands on. That is the
probe's model of a body, the gap the queued body-fit fix to the gate's probe is for (a body-fit test before a gap counts
as a fall). The drop itself still lands in the kitchen, east of the wall, where most of the hole is. ~~Recorded, not
patched: the alternative is no kitchen wall, which reverses the walker's call.~~

**Retracted, and patched after all (Deli Counter 0.235.0).** "No kitchen wall" was not the only alternative: the hole
can move. The frames below show the wall's top running into the hole and its new door under it, which reads as a wall
built through a floor opening, not as one designed beside it, and the same shape stands in all six delis. Deli
Counter 0.235.0 adds layout_lint L27 (a wall under a hole in its ceiling) and has the open-floor table slide a hole
off a wall it stands; the six delis' drops moved 0.5 m east to (8.5, -4), all in the kitchen. Measured and argued in
`docs/findings/open_floor_table_260/README.md` ("The first cold run: a wall under the drop"); the patch is
`patches/patch_dc_ceiling_holes.py`. The gate's 7 rows should come back as declared drop edges on the next run of this
mission, and that run is the proof.

**Frames:** `_scratch/review/shots_9338/` and `shots_9338i/` (the work light), four stations given by hand from the
package's own coordinates: the kitchen door from the aisles, the hole from the kitchen, the hole from above, and the
slid gate. The hole from the kitchen, in both lights, is the frame that showed the wall under the drop.
