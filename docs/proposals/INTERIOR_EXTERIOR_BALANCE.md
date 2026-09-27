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
