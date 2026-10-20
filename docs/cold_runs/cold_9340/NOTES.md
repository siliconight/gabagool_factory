# Cold run 9340 -- restaurant_row_001 on Deli Counter 0.236.0 and Zoo 1.114.0 (2026-10-20): every hole in a floor has a cause, first run

Staged from 9339. The tool changes since 9339 are Zoo 1.114.0 (5cedc35, `patches/patch_zoo_hole_causes.py`) and Deli
Counter 0.236.0 (9e720516, `patches/patch_dc_hole_causes.py`), the factory's roadmap 265: a drop's cause, and what
stands round it. This lot's deli, deli_a03 (`b0`), carries a `cut` hole -- its hideout over its kitchen, `cut_slab` --
so the package should hold a `hole_edge` round the cut, a `hole_spoil` on the kitchen floor and the crew's `hole_kit`
beside the hole; its stairwell drop is cut inside `deli_stair_up`'s own well and is the stair's, with nothing round it.
The seed is named, 9003, as 9339's pick, so the two packages compare piece for piece.

**Run:** 0 interventions (journal 0, unattributed files 0), DONE, drive 8.3 min.

**Findings 110 -> 118, every one of the 8 WALKTEST_WALKER_STUCK** (`findings_diff.py` here, against
`workspaces/cold-9339-ws`). All four walkers on both of deli_a03's candidates (seeds 9003 and 9205) reached 3 of 12
targets and stuck at the third, inside the drop's footprint on the first floor -- seed 9003's at (-43.3, 3.5, 0.7),
the hole's north-west corner, off the floor and pressing on `slab_col_1`'s west and north cut faces 0.3 m below the
floor line, its next waypoint 0.5 m outside the corner. Attributed, one cause: Deli Counter 0.236.0 drew the greybox of
a `hole_edge` as one box over the hole, its top 12 mm above the floor, and Lot bakes the walk test's navmesh from the
candidate's greybox lot with visual meshes in it (`geometry_parsed_geometry_type = 2`, `lot.py`), so the bake took the
box for floor and laid a path and a target across a hole no collider holds up. A floor hatch's greybox did the same,
on every hatch level; this lot has none. Measured over the library (`docs/findings/hole_causes_265/greybox_over_holes.py`):
16 dressed holes covered, 56.76 m2, on 0.236.0. **Fixed as Deli Counter 0.236.1** (`patches/patch_dc_hole_ring.py`):
the edge's and the hatch's greybox are a ring of four boxes outside the hole, their union still the slot's footprint;
none covered now. The prediction for the next run of this mission: WALKTEST_WALKER_STUCK 8 -> 0.

**What else moved against 9339**, read off the two packages (`LF_restaurant_row_001.portable-godot`):

- The modules: 506 GLBs against 503 -- the edge, the spoil and the kit; material entries 1,134 against 1,125, nine
  more, the three modules' three each (`PRESENTATION_TINT_MATERIALS` 73 -> 75 colour-only variants, the same finding
  re-measured); lightmap users 3,523 against 3,514, the nine meshes baked.
- The drop-edge gate: 0 undeclared, as on 9339; declared drop edges 20 -> 18 and standable cells 63,919 -> 63,916.
  The kit stands 0.35 m off the hole's south rim (`hole_causes.KIT_GAP`), a strip no body fits, so two rim cells
  there stopped being standable; the drop is still a route from its other three sides. Whether the kit should stand
  a body's width off -- the rim kept, the kit less "right at the work" -- is a gameplay call, left for the walker.
- `interactives.json`: identical to 9339's, 33 (deli_a03's stairwell drop is the stair's, so no floor hatch).

**Frames:** `_scratch/review/shots_9340/` and `shots_9340i/` (the work light), from a walk copy of the package
(`_scratch/review/walk_9340`): 9339's four stations as given there -- the kitchen door from the market, the hole from
the kitchen, the hole from above, the slid gate -- and two more, given from the package's frame (x = building x - 51,
z = -(building y + 2.51) for b0): the crew's kit from the hideout's south end, and the spoil from inside the kitchen.

`holes_9339_vs_9340.jpg` (here) sets them side by side in the level's light. From above, 9339's hole is a sawn square;
9340's is the same cut behind a torn concrete collar with the bars' stubs in its face, the kitchen's light coming up
through it, and the crew's tarp, saw, bag, coiled cord and work light beside it -- the light aimed into the hole (from
the south only the back of its head shows). From the kitchen, 9339's is a clean rectangle in the tile grid; 9340's is
the ceiling broken back round a dark band of plenum, the slab's cut face and two tile shards hanging. Seen and not
decided: the spoil on the kitchen floor is sparse at this distance -- a scatter of small fragments and two slab
pieces -- and the kit station is dark, the sofa across the lower half of the frame; both are for the walker's eye.
