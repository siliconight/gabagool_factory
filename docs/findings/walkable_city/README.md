# Lot's layout against the walkable-city brief (roadmap 199): the census

The walker filed `docs/reference/DYNAMIC_WALKABLE_CITY_LEVEL_DESIGN_BRIEF.md`
on 2026-10-07 to "inform future Lot layout". Nothing had been measured
against it. This counts what the generated levels are, in the brief's
terms, so the Lot work it asks for starts from a number.

## What was counted

`route_census.py --cold` reads every cold workspace's themed drawn spec
(`.level_factory/jobs/<mission>.themed_site_assemble/1/out/site.site.drawn.json`),
22 of them from cold runs 9180 to 9226 across four missions, and prints a
row a spec (`route_census_cold.txt`): the plate, the resolved site shape and
road grammar, the roads and their length, the junctions between them (a
road ending on another is a T, one crossing another an X), the road ends
that reach the plate's edge (the approaches a player, a responder or the
getaway can use), the cycles in the road graph (edges - nodes + components:
a loop a route can go round), the buildings, the objective and its distance
to the nearest junction, the paths, the fence and the backdrop.

## What it says

**Every level is one layout.** 22 of 22: site shape `row`, road grammar
`T`, two roads (161 to 242 m of street), one T junction, **two approaches**
at the plate's edge (the main road's two ends; the T's stem ends inside the
plate, 18 m short of the north edge on restaurant_row_001), **zero
cycles**, two or three buildings on the row, the objective 30 to 106 m from
the junction. The four missions differ in plate size, building count and
`route_shape` (`push_then_backtrack`, `linear_push`, `loop`), not in street
form. The `paths` are door-to-street walks (Lot 0.91.0's landings), not
routes between buildings; the one `drawn` path a level is the walk between
two buildings.

This is not news to the code. `level_factory/packages/pipeline/road_grammar.py`'s
docstring: `_street_for` "emitted exactly two roads on every site ever
generated -- one along the plate's south edge and one cross street running
north from it, a T -- and it derived them FROM the buildings, after they
were placed"; the module gave the T a name so another grammar could be
asked for, and states the next step, "a road graph first, with buildings
hung off it -- need `site_variation` and this module to swap places". The
brief's `""` resolves to `T`, and no brief has asked for anything else.

## The brief's gates, applied

| the brief asks | the levels have | reads as |
|---|---|---|
| a hub central in movement, with a reason for its location and stated approach sides | the objective is one building on the row, 30 to 106 m from the one junction; its reason is the mission's, its sides are the row's (front to the street, back to the plate's edge) | hard failure 1 is not hit (it has an approach); the "reason for location" and "visibility revealed in stages" are unstated |
| at least three distinct approach routes | two: the main road's west and east ends, the same profile mirrored | design warning: "every route has the same tactical profile" |
| a short loop near the hub, a long bypass of the exposed ground, a shortcut with a cost, recovery from a blocked edge | zero cycles in the road graph; the only alternative to the street is the plate's open ground behind the row | design warning: "all routes converge into one chokepoint" (the street) |
| dead ends only with a purpose | the T's stem, which serves the cross street's frontage and ends in the plate | unlabelled; a purpose (a yard, a lot) would make it the brief's cul-de-sac |
| edges explained | the fence and the backdrop since roadmap 228 (9224 to 9226) | met at the edge; the street "continues visually" only where the backdrop stands a road's continuation (none do yet) |
| verticality joining route nodes | Deli Counter's stairs and roof access (61 `roof_access` rooms in the specs), fire escapes placed twice ever (roadmap 171) | inside buildings yes; at site scale no raised route exists |
| traversal review per entry point | Laser Tag's route findings and route completion; Lot's `S_ONE_APPROACH` (one route across the site graph of buildings) and `S_STREET_CROSS` (a leg crossing a road) | partial: routes are judged on the building graph, not the street graph, and nothing reports approaches or loops |

## What 199 should build, in order

1. **The inversion** `road_grammar.py` names: a road graph first, buildings
   hung off it, with `T` reproducing today's output exactly (the module's
   equivalence test is the proof).
2. **Grammars that give the brief its counts,** each a few lines of the
   same vocabulary: `X` (a crossroads: 4 approaches, 0 loops), `block` (a
   main street, a back street and two cross streets: 4 approaches, 1 loop
   round the row), `spine` (a main street, a parallel alley and two links:
   2 to 4 approaches, 1 to 2 loops, the alley the brief's concealed service
   route). The brief's example seed is `block` with an alley: five
   approaches, two loops.
3. **The audit grows the brief's numbers** as INFO findings beside
   `S_ONE_APPROACH`: approaches at the edge, cycles, the hub's distance to
   the nearest junction, and a dead end with no frontage, so the next
   level's job.log says what its street form is.
4. **The traversal review** is Laser Tag's: fastest and safest already
   exist as route findings; "one blocked edge" is a run with a road end
   closed, which the fence can stand.

## Not measured

Exposure, sightlines and cover along each approach (Lot's tactical audit
reads legs, not approaches); the look of a street from a player's eye; and
whether a T is WRONG for a small plate: the brief says "when the level's
footprint allows it", and a 105 m yard may be a T with reason. The census
counts form; the brief's judgement is a person's.

## Instruments

- `route_census.py`: the census; `--cold` for every cold workspace.
- `route_census_cold.txt`: the run of 2026-10-10, 22 specs.
