# What a stranger's first level costs (roadmap 202)

**Question.** Roadmap 202's bar is the walker's: a consumer installs Blender
and Godot and nothing else, unpacks the factory, and gets levels out. What
stands between a fresh machine and a first level today, counted the way
CLAUDE.md counts a cold run: every question, edit or workaround is an
intervention.

This folder measures the install path and changes nothing in it. Everything
below was read on 2026-10-10 from the checkouts named, while cold run 9222 was
in flight. Nothing in a tool repo was run until that run ended.

## Measured

### 1. The building library does not travel

- **The default lot library is Deli Counter's build directory.**
  `level_factory/apps/cli/commands/__init__.py`, `_default_lot_library`:
  `build = Path(str(deli)) / "build"`.
- **Deli Counter's git ignores every mesh in it.**
  - `deli_counter/.gitignore`: `build/*.glb`, with `!build/*.manifest.json`
    let back in.
  - On this machine `build/` holds 3,385 files (149 MB). Of those, 146 are
    GLBs (71 MB) and 568 are tracked. The 568 are manifest, gameplay, slots,
    lights and godot_import JSON. No GLB is tracked.
- **The package is `git archive`, so it carries tracked files only.**
  `tools/make_factory_package.ps1` says so in its first line: "build\ outputs
  ... never enter a git object, so it cannot enter this zip".
- **The library's index starts from the GLBs.** `building_library.index` reads
  the ids from `*.glb` and needs `.glb`, `.gameplay.json` and `.slots.json`
  (`REQUIRED`). With no GLB, every list comes back empty.
- **What the stranger gets instead.**
  - `_default_lot_library` returns "keeps its generated building -- the
    library at ... has no family for archetype X". That sentence names the
    wrong cause: the library is not missing a family, it is empty.
  - The level then places one generated shell N times, with no Empties. That
    is roadmap 37's "one building four times", which the library default
    (LF 0.145.0) exists to prevent.
  - Nothing fails, so the stranger does not learn that their levels are not
    ours.
- **Freshness after unpacking: read, not yet measured.**
  - **How Level Factory checks it.** `building_library.stale_shells` calls a
    shell stale when the newest of Deli Counter's `GEOMETRY_SOURCES` has a
    later mtime than the shell's GLB. Its docstring already says "a fresh
    clone ... marks everything stale".
  - **What the package does to those times.** `git archive` stamps every
    tracked source with HEAD's commit time. So a library copied in beside
    them reads as stale wherever it was built before that commit, whatever
    the commit changed.
  - **What the stranger is then told.** `_write_site_spec` (in
    `apps/cli/commands/__init__.py`) prints `STALE LIBRARY` and, as "the
    fix", `python build.py --all`. That is a whole-library
    rebuild in Blender. It is reported, not enforced, so the run goes on, but
    the line reads as an instruction.

**The library is the only ignored thing a level reads.** Every tool repo's
ignored files were listed by folder on 2026-10-10, setting aside caches,
`__pycache__` and `.godot/`:

| repo | ignored | read by a level? |
|---|---|---|
| Deli Counter | `build/`: 837 files, 82.2 MB (GLBs 73.2 MB) | **yes**: the lot library |
| Deli Counter | `build/floorplans/`: 1,980 files, 33.0 MB | no: review images |
| Pixelcoat | `build/`, 372 | no: old skin builds. Level Factory reads `profiles/themes/`, which is tracked |
| Lot | `specs/`, 322 | no: reference and example sites with built shells copied in |
| Lot | `dist/`, 56 | no |
| Laser Tag | `*.uid`, `project.godot` | no: Godot writes them on import |
| Zoo | `_census`, `_preview*` | no |
| Lux | `walk/` | no |
| Dispatch | `_lf_smoke_out/` | no |

Deli Counter's own `build_freshness.py` called the library on this disk "146
shell(s) newer than lights.py -- up to date".

### 2. The doctor checks the wrong interpreter

- **There are two interpreters.** Level Factory's scheduler runs every Python
  tool with `tools.local.json`'s `python_executable`:
  `packages/jobs/scheduler.py:453`,
  `self.installation.get("python_executable", "") or "python3"`.
- **`doctor` checks the other one.** Its "python" check reads
  `sys.version_info`, the interpreter running Level Factory itself
  (`packages/tools/doctor.py`).
- **It never asks the tools' interpreter anything.** No version, and no
  import.
