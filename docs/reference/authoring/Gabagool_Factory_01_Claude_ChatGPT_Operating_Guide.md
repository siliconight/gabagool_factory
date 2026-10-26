# Gabagool Factory: operating guide for Claude and ChatGPT

**Purpose:** help an assistant use the factory, find the right source, and produce evidence without repeatedly inventing scripts or repairing generated output.

**Baseline:** uploaded `gabagool_factory_package_factory-v1.41.0 (2).zip`, inspected October 24, 2026. Level Factory is `0.227.0`. This guide describes that package, not an unseen working checkout. The companion [no-AI level authoring plan](Gabagool_Factory_02_No_AI_Level_Authoring_Plan.md) describes proposed work.

## 1. The operating model

The factory already runs without an AI model. Its Python and Godot tools generate, evaluate, dress, light, and export levels. Today, an assistant supplies the missing operator experience: translating a request into supported inputs, finding commands, interpreting failures, and extending capabilities.

Your first job is to operate the existing pipeline. Write new tool code only when an identified capability or defect requires it. A user asking for a level is not automatically asking for a new generator.

Keep these distinctions explicit:

| Work | What changes | What proves completion |
|---|---|---|
| Make content | Authored briefs, supported settings, candidate choice | Export and checks for the requested build; a human review of the result |
| Fix or extend a tool | The owning tool's source, tests, contracts, version | Regression proof, relevant gates, then a fresh build using the change |
| Investigate | Recorded observations and instruments | Evidence tied to a specific build, plus what remains uncertain |

The deliverable is a reusable pipeline and portable level content. A visually attractive result repaired by hand in generated output does not prove the pipeline can reproduce it.

## 2. First five minutes in a session

1. **Locate the actual factory root.** It contains `factory.manifest.json`, `START_HERE.md`, and `level_factory/`. Do not assume the author's Windows path exists on this machine.
2. **Identify the environment.** Record the factory version, OS, available Blender/Godot executables, and whether this is a ZIP snapshot or a Git checkout. A package without `.git` cannot supply commit history.
3. **Read the local instructions.** Check applicable `AGENTS.md` files if present, then `CLAUDE.md`. Despite its name, the latter contains conventions relevant to either assistant.
4. **Choose the task's starting documents below.** Do not load the entire repository or roadmap into context.
5. **Name the workspace and mission.** The factory checkout, authored input, job outputs, and exported package are different locations.
6. **State the scope of your evidence.** Source inspection, parser validation, a planned build, a completed engine run, and a human walk are different claims.

| Task | Read first | Then locate |
|---|---|---|
| Make a first level | `START_HERE.md`, `USING_THE_FACTORY.md` | `docs/first_level/batch.json` and its `briefs/` |
| Translate an idea | `docs/LEVEL_STANDARD.md`, especially Appendix A | `MissionBrief`, the brief warning list, and the field's actual consumer |
| Understand a failed stage | `PIPELINE_MAP.md`, relevant command help | That job's latest attempt, logs, normalized findings, producer and adapter |
| Change tool behavior | `CLAUDE.md`, `docs/SHIPPING_A_CHANGE.md`, `docs/FILING.md` | Owning source, tests, contracts, relevant roadmap item |
| Assess current UI | `level_factory/apps/desktop/windows/main_window.py` | `views/screens.py`, `packages/service/facade.py` |

**Evidence priority:** current source and observed output for the same version → executable tests/contracts → maintained instructions → historical prose. Documentation can contain preserved, later-corrected findings. Read their corrections before repeating a claim.

For example, Appendix A still describes morning/noon lighting as a gap. `_preset_for` and its tests implement both in this package. Conversely, the brief's attractive-sounding `verticality` field remains unimplemented as a generation control.

## 3. Search deliberately with ripgrep

Run these from the factory root. `rg --files` finds paths; `rg -n` finds matching lines; `rg -l` returns matching filenames. Use `-F` when searching a literal issue code or identifier. Quote patterns.

### Find the surface before reading implementation

```bash
rg --files -g 'AGENTS.md' -g 'CLAUDE.md' -g 'START_HERE.md' -g 'README.md'
rg --files level_factory/apps level_factory/packages level_factory/tests
rg -n '^class MissionBrief|^def _brief_model|UNBUILT_BRIEF_FIELDS' level_factory/packages/core/models.py level_factory/apps/cli/commands/__init__.py
rg -n '^def cmd_make|^def cmd_walk|^def cmd_export' level_factory/apps/cli/commands/__init__.py
```

