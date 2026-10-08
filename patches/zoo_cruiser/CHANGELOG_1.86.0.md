## [1.86.0] - the responders' cruiser: a 1990s Crown Victoria lettered for the DELCO COUNTY POLICE

### What the walker asked for

The walker, 2026-10-08, asked what the responders drive: "I would think a
classic 1990s Crown Victoria", with five photographs. For the department:
"Delco County Police Dept. as a start?". Then one more photograph, of the
interior.
- **The comps:** read for format only, none stored, no real department's
  name, seal, number or plate reproduced. `docs/reference/CRUISER_COMPS.md`
  at the factory root describes them.
- **The interior photo:** grey-blue cloth seats, a radio console between
  them.
- **Whose job the car is.** Responders arrive on the way back (roadmap 212).
  The gameplay layer spawns them; this is the car they arrive in.

### `cruiser`, a species of its own

The brief, by the authorship guide's three questions:
- **What it is for.** The responders' car: what pulls up while the crew
  makes for the van.
- **Who touches it.** Nobody in the crew. It is parked by whoever spawns it,
  and shot at.
- **What it is made of.** A Crown Victoria police sedan: `simple_car`'s
  body at that car's proportions, a 1990s patrol car's kit, and a
  department's livery.

**The car is `simple_car`'s.** It is drawn from a new `cruiser` row in
`car_forms.FORMS`, read off the 1998-2002 car's published sizes:

| what | the car | the row |
|---|---|---|
| length | 5.385 m | -- |
| width at the body | 1.986 m | -- |
| height | 1.443 m | -- |
| wheelbase | 2.913 m | 0.541 |
| front overhang | about 0.99 m | 0.184 |
| tyres | P225/60R16, r 0.338 m | 0.234 of the height |

- **From the comps:** a long hood, a near-vertical C-pillar with a quarter
  glass, and a long trunk.
- **The form is pinned** (`cruiser_forms.pin_form`). Four doors and a
  quarter glass, black steel wheels, body-colour bumpers, a side moulding,
  and the blue-grey cloth of the interior photo.
- **No jitter.** It is the same car in every level, as the van is.
- **Asked for, never drawn.** `auto` never parks one: it is not in
  `AUTO_POOL`, and `STREET_STYLES` is still the four `simple_car` offers.

**The slot** is the car with its kit: 2.196 x 5.545 x 1.578 m by default
(`cruiser_forms.SLOT`).
- **Width** is the mirror heads' outer faces.
- **Depth** runs from the push bar's front to the rear bumper.
- **Height** is the light bar's top.
- **The genome's range:** 2.1-2.3 x 5.35-5.75 x 1.5-1.66 m.

### The kit (`core/cruiser_forms.kit`, pure)

| part | where |
|---|---|
| light bar | across the roof, 0.40 of the way back: red on the driver's side (+X), blue on the other, a clear centre |
| push bar | on the nose: two uprights, a top bar and a lower bar, braced back into the bumper |
| spotlight | up the driver's A-pillar, its head outside the glass |
| whip | on the trunk lid behind the backlight |
| partition | inside, behind the front seat backs |
| radio console | inside, on the floor between the front seats |

- **Boxes on the car's one painted material.** Each part's colour is in
  `Wear`.
- **Named in the car's part family:** `Car_Kit` and `Car_Lens_*`. The
  export packs parts by family and material, so the kit goes into the car's
  painted mesh.
- **A cruiser exports five meshes,** one a material: the livery's body, the
  painted parts with the kit, the rubber trim, the cabin and the glass. That
  is five submissions, as the van has.
- *First build:* the kit was named `Cruiser_*`, a family of its own, and
  the export carried a sixth mesh on the painted material. The comment
  beside its colours already said "no draw call of its own". It said it
  before it was true.
- **The lights are parts, not lights.** The lenses are unlit, as
  `simple_car`'s lamps are. `ATT_lightbar` marks the bar's centre for a game
  layer that wants to light it.

### The livery (`core/cruiser_forms.livery_art`, pure)

