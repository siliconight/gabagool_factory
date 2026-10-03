## [0.132.0] - a building faces the street with its front door

Step 2 of `docs/proposals/LAND_USE_DESIGN.md` (the walker's land-use
guide, its 5.3 "frontage has a function"), agreed 2026-10-03. Measured
before (`lot/site_landuse.py` over the 36 lots on disk): a ground door
faced the road on 67 of 126 fronting buildings, and 312 of 920 door walks
met a wall with no door. The cause was one line: `site_placements` drew
every building's yaw at random from 0/90/180/270.

`packages/pipeline/front_door.py` reads a building's front off its own
Deli Counter gameplay file: a door tagged as the front (main_entry,
front_door, front_customer_entry, ...), else the widest door that is not a
service door, with a tie going to the south wall -- Deli Counter's
convention, 88 of the 92 fronts the first two rules find. Surveyed over
the 134 built buildings, it finds a front on 132; the two with no ground
door keep the drawn yaw. `facing_yaw` turns that wall to plan -y, where
the road grammar always runs the through road.

`site_placements(..., fronts=)` takes the yaws; both call sites pass them
and record each building's front and why on its spec record (`front`).
The random draw is still made, so a seed's nudges and roles do not move;
only the yaws do, and with them every seed's layout.

MEASURED (`patches/lf_front_doors/before_after.sh`, `docs/findings/
landuse_fronts_before_after.txt`): three briefs (gas_block_001,
club_block_014, crossroads_9600), three candidates each, built in fresh
workspaces by 0.131.0 (a git worktree) and by this, every other tool the
same, and measured by Lot's land-use census:

                                          before      after
    fronting a road, a door facing it     25 / 44     33 / 45
      the through road                    15 / 27     27 / 27
      a corner building on the cross st.  10 / 17      6 / 18
    walks to a wall with no door              19          12

Every building's front now faces the through road. What remains is corner
buildings: a building has one front, and it faces the through road, so its
side faces the cross street -- before, some corners faced the cross street
by luck of the draw, which is why crossroads_9600's two candidates dipped.
The 12 walks left are the lateral spurs the road grammar still authors to
those sides, which Lot already does not draw. Not fixed here, and recorded:
the building line's spread grew on several candidates (gas_block_001 seed
9080: 13 to 24 m), because turning a building moves its street face by
half the difference of its two extents and the across-the-road nudge is
unchanged -- step 3 of the design, one building line a street.

`tests/unit/test_front_door.py`: a tagged front beats a wider service
door; no tag, the widest non-service door; a tie goes south; windows,
breaches, upper floors and partitions are not fronts; each yaw turns its
wall to plan south in Lot's rotation; placements take the fronts and keep
every other draw; and the built library has a front on 95 % or more.