- **So `doctor` can PASS on a machine where no tool can start.**
- **The blank-path fallback is `python3`.** On a fresh Windows machine,
  `python3` is the Microsoft Store's app-execution alias. It runs no Python.
- **On this machine they agree, by luck.** `python3` and `python` resolve to
  the same 3.14.4 interpreter, and every cold run's `tools.local.json` leaves
  `python_executable` blank.
- **The adapters' own fallback is dead.** Each reads
  `context.get("python_executable") or "python"`, and the scheduler always
  fills the context first.

### 3. Which missing packages are on the level-making path

Blender 5.1.1's bundled Python is 3.13.9. It carries numpy, pip and pytest,
and lacks Pillow, pygltflib, jsonschema, PyYAML and cairosvg (roadmap 202,
measured 2026-10-07).

These are the import sites, from a search of every tracked `.py` in the ten
tool repos. "Top" is a module-level import; "lazy" is inside a function.

| package | on the path | where |
|---|---|---|
| Pillow | yes | Pixelcoat core, top: `image_io`, `atlas`, `alpha`, `decals`, `material_grammar`, `signage`, `transforms`, `pipeline_generation_7`. Patina, top: `decals`, `families`, `palette`, `photo`, `templates`, `trim`. |
| pygltflib | yes | Patina `gltf_io`, top. Deli Counter, lazy: `circulation`, `portable_building`, `themed_tscn`, `zfight_gate`. The presentation adapter hashes the first three as its own sources. |
| jsonschema | yes, through Patina | Patina `manifest`, top. Deli Counter's `validate._schema_check` skips with a note when it is absent. |
| PyYAML | no | Deli Counter's `spec_loader.load_spec`, only for a `.yaml` spec. The factory writes JSON. |
| cairosvg | no | Deli Counter's `migrations/ai_review.py` only. It is advisory and never gates. |

Pillow elsewhere is in developer tools and tests only:
- Level Factory's `tools/drip_assets.py`;
- Zoo's mint tools;
- Lux's film probes.

`import_probe.py` measures the top-level half of this under a real
interpreter. The lazy half rests on the search alone.

**Measured, 2026-10-10, after cold run 9222 ended.** Each entry point was
loaded under both interpreters, isolated (`-I`) and writing no bytecode
(`-B`). Every tool repo's `git status` was empty afterwards.

| entry point | Blender 5.1.1's Python 3.13.9 | this machine's 3.14.4 |
|---|---|---|
| Level Factory `apps.cli.main` | OK | OK |
| Level Factory `run_presentation_compose.py` | OK | OK |
| Deli Counter `new_level.py`, `build.py` | OK | OK |
| Deli Counter `portable_building`, `themed_tscn`, `circulation`, `zfight_gate` | OK | OK |
| Deli Counter `deli_counter.py` | MISSING bpy | MISSING bpy |
| Lot `lot.py`, `walktest.py` | OK | OK |
| Pixelcoat `pixelcoat.cli.main` | **MISSING PIL** | OK |
| Patina `patina.cli`, `patina.surface_dressing` | **MISSING pygltflib** | OK |
| Dispatch `dispatch.__main__` | OK | OK |
| Zoo `tools/zoo_cli.py` | OK | OK |

- **Under Blender's Python, two of the level path's tools cannot start:**
  Pixelcoat and Patina.
- **Patina names only its first gap.** It fails on `gltf_io`'s pygltflib
  before it reaches `manifest`'s jsonschema, which the search found at the
  top of a module too.
- **Deli Counter's lazy pygltflib is the search's finding, not the probe's.**
  The four modules load because the import sits inside the functions that
  read a GLB.

**Found alongside: Level Factory's Deli Counter probe has never answered.**
- `adapters/deli_counter`'s `probe` runs `python -m deli_counter contract`.
- `deli_counter.py` imports `bpy` at its line 33, so that command exits 1
  with `ModuleNotFoundError: No module named 'bpy'` on any interpreter that
  is not Blender's embedded one. Measured on 3.14.4, from the repo.
- `run_contract_probe` reads the failure as "the tool doesn't support it".
  The probe falls back to the base probe's version and capabilities, so
  nothing visible broke, and nothing could have told anybody.

### 4. Smaller things a stranger meets