Read the containing function and its adjacent comments. A matching line is a locator, not an understanding of the behavior.

### Trace a setting from request to output

```bash
rg -n -F 'time_of_day' level_factory/packages/core/models.py level_factory/apps/cli/commands/__init__.py
rg -n '^def _preset_for' level_factory/apps/cli/commands/__init__.py
rg --files level_factory/tests | rg 'time_of_day|preset'
rg -n -F 'preset_name' lux/addons/lux/presets
```

The required chain is **input field → normalization → planning/spec creation → adapter → producer → output/check**. A field appearing only in a dataclass, signature, or report does not prove that it changes the level.

### Find a failure's owner

```bash
rg -l -F 'WALKTEST_WALKER_STUCK' level_factory lot
rg -n -F 'WALKTEST_WALKER_STUCK' level_factory/packages/validation
rg -n -F 'WALKTEST_WALKER_STUCK' level_factory/tests
```

Locate the producer's actual output before writing a new reader. An absent or unknown schema must produce “unrecognized,” not a fabricated clean result.

### Search generated evidence explicitly

`rg` respects ignore rules and normally skips hidden paths. Generated workspace evidence can therefore disappear from a casual search. Target the exact workspace and deliberately enable hidden/ignored files there:

```bash
rg --files --hidden --no-ignore workspaces/restaurant/.level_factory/jobs -g '*walktest*.json' -g '*validation*.json' -g '*.log'
rg -n --hidden --no-ignore -F 'WALKTEST_WALKER_STUCK' workspaces/restaurant/.level_factory/validation
```

Use the actual path printed by your run; `workspaces/restaurant` is an example. Job directories may contain numbered attempts. Do not assume an old `out/` belongs to the latest successful attempt. Compare mission, candidate, attempt, layer, tool version, and fingerprints before comparing two artifacts.

### Keep large histories out of broad searches

The packaged `PIPELINE_ROADMAP.md` has **20,795 lines**. Start with its generated status index or search the exact issue/title:

```bash
rg -n '^##|^###|\| 200 \|' PIPELINE_ROADMAP.md
rg -n -F 'recorded, not built' level_factory/apps/cli/commands/__init__.py
```

For source work, narrow the owner and file type before searching. Avoid searching `CHANGELOG.md`, generated outputs, reference corpora, and vendored addon copies alongside live implementation. A zero-match result means “not found in this scope,” not “does not exist.” If `rg` is unavailable, use the host's file search and literal/regex search tools with the same scope discipline.

## 4. Who owns what

| Concern | First owner/location |
|---|---|
| Building floors, rooms, openings, stairs, structural collision, light anchors | `deli_counter/` |
| Character dimensions and derived clearances | `deli_counter/agent_contract.json` and its readers |
| Site assembly, circulation, cover, spawns, frontage | `lot/`; orchestration-side site choices also live in `level_factory/packages/pipeline/` |
| Structural modules, props, fixture hardware | `zoo/`, including `zoo/zoo_keeper/recipes/` |
| Surface materials and theme profiles | `pixelcoat/` |
| Cohesion and dressing plans | `patina/` |
| Light behavior, presets, fixture checks | `lux/` |
| Evaluation harness and advisory combat findings | `lasertag/` |
| CLI, orchestration, adapters, job execution, cache, validation, export | `level_factory/` |
| Portable mission handoff and gameplay intent | `dispatch/` |
| Certified combination and shared instructions | Factory root and `factory.manifest.json` |

Follow `PIPELINE_MAP.md` when a boundary is more specific than this table. Do not confuse the `pipeline/` tool with Level Factory's internal `packages/pipeline/`.

**Runtime boundary:** an exported shell and advisory gameplay anchors do not implement the consumer game's objectives, enemy AI, multiplayer authority, progression, or networking. Laser Tag's bots are an evaluation harness. Four crew members in that harness are not proof of a working four-player online heist.

## 5. What the current brief really controls

Use this as a warning map, then trace any field central to the user's request.

