# Urban mid-rise comps: the city's scale -- lot layout and building height

The walker, 2026-10-11, with three screenshots of another studio's game (a
watermark is visible on one): "more around potential lot layout city building
height". Shown in chat and not stored. Read for layout and scale only -- how
tall the buildings are, where they stand, what the street section is -- never
for that game's look, models or trade dress. Companion to
`PHILLY_STREET_COMPS.md` (the street's parts); this is the street's size.

## What the three frames show

**1. A corner at dusk, third person.** Mid-rise brick apartment blocks on
every side: one about eight storeys, one taller behind it, a long six-storey
block across the street standing behind a chain-link fence and a lawn. A tall
streetlight, traffic signals on a pole at the corner, a blue mailbox, a kerb
with a grass strip. Haze softens the far blocks; a red-violet dusk sky.

**2. The same city, first person at a crosswalk.** A five-storey corner
building: brick with bay windows and small balconies above, a lit restaurant
at street level under an awning -- the warm light the eye goes to first.
Across the intersection, eight- to ten-storey brick blocks; white high-rises
further off; street trees; a signal box on a pole in the foreground; crosswalk
stripes; puddles; haze.

**3. Down a street from above.** A four-lane street with a double yellow line,
lined on BOTH sides by mid-rise blocks of five to ten storeys standing right
at the sidewalk, one against the next. Street trees in pits along both
sidewalks; streetlights; a box truck and cars; taller buildings (twelve to
fifteen storeys) at the far end, so the skyline steps up with distance.

## What it says about lot layout and height

- **Height.** The street is defined by buildings of five to twelve storeys,
  not two or three; the tallest stand furthest away. The factory's library
  stands 3.2 to 13 m at the roof (two of 133 shells reach 12 m), and every
  level so far is one to three storeys.
- **The street wall.** Buildings stand at the sidewalk line and touch, block
  after block; a gap is an event (a fenced lawn, a lot), not the default. The
  factory's lots set buildings back behind pads and parking with plate
  between them -- the right answer for a Delco strip, the wrong one here.
- **Corners carry the life.** The corner building has the shop at grade (lit,
  awning), homes above. The middle of the block is residential.
- **The street section.** Two to four lanes, sidewalks wide enough for tree
  pits, signals at every corner.
- **Atmosphere.** Dusk haze is the depth cue that makes the far blocks read
  as far; lit ground floors carry the eye.

## Which tool would own each

| element | today | owner |
|---|---|---|
| mid-rise blocks (5-12 storeys), non-enterable | the Empties are three-storey rowhomes; the backdrop recipes carry rowhomes, a water tower, warehouses, trees | Deli Counter (a mid-rise Empty family: brick block, regular windows, parapet and penthouse; a corner variant with a lit shop at grade; a bay-window variant), Lot's backdrop recipes (taller massing by level) |
| the street wall: at the sidewalk line, touching | lots set buildings back behind pads and parking | Lot (an urban layout: zero setback, continuous rows, the enterable buildings among them), Level Factory (a brief that asks for it, so the Delco strip stays) |
| corner shops lit at grade, homes above | shops and homes are separate buildings | Deli Counter (the corner variant), Lux (the shop's light) |
| street trees in pits, signals at every corner | trees are roadmap 216; signals per junction exist | Lot, Zoo |
| dusk haze | five times of day | Lux (depth fog, which GL Compatibility supports, priced) |

## Costs to price before any of it ships

A ten-storey facade is a large surface: merged per side per material its draw
count is an Empty's, but its lightmap area, its shadow casting and the texture
memory it holds (roadmap 238) grow with it. Empties are kept dark inside with
their lit windows as paint, which is what keeps a street of them cheap; a
mid-rise family inherits that. Price it the cover merge's way before a level
carries a street of them.