- **Deli Counter's Blender search stops at 4.5.** `build.find_blender` tries
  the flag, then `$BLENDER`, then PATH, then
  `C:\Program Files\Blender Foundation\Blender 4.5` down to 4.1. A Blender
  5.x from the official installer is not on that list.
  - Level Factory passes `--blender` from `tools.local.json`, so this bites
    only when that field is blank, which is what `init` writes.
- **The package's last line points at the wrong page.** It sends the
  recipient to `USING_THE_FACTORY.md`, which is the operator's charter. It
  does not say how to install anything.
- **The cold driver is bash.** A Windows machine with only Blender and Godot
  has no bash: Git for Windows is what supplies it here.
- **Either Godot build will do.** Godot's Windows download carries a
  windowed `.exe` and a `_console.exe`, and every cold run here has driven
  the console one. This machine's `$DC_GODOT` names the windowed one.
  - Measured 2026-10-10: a headless `-s` script that prints and pushes an
    error, run under each with output piped (`godot_pipe.gd`, here).
    Both exit 0, with the line on stdout and the error on stderr.
  - So discovery takes whichever it is given. A preference for the console
    build was drafted and dropped on this measurement.
- **No Linux to test on.** This machine has no WSL distribution
  (`wsl.exe -l -v` prints its usage). So the Linux half is checked by
  reading, and the first real Linux run will be the collaborator's.
- **Blender 5.1.1's Python carries more than numpy.** Its site-packages also
  hold OpenImageIO, fastjsonschema, attrs, requests, pip, setuptools, pytest
  and zstandard. None of them is Pillow, pygltflib or jsonschema.
  - It ships a `README.txt` that says the directory "exists so that 3rd
    party packages can be installed here".
  - It ships a `sitecustomize.py` that puts `blender.shared` on the DLL path
    for the standalone `python.exe`. The factory's tools use none of the
    modules that need it.

## Shipped, 2026-10-10

- **Level Factory 0.167.0** (design steps 3 and 4).
  - `init` fills `tools.local.json`. The repositories are the checkouts the
    manifest names. The factory is found by walking up for
    `factory.manifest.json`, after the first draft's `parents[3]` failed
    `test_sibling_locator`.
  - The executables come from a flag, then `factory.local.json`, the
    environment, PATH, and Blender's installs.
  - `setup` writes `factory.local.json`.
  - A blank `python_executable` is the interpreter running Level Factory
    everywhere.
  - The doctor's `tools_python` check asks that interpreter its version
    and its imports.
- **Level Factory 0.168.0** (design step 2): `setup --venv`.
- **This machine** ran `setup` once. Its `factory.local.json` names
  `C:/blender/blender.exe` and Godot 4.7's console build.
  - A workspace `init` makes from it holds a `tools.local.json` identical to
    cold run 9222's.
  - So the cold driver stops copying the previous run's file. Instead it
    runs the doctor and stops on a FAIL or a NOT_CONFIGURED.
  - It also finds the factory from its own path, as `stage_batch.py` now
    does.

**Measured with the launcher drafted in `_scratch/front_door`.**
`factory.cmd` was run against a scratch factory holding 0.168.0's draft.
- With `BLENDER` set (this machine sets it globally), it ran Level Factory
  under Blender's 3.13.9.
- That run's `setup` reported, unprompted, the gap this folder measured:
  `tools_python 3.13.9 at C:\blender\5.1\python\bin\python.exe ...
  cannot import PIL.Image, pygltflib, jsonschema; make the factory its own
  with level-factory setup --venv`.
- With `BLENDER` unset, it fell through to PATH's 3.14.4.
- With `FACTORY_PYTHON` set, it ran that.

**Then the rest of the design, the same night.**
- **Level Factory 0.169.0:** `make`, one level from a batch start to finish,
  and `pick`, which moves the cold driver's candidate rule into Level Factory.
  `pick` agrees with the root script on all 46 cold workspaces.
- **The front door:** `START_HERE.md`, `factory.cmd` and `factory.sh`, and
  `docs/first_level/`, which holds cold run 9222's batch.
- **The package:** `tools/make_factory_package.ps1` carries Deli Counter's
  library, stamped later than its sources, and leaves the run record out. The
  first lean package was 72.1 MB, against about 987 MB with the record.

## Install test 1, 2026-10-10, 04:53 to 05:29

**The test.**
- **The package:** `gabagool_factory_package_20261010_0450.zip`, at root
  `e8a8938` and Level Factory `fc5600e` (0.169.0).
