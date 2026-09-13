# Late-1990s Delaware County: the art direction, and which tool owns each part

The walker, 2026-09-13, handed over a statement of what this place actually
looks like. It is recorded here in full, because it is the first description in
this repo of the THEME rather than of a technique, and because the frames it
judges are already being shot (`docs/cold_runs/cold_9041/frames/`).

Read it as a specification with an owner column. The pattern this repo keeps
falling into is a reference read once, admired, and turned into nothing; the
back half of this file exists so that cannot happen quietly. Everything the
pipeline cannot currently do is named as such rather than left implied.

## The statement

**The place did not look like architecture from the late 1990s.** It looked
like generations of southeastern Pennsylvania buildings repeatedly expanded,
repaired, enclosed and commercialised. The decade is a LAYER on older fabric,
not a style the buildings were built in.

**1. Buildings feel inherited, not designed at once.** A single building
carries an early-1900s stone or brick shell, a 1950s rear addition, aluminium
or vinyl siding from the 1970s or 80s, replacement windows and signage from the
1990s, and a porch enclosed later still. The mismatches ARE the identity. A
building that reads as one coherent design decision is wrong here even when it
is well made.

**2. Dense working- and middle-class housing.** Red-brick rowhouses. Brick or
stone twins -- twins should appear FREQUENTLY, not as an occasional variation.
Narrow detached houses. Small porches, shallow front yards, shared driveways,
rear alleys, detached garages, concrete steps rising straight from the
sidewalk.

**3. Local fieldstone as visual ballast.** Grey, tan and brown, heavy,
irregular, locally sourced -- not a clean veneer and not a decorative course.
It appears in facades, foundations, retaining walls, churches, schools, mills
and bridge abutments. It is the material that makes the county read as itself.

**4. Commercial architecture grew out of ROADS, not plazas.** Baltimore Pike,
MacDade Boulevard, Chester Pike, West Chester Pike, Township Line Road.
Buildings sit close to the road with parking beside or behind them. Converted
houses used as offices, one-story brick storefronts, small strip centres,
auto-parts stores, diners, pizza shops, bars, pharmacies, banks. Freestanding
pole signs accumulated at different dates and in different styles. Utility
wires and traffic signals dominate the view. The corridor is incremental and
contested, not master-planned.

**5. The late-1990s layer itself.** White aluminium or early vinyl replacement
windows. Beige, pale blue, cream and faded yellow siding. Dark green, burgundy
and navy awnings. Faux shutters. Brown asphalt-shingle roofs. Glass-block
basement windows. Storm doors with brass hardware. Fluorescent-lit box signs.
Internally illuminated plastic signs. Teal, mauve, peach and hunter-green
accents. Beige stucco or EIFS storefront remodels. Satellite dishes. Window air
conditioners. Security bars and roll-down gates.

**Nothing should look intentionally "retro".** The period is the present tense
of the level, not a costume worn over it.

### By area

| Area | Fabric |
| --- | --- |
| Upper Darby, Lansdowne, Yeadon | Dense brick twins and rows; trolley-suburb storefronts |
| Drexel Hill, Havertown | Stone-and-brick twins; enclosed porches |
| Springfield, Ridley, Morton, Folsom | Postwar detached, split-levels, Capes, ranches, strips |
| Media | Older borough fabric, Victorians, civic buildings |
| Chester, Marcus Hook | Rowhouses, industrial, vacant lots, corner stores |
| Newtown Square, Glen Mills, western Delco | More space, older stone, wooded roads |

### What makes it feel human

Similar buildings become different through USE. One twin keeps its stone
exposed, the other is sided over. One porch is open, the neighbour's is
enclosed. One storefront keeps its cornice, another hides it behind a remodel.
Rooflines align; windows, awnings, fences and additions do not. Property
boundaries are expressed through tiny changes of material rather than through
gaps.

In one sentence: late-1990s Delco is a compressed landscape of stone houses,
brick twins, postwar suburbs, aging commercial corridors and industrial
remnants -- shared architectural bones covered by decades of individual
decisions.

## What this asks of each tool

The routing rule in `USING_THE_FACTORY.md` holds: the owning tool grows the
capability and nothing is hand-authored in a workspace. What follows is that
routing applied to the five points above, with the state of each as of Lot
0.69.2 / Pixelcoat 0.36.0 / Zoo 0.61.x.

**Pixelcoat owns the surfaces.** The 1997 theme maps 29 kinds
(`profiles/themes/delco_1997.json`) and none of them is STONE -- no fieldstone
grammar exists, so point 3, the material the walker calls the county's visual
ballast, cannot currently be asked for by name. Nor does the theme carry
siding, asphalt shingle, glass block or EIFS. The colour direction in point 5
is specific enough to be a palette constraint rather than a mood: beige, pale
blue, cream, faded yellow for siding; dark green, burgundy, navy for awnings;
teal, mauve, peach, hunter green for accents.

**Zoo owns the objects.** 24 species minted. The street furniture of point 4 is
largely there -- signal, stop sign, mailbox, meter, payphone, newspaper box,
shelter, hydrant, bollard, five street trees. The utility wires and poles that
the walker says DOMINATE the view are not, and neither are satellite dishes,
window air conditioners, security bars, roll-down gates or awnings.

**Deli Counter owns the buildings, and this is where the direction bites
hardest.** Points 1 and 2 are not set dressing; they are a statement about how
a building is composed. A building generated from one archetype with one
material and one roofline is exactly the thing the walker says is wrong, and it
is what this pipeline makes. Two concrete asks fall out:

- **The twin.** A pair sharing a party wall, built as one shell and then
  differentiated -- one side's stone left exposed, the other sided; one porch
  open, the other enclosed. Frequent, not occasional. Nothing in the archetype
  set expresses a shared wall.
- **The accretion.** A shell carrying a later addition at a different height,
  in a different material, with a roofline that does not continue. The repo has
  no vocabulary for "this part was added later" -- every facade run is one
  decision.

**Lot owns the corridor.** Point 4 is a layout rule and it contradicts what Lot
currently does: the pipeline lays freestanding shells with a plate between them
and the road, and the walker's photographs are of buildings that MEET the
sidewalk with parking beside or behind. This was already the largest gap named
in `SET_DRESSING_REFERENCES.md` from the main-street shots; the art direction
raises it from a note to the defining feature of the commercial corridor.

**Patina owns the differentiation.** "Similar buildings become different
through use" is a placement rule, not a texture: the same shell, the same
species list, and a per-instance decision about which of a small set of
alterations it received. That is the mechanism that makes points 1 and 2 read,
and it is the cheapest of the asks here because it reuses geometry that already
exists.

## What is unproven

- The area table is the walker's, not measured. It is recorded as direction,
  and no tool should read it as data until somebody decides what a "region"
  would mean to a generator.
- The claim that the theme carries no stone grammar is from the 29 kinds listed
  in `profiles/themes/delco_1997.json` on 2026-09-13; `flagstone`,
  `granite_speckle` and `cobblestone` exist as grammars and are not mapped by
  the theme. Whether any of the three could stand in for fieldstone has not
  been rendered and should not be assumed.
- Nothing here has been costed. The twin and the accretion are described as
  asks, not as designs, and neither has a triangle budget or an archetype
  sketch behind it.
