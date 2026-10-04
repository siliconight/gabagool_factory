## [0.135.0] - one building line a street

Step 3 of `docs/proposals/LAND_USE_DESIGN.md` (the land-pressure guide's
5.7: variation is correlated, a street keeps a building line and a building
leaves it for a reason). Every building on a row took its own across-the-road
draw (`site_variation._ACROSS`, -10..10 m) and stood its own depth from it, so
the line was a residue: 10-24 m of spread along the through road on the nine
candidates of 0.134.0.

`packages/pipeline/street_line.py`: a building's STREET EDGE is the furthest
its collider hulls reach toward the street once turned (`south_reach`), read
per side from the same hulls `shell_footprint` measures as twice the
furthest face. Per side is the point. `gas_station_a02`'s canopy and
forecourt reach 32 m in front of its origin against 14 m behind it, and
Deli Counter's footprint -- the store -- ends 11 m in front: a line on the
stores would put every canopy on the sidewalk, and a line on the symmetric
extent would set every off-centre building back by its back yard. On a
`row`, `site_placements(..., extents=)` stands every street edge on one line
(`line_ys`) in place of the across draw, which is still made so no other
number a seed gives moves; a station's store then stands back behind its
forecourt, the design's explained exception, by construction. A shape that
turns keeps its stagger: its arms front different streets. Both placement
paths in the spec writer pass the extents and carry each building's
`street_reach` onto the spec; `road_grammar._south_face` hangs the road off
it; `ground_size(..., ys=)` sizes the plate from the row as placed.

MEASURED (`patches/lf_street_line/before_after.sh`, `docs/findings/
landuse_line_before_after.txt`): the three briefs, three candidates each,
built by 0.134.0 (a git worktree) and by this, every other tool the same:

    through-road building line spread   10-24 m  ->  0.0 m on 7 of 9
    the other 2 (gas_block_001 9181, 9282): 20.9 m, all of it
      gas_station_a02's store standing 23.0 m back behind its forecourt;
      every other building 2.15-2.16 m off the walk
    remainder                           down on 8 of 9 (club_block_014
                                        9282: 58.3 % -> 46.2 %); up 0.5 pt
                                        on gas_block_001 9282
    door to road                        unchanged, candidate for candidate

Laser Tag reshuffled, as it does when every building moves (findings
45 / 42 / 42 -> 40 / 42 / 45). By code across the nine: open sightlines
3 -> 0 (one new LOT_SIGHTLINE_UNBREAKABLE), overexposed zones -3, trivial
encounters +3, instant contact +1, blind map +2, enemy stuck +1. The flush
row's long frontage lane, the reason `_ACROSS` was a stagger, did not show
as open sightlines. On gas_block_001 seed 9080 -- the candidate the cold
runs ship -- the crew no longer dies (0 deaths, survival 13.7 -> 16.8 s,
TRIVIAL_ENCOUNTER), and all 25 enemy-stuck events are at one point, the
gas station store's north-east corner, plan (-48, -1): the objective is in
that store and the enemies are placed round it (Enemy_1 1.2 m off its east
wall). Located with Laser Tag 0.23.2's positions; why the enemy cannot round
the corner is not yet asked, and NOT attributed here beyond "the store
moved".

`tests/unit/test_street_line.py`: the reach follows the turn (literals for
`gas_station_a02` at 0/90/180/270); every street edge lands on one line,
origins straddling 0; a row's street edges stand on one line and x, yaw and
roles are unchanged, the station's store 21 m behind the line; an L keeps
its stagger exactly; the road lies the frontage, a sidewalk and half a
carriageway in front of the line; the plate holds the aligned row.