- **The unpack:** `Expand-Archive` into a folder that had never held a
  factory, `C:\stranger_202\gabagool`.
- **What was typed:** `START_HERE.md`'s commands, into cmd.exe there, by
  `install_test.cmd`. The logs are in `install_test_1/`.

**The one deviation, counted: `setup --venv` was not run.** It downloads
Pillow, pygltflib and jsonschema from PyPI, and downloads on this machine
wait for the walker's yes.
- `setup --python <this machine's 3.14.4>` stood in for it. That Python
  carries the three packages.
- Level Factory itself still ran under Blender's own 3.13.9, which the
  launcher found through `$BLENDER`.
- So the real install of the three packages into Blender's Python is
  unproven.

**What the unpack did, nothing else touched:**

| step | exit | what it printed |
|---|---|---|
| `setup` | 0 | every repository found under `C:/stranger_202/gabagool`; Blender from `$BLENDER`; `tools_python` PASS; worst WARN, all eight WARNs the stale certified table |
| `make` | 0 | 31.8 minutes; `init` filled every path from `factory.local.json`; the batch drew from `C:\stranger_202\gabagool\deli_counter\build`, where a tracked-files package would have drawn nothing; no `STALE LIBRARY` line |
| `walk` | 0 | preview built; walk bot climbed both ladders; shot bot five stations OK |

**The level is cold run 9222's, figure for figure.** The same brief, seed
base, tools and machine, from a different folder:

| | cold run 9222 | install test 1 |
|---|---|---|
| shell leg | 3 distinct, 0 blockers of 52 | 3 distinct, 0 blockers of 52 |
| pick | seed_9104, the same three lines | seed_9104, the same three lines |
| art leg | 0 blockers of 74 | 0 blockers of 74 |
| deal | `b0=scrapple_sons_deli` | `b0=scrapple_sons_deli` |
| bake | 479 models, 4,259 users, 100.5 s | 479 models, 4,259 users, 100.2 s |

**What it found. Each item would have been a stranger's question:**
- **`factory` was "not recognized".**
  - Git's bash sets `NoDefaultCurrentDirectoryInExePath=1`, and a cmd.exe it
    starts does not run commands from the current folder.
  - A cmd window opened from Explorer does not have that variable. PowerShell
    never runs a command from the current folder by name, and some hardened
    setups set the variable.
  - So the page now says `.\factory` everywhere on Windows, and the counted
    run typed that.
- **Eight `drift vs certified` WARNs on `setup`'s doctor,** for exactly the
  tools the package carries. Level Factory 0.170.0 re-grounds the table, with
  the real-tool smoke licensing it, and the stand-in repos with it.
- **Hints named `level-factory`, which an unpacked factory does not have.**
  0.170.0 makes them say what the launcher says was typed.
- **The walk preview put the player at (0, 1.5, 3)**, "default (no
  markers)". An export's `mission.tscn` loads its content at runtime, so its
  text has no markers. 0.171.0 spawns at the package's own `player_start`:
  the getaway van, (53.85, 0, 16.965).
- **The shot bot's five frames were 100% black, and all five read OK.**
  - It photographed during the shader warm-up's black cover (Level Factory
    0.100.0).
  - Its two measures, void (magenta) and jitter (a frame against its twin),
    cannot see a frame that shows nothing.
  - The same `walk` on 9222's own workspace did the same.
  - August's `lot_demo_001` preview still rendered with the same script, and
    9222's rendered with `site.tscn` but not `mission.tscn`.
  - 0.171.0 holds the warm-up and fails a one-colour frame. On 9222's preview
    the five frames then read mean luma 100.9 to 191.3, and **two stations
    FAIL on jitter**: Ladder_ladder_0_base at 3.60% and Ladder_ladder_1_top at
    2.33%, against a 2.0% gate. Their cause is not established.
