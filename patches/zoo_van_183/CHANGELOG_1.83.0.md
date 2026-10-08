## [1.83.0] - the getaway van after the walker's first look: a deeper header, a chassis, and the ghost of SKEEVY'S WOODER ICE

### What the walker said

On 1.82.0's frames (2026-10-08): "Looks great". Three asks came with it:
- "the windows in the front feel proportionally a little too tall?";
- the ghost lettering 1.82.0's comps suggested -- "show me this";
- "flesh out the bottom of the truck a bit...like giving it a driveshaft
  and rear differential", with an underside comp.

Then: "this van is also going to be the foundation of a hero prop that
get's reused in multiple missions, so we can afford to really make it look
good". This release answers the three asks. A hero pass is next.

### The header

1.82.0 ran the glass to 0.10 m under the roof. The P30 comp carries about
0.25-0.30 m of body above its windshield. `van_forms.HEADER` (0.28) is now
the painted band between the glass's top and the roof, across the windshield
and the cab's sides. `layout` carries it as `z_head`, the windshield's rake
and the side glass follow it, and the bulkhead's door stops under it. The
header is now 0.196-0.230 of the glass's height, up from 0.07-0.08.

### The chassis

**1.82.0 had nothing under the body.** A person on the sidewalk saw the
street straight through the 0.6 m between the body and the ground.
`van_forms.chassis` plans what a step van carries there, as `core.prims`
primitives the recipe draws face for face. 28 parts:
- two frame rails, running into both bumpers;
- four crossmembers;
- leaf springs at both axles;
- a front beam axle through the tyres' hollows;
- the rear axle housing, with the differential's pumpkin, its cover and the
  pinion's nose;
- the engine's sump, and the transmission under the cab;
- the driveshaft, with a U-joint yoke at each end;
- an exhaust: downpipe, pipe, muffler, tailpipe and out under the road side
  ahead of the rear wheels;
- the fuel tank outboard of the kerb-side rail, on two straps.

It is all painted on the body's own material by `van_forms.chassis_rgb`:
black steel under road grime, and the exhaust in rust. That adds 512
triangles and no submission. No sun reaches under a van, so nothing chalks.

**What hangs from what.** The first build read 1-2 coincident pairs at the
genome's corners. The next read three more, all at sizes BETWEEN the
corners: a rail hung from the body's floor met the front axle's top within
1.8 mm near a 3.0 m slot. The floor (`z_sill`, 1.5 r) and the axle (about
0.975 r) part as the slot's height moves the wheel's radius. The rails now
stand on the axle (`RAIL_ON_AXLE`), as rails stand on springs, and so do the
driveshaft and the exhaust. What reaches up into the body runs from the
floor.

**`prims.rod` gained `phase`,** as `prims.cyl` has. A level 6- or 10-sided
pipe at phase 0 has a facet flat on top and one underneath, and the
exhaust's elbows shared them. At `pi / (2 * sides)` no facet is square to an
axis. Every existing caller passes no phase and builds byte for byte as
before.

### The ghost, variant 1 -- the walker's to judge

The van ran as a water-ice truck, SKEEVY'S WOODER ICE, lettered in vinyl.
The crew peeled the vinyl off. The paint under the letters never saw the
sun, so the old name stands in the chalked side as deeper black -- the way a
removed decal ghosts on every faded van. That is the finish's own physics:
the letters are darker than the paint around them, never lighter.

**One image under the same paint.** `van_forms.ghost_art` paints a 1024 x
512 image, 3.6 x 1.8 m on the box's sides. It is white, with the letters in
`GHOST_INK` (a linear factor of 0.55), set in the shop's own hand
(`smooth_type.OWNERS["shop"]`).
- **The material.** `materials.make_wear_textured_material` puts the image
  under the paint's `Wear` colour on one material: the same kind, the same
  submission count.
- **The mapping.** `geometry.set_uv_by` with `van_forms.ghost_uv` maps the
  box's sides by their (y, z), read the right way round from either side,
  and sends every other face past the art's clamped corner to its white
  margin.

**What the frames found.** The first frame's even letters read as
somebody's paint job, not a peeled name. `GHOST_PATCH` now fades each
letter's darkening unevenly, between 0.30 and 1, by a smooth noise.

**What the GLB was checked for.** Both the texture and COLOR_0 reach it: a
material that reads no vertex colour exports COLOR_0 white. The art ships
beside the GLB in `_tex/`, as the deli case's does, on a clamped, mipmapped
sampler.

**The art is named by its definition**, not by its bytes. A hash of the PNG
named one picture two ways, because zlib builds compress the same pixels
differently. A hash of the pixels still did, because system Python and
Blender's numpy round the resampled letters a little differently.

**Off unless asked.** A slot asks with `variant: 1` (`module_variants` 2),
and the walker chooses whether it becomes the van's default.

### Built

| | default (2.6 x 6.8 x 3.05) |
|---|---|
| validation | PASS, exact fit 2.600 x 6.800 x 3.050 |
| triangles | 5,372 (5,152 and 5,592 at the genome's corners) |
| submissions | five, plain or ghost |
| coincident pairs | 0 at six probed sizes, and by the census |

The budget moves 5,500 -> 6,000: the largest slot builds 5,592. It is a
regression detector, not a frame cost. The van's price is its draw calls,
and they have not moved.

### Tests

**`tests/test_step_van.py`: 390 pure, 9 built.** All 399 passed inside
Blender 5.1.1. New:
- the header, at every corner;
- `test_nothing_under_the_body_shares_a_plane`. It runs
  `prims.coincident_pairs` -- the probe's own measurement -- over the
  chassis and the body's planes at every centimetre of height from 2.90 to
  3.30 m, three lengths, two widths and three wheel counts. It is the test
  the corners alone could not be;
- no chassis part cuts a tyre;
- the driveshaft runs from inside the transmission to inside the pinion,
  the differential sits between the inner tyres, the tailpipe exits under
  the road side, and the tank is on the kerb side;
- the chassis's grime and the exhaust's rust;
- `prims.rod`'s phase: 0 is the rod it always was, and the turned rod has
  no facet square to an axis;
- the ghost: every line set, a white margin, the right way round on both
  sides, on the box and off the primer patch at every corner;
- built: the chassis on the paint face for face, and the ghost's art and
  COLOR_0 both in the GLB;
- built: the same file every build, plain and ghost.

The census note in `test_coincident_faces.py` records the redraw: same
species, same three builds, count unchanged at 363.

**Unproven until it stands in a level.** Nothing places the van yet (roadmap
206, phase 2). The walker has not chosen on the ghost, and no frame time
has been measured with the van in a level.

**Suite:** 3,782 passed, 396 skipped, 1 xfailed in 333 s (`python -m pytest -q`): 1.82.0's 3,625 and 393, and test_step_van.py's 157 new pure tests and 3 new built ones (skipped without Blender; all 399 of the file passed inside Blender 5.1.1).