| Request | Current behavior in this package |
|---|---|
| Main building type | `archetype` is resolved into supported building choices; inspect the library and resolver rather than inventing names |
| Number and arrangement of buildings | `building_count`, `site_shape`, library selection; combinations remain subject to available content and gates |
| Street arrangement | `road_grammar`; separate from building arrangement |
| Materials | `theme`; confirm compatibility through discovery/doctor and the actual build |
| Time of day | Morning, noon, afternoon, evening, and midnight resolve to distinct named Lux presets |
| Rain at night | Rain currently selects **Heavy Rain**, overriding the time preset; do not promise a midnight rain result |
| Route shape, objective steps, extraction relationship, verticality, landmark | Recorded but not built from: `route_shape`, `objective_hypotheses`, `extraction_relationship`, `verticality`, `landmark` |
| Seed policy | `seed_policy` is recorded but unused; candidate generation uses the implemented seed derivation |
| Desired duration | `target_minutes` informs an advisory pacing estimate; it does not guarantee a measured full heist duration |
| Crew/enemy settings | Feed the evaluation scenario; the source explicitly notes that Lot's enemy-hook count is not fully wired to `enemy_count` |
| Plain-language notes | Preserve intent for review; they are not executable instructions or an AI prompt consumed by the generator |

`UNBUILT_BRIEF_FIELDS` in `apps/cli/commands/__init__.py` is explicit about the six unbuilt fields. `_brief_model` filters keys to the dataclass fields, so inventing a new JSON key can lose it at the model boundary without creating any behavior.

Also, `schemas/mission.brief.schema.json` is a lightweight descriptor using `fields`, not a complete standards-based JSON Schema validator. `FactoryService.validate_brief` performs only limited checks. Do not claim that “valid JSON” or that method proves full semantic support.

When translating a request, produce three short lists: **will generate**, **recorded for human review**, and **needs a capability change**. Preserve the user's ambition; do not silently substitute a supported feature and claim the original request was fulfilled.

## 6. The shortest existing build path

These commands are verified against the packaged CLI parser. Full generation requires the installed tools and machine checks. Use the package's supported Blender/Godot setup rather than assuming a globally installed Python has the right dependencies.

### Windows, from the factory root

```powershell
.\factory.cmd setup --venv --godot "C:\Godot\Godot_v4.7-stable_win64.exe"
.\factory.cmd -C workspaces/restaurant make docs/first_level/batch.json
.\factory.cmd -C workspaces/restaurant pick restaurant_row_001 --json
.\factory.cmd -C workspaces/restaurant validate restaurant_row_001 --json
.\factory.cmd -C workspaces/restaurant walk restaurant_row_001 --play
```

Replace the executable path with the actual installation. Supply `--blender` during setup if discovery needs it. If the launcher cannot find Blender's bundled Python at all, follow `START_HERE.md` to set the `BLENDER` environment variable for the relevant shell, or use an already configured interpreter.

### Linux, from the factory root

```bash
sh factory.sh setup --venv --godot /actual/path/to/godot
sh factory.sh -C workspaces/restaurant make docs/first_level/batch.json
sh factory.sh -C workspaces/restaurant pick restaurant_row_001 --json
sh factory.sh -C workspaces/restaurant validate restaurant_row_001 --json
sh factory.sh -C workspaces/restaurant walk restaurant_row_001 --play
```

The setup step downloads pinned Python dependencies once. The shell launcher can use Blender's bundled Python; no separate user-managed Python installation is required on the documented installation path. The package documents Windows and Linux. Do not describe macOS installation as certified without testing it.

`-C` identifies a **workspace**, not the factory root. `make` can initialize an empty/new workspace. For an existing workspace, run `doctor` first and inspect every required check. Do not treat exit code zero alone as proof that Blender and Godot are configured: the doctor command can classify `NOT_CONFIGURED` separately.

### What `make` does

It imports the batch, plans and runs the shell candidates, picks a candidate, records brief/candidate/shell approvals, runs art plus gameplay handoff, and exports. It uses the existing commands, so an assistant should not recreate this sequence with an improvised driver for routine work.

Three qualifications matter:

1. **Those approvals are automated workflow records.** They are not a human saying the level looks good.
2. **The picker can return a least-bad candidate when every candidate is “out.”** Its `every_out` flag and explanation must remain visible. Other gates can still stop the build. “Picked” does not mean accepted.
3. **`make` is not an instrumented cold run.** It does not establish zero interventions through the cold-run journal.

