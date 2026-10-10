# The ground behind the row: where a rear service lane would run

Roadmap 230 step 3 (the adjacency guide's connectors) and roadmap 199 (the
walkable city's loop). Every drawn site is a T: a main road with two
approaches at the plate's edges, one side road, no cycle
(`docs/findings/walkable_city/`). The guide's answer is a connector with
an owner and users behind the row -- a `service_lane` (3.5 to 5 m, van
scale) or a `rear_passage` -- which is also the return loop the brief
prefers. Before any tool lays one, this measures what stands behind the
row today, from the themed drawn spec of every cold workspace on disk
(`rear_census.py --cold`, 27 sites, 2026-10-11).

## What is there

| site (brief) | plate | row | rear band behind the yards | side road reaching into it | in the band |
|---|---|---|---|---|---|
| restaurant_row_001 (9185 .. 9231, 9 runs) | 177 x 99 | 3 buildings, 152 m | 28.5 m | at x -26.5, 16.5 m past the rear line | 1 parking field, 10-12 cover |
| club_block_014 (9204 .. 9221, 11 runs) | 185 x 101 | 3, 167 m | 26.5 m | at x 42, 14.5 m | 1 field, 10-11 cover |
| bank_block_001 (9194, 9214, 9215) | 173 x 95 | 3, 147 m | 22.5 m | at x -28.5, 10.5 m | no field, 7 cover |
| card_block_001 (9216) | 151 x 94 | 3, 117 m | 23.5 m | at x -21.5, 11.5 m | 2 fields, 10 cover |
| gas_stop_001 (9228) | 240 x 120 | 3, 190 m | 25.4 m | at x 51.5, 13.9 m | 1 field, 13 cover |
| warehouse_yard_001 (9180, 9226) | 105-109 x 100 | 2, 68-74 m | 21.5-22.5 m | at x -5 / 2, 9.5-10.5 m | 1 field, 9-13 cover |
| county_hospital_001 (9227, 9230; a courtyard) | 87 x 71 | 1, 40 m | 14.5 m | none | no field, 3 cover |

Read off the rows (the full table is `rear_census.txt`):

- **Every row site turns its back on the same side.** Every building
  fronts the main road (`fronts SSS`), its rear wall faces north, and the
  yards with a dumpster (Lot 0.90.0, 0.93.0) stand on those rear walls, 6 m
  out. The rear line of the row plus its yards is 21 to 35 m from the main
  road's centreline, and the plate's north edge is 21.5 to 28.5 m beyond
  it on every strip site. That band runs the row's whole length, 117 to
  190 m, with nothing in it but one parking field (Lot 0.94.0's, beside
  the side road) and the cover props.
- **The Empties are never behind the row.** Every terrace (14 to 34
  instances) stands across the main road, the other frontage. So the band
  behind the row is the one piece of the plate with no building on it.
- **One side road already reaches into the band**, 9.5 to 16.5 m past the
  row's rear line on every strip site (restaurant_row's ends at y 31.5
  against a rear line of 15 and yards to 21). A lane laid 3 m past the
  yards would cross it: a junction for free.
- **The hospital's courtyard has 14.5 m behind and no side road**: a
  campus does not want a lane, it wants the guide's institutional service
  edge; this measurement does not cover it.

## What a lane needs, by the guide's numbers

- **Width 3.5 to 5 m** (7.4, "small service lane for van-scale work"),
  laid at the yards' outer edge plus a 3 m apron, which puts it 3 to 6 m
  inside the band's 21.5 m minimum; the rest of the band stays what it is
  (the field, the fence line, the backdrop beyond).
- **Owner and users** (section 7, connectors): the row's businesses;
  deliveries to the rear doors (Lot 0.91.0 gives side and rear doors their
  landings), refuse (the dumpsters stand on it), staff. A door onto the
  lane is what the guide's P14 and P17 "staff or driver access" rules ask
  for, and what `S_ADJACENCY` would then be able to see.
- **The loop closes with two connectors to the main road, not one.** The
  side road is one. The second is an end connector between the last
  building and the plate's edge: restaurant_row's station spans x 35 to
  75 on a plate to 88.5, a 13 m gap; club_block's and gas_stop's far ends
  have the same shape. With both, the road graph has a cycle (main road,
  side road, lane, end connector) and the walk back from the objective can
  be the other way round -- the `return_loop: preferred` target
  (`S_TARGETS` reads "0 loop(s)" on every site today). A lane that only
  runs off the plate's edges adds approaches, not a loop.
- **A gate with a state** (the guide's connector catalog) where the end
  connector meets the lane, so the lane can be the crew's way in, the
  responders' way round, or shut, by the mission's declared state.

## Where it would be built

- **The roads are Level Factory's.** The spec's `roads` come from
  `site_variation`'s road grammar (`road_grammar_resolved`), which roadmap
  199 already names for the road-first inversion; the lane is one more
  element of that grammar (`rear_lane`), placed from the row's rear line
  and yards, which the spec carries. Lot lays its surface, kerbs and
  junctions as it lays the side road's, and its audit counts the loop
  (`site_targets.road_graph` already does) and the lane's users.
- **The price before the look:** a lane is a road: one more slab, two
  more junction surfaces, its own lamps (Lux 0.71.0's poles), and the
  responder and getaway routes change, which roadmap 212/215's gates
  measure.

## What this does not measure

Whether a lane reads as a lane (a person's eye, roadmap 18); the hospital
campus; what the navmesh does with a second way round (the walktest, in
the cold run that first lays one); and whether 3 m behind the yards is
clear in the BUILT scene rather than the spec (the pad is the spec's; the
dumpster's and bags' colliders are Zoo's).

## Instruments

- `rear_census.py`: reads a themed drawn spec, finds each building's rear
  side as the side opposite the nearest road (no rotation sign to guess;
  Lot's `site_extent.rotated_footprint` for the rect), and prints the band
  behind the row with what stands in it. It prints what it counted and
  stops.
- `rear_census.txt`: the 27 cold workspaces, 2026-10-11.