**One image on one material** (`materials.make_wear_textured_material`,
the van's ghost technique).
- **The sides** map into the image by their (y, z), read the right way
  round from either side (`livery_uv`). So a door's two-tone edge and the
  lettering are as sharp as a texel.
- **Every other face** samples the image's white patch and takes its colour
  per corner (`finish_rgb`): the roof white, the rest the body's colour.

**Two liveries, by the slot's `form`.** These are the two the comps hold:

| livery | what it is | the department |
|---|---|---|
| `black_white` (the default) | black, white doors and roof | DELCO COUNTY over POLICE on the doors |
| `white_blue` | white, a blue stripe fender to quarter | DELCO COUNTY POLICE on one line in the stripe |

- **Both carry** a gold seal at each end with unit 214, and the motto
  WE'LL GET YOUSE under the moulding.
- **Lettered where the car was cut.** `simple_car` now returns its door
  seams, its door skin's height and its moulding's centre line. The marks
  stand above the moulding and under the door handles.
- *The first frames* ran the moulding through POLICE and the front door's
  handle 7 mm into DELCO COUNTY.
- **A lower car's marks shrink together** (caps, gap, stripe and seals) to
  the door between the moulding and the handles.
  - Measured over 51 sizes: 0.92 of full size at the genome's lowest
    height, 0.99 at 1.55 m, and full size from 1.56 m. The default is full
    size.
  - Under `MARK_SCALE_MIN` (0.8) the car is one the livery was not drawn
    for, and it is refused.
  - The first census refused the lowest corner outright: marks to 0.794 m,
    handles from 0.775 m.
- **A line that does not set raises.** A door that silently lost its
  department would look like a choice.

### `simple_car`, for a recipe that builds on it

- **`build(plan, streams, collection, form=None)`.** A caller can pass a
  form it has already drawn and pinned. Without one, the car is drawn as it
  always was, from the same streams in the same order.
- **It returns what it built.**
  - `door_edges`, `door_skin_z` and `moulding_z`.
  - `interior`: the cabin floor's top, the front seat backs' rear face, the
    rear seat's front (or None) and the door cards' inner face.
  - Each value is computed once and used by the faces it describes, so it
    cannot drift from them.
- **`car_forms.SEDANS`.** Sedan, coupe and cruiser are built as sedans
  wherever a style decides a detail: a small quarter glass, wide tail lamps,
  and the plate low on the tail.
  - *The first build* drew the cruiser as an SUV there: a hatchback's
    quarter glass gave 1.45 m doors, with an SUV's tall corner lamps. Its
    doors are 1.67 m now.
- **Its own cars are unchanged, measured.** Every street style (4) at three
  sizes was built in 1.85.0 and in this version: 200 meshes, every vertex
  hashed at 1e-6 m. 0 differ, and their attachments are identical.

### The census and the tests

**Coincident faces.** `tools/coplanar_census.py --species cruiser`, Blender
5.1.1: 3 builds, 0 pairs, 3,476 tris at each corner, on the third run.
- **The first run:** 8-9 pairs a build, all in the kit.
  - The partition's posts stood 1-2 mm inside its rails' faces.
  - The rails' ends were flush with its posts.
  - Its bottom rail lay in the cabin floor's bottom plane.
  - Its middle posts were 1.37 mm off the headrests' sides.
  - The push bar's lower brace touched its lower bar.
- **The fixes.** `INSET` (4 mm, twice the probe's window) sets faces back,
  and the partition now stands from the cabin `simple_car` returns.
- **The second run:** the rail's underside was 2 mm over the body's pan, at
  a 10 mm sink into a 22 mm floor. It sinks by `INSET` now.
- **A sweep of 51 sizes found 0:** every centimetre of height at three
  widths, both liveries.

**`tests/test_cruiser.py`, 133 tests.**
- **The car:** the genome, a Crown Victoria's sizes, the pinned form, and
  `auto` never parking one.
- **The kit:**
  - it fills the slot and no more;
  - red on the driver's side, on four feet;
  - the spotlight on the A-pillar.
- **No two kit faces share a plane, at all 27 genome corners.** This is the
  census's check, for boxes, without Blender. It fails on the kit as it
  stood before the census: 810 face pairs across the 27 corners. A control
  shows the check finds the first cut's partition post.
- **The partition and the merge:** the partition stands between the seats
  and inside the doors, or is refused; the kit merges into the car's
  painted mesh.
- **The livery:**
  - every line sets, in both liveries;
  - the marks fit at the measured lowest, default and highest doors;
  - marks too small to read are refused;
  - the sides read the right way round.
- **`simple_car`'s hooks,** read as source: its cars are drawn as before,
  and the cabin it returns comes from the faces it built.

**The registries a new species joins**, as the van did:
- `test_genome.py`'s species set;
- `test_material_options_closed.py`'s `PAINTED`;
- `test_theme_style_resolution.py`: 94 to 95, the `delco` row a copy of the
  `default`, because the livery is in the image, not a theme;
- `test_coincident_faces.py`: 363 to 366 builds;
- `test_car_forms.py`: the street styles are still `simple_car`'s own, and
  `FORMS` is them plus the cruiser.

### Not done

- **Not in a level.** Lot places a responder slot of 2.0 x 5.4 x 1.5 m, a
  little smaller than this car. Deriving that slot from this species is
  roadmap 212's next step.
- **Not priced in a frame.** It is five meshes and 3,476 triangles a car.
  How many a level carries is the gameplay layer's to say.
- **The livery is not chosen.** `black_white` is the default; the walker
  has both to look at.

**Suite:** 4,015 passed, 395 skipped, 1 xfailed in 344 s
(`python -m pytest -q`).
- **Against 1.85.0:** its 3,876 and 395.
- **All 139 added tests pass,** and none goes: `test_cruiser.py`'s 133,
  five in `test_material_options_closed.py`, one in
  `test_recipe_reads_its_genome.py`.
- **On a `git archive` outside the factory,** both versions skip 27 more
  (1.85.0: 3,849 passed; 1.86.0: 3,988; 422 skipped each). 25 of those want
  Pixelcoat or Deli Counter beside the repo.

