# Cold run 5 — `precinct_yard_001`, seed_base 9001, UNSEEN VOCABULARY

**Begun** 2026-09-05 09:51 · **Ended** 10:2x · 2397 source files hashed across
10 tools
**Journal / snapshots:** `_runs/cold/cold_9001/`
**Brief:** `docs/cold_runs/cold_9001/` (seed_base 9001 → seeds 9001 / 9102 / 9203)

## Result

```
interventions NOTED in the journal      0
tool source files CHANGED on disk       3
  attributed to the pipeline, NOT counted   3
  UNATTRIBUTED, counted                     0
retries (same command re-run)           0
observations                            0

INTERVENTIONS: 0
```

**And a gated package came out.** `export --mode portable-godot` exited 0.

| run | vocabulary | interventions | outcome |
|---|---|---|---|
| cold_7001 | seen | 0 | exported on a gate later found broken (71) |
| cold_7002 | seen | 1 | blocked — theme did not exist (72) |
| cold_7003 | seen | 1 | blocked at export (73) |
| cold_8001 | seen, varied lot | 0 | **exported** |
| **cold_9001** | **unseen archetype + unbuilt shape** | **0** | **exported** |

Two consecutive runs at zero, producing packages, on different vocabulary.

## What was actually unseen, stated narrowly

**NEW:**
* `archetype: police_station` — a real Deli Counter preset that no brief had
  ever requested. Every brief on disk used `bank`, `urban_bank`,
  `casino_tower`, or the non-existent `mixed_block`. It resolved with no
  fallback (`_preset_for` raises rather than guessing) and built three times.
* `site_shape: courtyard` — one of the three shapes `site_variation` supports
  and the only one never built. Every site ever laid out was `row` or `L`.

**NOT NEW, and it could not be:** `theme: delco`. See the theme-matrix finding
below — a genuinely new theme is not buildable today. Holding the theme
constant also means only two variables moved against `cold_8001`.

## The prediction, recorded before the run, and half wrong

The brief predicted: *"the courtyard closes to a smaller plate than a row of
four, and Laser Tag's opening findings change because sightlines across a
courtyard are shorter."*

MEASURED on the same four shells, via `site_variation.ground_size`:

    row        256.0 x  72.0    area 18.4 k m2
    L          192.0 x 144.0    area 27.6 k m2
    courtyard  128.0 x 144.0    area 18.4 k m2

**"Smaller plate" is wrong by area — it is identical, 18.4 k m² either way.**
What changes is ASPECT: the longest dimension halves (256 → 128 m) while depth
doubles. The prediction confused "shorter" with "smaller".

The opening findings did change, and not in the direction implied:

    finding                      cold_8001 (row, 3)   cold_9001 (courtyard, 4)
    LOT_ENEMY_SPAWN_CLOSE               2 of 3               3 of 3
    LOT_ENEMY_SPAWN_STANDOFF            1 of 3               2 of 3

A tighter site puts enemies CLOSER to the crew spawn, so spawn findings got
slightly worse, not better. **This comparison is confounded** — 3 buildings
against 4, and different archetypes — so the direction is noted and no cause
is claimed.

## Two findings raised during setup

Both are filed as roadmap items rather than fixed here; neither was touched
during the run.

**Theme diversity is capped at two, structurally.** Pixelcoat carries nine
profiles (`bank casino delco rockay rockay_civic rockay_retail rockay_service
stadium street`); Zoo has four styles with real species coverage (`rockay`
56/56, `center_city` 54/56, `industrial_flats` 54/56, `delco` 39/56). The
intersection is `delco` and `rockay` — nothing else. Zoo's two best-covered
styles have no Pixelcoat profile; seven Pixelcoat profiles have zero Zoo
species. That is why all six briefs in existence use one of two themes: it is
not habit, it is the only thing that builds.

**`site_shape` silently falls back to `row`.** `_SHAPE_ALIASES` maps
unrecognised spellings to `row` rather than refusing, and neither
`street_block` nor `boardwalk_crescent` is in the table — so
`bank_block_001` and `category5_baie_dore_001` have never received the shape
they name. Verified as a control beside this run's pre-check:

    site_shape courtyard    -> courtyard
    site_shape street_block -> row          <-- silent

The archetype path was fixed for exactly this class of bug — "a
wrong-but-plausible building is the worst failure this adapter can produce" —
and raises. The shape path still guesses.

## The package

`workspaces/cold-9001-ws/.level_factory/exports/LF_precinct_yard_001.portable-godot`
— 181 files, 19 MB, `config/features=PackedStringArray("4.7")`.

Four per-building directories: `auto_shop_a01`, `courthouse_a01`,
`museum_a02`, `self_storage_a02`. 36 interactives (28 doors, 8 breach walls)
distributed 9 / 10 / 8 / 9 across them.

## Item 73 held, on a second run

DC and Lot revisions byte-identical at the functional lock and again after the
art pass, with no `+dirty` at either point. `deli_generate.seed_9203` and
`lot_assemble.seed_9203` CACHE-HIT rather than re-running. `specs/CATALOG.md`
appears in no changed-file list. That is the fix confirmed on a run it was not
developed against.

## What this still does not establish

* **The theme was not new**, and cannot be until the theme matrix is widened.
  So "unseen vocabulary" here means archetype and site shape, not theme.
* **Nobody has walked it.** `LT_MAP_TRAVERSAL` is 0% on all three candidates,
  as on every evaluation ever run. Gate-clean and opening is "works", not
  "good" (roadmap 18).
* **Two runs is not several.** Item 17 asks for repetition across specs; this
  is the second consecutive zero and the fifth run overall.
* The three shells of roadmap 98 still keep Deli Counter's `check.py` red.
