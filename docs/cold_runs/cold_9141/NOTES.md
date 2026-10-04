# Cold run 9141 -- doors to the street, pads and parking fields, untouched

gas_block_001, 9140's brief and seed (9080), on Level Factory 0.134.0, Lot
0.94.0, Zoo 1.58.0, Lux 0.66.0, Deli Counter 0.172.0, Pixelcoat 0.55.0,
exported with `--bake-lights`. **Zero interventions** (journal 0,
unattributed files 0, no retries, no observations). The same three
buildings (bank_tower_a02, freight_terminal_a01, gas_station_a03), now
each turned so its front door faces the through road.

Since 9140: Level Factory 0.132.0 (a building faces the street with its
front door), 0.133.0 and 0.134.0 (the pad's concrete and the field's
asphalt); Lot 0.93.0 (a concrete pad under each dumpster) and 0.94.0 (a
parking field in a gap between buildings, its driveway, its cars kept 12 m
from every enemy spawn).

    [export] light bake: 198 model(s) and 1554 primitive mesh(es) lightmapped,
             7 kept dynamic; 76 steady rig(s) baked, 17 failing left live;
             3463 users, 54.8 s in the editor

The shipped site: three fields (17 cars, 42 bay lines), three pads.

## Findings, 61 -> 63, attributed

Each changed finding set beside the builds that isolate a release
(`docs/findings/landuse_*_before_after.txt`, `fields_enemy_rule_check.txt`:
the same seeds, built by LF 0.132 alone, then with the pads, then the
fields with and without the enemy rule). Deterministic where it can be
checked: seed 9282's encounter read identically in three builds.

    by LF 0.132.0, the turned buildings (in the doors-only build already):
      LOT_PATH_END_OFF_DOOR        10 -> 5   walks to a doorless wall
      LOT_ENEMY_SPAWN_STANDOFF     1 -> 0    seed 9181
      LT_LOW_READINESS             1 -> 0    seed 9181
      LT_MAP_ENEMY_STUCK           seed 9282's gone
      LOT_SIGHTLINE_UNBREAKABLE    0 -> 1    seed 9181
      LT_OPEN_SIGHTLINE            0 -> 2    seed 9181
      LT_ROUTE_NEVER_COMPLETED     0 -> 1    seed 9181
      LT_MAP_BLIND_MAP, LT_MAP_TRIVIAL_ENCOUNTER, LT_MAP_INSTANT_CONTACT
                                   0 -> 1 each, seed 9282
      LOT_COVER_PLACED, LOT_ROUTE_COVER_PLACED
                                   0 -> 2 each, seed 9080: one piece, said
                                   by the greybox and the themed leg
    by the fields, without the enemy rule, and taken back by it:
      LT_MAP_INSTANT_CONTACT, LT_MAP_NO_REACTION_TIME, LT_MAP_OVEREXPOSED
                                   seed 9181 (9140 had all three too)
    by the fields, NOT taken back:
      LT_MAP_INSTANT_CONTACT       0 -> 1    seed 9080, the shipped one:
                                   first enemy shot 3.06 -> 2.86 s against
                                   a 3.0 s line, crew still first (2.47 s),
                                   survival 12.7 -> 13.7 s; no field car
                                   within 14 m of a marker, five kerb cars
                                   fewer (the driveways' cuts)
    NOT isolated:
      DISPATCH_FINDING             7 -> 8    seed 9080's art leg: "1 nav
                                   bridge link(s) were auto-added between
                                   the Deli Counter and Lot nav graphs
                                   (within 1.5m)". Informational; the
                                   shell-only builds run no handoff, and
                                   the shipped ground changed three ways.

The doors-to-the-street change is the larger mover, and it moves seed
9181 both ways: two open sightlines and an uncompleted route in, the low
readiness grade and a standoff out. 9181 was not the selected candidate in
either run.

## Land use (`tools/landuse_census.py`)

Seed 9080 against 9140: a door facing its road on 4 of 5 frontings (2 of 4
in 9140; the fifth is the corner building's side on the cross street);
parking 880 m2; pads 59.5 m2; remainder 60.6 % to 55.2 %, its largest
piece 10,915 to 9,664 m2.

## Price of the parking fields (`docs/findings/fields_price/`)

On/off on this package, Level Factory's fixed-station harness, 14 stations
x headings (52 compared), GL Compatibility, a quiet machine. "Off" is a
copy with every field node removed by `patches/lot_fields/strip_fields.py`;
the control is the same bytes run twice more, bracketing it.

    mean over headings          draws    median ms   GPU ms
    whole fields (on - off)     +52.0    +0.14       +0.08
      worst heading (extraction_14, yaw 90)
                                +258     +0.73
    cars only (17 cars)         +32.8    +0.15
      worst heading             +190     (max +1.55 ms)
    slabs + 42 bay lines        +19.1    -0.01
      worst heading             +68      (max +0.28 ms)
    control (same bytes)         0.0     +0.00/+0.01  -0.00/+0.02

On a 3.88 ms mean median frame, the fields cost 3.6 % of frame time and
5.6 % of draws, and tip one station (extraction_14) over the provisional
2,000-draw budget: 3 stations over with fields, 2 without. The cars are
the price -- about 11 draws a visible car -- and the stripes cost draws but
no frame time this harness can see.

**A VOID MEASUREMENT, KEPT.** The first "off" (`fields_b_VOID.json`)
stripped only `site.tscn`. The package loads `presentation/
lux.applied.tscn`, the Lux stage's re-save of the site, which keeps its own
copy of every node, so "off" read 0.00 draws different at all 53 headings
-- an instrument that could not see the change, not a free feature. The
strip now treats every scene that carries a field, and refuses a scene
missing any field car.

What a cheaper field would buy, for the walker to weigh rather than decided
here: the bay lines as one MultiMesh per field would take ~42 draws to ~3
and buy no measurable frame time; fewer cars (occupancy, or a cap per
field) is the lever that moves frame time, at the cost of fuller-looking
lots; a car module merged by material in Zoo would cut every car's draws,
kerb cars included (29 here), and is the general fix.

## Frames (`docs/findings/fields_frames/`)

From this run's walk copy (`patches/lot_fields/field_shots.gd`, written by
`make_shots.py` from the themed site's own `field_plan` and `yard_plan`):
each field from the street and from above, each pad from in front. Seen
here: the fields read as lots -- bay lines, cars nose in both sides of the
aisle, the driveway a gap in the sidewalk -- and the open-ground pebble
dressing lies thick on the aisles; the pads read as concrete under and in
front of the bins.

**RETRACTION (2026-10-03, cold run 9144's notes):** the stuck events said here to carry no
position always carried it, in `metadata.position`; these notes read Laser Tag's top-level
field, which 0.23.1 logged as (0, 0, 0) for every named event. Seed 9181's are 1,354 of 1,378
at one spot, six metres up inside `arena_a03`. Laser Tag 0.23.2 logs the real position.
