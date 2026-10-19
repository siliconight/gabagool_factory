# Deli Counter's freshness gate watches 22 of the 54 modules a shell build reaches (roadmap 259)

Found 2026-10-19 shipping Deli Counter 0.228.0, whose change lives in `level_design.py`: a module the
builder imports at build time (`deli_counter.py:3241` and `:3451`, the club rooms and the business id) and
that `build_freshness.GEOMETRY_SOURCES` does not list. 0.228.0 was rebuilt whole after its change, so this
is not a stale shell found; it is a guard that could not have seen one.

## What the gate is

`deli_counter/build_freshness.py` compares each built shell's modification time with the newest of
`GEOMETRY_SOURCES` -- "modules whose output is BAKED INTO a shell", deliberately not "the tools that read
shells afterwards (nav_gate, zfight_gate, circulation), which re-run against whatever is there". `check.py`,
the pre-commit hook, runs it before the nav gate. Level Factory reads the same tuple with `ast.literal_eval`
as the consumer's guard at the point of use (`level_factory/packages/pipeline/building_library.py`,
`_geometry_sources` and `stale_shells`), because a brief that sets a `lot_library` -- every cold-run brief
does -- has Lot stand the library's own `build/*.glb` (roadmap 258's reading), and `build/*.glb` is
gitignored, so no hash of the repo sees them. So the tuple is both guards' whole idea of what a shell is made of, and it
has to stay a literal for the second to read it.

## What was measured

`freshness_imports.py` (`freshness_imports.out.txt`; Deli Counter 3dd5d62e, 0.228.0). Following AST imports,
top-level and inside functions alike, from `build.py` and `deli_counter.py` through repo-local modules, a
build reaches **54** modules. `GEOMETRY_SOURCES` lists **23**: 22 reached, and `ladder_place.py`, which the
build path names only in comments (listed and not imported: the safe direction). **32** reached modules are
not listed.

`call_sites.py` (`call_sites.out.txt`) prints, for each of the 32, every reached module importing it and the
lines using it. Read off those lines:

**21 put their output into what a build writes** -- a listed builder module uses them for geometry, a
record, or the spec a preset generates:

| module | used by, for |
|---|---|
| `agent_contract` | stairwell (`LANDING_DEPTH`, the seam wall's underside), presets (`DOOR_W`), spec_types (door width, vault aperture) |
| `layout_lint` | stairwell (`_host_openings`, `DOOR_APPROACH_M`: where a stair can stand); level_design; stair_pitch |
| `ledge_cover` | deli_counter's `_vault_ledges` (0.227.0) |
| `level_design` | deli_counter (club rooms, business id), lights (`bar_aisle_width`, `club_building_id`), presets |
| `material_kind` | deli_counter (skin kinds), themed_tscn |
| `prop_species` | deli_counter (species, long axis, collision ownership), lights |
| `rarity` | deli_counter (`resolve_rarity`) |
| `setbacks` | deli_counter, floorplan, roofs, stairwell: every storey's extent |
| `skin_style` | deli_counter, floors, roofs |
| `stair_pitch` | presets (`lengthen`, `clear_walls`) |
| `stoop` | deli_counter (the Empty's stoop, 0.211.0), presets |
| `tactical` | ladder, stair_place, stairwell (`_room_at`, `build_graph`) |
| `tscn_export` | build (`tscn_from_manifest`), themed_tscn (transforms) |
| `vault_room` | deli_counter (the vault's slot and bearing faces) |
| `zoo_export` | build (`zoo_from_dir`) |
| `migrate_roller_grill`, `migrate_slush_machine`, `migrate_wall_crossing`, `migrate_window_poster`, `migrate_window_sign` | presets call each (`plan_grill`, `plan_station`, `trim`, `migrate`) |
| `migrate_furnish_recipes` | the window poster's and sign's migrations, which presets call |

**11 are readers or reports:** `circulation` and `zfight_gate` (readers; the gate's own comment names
them), and `evidence` with what it calls -- `combat_audit`, `enterability`, `guards`, `navigability`,
`pvp_heist`, `sightlines`, `validate`, `polybudget` -- whose reports `build.py` writes beside each shell
(`<name>.validation.json`, `.combat_audit.json`, `.navigation.json`). No tool outside Deli Counter reads
those reports: searched `level_factory/packages`, `lot`, `dispatch` and `tools`, none.

**And one data file.** `agent_contract.json` -- body sizes and every clearance derived from them -- is read
by `agent_contract.py` (`$DC_AGENT_CONTRACT`, else the file beside it). The tuple names it nowhere.

## What it means, and what it does not

A commit that changes only one of the 21, or the contract, passes the hook with every shell older than the
code that makes them, and Level Factory's guard then serves those shells to a level as fresh. Nothing here
says that has happened: the call sites say where a module is used on the build path, not that a change to it
was ever committed without a rebuild, and the 0.228.0 shells are newer than every module.

Not established: whether `ladder_place.py` is reached some way the AST cannot see (a dynamic import); what
each of the 21 would change in a shell if edited -- read off its call sites, not measured.

## What would close it

The tuple stays a literal. Add the 21 and `agent_contract.json` to `GEOMETRY_SOURCES`; name the 11 in a
second literal with a reason each; and a test that walks the same import graph and fails when a reached
module is in neither, so the next module the builder imports is classified the day it lands rather than
the day a stale shell is graded. The price: `layout_lint.py`, a lint edited often, then asks for a rebuild
on every change, because stairwell reads two of its names; moving those two into a geometry module would end
that. The content fingerprint the gate's own docstring calls "strictly better" is the larger step and not
this one.

## Built, 2026-10-19 (Deli Counter 0.229.0, 54f5b5d4)

`patches/patch_dc_freshness_sources.py`, its proofs in `patches/dc_freshness_sources/`. Twenty of the 21 and
`agent_contract.json` are in `GEOMETRY_SOURCES`, 44 entries where there were 23, still a literal. `NOT_BAKED`, a
second literal, names the 12 kept out with why. `test_freshness_sources.py` walks the build's imports as
`freshness_imports.py` does and fails on a module in neither; four of its five fail on 0.228.0. No rebuild was
needed: the newest source added, `level_design.py`, was written at 09:45:29 and the oldest judged shell at
09:47:47. Level Factory's guard reads the 44 and finds 0 stale.

**Left, by decision:** `layout_lint.py` stays unwatched, as `test_gates_that_only_read_shells_are_not_watched`
holds it, so a lint edit does not demand a rebuild. Stairwell still reads its `_host_openings` and
`DOOR_APPROACH_M`, and stair_pitch acts on its findings. Moving those two names into a geometry module would
watch them without watching the lint.
