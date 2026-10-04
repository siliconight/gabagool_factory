## 0.93.0 - a concrete pad under each dumpster

Step 4 of `docs/proposals/LAND_USE_DESIGN.md` (open land gets a role, the
land-pressure guide's 5.4), agreed by the walker 2026-10-03; its first use,
the one the site already implied. 0.90.0 stood a dumpster on the bare
plate, and a real one stands on a pad: it is heavy, the truck's forks drop
it on every lift, and the ground in front of it is where the truck works.

`site_yards.plan_yards` gives each dumpster a pad, from the wall's face
outward, centred along the wall on the container and never past the
wall's ends: `PAD_ALONG` 3.7 x `PAD_OUT` 3.0 m (a single-container
enclosure, about 12 x 10 ft) and an `APRON` of 3.0 m beyond, where a
front-load truck's forks reach -- the commonly published figures, read as
typical. It shrinks, apron first in 0.5 m steps, then width down to 0.3 m
beyond the container's sides, until it is clear of every surface Lot
already draws (`site_surfaces.tops`), of the other buildings by 0.3 m, of
what already stands but its own dumpster, of the other pads, and inside
the plate by 0.5 m; of the sizes that fit, the largest area wins. Overlap
with a drawn surface is decided by separating axes, not bounding boxes, so
a diagonal walk passing a pad's corner does not cost it its apron. A
dumpster whose pad cannot cover its own footprint is said
(`LOT_YARD_NO_ROOM`) and stands on the plate as before.

The pad is a `yard` slab (`yard_slabs`, `yard_<i>`), a courtyard's shape,
at `YARD_THICK` -- the courtyard's tier, since a pad never overlaps another
drawn surface. Drawn in the greybox at `YARD_COLOR` and skinned from the
spec's `ground_skins["yard"]` (Level Factory 0.133.0 names the theme's
concrete). `site_surfaces.tops` declares it, so dressing stands on it;
`site_steps` walks on it (`yard_`); the land-use census counts it as `yard`.
`assemble` plans the pads right after the dumpsters and records them in the
gameplay (`yard_plan`), where `tools/landuse_census.py` reads them.

MEASURED (`patches/lot_yards/before_after.sh`, `docs/findings/
landuse_yards_before_after.txt`): the three briefs of Level Factory
0.132.0's before/after (gas_block_001, club_block_014, crossroads_9600),
three candidates each, built fresh by this and compared with 0.92.0's
builds of the same seeds. Every one of the 27 dumpsters got a pad, none
said no room, 25 at full depth (3.37 x 6.0 m, clipped at the wall's end
because a dumpster stands 0.6 m in from its corner) and two at 5.5 m.
That is 58-60 m2 a lot, and the remainder falls by 0.25-0.32 points
(gas_block_001 seed 9080: 60.22 % to 59.90 %). Small, and said as small:
the remainder is the ground behind and around the row, not under the bins,
and the parking fields are the use sized to move it.

Findings 43 / 45 / 43 to 43 / 43 / 42, none gained. The three lost are
Laser Tag's bot-sim verdicts (club_block_014 seed 9282's TRIVIAL_ENCOUNTER
and LOW_COVER, crossroads_9600 seed 9701's TRIVIAL_ENCOUNTER) and are NOT
attributed to this: a pad is 14 mm of flat concrete and stands in no
sightline. The bots' outcomes on those seeds move run to run.

`tests/test_site_yards.py`: a pad runs from the back wall under the
dumpster and out past it, clipped at the wall's end (literals, not module
constants); its apron gives way to a walk, and a walk over the container's
own front leaves it none, said; a diagonal walk off its corner is cleared by
shape, and moved 0.1 m in, is not; the plate's edge and a neighbour bound
it; a row of buildings gets a pad each, none overlapping, the same twice;
and a pad is drawn, declared where it is drawn (`test_site_surface_tops`'s
own check), walked on and counted.