### A preview is not read-only

In this version, `walk` re-exports the package it wraps. `walk --no-bake-lights` can leave that package unbaked. Export normally requests a light bake, but the source documents a GPU/display requirement and an unbaked fallback when baking cannot run. Read `light_bake.json` and the export result before claiming baked lighting.

Keep a known-good export before taking experimental preview paths. Do not describe `--no-shots`, `--no-bot`, missing display output, or skipped checks as successful visual verification.

## 7. Make a new level without creating new code

1. Copy the first-level `batch.json` and sibling `briefs/<mission_id>.json` into an authored request folder in the user's level project. Keep that input under the project's normal backup/versioning policy.
2. Give the batch and mission distinct IDs. Match the mission ID in the batch, brief filename, and brief content. Mission IDs should be unique within a workspace: lookup scans batches and returns the first match.
3. Change supported fields. Preserve design intent that the factory cannot yet execute, but label it clearly as intent.
4. Use `make <path-to-batch.json> --mission <mission_id>` when a batch contains multiple missions.
5. Inspect the copied brief in the workspace: import can fill in the default lot library. Record that resolved input along with the source request.
6. Review candidates, findings, export completeness, and the actual level. Save the accepted seed and package identity.

**Choose one input authority.** `batch create` writes the workspace's brief from the supplied request. Editing only the workspace copy and then rerunning `make` with an older request can overwrite that edit. For the simple workflow, revise the source request and reimport deliberately. For staged expert operation, explicitly track which workspace brief is authoritative.

**A new seed is a new candidate, not a bug fix.** If a valid request repeatedly requires rerolling until the tools happen to succeed, record the failure rate and owning defect.

## 8. Staged operation and recovery

Use the staged CLI when the task requires a deliberate stop between shell generation, candidate review, and art. Read each command's `--help` in the current checkout. Existing commands include `init`, `batch create`, `plan`, `run`, `status`, `validate`, `pick`, `approve`, `export`, and `portability-test`.

The typical sequence is: initialize/configure → import → plan → run graybox → inspect candidates → approve brief and selected candidate → lock shell → run `--art --gameplay` → export → portability test → walk and review.

There is no documented `resume` subcommand here. Re-running `run` uses the scheduler/cache behavior. `run --force` invalidates planned cached answers; it is not a first response to every failure. Inspect what will change before using it.

| Symptom | First action |
|---|---|
| “Mission not found” | Check workspace root, imported batch, brief path, mission ID |
| Missing executable/dependency | Run doctor; fix setup, not generated scenes |
| `STOPPED at ...` | Read that leg's full output, exit code, job attempt, and normalized findings |
| All candidates are out | Read the disqualifying reasons; preserve the fact that selection is a fallback |
| Setting seems to do nothing | Trace its consumer; check unsupported fields and cache fingerprints |
| Level looks stale | Confirm request revision, effective brief, chosen candidate, output layer, and package path |
| Grade says pass but traversal looks wrong | Inspect the specific physical walk evidence and controller contract; a grade is not that proof |
| Source and documentation disagree | Verify implementation and a relevant test/output; record the discrepancy |

CLI exit codes are documented as: `0` success, `1` findings, `2` blocked, `3` configuration, `4` tool failure, `5` internal error, `130` cancelled. Interpret the command-specific result and artifacts as well. Preserve stderr and full logs; filtering for success phrases destroys failure evidence.

## 9. When a tool change is necessary

Name the missing capability or reproducible defect, the owner, the request/build that shows it, and the expected observable result. Then follow the current `CLAUDE.md` and `docs/SHIPPING_A_CHANGE.md`.

For this package, that includes reading touched files and interfaces, checking for an active cold run before editing tools, anchored patch records, regression proof, appropriate suites/gates, version/changelog updates, and factory-set recertification when required. Apply repository release procedures only within the user's authorized task; inspecting an uploaded package does not authorize pushing to a remote.

Read generated output as evidence. Fix the generator or supported authored input; do not patch vendored copies of addons inside workspaces. Keep source patches, investigations, cold-run evidence, and scratch in the locations documented by `docs/FILING.md`.

When editing GDScript, run the repository's `gdcheck.py` and the appropriate Godot load/runtime check. A grammar check cannot prove engine API compatibility. A headless engine run cannot measure rendered frame time.

