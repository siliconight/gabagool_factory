# No-AI authoring loop: progress record

**Read this first in every session, then verify the source it names before continuing.** It is the one record of
where the no-AI authoring work stands: the milestone, what is done and the evidence, the blockers, the decisions, and
the exact next action. The plan behind it is `docs/reference/authoring/Gabagool_Factory_02_No_AI_Level_Authoring_Plan.md`
(with the operating guide and the Python/Blender/Godot contracts guide beside it). This file does not repeat the plan.
Roadmap items 310-318 carry the work items and their acceptance criteria.

## Milestone 1 -- one graphical creation loop on Restaurant Row

A new user configures the tools, creates a level, generates and selects a candidate, walks it, changes a supported
setting, saves and reopens the project, and exports. They do this from a Godot authoring project with the Factory
panel, with no terminal, no JSON editing and no AI.

**Status: increments 1-16 shipped (Level Factory 0.243.0-0.257.0); the walker has run steps 1-5 in the editor (`docs/findings/walk_2026-10-26_panel/`): every step of the loop exists and has run for real through the worker AND through the launcher the panel uses (`factory.cmd`, `levels/launcher_trial`: generate, choose, walk, export, every checklist line ok). The launcher's Python is prepared (the walker's yes, 2026-10-26). Milestone acceptance (318) needs a person running the loop in a windowed editor.**

## Assessment against the plan (2026-10-26)

The plan was written against factory-v1.41.0 / Level Factory 0.227.0. The certified set is still 1.41.0; the working
tools are ahead (Level Factory 0.242.0, Deli Counter 0.270.0, Zoo 1.130.0, Lot 0.131.0; the doctor reports the drift).

**Works today, reusable as is**
- The engine: briefs -> plan -> graybox candidates -> pick -> art and gameplay -> export, run by `make` or the staged
  CLI, with the scheduler, cache, per-attempt logs, findings, functional lock and export closure. Cold runs on
  Restaurant Row reach 0 interventions (9391-9393).
