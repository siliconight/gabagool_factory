# Which half `add_hemisphere` keeps (roadmap 232)

**The question.** Zoo's `geometry.add_hemisphere` documents an "upper
hemisphere shell (open bottom)". Cold run 9239 found the dome fixture's glass
hung up into the ceiling, and `docs/cold_runs/cold_9239/hemisphere_probe.py`
printed why: the helper keeps the LOWER half. The dome stopped depending on
the helper in Zoo 1.98.1. This folder asks what the helper does to its other
four callers, and whether the fix changes the dome. The fix shipped as
**Zoo 1.99.1** (`patches/patch_zoo_hemisphere_fix.py`).

Every measurement below is in Blender 5.1.1, Blender's world frame (Z up,
metres). "1.99.0" is an untouched clone of Zoo at 1.99.0; "1.99.1" is the
same clone with the patch applied as a draft.

## The helper (`half_probe.py`, `half_1.99.0.txt`, `half_1.99.1.txt`)

One hemisphere at the origin, radii (0.5, 0.5, 0.3).

| segments | rings | 1.99.0 z range | 1.99.0 vertices outside the radii | 1.99.1 z range | 1.99.1 outside |
|---|---|---|---|---|---|
| 10 | 6 | -0.3 .. 0 | 0 | 0 .. +0.3 | 0 |
| 12 | 6 | -0.3 .. 0 | 0 | 0 .. +0.3 | 0 |
| 14 | 7 | -0.3 .. 0 | **14, at radius 0.975** | 0 .. +0.3 | 0 |
| 20 | 10 | -0.3 .. 0 | 0 | 0 .. +0.3 | 0 |

The bisect pointed its plane normal down, and `clear_inner` clears the side
BEHIND the normal, so the upper half went. At an odd ring count no ring lies
on the cut plane, the bisect makes the rim's vertices new, and the helper
transformed only the sphere's own: the 14 new ones stayed at the unit
sphere's scale, 0.975 from the axis, nearly twice the radius asked for. The helmet's genome allows `segments` 12
to 32, so 14, 18, 22, 26 and 30 all reach it; a plan takes the genome's
default of 20 unless a prompt names a count.

## The callers (`caps_probe.py`, `caps_1.99.0.txt`, `caps_1.99.1.txt`)

Each species at its genome's default corner, planned through
`core.kit.plan_kit` and built through `bpylayer.build.build_module`, the path
a kit build takes. CROWN REACH is how far from the cap's own vertical axis
its topmost vertices lie: near 0 for a dome's pole, the full radius for a
flat top or a bowl's rim.

| species | cap part | 1.99.0 crown reach | 1.99.1 crown reach | 1.99.0 module height | 1.99.1 module height | slot height |
|---|---|---|---|---|---|---|
| bollard | Bollard_Pipe | 0.0830 | 0.0000 | 1.050 | 1.050 | 1.05 |
| exhaust_fan | ExhaustFan_Dome | 0.3500 | 0.0000 | **0.385** | 0.550 | 0.55 |
| soda_cup | Cup_LidDome | 0.0247 | 0.0000 | 0.240 | 0.240 | 0.16 + straw |
| helmet | Helmet_Shell | 0.1299 | 0.0000 | 0.161 | 0.161 | 0.16 |

Triangle counts are the same before and after for every part. The bollard
kept its height before because its cap hid inside it; 1.99.1 shortens the
pipe by the cap's rise so the crown lands at the top of the slot. The
exhaust fan stood at 70 % of its slot, because the build re-centres a module
but does not stretch it.

**Seen** in `caps.png`, rendered with `zoo/tools/preview_specimen.py`, 1.99.0
left and 1.99.1 right: the bollard was flat-topped and is capped; the fan's
hood was an open bowl around its drum and is a mushroom; the cup's lid was
flat and is domed around its straw; the helmet was an upturned bowl and is a
shell.

## The dome (`dome_same_probe.py`)

Built on both clones, `Dome_Canopy` (60 vertices, 84 faces) and `Dome_Glass`
(101 vertices, 101 faces) match vertex for vertex, and face centre and face
normal for face, to 0.01 mm. 1.98.1 lays the bowl by |z| and closes it,
so its shape does not depend on the half the helper keeps; that its
normals come out the same as well is measured here, not argued.

## The coincident-face census (`census_1.99.0.txt`, `census_1.99.1.txt`)

`zoo/tools/coplanar_census.py` on the five species, min, default and max
corners. On 1.99.0 it reproduced the rows of Zoo's
`tests/test_coincident_faces.py` for the three species that have one,
exactly, which is the control that it reads what the table recorded. On
1.99.1:

- **Unchanged:** the bollard's row, every triangle count, and the helmet and
  the dome, which stay at 0 pairs.
- **The soda cup's nearest cover** went from 0.21 mm to 2.0 mm. The cover is
  the distance along the pair's normal to the first other surface, and the
  0.21 mm was the hidden lid dome's bowl passing over the body and lip's
  pair. The nearest surface now is the lid's underside.
- **The exhaust fan's count** went from 3 to 4. At the default corner its
  one buried pair, the drum's foot on the curb at 1,725.46 cm2, is reported
  as two pairs of 1,150.31 and 575.15 cm2. Same parts, same area, same gap;
  no coincidence is new. Nothing here says why the probe splits it, and it
  was not chased.

## What is evidence of what

- The helper's half and the odd-ring vertices are measured on the helper
  alone (`half_probe.py`), before and after.
- The four species' caps are measured on builds through the kit path, at
  the default corner only. The min and max corners were built by the census
  and built clean of errors, but their crowns were not measured.
- Nothing in a level is evidence here. No job asks Zoo for any of the four
  species today: no level-factory job sets `roof_props_slots`, so roof props
  are never built, and no tool names a bollard, a soda cup or a helmet.
- **Not fixed:** the exhaust fan's hood is an open shell, so seen from below
  its inside faces are culled and the sky shows through the ring between the
  hood's rim and the drum. A camera on the street rarely sees the underside
  of a roof fan, and roof props are not built in levels, so it stays a note.
