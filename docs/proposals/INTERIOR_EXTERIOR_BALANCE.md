# Inside against outside, day against night

The walker, 2026-09-26, after a night package whose deli read as unnavigable
black: "this is tough, but a legitimate thing to understand about lighting
inside and outside when its day vs. night."

It is, and the pipeline currently has no model of it at all. This is what it
does instead, measured.

## The relationship being described

In the world, interior lights are the same brightness at noon and midnight.
What changes is everything around them, and a camera with one exposure turns
that into an inversion:

* **Day.** Outside is far brighter than inside. From the street a window is a
  dark hole; from inside it is a blown-out rectangle. Interior lamps are on
  and contribute almost nothing to the look.
* **Night.** The relationship flips. A lit shop window is the brightest thing
  on the street, the interior is the beacon, and the practicals are doing all
  the work.

A level that reads correctly needs that inversion. This one cannot produce it,
and the reason is a single constant.

## What the presets actually do

                           sky    sun   ambient   exposure   probes
    delco_summer_afternoon 1.10   1.50   1.10       1.00      replace
    blue_hour              0.70   0.90   0.90       1.05      replace
    delco_night            0.35   0.75   0.55       1.05      replace
    heavy_rain             0.60   0.50   1.00       0.95      replace
    gas_station_fluorescent 0.40  0.20   0.70       1.05      replace

**The exterior moves by about 3x between the brightest and darkest preset.
Exposure barely moves at all** -- 0.95 to 1.05 across the set, which is right:
the doc the walker supplied says not to fix lighting with exposure.

## What the interior does: nothing

Every interior practical is a flat constant, independent of preset. The
fluorescent -- the light in almost every room this factory builds -- is
`energy = 1.0` in every package measured, and what it puts on the floor
beneath it falls off with ceiling height:

    ceiling drop 2.6 m   0.1405
    ceiling drop 2.9 m   0.0928
    ceiling drop 3.2 m   0.0570
    ceiling drop 3.8 m   0.0314

That figure is not an estimate; it is `office_floor_value`, the function this
whole lighting file uses as its unit.

**So one fluorescent delivers about a tenth of what the AMBIENT term is
adding:**

    Delco Night   ambient 0.55  =  6x one fluorescent at a 2.9 m ceiling
    Blue Hour     ambient 0.90  = 10x
    Afternoon     ambient 1.10  = 12x

In every preset, in every room, the lamps on the ceiling are a minority
contributor to the light in the room. Interiors are lit by the sky.

## Which makes the inversion impossible

Take the ratio of what an interior delivers to what the exterior ambient
delivers:

    day    0.093 / 1.10  = 0.08
    night  0.093 / 0.55  = 0.17

It doubles between day and night, so the pipeline is directionally right --
and it never comes close to 1.0. **An interior is never brighter than the sky
term, at any time of day, so a lit window can never be a beacon.** At night the
street has no bright interiors to look at, and inside a room with the sky
occluded there is very little left, which is the black deli.

`room_probes_replace_ambient = true` in every preset, so indoors the flat
ambient is replaced by a room probe. That is the correct architecture -- a
sealed room should not be lit by a sky it cannot see -- and it is also why the
failure is worst exactly where it matters: in a room with no window, the
probe is dark, the ambient is gone, and all that remains is 0.093 per lamp.

## The rule that follows, derived rather than chosen

**For an interior to read as lit from outside at night, what it delivers on
its own floor has to exceed the exterior ambient it is seen against.** At
Delco Night's 0.55 that means roughly 0.6 delivered, which is about six
fluorescents' worth on one patch of floor, or one at six times the energy.

**For an interior to read as interior in daylight, it has to sit below the
exterior** -- otherwise a shopfront at noon looks like a shopfront at night --
**but above the floor where it becomes a void.** Where that floor sits is a
look call and nobody here has named it.

Those two bounds cannot both be met by one constant, which is the whole
finding: **`FLUORESCENT_ENERGY` and its siblings want to be a function of the
preset, not a number.**

## What this does not say

It does not say the fluorescent is "too dim". It is the UNIT the rest of the
system is measured in -- `office_floor_value` is defined as what one of them
puts on a floor -- so changing it moves every derived energy in the file with
it, including the canopy and the streetlights that were just tuned. That is a
change to make deliberately and measure, not a number to nudge.

It also does not say which direction to move. A brighter interior at night is
clearly wanted; whether daylight interiors are currently too dark is
unmeasured, because every cold run before 9082 was a daylight preset and
nobody was looking at interiors when they were.

## What to do first

Measure before touching anything. `tools/pool_exposure.gd` already reports a
histogram; point it at a station INSIDE a building under each preset and get
the black fraction and p50 for the same room at noon, at dusk and at night.
Three numbers, one room, one variable.

That would say whether the daylight interior is already a void, which decides
whether this is one fix or two.

## Measured (2026-09-28, cold run 9102's walk copy)

The prescribed first step, on the store the walker's night photographs are
about: gas_station_a02, with its see-through storefront (Zoo 1.18.0) and a
fluorescent row over the sales floor (Deli Counter 0.154.0). `look_shots.py`
with given stations, the walk copy's ONE preset line swapped per run and
restored byte for byte; RTX 2060, gl_compatibility, 1600 x 900, whole-frame
Rec.709 luma on 8-bit sRGB after the post stack.

                         inside the     inside, facing   the storefront from
                         sales floor    the glass        15 m out, square
                         mean  p50      mean  p95        mean  p95  crushed
    delco_summer_after.  42.1   44      48.0  127        54.9  180    0.0%
    blue_hour            18.2   20      22.7   97        14.9   83   44.0%
    delco_night           8.4    9      13.8   62         4.2    3   59.1%

