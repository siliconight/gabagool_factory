# The cruiser's build: coincident faces, the livery's fit, and simple_car unchanged (Zoo 1.86.0, roadmap 212)

**Question.** Zoo 1.86.0 adds `cruiser`, the responders' 1990s Crown
Victoria, built on `simple_car` (`patches/patch_zoo_cruiser.py`). Three
things had to be shown before it shipped:
- **Faces:** does it build without coincident faces at every size its
  genome allows?
- **The livery:** does it letter every door it can be given?
- **`simple_car`:** are its own cars unchanged by the hooks the cruiser
  needed?

**Frame and units.** Blender world space, Z up, metres. Census builds are
re-centred, as `build_module` ships them; `car_hashes.py` reads the recipe's
own build frame, z 0 .. H. Areas are cm2, gaps mm.

## Coincident faces

`tools/coplanar_census.py --species cruiser`, Blender 5.1.1, at the genome's
min, default and max corners. The probe's defaults: within 2 mm, overlapping
by at least 1 mm2.

| run | output | builds | pairs |
|---|---|---|---|
| 1 | `census_1.txt` | 2 of 3 | 9 at default, 8 at max |
| 2 | `census_2.txt` | 3 of 3 | 1 at default |
| 3 | `census_3.txt` | 3 of 3 | 0 |
| 4, after the kit's rename | `census_4.txt` | 3 of 3 | 0 |

### Run 1: every pair was the kit's

`pair_where.py` printed each pair's sample points:

| pair | facing, gap | area | where |
|---|---|---|---|
| partition's bottom rail / cabin floor | SAME, 0 mm | 329 cm2 | the rail's underside in the floor slab's bottom plane, z = clear + 0.12 |
| partition posts / rails | SAME, 2.00 mm | 20 cm2 | the posts' y faces 2 mm inside the rails' |
| middle bar / posts | SAME, 1.00 mm | 20 cm2 a face | the bar 1 mm inside the posts' faces |
| inner posts / headrests | SAME, 1.37 mm | 14.4 cm2 | at x = +/-0.288 |
| inner posts / headrests | OPP, 1.37 mm | 14.4 cm2 | at x = +/-0.288 |
| outer posts / rails' ends | SAME, 0 mm | 4.18 cm2 | at x = +/-0.863 |
| push bar's lower brace / lower bar | OPP, 0 mm | 4.00 cm2 | the brace's top on the bar's underside |

- **Why the posts met the headrests.** The partition stood at a guessed
  y_fs + 0.38, through the headrests, whose rear face is at y_fs + 0.39.
- **The lowest corner did not build.** Its marks reached 0.794 m, and the
  door handles hang from 0.775 m.