- **Hints named commands a stranger lacks:**
  - the walk's `& "<godot>" ...` is PowerShell's call operator, an error in
    cmd;
  - the export's `godot --headless ...` and `python tools/walk_export.py
    ...`;
  - `HANDOFF.md`'s walk instruction.

  0.171.0 points every one at `walk`.

**The count.** Everything in the test was typed from the page. That makes 1
intervention, the stand-in for the download, and 0 otherwise. The findings
above are the page's and the tools' defects, which a stranger would have
paid for in questions, and each is fixed in the release named.

**Not yet tested:**
- **the real `setup --venv`,** which needs the walker's yes for a download;
- **Linux,** which needs a Linux machine. Read for it instead: Level
  Factory's job runner already gives a POSIX child its own session. The
  Windows-only lines on the level path are install paths that will simply not
  exist there, and developer tools.
- **A second install test,** at the releases above, from a new package.

## Install test 2, 2026-10-10, 05:53 to 06:30

**The test.** The same, at the releases install test 1's findings produced.
- **The package:** made from root `67a75ec` and Level Factory `bb8ccfd`
  (0.171.0), as `gabagool_factory_package_20261010_0553.zip`.
- **The unpack:** into a new folder, `C:\stranger_202b\gabagool`.
- **What was typed:** the same `install_test.cmd`, through
  `install_test_2.sh`, which also builds and unpacks the package. Logs are
  in `install_test_2/`.
- **The same counted deviation:** `setup --python` for `--venv`.

| step | exit | what it printed |
|---|---|---|
| `setup` | 0 | every tool PASS (they were eight WARNs); the only WARN is Windows' long-paths reminder; `then run: .\factory -C ... doctor` |
| `make` | 0 | 31.5 minutes; 0 of 52 and 0 of 74 blockers; seed_9104; `b0=scrapple_sons_deli`; 479 models and 4,259 users baked, 96.2 s; the export's hint `.\factory -C ... walk restaurant_row_001 --play` |
| `walk` | 1 | the player at `anchor:player_start (...getaway_van_crew_spawn_0) (x=53.85, y=0.6, z=16.965)`; walk bot climbed both ladders; shot bot frames carry a picture (void 60.66% on the exterior); two ladder stations FAIL on jitter, 3.64% and 2.32% |

**What each fix did:**
- **Level Factory 0.170.0 held.** It put every tool through the doctor at
  PASS and named `.\factory`.
- **0.171.0 held.** It put the player at the van, gave the review frames a
  picture, and named `walk` in every hint.
- **Walk's exit 1 is roadmap 225.** These are the same two stations, and the
  same texture sparkle, that the gate reads as a fight. A stranger would
  have read "this level does not pass its own traversal/visual check" as a
  broken level. Level Factory 0.172.0, released after this test, notes them
  as sparkle and passes them. A control z-fight still fails it.

**The count:** 1, the stand-in for the download, as before. The walk's
false failure is the one finding, fixed after the test.

**What it certified: factory 1.35.0.** `factory.manifest.json` names the set
this test ran, and `verify-manifest` reads all ten OK; it had read eight DRIFT
and one INCOMPATIBLE that morning:

| tool | version |
|---|---|
| Deli Counter | 0.205.0 |
| Dispatch | 0.5.2 |
| Laser Tag | 0.25.0 |
| Level Factory | 0.171.0 |
| Lot | 0.105.0 |
| Lux | 0.72.0 |
| Patina | 0.30.0 |
| Pipeline | 0.6.0 |
| Pixelcoat | 0.62.0 |
| Zoo | 1.94.0 |

Each tool is tagged at the commit tested, and the factory at
`factory-v1.35.0`. Level Factory 0.172.0 is not in this set.

## Install test 3, 2026-10-10, 07:49 to 08:27

**The test.** The same, at the releases install test 2's one finding and
cold run 9223 produced.
- **The package:** made from root `ebfaf4d`, Level Factory `8a35490`
  (0.172.1) and Lot `e3b8b46` (0.106.0), as
  `gabagool_factory_package_20261010_0749.zip`, 71.7 MB.
- **The unpack:** into a new folder, `C:\stranger_202_3\gabagool`.
- **What was typed:** the same `install_test.cmd`, through
  `install_test.sh 3`, which also builds and unpacks the package and, new,
  prints every doctor row of `setup` that is not PASS. Logs are in
  `install_test_3/`.
- **The same counted deviation:** `setup --python` for `--venv`.

**A first attempt was stopped at its unpack,** before `setup` ran. Cold run
9223's doctor had WARNed `tool:lot ... drift vs certified 0.105.0`, and its
notes had named only the long-paths WARN beside it. A package at Level
Factory 0.172.0 would have printed that advice to a stranger. Level Factory
0.172.1 re-grounds the row; the attempt's folder and zip were removed and
nothing from it counts.

| step | exit | what it printed |
|---|---|---|
| `setup` | 0 | every tool PASS, `tool:lot vLot 0.106.0`; the only WARN is Windows' long-paths reminder |
| `make` | 0 | 32.1 minutes; 0 of 52 and 0 of 74 blockers; seed_9104; `b0=scrapple_sons_deli`; 479 models and 4,259 users baked, 102.2 s; the export's hint `.\factory -C ... walk restaurant_row_001 --play` |
| `walk` | 0 | the player at `anchor:player_start (...getaway_van_crew_spawn_0) (x=53.85, y=0.6, z=16.965)`; walk bot climbed both ladders; shot bot five stations OK, fighting 0.00% to 0.12%, `Ladder_ladder_0_base` and `Ladder_ladder_1_top` noted `sparkle: small flips of one texture, not a fight` at jitter 3.61% and 2.35% |

**What each fix did:**
- **Level Factory 0.172.0 held.** The two stations that failed test 2's
  walk on sparkle pass, named as sparkle. The exterior reads fighting
  0.0%.
- **0.172.1 held.** `tool:lot` reads PASS at 0.106.0.
- **Lot 0.106.0 is in the set.** The level is 9223's: the same seed, deal
  and bake figures as 9222's, with the lamp clear of the band.

**The count:** 1, the stand-in for the download, as before. No finding.

**What is left on a stranger's first `setup`:** one WARN,
`windows_long_paths`, which the doctor prints on every Windows machine
without reading the flag (roadmap 227, `docs/findings/long_paths/`).

**What it certified: factory 1.36.0.** `factory.manifest.json` names the set
this test ran, and `verify-manifest` reads all ten OK:

| tool | version |
|---|---|
| Deli Counter | 0.205.0 |
| Dispatch | 0.5.2 |
| Laser Tag | 0.25.0 |
| Level Factory | 0.172.1 |
| Lot | 0.106.0 |
| Lux | 0.72.0 |
| Patina | 0.30.0 |
| Pipeline | 0.6.0 |
| Pixelcoat | 0.62.0 |
| Zoo | 1.94.0 |

Level Factory and Lot are tagged at the commits tested, and the factory at
`factory-v1.36.0`; the other eight repos' tags from 1.35.0 stand.

## Design, proposed 2026-10-10 (kept as it was first proposed; all built since)

Each step names the intervention it removes.

1. **One setup command, run by Blender's own Python.**
   - Two launchers at the factory root find Blender: `factory.cmd` for
     Windows and `factory.sh` for Linux. They look at `$BLENDER`, then PATH,
     then the usual installs (5.x included). They then run
     `-m level_factory` with the `python` beside it.
   - Level Factory needs no third-party package to start. Measured
     2026-10-07: its CLI runs under 3.13.9.
   - Removes: "install Python".
2. **`setup` makes a venv from that Python and installs three packages.**
   - The venv uses `--system-site-packages`, so it keeps Blender's numpy.
   - It installs Pillow, pygltflib and jsonschema at pinned versions.
   - It leaves the user's Blender untouched and needs no admin rights.
   - It needs the network once.
   - Removes: "pip install what?".
   - **The walker's call: pip at setup, or wheels in the package.** Wheels
     in the package work offline, but they tie the package to one Python
     version. Blender's Python moves with Blender's release.
3. **`init` fills `tools.local.json` instead of writing it blank.**
   - The tool repositories come from the factory root, as Level Factory's
     siblings.
   - Blender and Godot come from the chain above, or from what `setup`
     recorded.
   - `python_executable` is the venv.
   - Removes: "edit ten paths".
4. **`doctor` asks the tools' interpreter.** It reports that interpreter's
   version and whether it can import Pillow, pygltflib, jsonschema and
   numpy. A blank `python_executable` stops falling back to `python3`.
   - Removes: a PASS that no tool can run under.
5. **The package carries the library.**
   - It includes Deli Counter's built shells and their sidecars, at the
     certified Deli Counter.
   - It checks them fresh with `build_freshness.py` before zipping. It
     stamps them later than the sources, so the consumer's mtime check
     agrees with the owner's verdict.
   - Removes: levels that are one building N times, and a `build.py --all`
     instruction.
6. **One page, `START_HERE.md`:** install Blender and Godot, unpack, setup,
   doctor, one brief, run, approve, export, open in Godot.
7. **The test.** Unpack into a fresh path, not `C:\Projects\gabagool_studios`,
   follow only that page, and count every question or edit. Then fix and
   repeat until the count is zero.
