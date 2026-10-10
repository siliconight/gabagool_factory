# Cold run 9231 -- 0 interventions, 0 retries, STOPPED at the export: the first level drawn by a template, and the draw that disagreed with itself

restaurant_row_001 (`corner_deli`, a `strip` site), evening and clear,
seed auto, staged from 9229's batch with one field ADDED to its brief:
`"cluster": "auto"` (a brief edit in `briefs/`, which is allowed). The
first level drawn by the adjacency guide's cluster templates (Level
Factory 0.176.0, roadmap 230 step 1) and audited by its pair rules (Lot
0.111.0, step 2), with Deli Counter 0.206.1's home rule (roadmap 229).

Tool versions hashed at `--begin` (`_runs/cold/cold_9231/before.json`):
Deli Counter 0.206.1, Dispatch 0.5.2, Laser Tag 0.25.0, Level Factory
0.176.0, Lot 0.111.0, Lux 0.74.0, Patina 0.30.0, Pipeline 0.6.0, Pixelcoat
0.62.0, Zoo 1.97.0. Against 9229: Deli Counter 0.206.0 to 0.206.1, Level
Factory 0.175.1 to 0.176.0, Lot 0.110.0 to 0.111.0.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 0,
and the driver STOPPED at the export** (`driver.log`: `STOPPED: export`,
exit 2). Nobody touched anything, and the run is not a success: the
export's closure gate refused the package. The record below says what
each stage did, what the gate caught, and why.

- **The shell leg:** 3 candidates built, all distinct, 0 blockers of 55;
  picked seed_9104 on the walktest and Laser Tag's route findings (seed
  9003: 1 major; 9104: 0; 9205: 1; route completion 1.00 on all three).
- **The art leg:** 0 blockers of 78.
- **The export:** `EXPORT_CLOSURE_BROKEN: 1 unresolved res:// reference(s)
  ... 1 unresolved relative` -- `presentation/lux.applied.tscn: unresolved
  res://buildings/rail_station_a02.glb`, `site.tscn: relative ext_resource
  resolves to nothing: buildings/rail_station_a02.glb`, and `2 scene(s)
  ship and res://mission.tscn reaches none of them: lot/pharmacy_a01/site.tscn,
  site.tscn`. The light bake then failed (`bake.tscn did not open`) and the
  package shipped unbaked. The gate stopped the driver, as it should.

## What the template did, stage by stage

- **The brief's `auto` resolved** to `C03_station_neighborhood` from the
  archetype's words, in every candidate's site spec (`cluster_resolved`:
  asked `auto`, got `C03_station_neighborhood`, known, preferred `deli,
  cr_deli, night_deli, pharmacy, office, office_stepped, bank_tower,
  apartment_walkup, twin`).
- **The three candidates' lots are byte for byte 9229's** (`deli_a03 +
  depot_a01 + self_storage_a01`, `deli_a01 + office + rail_station_a02`,
  `deli_a03 + supermarket_a01 + parking_garage`): the SITE draw did not take
  the template. The picked site is 9229's lot at 9229's positions, roads
  and 24 Empties.
- **The art leg dressed a different lot:** its jobs are `deli_a01`,
  `office` and `pharmacy_a01` (`patina_apply.pharmacy_a01`,
  `zoo_kit_build.pharmacy_a01`, `lux_fixture_gate.pharmacy_a01` ...
  succeeded) and no job for `rail_station_a02`. The planner's fan-out and
  the compose spec drew through `lot_for_brief`, which 0.176.0 threaded
  the template through (anchor deli, then the template's pharmacy and
  office); the site spec builder draws through its own `pick_lot` call,
  anchored but untemplated (`apps/cli/commands/__init__.py`, the fourth
  draw, which 0.176.0's note -- "`grep lot_for` over the package names all
  three call sites" -- does not name because it is a `pick_lot`). The
  planner's disagreement guard (`_art_entry`) compares the art jobs with
  the compose spec's lot, which agreed with them; nothing before the
  export compares either with the site spec.
- **So the export's package** placed the station without art (its glb
  unresolved) and carried a themed pharmacy scene nothing reaches, and the
  closure gate, written for exactly this shape, refused it.
- **Level Factory 0.176.1** (`patches/patch_lf_cluster_site.py`): the
  template is read off the brief in one function,
  `building_library.preferred_for_brief`, which `lot_for_brief` and the
  site spec builder both ask; a test walks `apps/` and `packages/` for every
  `pick_lot(` outside the library and refuses one without `preferred=`.
  Cold run 9232 re-runs this brief on it.

## What the pair rules said (Lot 0.111.0, the first `S_ADJACENCY` lines)

In the themed site audit (`themed_site_assemble/1/job.log`), INFO: `b0
(deli_a01) and b2 (rail_station_a02) are across_local_street: P17 prefer --
an actual platform access route in the selected year`; `b1 (office) and b2
(rail_station_a02) are same_block: P17 prefer`. Candidate seed_9003's
audit: `b0 (deli_a03) and b1 (depot_a01) are same_block: P14 prefer --
staff or driver access to the food identified`. The judge runs, reads the
relation from geometry, and says why a pair is good; no MED on these lots.

## What the home rule did (Deli Counter 0.206.1)

The merged lights of the themed site carry ONE anchor for the deli's
apartment hideout (`b0/apartment_hideout_ceiling`) where 9229's carried
three (`_ceiling`, `_r1`, `_r2`); the deli's generate log reads `17 row(s)
laid to the work` where 9229's read 24. Site-wide: 42 fluorescent rows and
163 lamps where 9229 had 44 and 174. Not seen: the package is unbaked, so
the interior frames wait for 9232.

## Also in the record

- `LOT_PERIMETER_FENCED: 6 run(s), 589.7 m`; `LOT_BACKDROP_PLACED: recipe
  borough, 277 piece(s) (backdrop_rowhome 276, water_tower 1) by side (N 96,
  S 101, E 41, W 38), 7 module(s), 1 water tower(s)`; the export's backdrop
  `277 instances of 7 module(s) on their sides, 25 draw calls`, as 9229.
- Not priced, not shot: the package is the refused one.

## What this run proves and does not

It proves the closure gate: a level whose art and site disagree does not
ship. It proves the template resolves and records itself, and that the
pair rules read a drawn lot. It does not prove the draw by template in a
shipped level, which is 9232's job, and it does not prove the home rule's
look.