**The fixes, each at its source:**
- **`INSET` (4 mm, twice the probe's window).** Rails end inside the outer
  posts, posts stand inside the rails' faces, and the middle bar stands
  inside the posts'.
- **The brace** moved under the lower bar.
- **The partition stands from the cabin `simple_car` now returns:**
  - 0.03 behind the seat backs' rear face;
  - `INSET` short of the door cards' inner face. At `hw - 0.13` its ends
    stood 2 mm past that face (`hw - 0.132`). Run 1 found no pair there,
    and the ends now stop short of the face whether or not a card stands
    at the partition's y.
  - Refused if it does not fit before the rear seat.

### Run 2: one pair

The rail's underside sat 2 mm over the body's floor pan: OPP, 333.56 cm2.
- **Why.** The floor slab is 22 mm thick, and the pan lies 12 mm under its
  top. A 10 mm sink therefore stood the rail 2 mm over the pan.
- **The fix.** It sinks by `INSET`: 8 mm over the pan, 4 mm under the top.
  The console does too.

### Run 4: the draw calls

After the kit's rename into the car's part family (below), every build
exports six primitives, five visual and the collision proxy: `Car_Body`,
`Car_painted`, `Car_trim_rubber`, `Car_Interior`, `Car_glass` and
`Cruiser-colonly`. Run 1 exported seven: `Cruiser_Car_painted` too.

## Between the corners: 51 sizes, both liveries

Corners alone have missed pairs before: the getaway van's chassis, Zoo
1.83.0. `pair_sweep.py` builds every centimetre of height from 1.50 to 1.66
m, at the lowest, default and highest width and depth, through the census's
build path.

| livery | output | builds | pairs | did not build |
|---|---|---|---|---|
| `black_white` | `sweep_black_white.txt` | 51 | 0 | 0 |
| `white_blue` | `sweep_white_blue.txt` | 51 | 0 | 0 |

- **Every build is 3,476 tris.**
- **The livery reached the recipe.** Each output's "[cruiser] livery="
  lines name its livery 51 times.
- **The "form None" on every "[sweep]" line is wrong.** The instrument read
  the module's params, where a slot's form does not live. The script beside
  this README no longer prints it.

**The marks' scale, black_white**, from the recipe's own lines:

| height | the marks' scale |
|---|---|
| 1.50 m (the genome's min) | 0.92 |
| 1.51 m | 0.93 |
| 1.52 m | 0.94 |
| 1.53 m | 0.96 |
| 1.54 m | 0.97 |
| 1.55 m | 0.99 |
| 1.56 m and above | 1.00 |

- **The scale depends on height alone:** three builds a height, one at each
  width and depth.
- **The default, 1.578 m, is full size.** The refusal floor,
  `MARK_SCALE_MIN`, is 0.8.
- **`white_blue` is 1.00 at every size.** Its stripe needs 0.22 m to the
  black-and-white's 0.24.

## The kit's faces, without Blender

`tests/test_cruiser.py::test_no_two_kit_faces_share_a_plane` is the
census's check for boxes. It runs the kit at all 27 genome corners, through
the test's own layout and cabin.

**It fails without the fix** (`kit_faces_before.py`, `kit_faces_before.txt`):
- **Before the census:** 810 coincident face pairs over the 27 corners, 30
  at each.
- **As shipped:** 0 at every corner.
- **The kit as it stood** is `cruiser_forms_pre_census.py`. It was rebuilt
  by reversing the census's edits, its relative import made absolute.

**Two instruments, two counts.** The test counts face pairs and the census
counts object pairs, so 30 here and 6-7 kit pairs there are the same
defects read at two granularities.

## The draw calls: the kit was a sixth mesh

`bpylayer/merge.py` packs a module's parts by `partnames.family` (the name
before its first underscore) and material.
- **The first build** named the kit `Cruiser_Kit` and `Cruiser_Lens_*`.
  Those are a family of their own, so the export carried two meshes on the
  one painted material, where the van carries one.
- **The comment beside the kit's colours already said** "no draw call of its
  own". It said it before it was true.
- **Renamed `Car_Kit` and `Car_Lens_*`:** five meshes, one a material.
  `test_the_kit_merges_into_the_cars_painted_mesh` pins the family.

## simple_car's own cars, unchanged

The cruiser needed four things from `simple_car`:
- a `form` argument;
- `car_forms.SEDANS` where it decided sedan details;
- one hoisted moulding line;
- its door, moulding and cabin values, returned. Each is computed once and
  used by the faces it describes.

Every one is meant to change nothing for the street's cars. **Measured
rather than assumed:**
- **What was built.** `car_hashes.py` builds each street style (sedan,
  coupe, hatchback, suv) at three slots, through `dna.resolve_module_plan`
  with `body_style` set. It does this in the shipped 1.85.0 tree
  (`car_hashes_1850.json`) and the changed one (`car_hashes_1860.json`).
- **What was hashed.** Every vertex at 1e-6 m, and every face.
- **The result** (`compare_hashes.py`, in `compare_hashes.txt`): 12 builds,
  200 meshes, 0 differ, and the attachments are identical.
- **The control.** The same style at two sizes hashes differently, so the
  hash can move.

## The frames

`tools/preview_specimen.py`, eye 1.7 m, 8.5 m out, the default slot:

| frame | what it shows |
|---|---|
| `black_white_side.png` | the driver's side |
| `white_blue_side.png` | the driver's side |
| `white_blue_front.png` | front three-quarter |
| `black_white_rear.png` | rear three-quarter, the passenger side: the livery reads the right way round |
| `black_white_side_min.png` | the lowest slot, marks at 0.92 |

**The light bar is red on the driver's side from every angle.** Which
livery is the default is the walker's to choose.

## Not settled

- **Not in a level.** Lot's responder slot is a hand-set 2.0 x 5.4 x 1.5 m
  (`lot/site_responders.py:59`, "not derived: Zoo has no cruiser species
  yet"). It now can be derived.
- **Not priced in a frame.** The cost is five meshes and 3,476 triangles a
  car. How many a level carries is the gameplay layer's to say.
- **The test's cabin is an approximation.** `_interior` reads
  `simple_car`'s literals, which a source test pins. The real cabin is only
  in Blender, where the census and the sweep read it.
