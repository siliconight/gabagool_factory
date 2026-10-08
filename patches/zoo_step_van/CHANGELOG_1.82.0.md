## [1.82.0] - the getaway van: a P30-style step van, matte black gone chalky, that has been on many jobs

### What the walker asked for

The walker, 2026-10-07: "a Box Truck. Like a Chevrolet P30. Matte
Black....faded, with patina, like a worn in truck...that's been on many
jobs.... Our very own 'millenial falcon'", with four photographs: a white
water-ice step van, a white P30, a dark grey riveted food truck and a
near-black faded step van. Then: "location of the getaway vehicle should be
the same as the missions spawn point. you spawn, do the job, then return to
the car". The van is where a level starts and ends (roadmap 206). The
photographs were read for format only and none is stored;
`docs/reference/GETAWAY_VAN_COMPS.md` at the factory root describes them.

### `step_van`, a species of its own

The brief, by the authorship guide's three questions:
- **What it is for.** Getting the crew and the score away. It stands at the
  kerb where the mission starts, and the job ends when the crew is back in
  it.
- **Who touches it.** The crew, through the kerb-side door, every job, and
  the driver behind the wheel.
- **What it is made of.** A P30-style step van: a tall box on a chassis, a
  flat-nosed cab with a raked two-piece windshield, round headlamps in
  square bezels with amber lamps over them, heavy black bumpers, tall
  mirrors on tube arms, amber clearance lamps along the cab roof, dual rear
  wheels on steel discs, and rear doors. It carries no maker's mark and no
  lettering.

**Laid out in pure Python** (`core/van_forms.py`) and built by
`recipes/step_van.py`:
- **The box** is one loft of round-edged sections from the bulkhead to the
  rear doors. Its bottom rises over the rear axle, so the arch is in the
  silhouette.
- **The cab's lower body** stands `CAB_INSET` (4 mm) inside the box, which
  gives the seam a P30's cab makes against its body. Its bottom rises over
  the front axle.
- **The cab's upper is open** (simple_car 0.79.0's rule: a solid behind
  glass reads as a painted wall). It has a roof slab, a raked windshield
  frame, B-pillars and glass in every opening. Behind the glass sit a dash,
  an engine cover, two seats, a wheel and the bulkhead's door into the box.
- **The slot is exact.** The width runs to the mirror heads' outer faces,
  the depth to the bumpers' and the height to the clearance lamps' tops. A
  longer slot is a longer box behind the same cab.

### The finish is the truck's history

One material carries the paint. `paint_matte` is a new kind: roughness
0.86, a dielectric, with no skin pack in any theme, because the colour is
the van's own. The paint is white, and its colour goes per corner into
`Wear` through `geometry.tint_wear_by` (new: `tint_wear` with a colour that
varies over the part) and `van_forms.finish_rgb`. Four layers sit over the
plan's colour:
- **Sun.** Near-black low down and in the shade, chalked toward a warm
  charcoal on the roof and the upper panels, and mottled.
- **Dust.** Road dust on the lower third.
- **Rust.** A bloom around each arch and along the rocker, on the sides
  only.
- **Primer.** One filled dent in grey primer on the kerb side's rear
  quarter, which is the side the crew walks up to every time.

The finish is deterministic from position alone, so the crew's van is the
same van in every level.

**What the first frames got wrong.** The first draft chalked the sides
linearly up to the roof, and the van read as cloudy mid-grey. `SIDE_SUN` now
keeps the sides black first and faded second, as the walker ordered the
words: half the side measures darker than 0.06 linear, and the roof about
1.5 times that. The primer drew as a blocky rectangle, because colour can
only change where there are vertices. The box now has 0.20 m stations and
ten side rows instead of 0.28 m and seven, and the patch's edge is noisy.

**The genome is read.** The body's kind and base colour are the plan's, so
editing the genome repaints the van. The chalk derives from the base: full
sun takes the paint `CHALK_T` (0.25) of the way to `SUN_BLEACH`. At the
genome's colour that is exactly the chalk the frames were judged at.

### Built

