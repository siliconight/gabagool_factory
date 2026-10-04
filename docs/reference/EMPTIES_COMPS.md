# Empties: the walker's comps, and what each tool owes them

The walker, 2026-10-04. An EMPTY is a non-enterable building shell (roadmap
item 106); they stand around the walkable level and across its streets.
Shown the shells Deli Counter builds today, sealed greybox boxes placed side
by side, the walker said: "from the pictures that just looks like a
continuous concrete wall". Then the walker sent five photographs: one
rowhome street, then four industrial and loft buildings. The images were
shown in chat and are not stored here. What follows is what was read off
them -- format only; no real business, sign or mark is reproduced.

## Family 1: the rowhome terrace (Philadelphia / Delco)

One photograph: three attached brick rowhouses on a city street.

- **ATTACHED, AND DIFFERENT HOUSE TO HOUSE.** Party walls, no gaps; the row
  reads as separate houses because each differs. In the photo: two red
  brick, one painted white; three cornice colours (cream, black, black);
  door colours wood, navy and blue-grey.
- **Proportion.** Each house is two window bays wide, about 5.5-6.5 m, and
  three storeys of about 3.2 m.
- **Upper floors.** Two windows per storey, stacked on the same bays:
  - double-hung 6-over-6 sash;
  - dark shutters (black or deep green), hung open beside each window;
  - white stone sills and lintels.
- **Ground floor.**
  - The door at one side, with a rectangular transom or an arched fanlight
    and a stone surround.
  - Two to four marble steps up to it: a stoop.
  - Two windows beside it.
  - A marble base band about 0.6 m tall, with cast-iron basement vents.
  - Window boxes on some sills.
- **Cornice.** A heavy bracketed wooden cornice with dentils, about 0.5 m
  deep, at the roofline; each house's sits at its own height.
- **The occasional arched passage door** between two houses: the alley entry.
- On the sidewalk: street trees, a lamp, parked cars.

## Family 2: the industrial loft

Four photographs: a brick factory row seen down a street, a tan-brick civic
building, a red brick factory with a corner tower, and a painted-red corner
loft.

- **Scale.** Three to seven storeys, 20-60 m along the street.
- **A STRUCTURAL GRID.** Brick piers (pilasters) between regular bays, a
  stone or concrete base, band courses at the floor lines, and a parapet
  with stone coping. In two of the four, the grid is concrete with brick
  infill.
- **Windows.** One big steel window per bay per storey, multi-pane (small
  lights in a steel grid), some with an opening hopper. The civic one has
  tall arched windows on its upper floors, paired per bay.
- **Ground floor.** Varied: storefront bays in two, blank brick with a
  corner door in one; vents and a loading door.
- **Silhouette.**
  - A corner stair tower, or a roof bulkhead or water tank, a storey higher
    than the rest.
  - A date stone or name panel in the parapet.
  - One has a hipped roof with tile.
- **At ground: a chain-link fence along one of them**, which is the walker's
  boundary rule (`fence-marks-the-playable-edge`).

## What each tool already has, and what it owes

| Feature | Have | Owner |
|---|---|---|
| Openings on an Empty (windows, door, shopfront) | `ext_walls` openings, as every building uses; Empties author none | Deli Counter presets |
| A door that looks real and stays solid | doors CARVE collision (`_wall_collision`) | Deli Counter: an Empty's doors do not carve |
| No gameplay from an Empty's openings | `_record_openings` appends them | Deli Counter: skip on an Empty |
| Variety per house: width, storeys, wall material, cornice height | presets take params; two fixed shells built | Deli Counter: a family of variants |
| Piers, plinth, band, cap on a wall | Zoo `arch.relief_parts` (subtractive, collision-safe) | Zoo: exists; Empties' styles tune it |
| Brick, painted brick, stone, concrete skins | Pixelcoat theme packs | exists |
| Divided-light sash, steel factory sash, a dark room behind, blinds | the window pane is flat; an Empty's glazes opaque `glass_facade` | Pixelcoat: paint the pane -- bars, depth, the odd blind -- one material |
| Shutters, stone sills and lintels, stoop, cornice with brackets | none | Zoo: new trim species, placed from Deli Counter slots |
| Corner tower, bulkhead, water tank, date stone | parapets only | Deli Counter (massing) and Zoo (props) |
| Placement around the level, never on a route | Lot `blockers` instance a shell scene; nothing places them | Level Factory: brief field, planner, compose |
| Themed like the real buildings | the art pipeline runs per lot building | Level Factory: Empties join it as art-only archetypes |
| A fence where playable meets an Empty's back or a lot | Pixelcoat 0.56.0 `chain_link` | Zoo `chain_link_fence`, Lot placement |
| Few draws | 131-166 mesh nodes per built Empty today | merge per material per Empty (it is seen as one thing) |

## Order

1. Deli Counter: Empty presets with openings and per-house variety, doors
   solid, no gameplay; the rowhome family first, then the loft family.
2. Pixelcoat: painted Empty glazing (6-over-6 sash, steel factory sash,
   dark depth).
3. Level Factory: Empties placed across the through road as a terrace with
   breaks, themed through the art pipeline as Lot blockers.
4. Look in a cold run; the walker's eye.
5. Zoo trim: shutters, sills, lintels, stoops, cornices.
6. Runtime: merge each Empty per material; price on and off.
7. The fence at the playable edge; then the skybox backdrops.
