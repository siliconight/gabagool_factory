# Indoor fixture placement: the walker's references, digested

The walker, 2026-10-10: "making indoor light fixtures not always be in a
perfect line, so it looks a little less robotic in the line/lighting
placement", with nine references and a sheet of fixture types. Roadmap 229
tracks the work; `docs/findings/fixture_rows/` counts what the kit does now.
This file is what the references say, in this repo's words, with the numbers
kept exactly. It fills blanks; it does not override a look the walker has
seen and kept (`references-fill-blanks-not-override`).

## The sheet of fixture types

An infographic the walker attached: twenty named fixtures, each drawn in a
room corner, and a section through a room showing where each kind sits.
The vocabulary, grouped by where the fixture mounts, with the Zoo species
that builds it today (`zoo_keeper/core/fixtures.py:FIXTURES`) or the gap:

| on the sheet | mounts | kit today |
|---|---|---|
| open fluorescent luminaire, reflector, industrial; open fluorescent striplight | surface or chain-hung under the ceiling, in rows | `fluorescent_fixture` (a troffer, DC's `fluorescent` row) stands in for all of these |
| suspended linear fluorescent; suspended direct/indirect (mostly up) | hung on stems, rows | none |
| recessed round downlight; recessed round wall-washer; recessed fluorescent (the section) | in the ceiling | none; the club's `club_fixture` can is the nearest |
| open HID high-bay, metal reflector; open HID high-bay, glass or plastic reflector | hung high, a grid, for tall rooms | none |
| decorative pendant, downward; indirect pendant (the section) | hung over a table, a bar, a counter | `pendant_fixture` (a bare bulb on a cord; DC's `pendant` and `counter_accent`) |
| track lighting, metal halide; track lighting, incandescent | a rail under the ceiling, heads aimed | none |
| functional wall sconce; decorative wall sconce; wall-mounted uplighting | on the wall at head height or above | none indoors; `wall_pack` is the outdoor cousin |
| cove-mounted uplighting; recessed cove fixture (the section) | hidden in a ledge, washing the ceiling | none |
| task lighting, fixed and furniture-integrated; under-cabinet lighting (the section); compact fluorescent task light; portable task lighting; portable torchiere uplight | on or under the furniture, on the floor | none |
| LED exit sign | over every door on an exit route | none |

The section drawing puts them in one room: a recessed cove at the ceiling's
edge, an indirect pendant and a direct/indirect pendant down the middle, a
recessed fluorescent and a recessed can, a wall wash and a wall sconce on
the far wall, under-cabinet and task lights at the counter. One room, eight
kinds, and none of them in a row down the centre.

## The rules, by source

**lampsusa.com, "Light fixtures: the ultimate guide to room lighting"** (the
one the walker liked; 145 KB of page, read whole). No distances or heights;
its value is the taxonomy and the room-by-room list.
- **Three kinds of room, three layouts.** A formal room is balanced, evenly
  spaced, symmetrical. A relaxed room avoids symmetry and pattern, with
  placement that reads as somewhat random. A dynamic room is asymmetric,
  with some areas noticeably brighter than others, or clusters of smaller
  lights. This is the rule the walker's ask is asking for, and it says the
  grid is RIGHT in the formal room: an office, a bank, a ward, a terminal.
- **Layer: at least two kinds a room** (a ceiling fixture and wall lights; a
  pendant and lamps), light overlapping between fixtures so there are no
  hard shadows; up-lights and accents in the dark corners.
- **By room:** kitchen, a pendant or flush mount over the sink, pendants in
  a row or a cluster over the island, recessed cans spread evenly or near
  the edges, under-cabinet strips. Dining, a chandelier or one or two
  pendants over the table (nobody walks under a table). Bathroom, a strip
  above the mirror or a light either side of it, an enclosed ceiling
  fixture. Bedroom, lamps either side of the bed, one pendant. Hallway,
  flush mounts and wall lights close to the wall. Stairs, lit from above,
  the rails included. Foyer, a pendant or chandelier where the ceiling is
  high, one or two wall lights by the hooks. Basement and media room, no
  chandelier under a low ceiling; flush, recessed or spots, spread so no
  side is dark; a pendant over the seating. Office, a pendant where the
  ceiling is high, a lamp at the desk. Wall lights go on the less-lit side
  of a room; table lamps come in pairs.
- **A sizing rule of thumb** for incandescent wattage: length x width in
  feet x 1.5 (a 10 x 6 ft room, 90 W); older eyes, up to 50 % more.

**dsgmetro.com, "Lighting fixture positioning guide."** Qualitative, and
the first sentence is the whole brief: start with function, not symmetry.
- Light what needs light (people, surfaces, counters, walls, art), not the
  floor by default.
- Check the ceiling before fixing a location: its height and shape, the
  framing, and the conflicts with beams, ducts, sprinklers and speakers.
  That is the list of CAUSES a real row has for being where it is.
- Kitchen: task light over the counters, islands and sinks; never a
  downlight directly behind the person working, it shadows the counter.
- Living room: wall washing, lamps and accents, not downlights alone.
- Hallway: low-glare, consistent light; step or toe-kick lights where they
  suit.
- Keep general, task and accent lighting on separate control zones.

**woodmagazine.com, "Light fixture positioning made simple."** The one
source with a formula, for continuous rows of two-lamp fluorescent
fixtures over a workshop (the page refuses the fetch tool; read in the
browser pane).
- A: the height from the main work surface to the fixture (the ceiling,
  or the hung height, usually 8 to 10 ft above the floor).
- B, the distance between rows: at most 1.5 x A.
- C, the distance from the outer row to the wall: at most a third to a
  half of B.
- Worked: a 24 x 24 ft two-car garage shop, 9 ft ceiling, benches 36 in
  high; 16 ft rows (two 8 ft or four 4 ft fixtures end to end). A = 6 ft,
  B = 9 ft, C = 4.5 ft. Two rows 9 ft apart leave 7.5 ft to the walls and
  the sides too dark; one centre row and two more at 8 ft puts the outer
  rows 4 ft from the walls, which lights the shop.
- In this kit's units: a 3.2 m storey with its slab and the 0.1 m gap puts
  the lamp near 3.0 m; over a 0.9 to 1.05 m counter A is about 2.0 m, so
  rows at most 3.0 m apart and the outer row within 1.0 to 1.5 m of the
  wall. A sales floor 8 m wide is three rows; a 4 m stockroom is one; a
  corridor is one. The kit lays one row in every room (see the census).

**legacy.wbdg.org, "Daylighting."** The electric side of windows.
- Daylight reaches in about 2.5 x the window's height (head to sill), so
  the daylight window should start at least 7 ft 6 in above the floor;
  floor plates no deeper than 60 ft south to north.
- The first 10 to 15 ft from the perimeter has enough daylight to dim or
  switch the electric fixtures there: a store's window row is OFF by day
  while the back rows are on. A cause for an uneven ceiling by daylight,
  and a hook for the five-times-of-day work.
- Reflectances: ceilings above 80 %, walls above 50 %, floors about 20 %.
  Visible transmittance 50 to 75 % for daylight glass, under 40 % for view
  glass. Orientation within 15 degrees of south. GSA's reading of IES: 50
  footcandles at desk height, or 30 or less with indirect ambient plus task
  light. Occupancy sensors save 10 to 50 %.
- Light shelves redirect sun to the ceiling, work on a south face and
  rarely on east or west; clerestories and monitors reach deeper with less
  glare.

**lampsexpo.com, "Light fixture location ratings."** Dry, damp, wet.
- Dry: indoors with no moisture (a foyer chandelier, a living room).
- Damp: humid or steamy, and covered outdoor spaces (a bathroom vanity, a
  fan under a covered porch).
- Wet: direct water (an exposed deck, a sconce by a spa, an outdoor
  shower). No distances given. For the kit: a porch light and a canopy
  lens are damp fixtures, a wall pack on a bare wall is wet, and a
  bathroom's strip is enclosed.

**paclights.com, "Construction lighting standards."** Thin.
- General construction at least 50 lux; detailed work such as electrical,
  200 lux or more; precision work higher, unstated.
- A uniformity target "of at least 0.5", which the page then defines
  inconsistently (average at least twice the minimum); read it as min/avg
  0.5 and check the IES source before using it.
- Glare handled by position, fixture type, diffusers and indirect light;
  no spacing-to-height ratio, no high-bay threshold.

**inductionlightingfixtures.com, "Workplace lighting standards."** Thin.
- OSHA footcandle floors: 5 in tunnels and hallways; 30 in offices; a
  baseline the page states as one lumen per square foot. No values for
  aisles, docks, stairs or restrooms; no colour temperatures; "spaced out"
  is its only layout rule.
- Fixture covers mounted with no gap an adult can reach a finger into.

**ledlightingsupply.com, "Lighting codes and standards."** Controls, not
layout.
- Lighting power density is limited in watts a square foot (no figures).
- Partial-on: the first stage no more than 50 % of connected load.
- ASHRAE 90.1 daylight steps: full, two thirds, one third, off; exterior
  lighting with at least a 30 % reduction. 90.1-2019 and IECC 2021, revised
  about every three years.

**baylighting.net, "Keystone SmartLoop in commercial retrofits."**
Controls and wiring. Troffers in offices, high-bays in warehouses, aisles
that light as a worker enters them; nothing on spacing or grids. Lighting is
about 17 % of US commercial electricity; controls cut it 20 to 60 %.

## What this repo takes from it

- **The line is a symptom of one rule for every room.** The sources agree
  that where a fixture goes follows what it lights, and that the formal
  room's grid is a correct answer, not a defect. The fix is specificity by
  room use, not noise (`HUMAN_AUTHORSHIP_GUIDE.md`: uniform irregularity is
  its first anti-pattern).
- **Wide rooms take more rows, laid to the work**, by WOOD's formula; the
  kit's one-row-a-room is right only up to about 3 m of width.
- **A row's offsets come from the ceiling:** framing, ducts, beams, tiles,
  hatches, and the fixture added later. Each is a cause the seed can
  reproduce.
- **The species gap** is the sheet's middle: a strip light, a sconce, a
  high-bay, an exit sign; recessed cans and under-cabinet light as paint or
  emission on the pieces that carry them.
- **Daylight switches the window row.** By day the perimeter 3 to 4.5 m in
  is daylit and its fixtures are off; that belongs to the time-of-day
  work, and it is a second, honest cause for a ceiling that is not uniform.
