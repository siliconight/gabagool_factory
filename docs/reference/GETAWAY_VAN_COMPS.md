# The getaway van: the walker's comps, and what each tool owes them

The walker, 2026-10-07, answering where a heist's extraction goes:

> For the getaway car, I want a Box Truck. Like a Chevrolet P30. Matte
> Black....faded, with patina, like a worn in truck...that's been on many
> jobs.... Our very own "millenial falcon"

> location of the getaway vehicle should be the same as the missions spawn
> point. you spawn, do the job, then return to the car

Four photographs came with it. They were shown in chat and are not stored
here. What follows is what was read off them -- format only; no real
business, sign or mark is reproduced. Roadmap 206 tracks the work.

## WHAT IT IS

A **step van**: the 1970s-90s walk-in delivery truck on a P30-style chassis --
bread vans, parcel vans, Philly water-ice and food trucks. Its body and cab
are ONE box, which is what makes it read as a step van and not a box truck
with a separate cab:

- **Body:** a tall rectangular box, slab sides, a gently rounded roof edge,
  a horizontal belt line (a pressed rib) along the side at about mid-height.
  Rear wheel arches cut square-ish into the side; the rear sits high.
- **Front:** a short sloped nose under a flat, near-vertical front face. Two
  flat windshield panes, split by a centre pillar, each with its own wiper.
  Two round headlights in square chrome bezels, amber turn lamps above them,
  a plain rectangular grille between, a heavy black bumper.
- **Side:** a walk-in door just behind the front wheel (a sliding or folding
  door with its own window), a small louvred vent below the cab window,
  tall square mirrors on bent tube arms.
- **Roof:** amber clearance lamps along the front edge, sometimes a light
  bar. One comp carries a big round extractor-fan stack (a food truck's).
- **Wheels:** steel wheels, plain hubs, dual rears optional.
- **Scale:** about 6.5-7.5 m long, 2.4 m wide, 3.0-3.2 m tall.

## THE FOUR COMPS

1. **A Philadelphia water-ice step van**, white, red hand-lettered name on
   the body, a serving window with a menu board beside it. The local
   reference: Delco's own kind of truck. *Take:* the shape, the serving
   window, the way a small business letters its van by hand.
2. **A plain white P30 step van**, unbranded, amber roof lamps and light
   bar, light grime along the roof seams. *Take:* the cleanest read of the
   body -- proportions, nose, windshield, bezels, belt line.
3. **A dark grey food truck**, riveted panel seams, a hinged awning over a
   serving window, a painted chef mascot, a roof extractor. *Take:* the
   riveted panels and a dark finish over flat aluminium.
4. **A near-black step van in a suburban driveway**, sun-faded, a painted
   roundel on the nose, a stepping stool at the door. *Take:* the finish --
   black gone dull and uneven, lighter where the sun hit it.

## THE FINISH THE WALKER ASKED FOR

**Matte black, faded, with patina.** It reads as a working truck that has
been on many jobs:
- **Paint:** flat black, never gloss; sun-faded toward charcoal on the roof
  and the upper sides, deeper on the lower panels.
- **Wear:** scuffed paint at the door edges and the bumper corners, rust
  bloom at the wheel arches and the panel seams, dust and road grime on the
  lower third, a dull rubber bumper.
- **History (the authorship guide's "why is this here?"):** an old food or
  water-ice van bought cheap and painted over. The ghost of its old
  hand-lettering may show through the black on the body side. A suggestion,
  not the walker's call yet -- confirm with a frame. Any lettering is an
  invented Delco name, PG-13, no real mark.
- **One per level.** It is a hero prop, the crew's own -- the "Millennium
  Falcon" -- so it is the same truck in every level, worn the same way, not
  a colour variant of a parked car.

## WHERE IT STANDS

**At the mission's spawn point**, at the curb, along the road. The crew
spawns at the van, does the job and returns to it, so the van IS the
extraction. This is what 159 of 181 cold-run briefs asked for in the field
nothing read, `extraction_relationship: "crew_start_backtrack"`.

## WHAT EACH TOOL OWES IT (to be confirmed against the code)

- **Zoo -- built, 1.82.0:** the species `step_van`, and its finish with it.
  The paint is the van's own: per corner in vertex colour on one
  `paint_matte` material, sun-chalk, dust, rust and a primer patch, so no
  theme pack repaints it. Not built: the ghost lettering (the walker's
  call), the wipers, the roof stack.
- **Patina / Pixelcoat:** nothing as it stands, because the finish lives in
  Zoo. *As first filed:* "the finish -- flat black paint, sun fade, rust
  bloom, grime."
- **Lot:** one van at the spawn point, at the curb, oriented along the road;
  the spawn and the extraction markers on it.
- **Level Factory:** the site spec's extraction is the spawn, never a
  building drawn by seed; the package marks the van as the mission's start
  and its extraction (roadmap 204).
- **Laser Tag:** the crew's route ends where it began.
