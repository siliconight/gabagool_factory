# Cold run 9140 -- the day's stack, untouched, with the lights baked

gas_block_001, 9139's brief and seed (9080), on Lot 0.92.0, Zoo 1.58.0,
Lux 0.66.0, Level Factory 0.131.0, Deli Counter 0.172.0, Pixelcoat 0.55.0,
exported with `--bake-lights`. **Zero interventions** (journal 0,
unattributed files 0, no retries, no observations). The same three
buildings as 9135-9139 (bank_tower_a02, freight_terminal_a01,
gas_station_a03).

Since 9139: Zoo 1.55-1.58 (turning grill parts, churning slush, swaying
crowns, the heat lamp, the dumpster); Lux 0.63-0.66 (the heat lamp's rig,
the pole lamp beside its pole with its shadow bias, the lightmap that
follows the level's state); Lot 0.88-0.92 (walks to real doors, landings,
no walk between buildings, the dumpsters, the land-use census); Level
Factory 0.129-0.131 (moving parts, wind, `export --bake-lights`).

## The bake, in a cold run for the first time

    [export] light bake: 193 model(s) and 1370 primitive mesh(es) lightmapped,
             7 kept dynamic; 77 steady rig(s) baked, 17 failing left live;
             3263 users, 57.1 s in the editor

The package's walk copy, through Lux's own calls (`patches/lightbake_probe/
runtime_switch_probe.gd`), overhead / station front / street, luminance and
draws:

    baked at load    0.153 / 2,614   0.166 / 1,344   0.097 / 1,575
    real time        0.156 / 3,253   0.169 / 1,429   0.091 / 1,960
    power cut        0.119 / 2,401   0.069 / 1,249   0.078 / 1,459
    power back       0.153 / 2,615   0.165 / 1,344   0.097 / 1,576

## Findings, 51 -> 61, attributed

    LOT_PATH_END_OFF_DOOR      0 -> 10   by code: Lot 0.88.0 began saying a
                                         walk that meets no door (0.91.0
                                         stopped drawing it); across the
                                         three candidates
    LT_MAP_TRIVIAL_ENCOUNTER   1 -> 0    seed 9080
    LT_MAP_ENEMY_STUCK         3 -> 2    seed 9080's (8 events) is gone
    LT_MAP_PLAYER_STUCK        2 -> 3    seed 9080 gained one (1 event);
                                         9181 2,156 -> 649; 9282 263 -> 282
    LT_LOW_READINESS           0 -> 1    seed 9181, grade FAIL (48)

The selected candidate (9080) reads better than 9139: its enemy-stuck and
trivial-encounter findings are gone and its player stuck once.

**NOT ATTRIBUTED: seed 9181's route.** The bot walked 51 % of the route on
average against 86 % in 9139, finishing 8 % of runs in both, and the
readiness grade is a FAIL. Its stuck events carry no position (every one
reads (0, 0, 0) in `lasertag.report.json`), so the instrument cannot say
where it sticks, and the candidate is one where the crew comes under fire
2.1 s in and dies around 6 s, in both runs -- how far the bot gets before
dying is a noisy number there. Suspects, unproven: the three dumpsters
(new solids) and the walks no longer drawn. 9181 was not the selected
candidate. Worth an instrument that records where a stuck happens before
anything is concluded.

## Land use, before step 2 (`tools/landuse_census.py`)

The shipped candidate: remainder 61 % of the plate, coverage 17 %; the
through road's building line spreads 13 m, and two of its three fronting
buildings have a door facing it. This is the "before" for Level Factory
0.132.0 (doors to the street).