At the default 2.6 x 6.8 x 3.05:
- PASS, with an exact fit (2.600 x 6.800 x 3.050).
- 4,860 triangles against a budget of 5,500 (4,640 and 5,080 at the
  genome's corners).
- **Five submissions:**
  - `M_Van_paint`, the body;
  - `M_Van_painted` (lamps, plate, brightwork and wheels), one material
    with each part's colour in `Wear`;
  - `M_Van_rubber` (tyres and black trim);
  - `M_Van_interior`;
  - `M_Van_glass`, blended.
- **0 coincident pairs** at six sizes (the corners and three between them)
  by `tools/coplanar_probe.py`, and by `tools/coplanar_census.py`.

**The van stood 10.3 mm off the ground.** `_lathe_x` puts a tyre vertex
every 360/seg degrees from the axle's level. One points straight down only
when the segment count is a multiple of 4, and at the default 14 the lowest
stands at 0.975 r. With the axle at r, the van built 3.040 m tall in its
3.05 m slot, and 2.890 in 2.9 and 3.289 in 3.3. Centred in its slot, that
would float it about 5 mm. `van_forms.axle_height` now derives the axle
height, and the built fit test fails at all three sizes with it reverted.
`simple_car`'s default of 12 puts a vertex at the bottom, so its shipped
wheels touch the ground. The same arithmetic would float it at any count in
its range that is not a multiple of 4.

**The probe found 10-12 coincident pairs a build first.** Each was moved at
its source:
- the seat backs flush with their bases, and the steering column;
- the engine cover's bottom and the dash's on one plane (96 cm2);
- the grille bars' backs 2 mm off the grille's face (380 cm2), and the rear
  door seams' backs 2 mm off the tail lamps' and the plate's. The probe's
  window is <= 2.0 mm, so a fix to exactly 2 mm still read;
- the B-pillar's face 2 mm off the rear door seam, where the seam runs into
  the lower body (5.2 cm2);
- the cab roof. It was first shifted (-4, +4) mm, exactly along its own
  45-degree facet, which made two 20.47 cm2 same-facing pairs.
  `CAB_ROOF_INSET` and `CAB_ROOF_RISE` derive a 12 mm shift at 120 degrees
  that clears every facet by at least 3.1 mm.

**Also.** `.gitignore` gains `_coplanar/`, the probe's default output
directory, which stood loose in the repo after the van's probes.

### Tests

**`tests/test_step_van.py`: 233 pure, 6 built.** The 6 built tests passed
inside Blender 5.1.1. With `axle_height` put back to r, the 3 fit tests
fail. None of them can be collected on 1.81.0, where the module does not
exist. They cover:
- the slot exact, and the parts in a step van's order, at the genome's 27
  corners;
- the wheels in their arches, and the tread on the ground at every wheel
  count;
- the crew's door wider than the crew (two of Deli Counter's 0.35 m radii);
- the finish black first and faded second, rust low and never on the roof,
  the primer on the kerb side only, the same van every time, and the
  genome's colour as the paint;
- `paint_matte` matte and a dielectric, and the recipe read as source (one
  paint material, in the plan's kind and colour);
- a `MEASURED` record of the six probed sizes;
- built: PASS and an exact fit at three sizes, five submissions with one
  paint, the paint in the vertex, and the same file every build.

**The species is registered** in:
- `test_genome.py`;
- `test_theme_style_resolution.py`, whose count goes from 93 to 94. Its
  `delco` row is a copy of its `default`, because `theme_style` returns None
  rather than falling back, and the count test said so;
- `test_coincident_faces.py`, whose census goes from 360 builds to 363 after
  `tools/coplanar_census.py --species step_van` ran in Blender 5.1.1: "3
  builds, 0 with coincident pairs, 0 that did not build" (4,640 / 4,860 /
  5,080 tris). The first full suite failed on exactly that line.

It is not in `test_material_options_closed.py`. The genome offers only
`paint_matte`, and the trim's `metal_painted` is a constant in the recipe,
as the display case's aluminium frame is. The first draft also offered
`metal_painted`, which the recipe would have ignored.

**Unproven until it stands in a level.** Nothing places the van yet. Lot
must park it at the spawn (roadmap 206, phase 2), and a cold run must show
it. The walker has not yet seen these frames.

**Suite:** 3,625 passed, 393 skipped, 1 xfailed in 318 s (`python -m pytest -q`): 1.81.0's 3,388 and 387, test_step_van.py's 233 and 6 (built, skipped without Blender; the 6 passed inside Blender 5.1.1), and 4 more in the tests that sweep every species.

