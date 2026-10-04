## 0.94.0 - a parking field in a gap between buildings

Step 4 of `docs/proposals/LAND_USE_DESIGN.md` (open land gets a role, the
land-pressure guide's 5.4), agreed by the walker 2026-10-03; its second use,
and the one sized to move the remainder. A gap between two storefronts was
bare plate. In a suburban strip -- the guide's "broad gaps often occupied by
parking or circulation" -- it is the lot the customers park in.

`site_fields.plan_fields`: along each road with a sidewalk, on each side a
building fronts, the gaps between the fronting buildings' spans (and from
the road's drawn ends to the first and last) take one field each when they
hold it. A field is one module from common practice: a two-way aisle
(24 ft, 7.3 m) square to the road and 90-degree bays (9 x 18 ft, 2.7 x
5.5 m) both sides of it, so 18.3 m along the road, 1.0 m clear of the
buildings either side. Its driveway keeps 15 m (50 ft) from any junction,
sliding along the gap when it can. It is as deep as it can be, two to six
bays, while it stays clear of every drawn surface (separating axes), of
what stands, of the plate's edge, and no deeper than the buildings beside
it. Gaps on the lots on disk run 10-37 m (`patches/lot_fields/
gap_survey.py`).

THE DRIVEWAY is a new crosser kind in `site_streets.kerb_crossings`,
`driveway`: from the carriageway's edge to the back of walk, so it drops
the one kerb it crosses and never meets the centre line -- no crosswalk, no
stop bar -- and `site_furniture` gives it none of a crossing's corner
pieces (no hydrant, bin or blade post; the test's control is a walk cutting
the same kerb, which gets all three). The kerb lane's bays already skip
every cut, so no kerb car parks across it.

THE CARS: a seeded share of the bays (`site_parking.OCCUPANCY`, a SHA-1 of
the bay) holds one of `site_parking.CARS`, nose in, as a cover record --
the same collision piece a kerb car is, standing in the cover planner's
measurement. A car keeps `site_cover.MARKER_CLEARANCE` from every marker,
1.5 m from every door's approach point, and `ENEMY_CLEAR` (12 m) from every
enemy spawn -- see below for why that last rule exists.

The field is a `parking` slab (`field_slabs`, `field_<i>`) at the road's own
height, so the asphalt runs from the carriageway through the dropped kerb
into the field, skinned from `ground_skins["parking"]` (Level Factory
0.134.0: the theme's asphalt). Its bay lines are the road's paint, drawn as
the road's marking quads (`fmark_<n>_bay_line`) and carried in
`<site>.markings.json`. `tops` declares the slab, `site_steps` walks on it,
the census counts it as `parking`. `assemble` plans the fields BEFORE the
street's furniture, so lamps, trees and kerb bays step round the driveway,
and the pylons, dumpsters and pads planned after keep off the fields. The
gameplay records the fields, their cars and the cars' `cover_<i>` nodes
(`field_plan`).

MEASURED (`patches/lot_fields/before_after.sh`, `docs/findings/
landuse_fields_before_after.txt`), the nine candidates of 0.93.0's
before/after, built fresh by this:

    fields a lot          1-4 (23 in all, every one six bays deep)
    parking               288-1,176 m2 a lot
    cars in the fields    6-30 a lot (before the enemy rule)
    remainder             down 1.5-6.1 points; gas_block_001 seed 9080
                          59.90 % to 55.17 %, its largest piece
                          10,544 to 9,664 m2

A REGRESSION FOUND, AND ANSWERED BY A DERIVED RULE. The first build had no
enemy rule. On gas_block_001 Laser Tag added four findings, every marker
unmoved. Three were seed 9181's: four field cars stood 4-10 m from Enemy_0,
the crew's survival fell from 70.6 s to 5.5 s and the enemies fired first
(1.9 s against the crew's 4.0 s). `site_cover` already states the
principle -- cover is biased to the crew's end, because a piece at the
other "hands the enemy the wall to hold" -- and the field's cars ignored
it. `ENEMY_CLEAR` = Laser Tag's enemy speed (4.0 m/s) x its instant-contact
window (3.0 s): all the ground an enemy reaches before the gate calls the
contact instant. Rebuilt with it (`patches/lot_fields/enemy_rule_check.sh`,
`docs/findings/fields_enemy_rule_check.txt`), seed 9181 has 19 field cars
not 25, the crew fires first again (2.93 s, the enemy 3.19 s; 3.13 / 3.66
with no fields), route progress 0.61 (0.65 with no fields, 0.35 without the
rule), and OVEREXPOSED, NO_REACTION_TIME and INSTANT_CONTACT are gone.

NOT answered, and said: seed 9181's survival recovered to 37.3 s, not to
70.6 s, and it gained LT_MAP_ENEMY_STUCK, whose events carry no position.
Seed 9080's INSTANT_CONTACT stays: no car there is within 14 m of a marker
and the rule removes none, the first enemy shot moved 3.06 to 2.86 s
across the 3.0 s line, the crew still fires first (2.47 s), and its
survival rose 12.7 to 13.7 s; the build also lost five kerb cars to the
driveways' cuts (34 to 29), which is the other thing that changed on its
ground. Seed 9282 read identically in all three builds -- the bot sim is
deterministic, so the differences above are the geometry's. Findings
43 / 43 / 42 to 45 / 42 / 42.

`tests/test_site_fields.py`: one field centred in a 30 m gap, four bays to
the buildings' backs (literals); none in a 17 m gap; none within 15 m of a
junction and one when the junction moves; the plate's edge, a walk and a
standing piece bound its depth; the driveway drops one kerb, is no
crossing, paints nothing and takes no kerb bay; it gets no corner
furniture where a walk does; no car within 12 m of an enemy, and only
those removed; cars nose in, inside the field, clear of a marker, the same
twice; bay lines inside the field; and a field is drawn, declared where it
is drawn, walked on, painted, counted and in the markings manifest. The
kerb probe's own `assemble` test now plans a field and its manifest
carries `bay_line`.
