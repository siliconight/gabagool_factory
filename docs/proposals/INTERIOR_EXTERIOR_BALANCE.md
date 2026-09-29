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

## After the spill (cold run 9105)

The walker, 2026-09-29: "do the outward spill next". Deli Counter 0.156.0
derives a `storefront_spill` along the glass of every room whose row reaches
it (one per two heads of glass, at the glass head, facing out); Zoo 1.22.0
records it as hardware-elsewhere; Lux 0.57.0 bakes each as a one-lamp
fluorescent rig tilted 45 degrees out and down with the window's 45-degree
cone, scaled by the preset like the room it comes from, killed by a power
cut. 35 in the library, 7 at gas_station_a02. Cold run 9105, zero
interventions, findings identical to 9104 (58).

THE LEVEL IS FRAME-MATCHED, and the first answer was nothing. The physical
rule -- the pavement takes what the lit floor inside takes, less the glass,
0.378 at Delco Night -- was stood outside the store at runtime on 9104's walk
copy and the pavement in front of the glass read luma 0.8 with it and
without. The dial was live (x20 lit three pools); the forecourt pad's 32
range-sphere claimants were not it (the engine read a raised
`max_lights_per_object` of 64 and neither frame moved). The room's floor is
lifted by its probe's ambient and a carpet's albedo, the pavement by
neither, under a night grade that crushes its toe. Matched in frames
instead, pavement luma against the carpet through the same glass (x1 / x5 /
x10 / x20: 0.8 / 8.8 / 21.9 / 44.0 against 17.6 wanted): x8.4, written into
`LuxLightLoader.SPILL_FRAME_MATCH` with the settings it was measured at.

Night, graded, the same cameras (mean / p95):

                                   9104          9105
    through the storefront      11.0 / 64      22.1 / 93
    the forecourt, south corner  6.7 / 43      18.5 / 100
    the store from 8 m           9.1 / 43      20.8 / 94
    along the sidewalk           8.2 / 45      17.6 / 83
    the forecourt, north corner  6.4 / 24       6.4 / 24
    the street at 30 m           5.5 / 21       5.4 / 20
    inside the sales floor      16.1 / 58      15.1 / 58

    region luma: the pavement in front of the glass 0.8 -> 13.2, the pool
    seen from the south corner 0.8 -> 32.9.

Noon (the afternoon preset, scale 1.0): the pavement in front of the glass
50.1 -> 54.5 and the south pool 85.0 -> 91.6 -- a store's light at noon is a
tenth of the sunlit pavement, as the preset scaling intends.

COST. Draws: 4 of 53 headings -2 or -3, both 9105 runs agreeing, the rest
identical. Frame time: median p95 3.46 ms (9104) against 3.97 and 3.48 --
the two 9105 runs disagree with each other by more than 3.48 differs from
3.46, so noise; max p95 10.51 against 10.46 / 10.60; stations over the
provisional budget 7 of 14 on both.

THE PER-MESH BUDGET, AND IT IS VISIBLE THIS TIME. Meshes over 8 lights 39 ->
51 (census; the perf harness's own count 38 -> 50). The spills reach into
the store as well as out of it -- a tilted spot's culling box extends about
3.3 m back through the glass -- and b2's sales floor FLOOR and CEILING are
each one mesh the size of the room, already at 16 claimants for 8 slots. At
20 the engine's choice of eight moved, and the room lost some of its own
lamps: the carpet through the glass 19.7 -> 16.9, the sales floor 16.1 ->
15.1. PROVEN, not inferred: the same 9105 build with
`max_lights_per_object` raised to 64 read the carpet 20.1 and the room 16.0,
9104's figures, with the pavement unchanged at 13.2. (A first attempt at
that control patched an anchor the fresh export did not have -- 157
renderable lights, not 150 -- and ran unchanged; it was caught by its own
assertion and rerun.)

The store is still brighter than 9103 (8.8) and the pavement is lit where it
was black. The defect underneath is older than this change: a room's floor
and ceiling are merged into one mesh per material (Zoo 1.1.0's merge, right
for draw calls), which makes every room-sized plate one claimant list for
the whole room -- roadmap 54's law met from the other side.

STILL OPEN: the street at 30 m (5.4) -- it is 30 m of dark road with the
canopy between; the grade is the last lever, and the walker has not pulled
it.

## After splitting the floor and ceiling tiles (cold run 9106)

The walker, 2026-09-29: "yes, split the floor and ceiling tiles". Zoo 1.23.0
stops merging `Floor` and `Ceiling` parts, so the light-budget tiles
`arch.tile_parts` has cut since roadmap 54 (8 m) reach Godot as their own
meshes -- the sales floor's floor and ceiling six each. Roofs still merge.
Cold run 9106, zero interventions, findings identical to 9105 (58).

THE LOOK CAME BACK. Night, graded, the same cameras: the carpet seen through
the glass 16.9 -> 20.5 (9104, before the spill, 19.7), the sales floor 15.1
-> 16.1, the pavement's spill unchanged at 13.2. Meshes over 8 lights 51 ->
42; every room-sized floor and ceiling that was one mesh at 15-21 claimants
across all three buildings is now tiles, the store's worst at 9-11.

AND IT COST DRAW CALLS -- the rule this repo holds hardest. Priced in one
session, 9105 against 9106 twice, the runs agreeing:

    draws        51 of 53 headings up, +4 to +230; summed 71,802 -> 77,139
                 (+7.4%); 4,666 -> 4,918 meshes
    frame time   median p95 4.76 ms -> 5.11 / 5.19; max 12.14 -> 12.61 / 12.73
                 (longest_sightline +209 draws, 8.45 -> 9.6 ms)
    budget       stations over the provisional 2000 draws / 11 ms: 7 -> 11 / 10

The split is library-wide, not the store's: every floor and ceiling over 8 m
on a side in b0, b1 and b2 is tiles now, and interiors have no occlusion
culling, so a heading that looks across a building draws every tile in the
frustum. PUT TO THE WALKER, not decided here: keep it (the look and the light
budget, at +7% draws), narrow it to the rooms lit from outside through
storefront glass (the rooms where the regression was), or revert it (9105's
look, the room ~15% dimmer at the glass).