- Launchers: `factory.cmd` / `factory.sh` find a Python (venv, Blender's own, PATH) and forward every argument to the
  CLI. A panel can drive the factory through them with no Python of its own.
- The doctor has structured checks (`packages/tools/doctor.run_doctor`, `report.as_dict()`): Python, Blender, Godot,
  each tool's version and certification drift. On this machine Blender 5.1.1 and Godot 4.7 are found.
- Time-of-day presets (five) and theme resolve to real Lux and Pixelcoat choices.
- The first-level request: `docs/first_level/batch.json` and `briefs/restaurant_row_001.json`.

**Partly there**
- `FactoryService` (`level_factory/packages/service/facade.py`) separates views from actions, but its actions call
  the CLI handlers through a `SimpleNamespace` and capture global stdout/stderr. It is synchronous and its results
  are text, not structured data.
- The PySide6 desktop app (eight screens) has no brief editor or new-level flow. PySide6 is not installed on this
  machine; the plan makes Godot the primary surface, so the desktop app stays a diagnostic tool.
- The doctor prints its JSON through the Windows console encoding: `—` arrives as `�`. Results must travel in UTF-8
  files, never parsed from stdout.
- `walk` re-exports the mission's package to wrap it (`cmd_walk` calls `cmd_export`), so a preview can change the
  export. Preview and accepted export are not yet separate.
- The picker returns a least-bad candidate when every candidate is out (`pick.py`, `every_out`), and `make` records
  approvals automatically. The UI must show both for what they are.

**Missing (blocks the first release)**
- A Godot authoring project and Factory panel (no `apps/godot/` exists).
- A versioned request/result/progress protocol between the panel and the factory, with typed operations.
- A saved design document (the level's authored source) that the panel creates, edits, saves and reopens.
- A capability catalog: which brief fields drive generation and which are intent only. Six fields are recorded but
  unbuilt: `route_shape`, `objective_hypotheses`, `extraction_relationship`, `verticality`, `landmark`,
  `seed_policy` (`UNBUILT_BRIEF_FIELDS`).
- Asynchronous generate, select, walk, export and cancel driven from the panel, each tied to a design revision.
- Candidate images that come from the same build as the candidate's metrics.

## Decisions (routine, made here; change any by editing this list)

0. **A level is a design saved by the factory at `<factory>/levels/<slug>/design.json`** (`levels/` is user content,
   ignored by the root repo), its factory workspace beside it in `workspace/`; outside the Godot project and the tool
   repos. The panel never writes a design itself.

1. **Protocol v1 is files in a run directory**: `request.json` in, `events.jsonl` (append-only progress) and
   `result.json` (written atomically, last) out, all UTF-8. Every file is versioned (`gabagool.service.*.v1`);
   unknown operations and malformed requests produce an error result, never an empty success. The panel never
   parses stdout or log text. This follows the plan's section 5B and the contracts guide's publication rules.
2. **The panel calls the factory through its launcher** (`factory.cmd service-run <run dir>` / `sh factory.sh
   ...`), started with `OS.create_process` and watched by polling the run directory from a `Timer`, so the editor
   thread never blocks.
3. **Operations live in `level_factory/packages/service/operations.py`** and return plain dictionaries. The CLI, the
   worker and later the desktop app call the same functions. Extraction from the CLI handlers happens one operation
   at a time, as each is needed.
4. **The Godot side lives at `level_factory/apps/godot/`**: `addons/gabagool_factory/` (the plugin) and a
   ready-to-open authoring project that uses it.
5. **Every record the loop reads or writes has a data schema** (Level Factory 0.252.0, the walker's request
   2026-10-26): JSON Schema draft 2020-12 files in `level_factory/schemas/authoring/`, one per record, named by the
   record's own `schema` field. They are checked by `packages/service/schemas.py`, which needs no `jsonschema`
   package (Blender's Python has none) and refuses a schema keyword it does not implement. A new field means editing
   the schema in the same change; a breaking change means a new `.v2` id, never a quiet edit of `.v1`. The walker's
   *Level Factory Design Standard* (the gold-standard proposal, kept as `docs/reference/LEVEL_FACTORY_STANDARD_v0.docx`
   and operationalised in `docs/LEVEL_STANDARD.md`) is a DESIGN schema, not a data one. Its Score and Route records
   become data schemas when the factory has something that fills them.

## Increments

| # | User capability | State | Evidence |
|---|---|---|---|
| 1 | Open the authoring project, point the panel at the factory, and see whether Blender, Godot and the tools are ready, with each problem's fix | shipped, LF 0.243.0 (e698a7e) | Suite 2,650 / 0 failed. `tests/service/test_worker.py` 13 cases (fail on 0.242.0). Headless Godot: `apps/godot/tests/test_service_client.gd` 6/6, the client running real operations; `test_factory_dock.gd` 6/6, the dock through the installed `factory.cmd`. Editor load headless: no errors. `patches/lf_service_panel/` |
| 2 | Prepare the tools' Python from the panel when it is missing what they need | shipped, LF 0.244.0 (b504d35); RUN for real 2026-10-26 | Suite 2,655 / 0 failed. `tests/service/test_prepare_environment.py` 4 cases with a fake `make_venv` (fail on 0.243.0); dock test 8/8, the button shown only when the tools' Python blocks. `patches/lf_prepare_env/` |
| 3 | Start a new level from the Restaurant Row template and see which choices drive generation and which only record intent; save and reopen it | shipped, LF 0.245.0 (07a315f) | Suite 2,668 / 0 failed. `tests/service/test_design.py` (fail on 0.244.0): options equal their owners', each time a distinct Lux preset, rain's substitution, streets and layout count reaching the pipeline, the first-level brief reproduced at the template's defaults, create-save-reopen, unknown fields kept. Godot `test_level_panel.gd` 9/9 through the installed launcher. `patches/lf_design/` |
| 4 | Generate layouts for the level and choose one, from the panel, with progress and a way to stop | shipped, LF 0.246.0 (5110786) | Suite 2,676 / 0 failed. `tests/service/test_layouts.py` (fail on 0.245.0). Godot `test_level_layouts.gd` 11/11. REAL: design `levels/panel_trial` generated through the worker in 1 min 40 s (system Python), three valid layouts (9003 PASS 90, 9104 PASS_WITH_TUNING 89, 9205 PASS 100, recommended), 95 progress events; seed 9205 chosen through the installed worker, gate recorded `by: panel`, "a choice, not a review". `patches/lf_layouts/` |
| 5 | Walk the chosen layout from the panel, labelled with the revision and layout it shows | shipped, LF 0.247.0 (6942d67) | Suite 2,683 / 0 failed. `tests/service/test_walking.py` (fail on 0.246.0). Godot `test_level_walk.gd` 6/6. REAL: `levels/panel_trial`'s chosen layout walked through the worker in 8 min 42 s (system Python) -- art, lighting, gameplay, an export with a light bake (141 models, 65.5 s), the preview built and its self-check passed, named "Panel Trial, revision 1, layout seed 9205". `patches/lf_walk/` |
| 6 | Change a supported setting (time of day) on the Level tab and see it in the next walk | shipped, LF 0.248.0 (14fc3c8) | Suite 2,688 / 0 failed. `tests/service/test_revise.py` (fail on 0.247.0). Godot `test_level_edit.gd` 8/8, all six Godot tests pass. REAL: `levels/panel_trial` evening -> midnight saved as revision 2 (`rebuilds: lighting`) and walked through the worker in 7 min 20 s, named revision 2, self-check passed; re-ran `lux_apply`, `lot_assemble` x3, `themed_site_assemble`, `presentation_compose`; the shells, kit, dressing, walk tests and Laser Tag cache hits. `patches/lf_revise/` |
| 7 | Export the walked level as a snapshot to a folder the designer chooses, with a checklist | shipped, LF 0.249.0 (7054c70) | Suite 2,695 / 0 failed. `tests/service/test_exporting.py` (fail on 0.248.0). Godot `test_level_export.gd` 5/5; all seven Godot tests pass. REAL: the trial design's walked revision 2 exported through the worker in 85 s, every checklist line ok -- 2,786 files none missing, portability PASS (engine check passed), 2,750 lightmapped, gl_compatibility, 0 major (`patches/lf_export/trial_snapshot_manifest.json`; the 166 MB copy deleted after). |
| 8 | Each layout's top-down plan beside its row, drawn from that layout's own build (314) | shipped, LF 0.250.0 (c88cd62) | Suite 2,684 / 0 failed. `tests/service/test_plan_image.py` (fails on 0.249.0); Godot `test_level_plan.gd` 5/5, all eight pass. REAL: `launcher_trial`'s three layouts drawn and rendered through Godot 4.7's SVG loader, each different, the objective at the pixel its footprint predicts. FOUND: Godot's SVG loader draws no `<text>`, so the key is panel text. `patches/lf_plan/` (with `launcher_loop.out.txt`: choose 1 s, walk 555 s, export 98 s through `factory.cmd`) |
| 9 | Reopen a level and see where it stands: layouts and plans, the chosen one, the last walk and export, each saying if the level changed since (318's "save and reopen") | shipped, LF 0.251.0 (dd39851) | Suite 2,690 / 0 failed. `tests/service/test_standing.py` (fails on 0.250.0); Godot `test_level_reopen.gd` 9/9, all nine pass. FIXED: opening a level after another left the other's layouts, walk and export on the tab. REAL: both trial levels read back (three layouts, chosen 9205, walk and export current; a deleted snapshot reported). `patches/lf_standing/` |
| 10 | Every record the loop reads or writes has a data schema, checked by its reader and writer (the walker's request) | shipped, LF 0.252.0 (1f6d495) | Suite 2,713 / 0 failed; all nine Godot tests pass. `tests/service/test_schemas.py` (fails on 0.251.0): 8 JSON Schema files in `level_factory/schemas/authoring/`, real records from the trial levels kept as fixtures, each broken one field at a time and failing under both the built-in check and `jsonschema` 4.26.0, which agree on every case; passes without `jsonschema`. MEASURED: every loop record on disk (2 designs, 2 build records, 3 walk records, 2 export records, 2 manifests, 14 requests, 14 results, 845 events) passes both. REAL: `launcher_trial` regenerated through `factory.cmd` on 0.252.0 in 42 s, its build record, 43 events and result valid, plans drawn; reopened clean. `patches/lf_schemas/` |
| 11 | The Level Standard's designer brief on the form: Players as a real control, Fantasy / Scale / Density / Tone / Playstyle as intent | shipped, LF 0.253.0 (c49588c) | Suite 2,719 / 0 failed; all nine Godot tests pass, the real factory's form showing 20 controls. `tests/service/test_brief_fields.py` (4 of 5 fail on 0.252.0; the fifth guards a design saved before Players). Players is `crew_size`, read by Lot's crew spawns and Laser Tag's crew, so it rebuilds the layouts; the five intent fields change nothing built and stay out of the pipeline's brief. `patches/lf_brief/` |
| 12 | A job's receipt records everything its cache digest hashes, so a re-run can be attributed | shipped, LF 0.254.0 (507450f) | Suite 2,725 / 0 failed. `tests/unit/test_receipt_names_every_digest_input.py` through the real scheduler (fails on 0.253.0). MEASURED with it: an unchanged rebuild runs 0 of 90 jobs; a time-of-day change runs 1, `lux_apply` (`docs/findings/rerun_receipts/`). `patches/lf_receipt/` |
| 13 | Setup says what it downloads, licences included, before downloading, and holds every pin to its licence (the walker: MIT everywhere, download at setup) | shipped, LF 0.255.0 (b6a0b76) | Suite 2,734 / 0 failed; all ten Godot tests pass. `tests/unit/test_setup_licences.py` (all 8 fail on 0.254.0). REAL: `discover_installation` through `factory.cmd` returns the twelve packages and licences; this machine's `.venv` holds every recorded version and licence. `docs/THIRD_PARTY.md`, `patches/lf_licences/` |
| 14 | The walker's first windowed run (318), 2026-10-26: Setup, New level, Generate, Use this layout, Walk; the walk then explored by hand | DONE IN PART: steps 1-5 by the walker in the editor; the walk handed over an unplayable preview | `docs/findings/walk_2026-10-26_panel/`: 7 panel defects (P1-P7) and 7 level findings (L1-L7). Interventions on the way: the walker ran Godot's import by hand to make the preview playable (L1). |
| 15 | The panel defects from that run: progress against a fixed plan, whole numbers, Setup tooltips, walk stages and a moving bar, re-attaching after a restart, Open the last walk | shipped, LF 0.256.0 (05352ca) | Suite 2,736 / 0 failed; all twelve Godot tests pass. `patches/lf_panel_polish/` |
| 16 | A walk whose preview did not finish importing fails, at the light bake's 1,800 s bound; project.godot in the editor's format | shipped, LF 0.257.0 (5369126) | Suite 2,743 / 0 failed; all twelve Godot tests pass. `patches/lf_import_gate/` |
| 17 | The rest of 318: change Time of day, Save, Walk, reopen, Export -- by the walker, on 0.257.0 | waiting on the walker | -- |

## Blockers and open questions

- **RESOLVED 2026-10-26:** `prepare_environment` run through `factory.cmd` with the walker's yes (12 s, pip cache):
  `<factory>/.venv` (Python 3.13.9 from Blender's, Pillow 12.3.0, pygltflib, jsonschema 4.26.0) recorded as
  `python_executable`; setup now `ready`, nothing blocking. Proven by a level created and generated entirely through
  `factory.cmd` (`levels/launcher_trial`, 1 min 51 s, three valid layouts). Workspaces made from now on run the tools
  under it, the cold runs' included.
- **Was: on this machine the launcher ran the factory on Blender's own Python** (`BLENDER` set, no
  `.venv`), which cannot import `PIL`, `pygltflib`, `jsonschema`. The panel reports it correctly ("Python the tools
  run under: problem"), but its fix is `factory setup --venv`, a terminal step that downloads packages once. A new
  user stops here. Increment 2 (0.244.0) puts it behind a button. **Pressing it for real is waiting on the walker's
  yes**: it downloads Pillow, pygltflib and jsonschema into `<factory>/.venv` and records that Python in
  `factory.local.json`, so workspaces made afterwards run the tools under it rather than the system Python 3.14 the
  cold runs use today.
- **Through the launcher, generation would run the tools under Blender's Python**, which lacks their packages: the
  real build above ran under the system Python. Same decision as the environment above.
- **Found in increment 6:** a time-of-day change re-assembles the site (`lot_assemble`) for EVERY layout, not just
  the chosen one -- Lot's site lights follow the time of day -- so "rebuilds: lighting" understates it and the
  re-walk does three layouts' site work for one. Owner: Level Factory's planner (art legs could plan the chosen
  candidate's site only).
- **Unverified in increment 5:** the preview opened by the panel in a windowed editor and walked by a person (the
  preview exists at `levels/panel_trial/workspace/.level_factory/preview/panel_trial_001_walk`).
- **Unverified in increment 4:** a person pressing Generate in a windowed editor; Stop against a real build (the
  cancel path is tested with a fake leg and the client's cancel file, not a killed Blender).
- **Unverified in increment 1:** the panel seen in a windowed editor by a person; Browse's choice surviving a
  reopen (editor settings); Find Blender / Find Godot through the panel (`configure_installation` is tested in
  Python, not through the dock).

## Next action

1. **318 by a person:** open `level_factory/apps/godot` in Godot 4.7, Gabagool Factory dock -> Setup -> Level tab:
   New level, Generate layouts, Use this layout, Walk level, change Time of day, Save changes, Walk level, reopen the
   project, Export.... Record each step and any intervention in this file.
2. Meanwhile, independent work: jobs re-running with every recorded input unchanged (`docs/findings/rerun_receipts/`;
   this RETRACTS increment 6's "a lighting change re-assembles every layout" -- revision 1's walk, which changed
   nothing, re-ran them too). MEASURED on Level Factory 0.254.0 (whole-digest receipts): a time-of-day change
   re-runs 1 job of 90, `lux_apply`; an unchanged rebuild runs 0. DONE;
   the licence guards (DONE, 0.255.0); an audit of third-party ASSETS bundled in the repos (fonts, textures); written schemas
   for the eleven record types the loop reads and writes (none has a schema file; the walker mentioned a schema sheet,
   2026-10-26: it was the design standard, now decision 5) -- DONE in 0.252.0; the parked 309 bridge (clone `_scratch/lf_anchor`, re-base on 0.251.0). Levels generated
   before 0.250.0 show no plans until generated again.

Increment 7, as planned (roadmap 317): `export_level {path, destination}` -- after a walk of the current revision, run
the existing `export` and `portability-test` legs and copy the workspace's export into a NEW folder the designer
picks (refuse an existing non-empty one), with a manifest naming design revision and layout, and a checklist
(package complete, portability, light bake from `light_bake.json`, findings left). Read `cmd_export`,
`cmd_portability_test` and `packages/exporting/export.py`'s manifest first. Then 318: the whole loop by a person.

Increment 6, as planned (roadmap 316): `update_design` (the expected revision guards against overwriting a newer save;
returns what the change rebuilds), `walk_level` re-importing the current revision's brief before the art leg and
refusing when a changed control rebuilds the layout, and editable controls with Save and Undo on the Level tab.
Working notes: `patches/lf_revise/src/revise_notes.md`. Proof wanted: `levels/panel_trial` evening -> midnight,
walk again, only the lighting jobs rebuild, the label says revision 2.

Increment 5, as planned (roadmap 315): an operation `walk_level {path}` -- record the brief and shell-lock gates as the
panel's automatic steps (labelled so, not a review), run the art and gameplay legs for the chosen layout, then build
the walk preview and launch it, the result naming the design revision and layout. Read `cmd_walk`,
`packages/preview/walk_preview.py` and `cmd_export` first; a preview must never overwrite an accepted export (317's
snapshot goes to its own folder).

Increment 4, as planned (roadmap 314): an operation `generate_layouts {path}` that derives the brief from the design, makes
the design's workspace (`init_workspace` with discovered tools), imports the batch, plans and runs the graybox
candidates with progress events and a stop, and returns each candidate's status and evidence; the Level tab's
Generate and Choose. Read `apps/cli/commands/__init__.py` `cmd_make` and `cmd_batch_create`, `packages/jobs/runner.py`
and `scheduler.py` (cancellation) and `packages/pipeline/pick.py` first.

Increment 3, as planned (roadmap 312 and 313): a capability catalog for the brief's fields (`MissionBrief`,
`UNBUILT_BRIEF_FIELDS`, the time-of-day and theme resolvers) and a `create_design` operation writing a versioned design
from `docs/first_level/briefs/restaurant_row_001.json`; the dock's New level section draws its form from the catalog.
Read `level_factory/packages/core/models.py` (`MissionBrief`) and `apps/cli/commands/__init__.py` (`_brief_model`,
the time-of-day resolver) first.
