# Street trees: where a Philadelphia street plants them (roadmap 241)

Filed 2026-10-14 for roadmap 241. The urban comps (`URBAN_MIDRISE_COMPS.md`) show "street trees in pits along
both sidewalks". Lot already planted a tree in a grate on both sidewalks, but halfway between lamps 25 m apart:
a Delco strip's spacing (`lot/site_furniture.py`, `TREE_OFFSET`). This note is the spacing read at source before
a number was written down, as the hydrant and drain figures were (`STREET_DRAINS.md`).

## The source

The Pennsylvania Horticultural Society's TreeVitalize program, "Property Owner Request to Plant a Street Tree in
Philadelphia", revised 2010-02-03, page 2, "When selecting a tree location, please follow these guidelines"
([the form as a community association distributed it][phs]). TreeVitalize was the state's (DCNR) partnership,
led by PHS in southeast Pennsylvania, and the Fairmount Park Commission's arborist approved each site. Its
rules, in this repo's words:

- **Tree to tree:** 15 to 30 ft (4.57 to 9.14 m), by the tree's mature size and form.
- **From a street corner, a stop sign or a traffic light:** 30 ft (9.14 m).
- **From a light pole, a utility pole or a fire hydrant:** 15 ft (4.57 m).
- **From a driveway, a manhole cover, a storm drain or a main utility line:** 5 ft (1.52 m).
- **Not** in front of steps, doorways or alleys, nor between handicapped parking signs.
- **The pit:** 3 by 3 ft at the least, larger where it can be. Its edge is 18 in from utility lines, and 3 ft
  from steps, stoops or walls, so that 3 ft of sidewalk stays unobstructed (the form cites the ADA).
- **What a street tree is:** one planted between the curb and the sidewalk.

The form also names a local contact for the program. That is not reproduced here.

## Used (Lot 0.123.0)

On a street whose site says it is urban (Level Factory 0.205.0 writes `streetscape: "urban"`):
- **A tree every 30 ft (9.144 m)** along each sidewalk. The five species Lot plants (red maple, pin oak, honey
  locust, London plane, callery pear) are shade trees, so the range's upper end.
- **Each block's row centred between its corners**, kept 30 ft (9.144 m) from a crossing road's dropped kerb.
- **Each tree is placed as a strip's is** (`site_furniture._nudged`): one whose station meets a piece already
  standing, a marker or a shop band steps 2 or 4 m along the band; one whose station falls within 0.8 m of a
  dropped kerb (`CUT_CLEARANCE`; a side street, a path or a driveway) is not planted. CORRECTED 2026-10-14:
  this said every tree "steps clear of every cut", as Lot 0.123.0's changelog and its `urban_tree_stations`
  docstring do. `_nudged` returns before stepping when the station itself meets a cut.

A Delco strip keeps the lamps' stations. A strip is not a city block, and its planting is the one the walker has
seen in every level so far.

## Not used yet

- **15 ft from poles is approximated, not enforced.** The pole line is planned after the trees and steps clear of
  each tree's crown (`site_poles._room`). With trees 9.144 m apart, a pole stands in the window between two
  crowns, nearer than 15 ft to one of them.
- **Hydrants at door paths may give way.** A path cut's hydrant (`plan_furniture`, a hydrant past every cut
  but a driveway) is planned after the trees. On a dense row it can find a crown where it would stand.
- **Curb or building side.** The form plants between the curb and the sidewalk. Lot plants on the band's outer
  half, away from the road, so a body stepping off at a cut meets a clear kerb edge; that is unchanged.

[phs]: https://lomophilly.org/wp-content/uploads/2008/10/fall2010_tree_application1.pdf