**The interior follows the sky, not its lamps.** The same room is five times
darker at night than at noon with its fixtures unchanged, which is this
document's finding measured in a frame: the practicals are a minority of the
light even where they are the only light that should be on. And at night the
storefront from outside is 4.2 -- the glass passes what is behind it, and
what is behind it is 8.4.

So the daylight interior is NOT a void (42) and the night interior is (8.4):
this is ONE fix, at night. Nothing here has changed the constant yet; the
decision it needs is recorded in the next step, not taken.

## After Lux 0.55.0 (cold run 9103)

The walker, 2026-09-28: "brighten fluorescents at night, keep pendants
moody". Lux 0.55.0 multiplies every fluorescent rig by the preset's
`fluorescent_energy_scale`, derived from its sky (Delco Night 6.0); bare
bulbs refuse it. On 9103's shipped package, `look_shots.py`, the walk copy's
Delco Night at 1.0 against the shipped 6.0, one build, the player's graded
frame:

                               scale 1.0          scale 6.0
                               mean   p95         mean   p95
    inside the sales floor      6.5    13          8.9    29
    outside, through the glass  5.6    27          6.2    31
    the storefront from 15 m    4.2     3          4.2     3
    the office (bare bulbs)    20.3    74         21.4    77

**The room reads; the street does not see it yet.** Inside, the shelves and
the cooler wall come out of black and the bright end doubles. Outside, the
change is a tenth of a stop. What stands between the lamps and the street,
each a separate lever and none pulled here:

  * the NIGHT GRADE compresses the interior's gain (pre-grade the same room
    went 1.9 -> 15.7; graded, 6.5 -> 8.9) -- a grade question, and this
    document says not to fix lighting with exposure;
  * each troffer's REACH is `drop + 0.75`, a per-mesh light-budget number
    (roadmap 54), so it floors a ~2.9 m pool and the walls and the glass
    line stay outside every pool;
  * the storefront PANE is the theme's glass at 0.38 opacity with a tint,
    which takes about a third of what is behind it;
  * nothing SPILLS: no light leaves the store onto the pavement (priced as
    real lights against the forecourt's budget of 8, not built).

A pre-grade probe once read the first bullet as the fix working (a table in
Lux 0.55.0's changelog, corrected there): the instrument that hides the HUD
by hiding every CanvasLayer also hides Lux's post stack.

## After the glass and the reach (cold run 9104)

The walker, 2026-09-28: "yes, do the glass first then the troffer reach" --
the first two of the four levers above; the grade and outward spill are not
pulled. Measured on 9103's walk copy before anything shipped (the values set
at runtime), then shipped as Zoo 1.20.0 (a storefront pane is clear float
glass, opacity 0.12, its own material), Deli Counter 0.155.0 + Zoo 1.21.0 +
Lux 0.56.0 (a ceiling row walled by storefront glass carries `reach`, the
metres to the glass, and its range is derived to the floor there: 7.5, the
clamp, for gas_station_a02's sales floor against 4.55). Cold run 9104, zero
interventions, findings identical to 9103 (58).

Night, look_shots, the player's graded frame, the same eight cameras on each
build (mean / p95; the 9103 column reproduced 9103's own recorded figures):

                                   9103          9104
    inside the sales floor       8.8 / 29      15.9 / 58
    through the storefront       6.2 / 31      11.2 / 65
    the forecourt, south corner  3.8 / 32       6.7 / 43
    the store from 8 m           6.9 / 31       9.1 / 43   (centre 30.5 -> 34.6)
    the forecourt, north corner  6.1 / 23       6.3 / 24
    the street at 30 m           5.4 / 19       5.5 / 21
    the office (bare bulbs)     21.4 / 77      21.3 / 77

REFUTED, kept: `storefront_square` (15 m, the camera the section above used
for "the street does not see it") stands behind a pump island that fills the
lower half of its frame; its 4.2 -> 4.5 is the island, not the store. The
three forecourt cameras replaced it.

The row moved 3.5 m toward the glass at the old range was also measured, and
was WORSE through the glass (8.2 against 9.0 with the glass alone): the pool
moved and did not grow. It did not ship.

COST. Draws: 4 of 53 headings -1, the rest identical, both 9104 runs agreeing;
median p95 frame time 3.75 ms (9103) against 3.56 and 3.46 (9104), stations
over the provisional budget 7 of 14 on both. THE PER-MESH LIGHT BUDGET MOVED:
meshes over 8 lights 35 -> 39 (`mesh_light_census`; the perf harness's own
count 34 -> 38), all of them b2's -- the stockroom's ceiling (13) and floor
(12) and the back hall's (10, 10) are newly over, reached through the
partition by the sales floor's 7.5 m lamps, and the sales floor's own ceiling
and floor, over before this, went 15 -> 16 and 12 -> 16. The census counts a
range sphere through walls and is an upper bound. Frames of the stockroom and
back hall on 9104 with those five lamps at 7.5 and at 4.55 (one build) read
4.0 / 4.1 and 70.5 / 70.5: nothing a camera there can see moved. That is
four cameras, not a walk, and roadmap 54's seam is a thing a person sees
moving; it stays a named risk rather than a cleared one.

WHAT IS STILL OPEN: the street at 30 m does not see the store yet (5.4 ->
5.5); the grade and outward spill are the levers left, and a street-level
view of the forecourt under its canopy is its own lighting question.