For performance work, preserve the package's Compatibility-renderer target and measure representative camera stations, draw submissions, CPU/GPU frame time, and memory as relevant. The repository's draw-call findings are measurements for its scenes, not a universal rule that geometry or shaders never matter.

## 10. Handoff at the end of an assistant session

Use this compact record so another assistant can resume without treating memory as source:

```text
Goal and current work type:
Factory version / checkout identity:
Workspace / batch / mission / source request:
Effective request and selected candidate seed:
What changed, with owning files:
Commands run and exit codes:
Produced package and build/attempt identity:
Checks passed / failed / skipped / not run:
Unsupported requests and remaining findings:
Human review status:
Next action and exact source to read:
```

After context loss, re-read the files needed for the next action. Do not “continue” by copying remembered function signatures into new patches.

## 11. Ready-to-use opening instruction

Give the assistant this guide alongside the factory. If adopted into the repository, place the full guide under `docs/` and add a short pointer from the existing `CLAUDE.md` and an applicable `AGENTS.md`. Keep one shared operating guide rather than separate, drifting instructions for each model. This review has not modified those repository files.

> Use the attached/current Gabagool Factory as an existing toolchain. Start at its actual root, read applicable repository instructions, and identify the factory version, workspace, and mission. Use `START_HERE.md` for execution, `USING_THE_FACTORY.md` for ownership, and scoped `rg` searches to trace only the relevant inputs and producers. Before building, distinguish settings that drive generation from recorded intent and missing capabilities. Prefer the existing `make` command or staged CLI over new scripts. Preserve full logs and identify the exact build behind every claim. Fix defects in the owning tool, never generated output. Report what ran, what passed, what remains unproven, and whether the result received a human walk. If the request requires a new capability, describe the smallest reusable addition before implementing it within the authorized scope.

## 12. Inspection record and source pointers

This review left the uploaded package unchanged. The ZIP uses Windows-style path separators; extraction for this review normalized separators into an isolated inspection directory. Six key extracted files were compared byte-for-byte with the archive, including `CLAUDE.md`, `START_HERE.md`, `PIPELINE_MAP.md`, `USING_THE_FACTORY.md`, and both CLI entry/implementation files. All matched. All ten installed tool version strings matched their manifest pins after removing tool-name prefixes; this is not a new certification run.

| Executed here | Result |
|---|---|
| CLI help, `make --help`, `walk --help` | Exit 0 |
| Initialize isolated workspace | Exit 0 |
| Import packaged first-level batch | Exit 0; explicitly warned about the five populated unbuilt fields |
| Plan `restaurant_row_001 --json` | Exit 0; 3 candidates, 12 graybox jobs |
| Six documented CLI argument forms | Accepted by the current parser |
| Direct time-preset resolution | Five supported time slots resolved; midnight plus rain resolved to Heavy Rain |
| Direct all-out picker case | Returned `every_out=True` |
| Doctor | Exit 3; Blender/Godot absent and Python dependencies missing |
| Full generation, GUI launch, Godot walk, GPU bake/performance | Not run |

Primary source locations, relative to the factory root:

- `factory.manifest.json` — certified version set.
- `level_factory/apps/cli/main.py` — flags, help, documented exit codes.
- `level_factory/apps/cli/commands/__init__.py` — `_brief_model`, `UNBUILT_BRIEF_FIELDS`, `cmd_make`, `cmd_batch_create`, `_preset_for`, `cmd_walk`, `cmd_export`.
- `level_factory/packages/core/models.py` — `MissionBrief` and functional signature.
- `level_factory/packages/pipeline/pick.py` — ranking, evidence readers, all-out fallback.
- `level_factory/packages/jobs/runner.py` and `scheduler.py` — execution, cancellation infrastructure, cache and findings handling.
- `level_factory/apps/desktop/` and `packages/service/facade.py` — existing desktop screens and action bindings.
- `level_factory/schemas/mission.brief.schema.json` — current descriptor, not full semantic validation.
- `level_factory/tests/unit/test_make_and_pick.py`, `test_time_of_day_presets.py`, and `tests/service/test_facade.py` — relevant existing verification surfaces; their suites were not executed in this review.

Refresh this guide when commands, field support, ownership, or package versions change. Keep executable help and current source authoritative.
