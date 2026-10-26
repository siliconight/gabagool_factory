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

**Status: increments 1-2 shipped (Level Factory 0.243.0, 0.244.0); increment 3 (a new level from the Restaurant Row template) next.**

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

## Increments

| # | User capability | State | Evidence |
|---|---|---|---|
| 1 | Open the authoring project, point the panel at the factory, and see whether Blender, Godot and the tools are ready, with each problem's fix | shipped, LF 0.243.0 (e698a7e) | Suite 2,650 / 0 failed. `tests/service/test_worker.py` 13 cases (fail on 0.242.0). Headless Godot: `apps/godot/tests/test_service_client.gd` 6/6, the client running real operations; `test_factory_dock.gd` 6/6, the dock through the installed `factory.cmd`. Editor load headless: no errors. `patches/lf_service_panel/` |
| 2 | Prepare the tools' Python from the panel when it is missing what they need | shipped, LF 0.244.0 (b504d35); live download NOT run | Suite 2,655 / 0 failed. `tests/service/test_prepare_environment.py` 4 cases with a fake `make_venv` (fail on 0.243.0); dock test 8/8, the button shown only when the tools' Python blocks. `patches/lf_prepare_env/` |
| 3 | Start a new level from the Restaurant Row template and see which choices drive generation and which only record intent | next | -- |

## Blockers and open questions

- **Found by increment 1, on this machine: the launcher runs the factory on Blender's own Python** (`BLENDER` set, no
  `.venv`), which cannot import `PIL`, `pygltflib`, `jsonschema`. The panel reports it correctly ("Python the tools
  run under: problem"), but its fix is `factory setup --venv`, a terminal step that downloads packages once. A new
  user stops here. Increment 2 (0.244.0) puts it behind a button. **Pressing it for real is waiting on the walker's
  yes**: it downloads Pillow, pygltflib and jsonschema into `<factory>/.venv` and records that Python in
  `factory.local.json`, so workspaces made afterwards run the tools under it rather than the system Python 3.14 the
  cold runs use today.
- **Unverified in increment 1:** the panel seen in a windowed editor by a person; Browse's choice surviving a
  reopen (editor settings); Find Blender / Find Godot through the panel (`configure_installation` is tested in
  Python, not through the dock).

## Next action

Increment 3 (roadmap 312 and 313): a capability catalog for the brief's fields (`MissionBrief`,
`UNBUILT_BRIEF_FIELDS`, the time-of-day and theme resolvers) and a `create_design` operation writing a versioned design
from `docs/first_level/briefs/restaurant_row_001.json`; the dock's New level section draws its form from the catalog.
Read `level_factory/packages/core/models.py` (`MissionBrief`) and `apps/cli/commands/__init__.py` (`_brief_model`,
the time-of-day resolver) first.
