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

## Design, proposed 2026-10-10 (nothing built yet)

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
