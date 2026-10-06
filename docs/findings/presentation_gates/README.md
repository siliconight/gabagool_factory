# The presentation gates: one read of sixteen, a gate that cannot pass, and furniture over stair holes

Found 2026-10-06 while cold run 9187 ran, checking roadmap 177 ("a gate has
printed FAIL on five consecutive cold runs and nobody read it") against the
runs since.

## What the job log says, and what produced it

Every cold run from 9164 to 9187, every one counted at 0 interventions, ends
`presentation_compose` the same way:

    [compose] z-fight gate [OK]: 0 coplanar pair(s) across 63 solids
    [compose] circulation gate [FAIL]: 0 prop conflict(s) across ? circulation volume(s)
    (exit=6 ...)

- **The constant 63 is one building.** The job composes the mission's own
  shell and then every building of the picked lot. In 9187 that is 16
  composes: deli_a01, twelve Empties, office and rail_station_a02.
- `job.log` keeps only the LAST command's lines. Here that is
  gs_empty_rowhome_l, whose package has 63 solids on every run that draws it.
- The exit code is advisory by design (`exit_advisory`), so the job records
  SUCCEEDED.

## Level Factory reads one manifest of sixteen

`adapters/presentation/__init__.py` `normalize_validation` takes
`next(p for p in output_paths if p.name == "portable_resource_manifest.json")`
over the sorted outputs. That is `lot/deli_a01/`'s manifest. Its closure,
placement and z-fight branches never see the other fifteen.

9187's validation record holds one `PRESENTATION_ZFIGHT`: "203 coplanar face
pair(s) across 761 solids", deli_a01's. The per-building summaries
(`lot/*/compose.summary.json`) say three buildings fail:

| building | z-fight | recorded |
|---|---|---|
| deli_a01 | 203 pairs / 761 solids | yes |
| office | 121 / 422 | **no** |
| rail_station_a02 | 117 / 397 | **no** |
| the twelve Empties | 0 | -- |

`normalize_validation` has no circulation branch at all, so no circulation
result has ever reached a finding.

## The driver prints the circulation gate from the wrong level of its schema

With a dressing layer and a greybox, Deli Counter's manifest writes
`circulation_check = {"ok", "shell", "dressing"}`. That is two arms and a
combined verdict, with no `conflicts` or `volumes` at the top.
`run_presentation_compose.py` prints `len(circ.get("conflicts"))` and
`circ.get("volumes", "?")`, which is "0 ... ?" on every building. The FAIL is
the combined `ok`.

## The dressing arm cannot pass since the covers were merged

`circulation.check_dressing` boxes each NODE of the dressing GLB. Zoo merges a
building's covers per side per material (1.68.0, roadmap 180). On
gs_empty_rowhome_l, 9 nodes carry 109 covers, and each concrete node's box is
the whole building, about 6.7 x 7.1 x 12 m.
- Every doorway volume lies inside those boxes.
- The doorway allowance (`DOOR_TRIM_PEN`, 0.12 m) assumed a thin strip hugging
  the aperture.
- So every building with covers fails: 9, 48, 28 and 27 conflicts on the four
  measured (`cover_components_9187.txt`).
- The dressing layer is non-collision by construction (Zoo's `dress_cover`;
  the build record says `"collision": "none"`).

**Per-part boxes restore what the gate was written against**
(`cover_components.py`):
- Position-welded, index-connected components of each node's mesh give
  196 to 249 parts per building.
- The largest is a 5.42 m downspout; nothing is building-sized.
- Against the parts: **0 conflicts on all four buildings.**
- **The positive control:** a 1 m crate planted in a doorway is caught,
  penetration 0.95.

**Refuted first, kept.** Index connectivity without welding returns one
component per FACE, because faces carry their own vertices for split normals
and UVs. That gave 1,452 planes on gs_empty_rowhome_l. A plane has zero
thickness, so `_pen` can never flag it: a gate that cannot fail, reading 0
for the wrong reason.

## The shell arm: a false positive and a real defect

DC's own props, read from the greybox by `surface_roles` role `prop`:
- **office** `stair_guard_back_10` is 0.26 m inside `office_stair_0`. The
  mission shell's `stair_guard_back_15` is 0.34 m inside its stair.
  - Stair guards come from `stairwell.stair_guards`, baked as volumes named
    `stair_guard_{kind}_{k}`. Every volume defaults to role `prop`.
  - A guard stands at its own stair's hole edge by design.
- **deli_a01** `counter_island_upper_hall_2` is 0.8 m inside `deli_stair_up`.
  **This one is real.**

## Furniture over stair holes (`furniture_over_holes.py`)

A volume that overlaps a slab opening on its own storey, by
`stairwell.slab_openings` (the holes the builder cuts). Stair guards are
reported apart and number 0: they stand beside holes, not over them.

**57 volumes in 17 of 146 shells** (`furniture_over_holes.txt`). What each
means varies, and a census cannot tell them apart:
- **The deli family (a01, a02, a03), the same in all three.**
  - `counter_island_upper_hall_0` is 41% over the up-stair's hole at its
    ARRIVAL end, y 6.18 to 6.98. That part of the hole is the discharge plate,
    so the island stands across about 0.5 m of the flight's 1.6 m width where
    a climber steps off.
  - `counter_island_upper_hall_2` is 54% over the hole above the flight's
    foot: a counter half over the stairwell.
  - `crate_stack_stairwell_1` is 13% over the basement stair's hole.
- **cbp_town_finale, final_stand:** tables, chairs, cartons and desks 100% over
  openings on storeys 1 and 2. Not looked at in a frame: floating, or an
  authored opening the census misreads.
- **foundry_heist_vertical:** `skylight_box` 54% and `roof_ac_block_a` 52% over
  roof openings. Possibly by design.
- **The parking garages:** a column half over the ramp opening.

## Over a hole, or in a stair's walk (`stale_pieces.py`, `stale_pieces.txt`)

**The same question, plus a stair's walk.** That is a flight's rectangle on
the storey it climbs from, and its landing rects.
- **64 pieces in 18 shells:** 55 over a hole, 17 in a walk, 10 both.
- **Refuted first, kept:** the first run filed every landing rect under the
  stair's lowest storey. `stair_endpoints` carries no storey: "lower" is the
  lowest and "upper" the highest.

**Two causes the census cannot tell apart.**
- **Stale.** The presets, `seed_cover` and `furnish` each clear a piece of
  the stairs when they place it, and each is idempotent by name, so a piece
  placed before a stair changed is never asked again.
  - The deli islands date from Deli Counter 0.80.0. The stair's default run
    has lengthened since.
  - **twin_a01's two wardrobes were put over its widened hole by 0.190.0**,
    0.12 m2 each, measured on 0.189.0's spec and on 0.190.0's. Its swept gate
    passed it: walking is unaffected, and nothing checked pieces against
    openings.
- **Unseen.** `furnish` and `seed_cover` clear the stairs
  (`_stair_reserved_rects`), not an authored `slab_holes` opening.
  - apartment_walkup_a01's dining set stands over an authored 2 x 2 m hole.
  - Moved, it failed the fixed point of furnish: the refurnish puts it back.

**Deli Counter 0.192.0:**
- L23 (WARN) asks every piece of the spec as it stands.
- `reseat_piece` moves one by its own placement rule.
- `migrate_stale_pieces.py` moved 17 pieces in 10 shells and refurnished
  each.
- `stale_pieces_baseline.json` freezes 47 in 8 shells, each with why.
- **The gate:** all 11 shells rebuilt keep 0.191.0's verdicts. The deli
  shells' circulation arm is clean.

**The census's storey rule is not L23's.** `stale_pieces.py` rounds a piece's
base to the nearest storey, which files a hung sign on the storey above.
L23's `piece_story` takes the nearest floor within 0.25 m, and floors
anything else. On the library both give the same 64 pieces.

## What is not established

- Whether the deli islands are visible in a level as floating, or only as an
  obstruction at the stair's arrival. No frame was taken.
- The cbp_town_finale and final_stand rows, case by case.
- What the z-fight pairs on office and rail_station_a02 are. deli_a01's worst
  pairs, from the one finding that was recorded, are slab tiles against a
  server rack cluster.
- **A walkable piece at a door.** twin_a01's `porch_deck_left` and
  `stoop_right` read 0.2 m into its front doorways' volumes, and the shell
  arm fails it. A stoop is where a body steps up to a door. The gate has no
  notion of a piece being walked on.
- The furnish fix for authored openings, and what it does to cbp_town_finale,
  final_stand and apartment_walkup_a01 when they are refurnished.
