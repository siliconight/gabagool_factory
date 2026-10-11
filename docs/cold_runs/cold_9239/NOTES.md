# Cold run 9239 -- the dome on 9233's lot: the pipeline carried it, and the dome itself was wrong twice

**What it tested:** roadmap 229's species step, landed as Zoo 1.98.0,
Lux 0.75.0 and Deli Counter 0.208.0: a home's room hangs a flush-mount
dome a bay where it hung an office troffer. On 9233's lot
(restaurant_row_001, seed auto), whose one home room is the deli's
apartment hideout (two rows of three), priced against 9238's package.

**Result: 0 interventions, 0 stops, findings 123 as 9238's.** The domes
travelled the whole way: the site's lights manifest carries the hideout's
two rows as `dome` anchors (`b0/apartment_hideout_ceiling`, `_r1`, three
lamps each, 7 m apart), Zoo's fixture job for the deli placed six
`dome_fixture` hardware pieces hung from the ceiling and skipped none, and
the bake read 213 steady rigs and 29 failing where 9238 read 212 and 30 --
the hideout's bad troffer tube gone, because a dome is never chosen to
fail -- and 3,524 lightmap users where 9238 had 3,518, the six domes.

## Seen (`fixtures.png`; `fixture_frames.sh`, `tools/fixture_stations.py`)

Inside the hideout, 3 m off each row's first lamp, 9238 left and 9239
right. The LIGHT changed as meant: 9238's room is a cool, dim grey under
one bright white troffer, and 9239's reads warm throughout, walls and
ceiling a lamp-lit brown. **The FIXTURE did not:** each dome read as a
small dark disc on the ceiling with a knob hanging under it, not a lit
bowl.

**Measured, not guessed** (`dome_extent_probe.py`, this folder on the shipped
`lot/deli_a01/art/fixtures/deli_a01_fixtures.glb`): the canopy spans y
6.178 .. 6.200 (the ceiling at 6.2), the finial 6.092 .. 6.112 -- where the
bowl's bottom should be -- and the GLASS 6.178 .. 6.254, from the canopy's
underside to 5.4 cm ABOVE the ceiling plane, its normals averaging up. The
bowl pointed up into the ceiling. Printed in Blender 5.1.1
(`hemisphere_probe.py`, this folder): `geometry.add_hemisphere` -- "Upper
hemisphere shell (open bottom)" by its docstring -- keeps the LOWER half,
z -1 .. 0 at unit radius, faces down and out. 1.98.0 mirrored what it took
for an upper half downward, and so turned it up.

## The price (`price/`, 9238's package the control)

    measured control_1  53 headings  draws mean 2524 worst 5257  p95 median 5.34 ms
    measured glow       53 headings  draws mean 2529 worst 5269  p95 median 5.27 ms
    measured control_2  53 headings  draws mean 2524 worst 5257  p95 median 5.19 ms
    controls' spread, median over 53 headings: p95 0.13 ms, draws 0.0 (the noise floor)
    draws vs controls' mean: median 6.0  min 0.0  max 12.0
    p95 ms vs controls' mean: median -0.01  min -0.59  max +1.14

No frame time: -0.01 ms p95 at the median inside a 0.13 ms spread. But
**+6 draws at 24 of 53 headings** (12 at two, 0 at 19), exactly one per
dome, from stations all over the level. Read off the two fixtures GLBs:
9238's deli carried 91 troffers as 182 meshes (housing and diffuser, two
materials); 9239's carries 85 troffers and 6 domes as 170 + 18 meshes --
three a dome, because the canopy and the finial share a material but were
built as two objects, and the fixtures GLB is exported unmerged (a layer,
not a module: merging across fixtures would cost culling). So a dome cost
one draw more than the troffer it replaced wherever it was drawn.

## The fixes

Zoo 1.98.1 (`patches/patch_zoo_dome_fix.py`): the bowl laid at `rim -
|z|`, so it hangs below the rim whichever half the helper keeps, its rim
closed 4 mm inside the canopy so the finisher's normal recalculation has an
inside to face away from; the canopy and the finial one object. Built in
Blender: the glass from 3.7 cm down to -4.5 cm in the module frame under
the canopy's underside at 3.3 cm, faces down and out, two meshes; the
census 310 tris and 0 pairs at every corner. Cold run 9241 re-reads both:
the frames and the draws against 9238's package.

**Found on the way, and recorded rather than fixed:** `add_hemisphere`'s
four other callers -- `bollard`, `exhaust_fan`, `soda_cup` and `helmet` --
all place it as a cap on top, so each builds its cap hanging inside its
own body. Each needs its census and a frame; a roadmap item.

## What is evidence of what

- The light's look and the bake's numbers are the dome rig's (Lux 0.75.0)
  and the type's (Deli Counter 0.208.0); they stand.
- The fixture's look and the +6 draws are Zoo 1.98.0's and are superseded
  by 1.98.1, unproven in a level until 9241.
- One room on one lot. A residence-heavy lot is the look still owed.

## Instruments

- `price/`: the perf reports, `price.txt`, `vs_mean.txt`, `price_vs_mean.py`.
- `fixture_frames.sh` and `tools/fixture_stations.py`: the four frames; the
  sheet `fixtures.png`.
- `dome_extent_probe.py`, `dome_normals_probe.py`: where a fixtures GLB's dome
  glass sits against its canopy, and which way its faces point.
- `hemisphere_probe.py` (in Blender): which half `geometry.add_hemisphere` keeps.
- `dome_build_probe.py` (in Blender): one dome built through the census's path,
  its parts' heights and normals -- how 1.98.1 was checked before the census.
