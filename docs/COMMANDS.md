# Commands, and the four that bite

Every entry here was run from `C:\Projects\gabagool_studios\gabagool_factory`
unless it says otherwise. **The working directory is part of the command** —
three of the four traps below are a command run from the wrong one.

This file is for mechanics. The reasoning that governs when to run any of it is
in `CLAUDE.md`; the architecture is in `PIPELINE_MAP.md`; the content routing is
in `USING_THE_FACTORY.md`.
The performance policy a measurement is taken against is `docs/PERFORMANCE_CONTRACT.md`.

---

## The four that have cost a round trip

### 1. `pytest -q` in level_factory prints no pass/fail line

Its conftest replaces pytest's summary with its own sentence, so `| tail` shows
skip notes and a closing remark and **no count**. Reading the tail of that log
and calling it clean is a mistake this repo has already paid for once
(`CLAUDE.md`, the verification section). Two honest reads:

```bash
cd level_factory && python -m pytest -q > out.txt 2>&1; echo "exit=$?"
```

Exit `0` is the reliable signal. For a count, tally the progress characters —
`.` pass, `s` skip, `x` xfail, `F`/`E` failure:

```bash
python -c "import re,sys;from collections import Counter;L=open('out.txt',encoding='utf-8',errors='replace').read().splitlines();c=''.join(re.sub(r'\s*\[\s*\d+%\]$','',l) for l in L if re.search(r'\[\s*\d+%\]$',l));print(len(c),dict(Counter(c)))"
```

### 2. `gdcheck.py` is run from the factory root, not from a tool repo

The path argument is relative to wherever you are, and the script lives at the
root:

```bash
python tools/gdcheck.py level_factory/tools/wet_ab.gd
```

Running it from inside `level_factory/` gives
`can't open file '...level_factory\tools\gdcheck.py'`, which reads like the
script is missing.

### 3. A script that imports a tool package needs that repo on `PYTHONPATH`

`python -m pixelcoat.cli.main …` works from inside `pixelcoat/` because the
package is right there. A *script* living elsewhere that does
`from pixelcoat.core import …` does not, and fails with
`ModuleNotFoundError: No module named 'pixelcoat'`:

```bash
cd pixelcoat && PYTHONPATH="C:\Projects\gabagool_studios\gabagool_factory\pixelcoat" python /path/to/script.py
```

### 4. `PIPELINE_ROADMAP.md` carries a generated index — regenerate, then check

Never hand-edit the block marked `BEGIN GENERATED`. After editing an item:

```bash
python tools/roadmap_status.py --write
python tools/roadmap_status.py --check
```

`--check` must print `index matches its items`. The full editing procedure,
including why anchors must match the whole status block, is the
`gabagool-roadmap-edit` skill.

---

## Tests, per repo

The layout is not uniform. Run from inside the repo.

| Repo | Command | Note |
|---|---|---|
| `level_factory` | `python -m pytest -q` | see trap 1; 12 skips are the real-tool smoke, needing `LF_TOOLS_DIR` |
| `pixelcoat` | `python -m pytest -q` | |
| `lot` | `python -m pytest -q` | |
| `zoo` | `python -m pytest -q` | |
| `patina` | `python -m pytest -q` | |
| `dispatch` | `python -m pytest -q` | |
| `pipeline` | `python -m pytest -q` | |
| `deli_counter` | `python -m pytest -q` | tests are `test_*.py` at the REPO ROOT, not under `tests/` |
| `lasertag`, `lux` | — | Godot addon repos, no Python suite; check `.gd` with `gdcheck.py` |

**In Pixelcoat, a release bumps `pixelcoat/version.py`'s `_FALLBACK` with
`VERSION`.**
- `tests/test_version_is_single_sourced.py` holds the two equal.
- Pixelcoat 0.58.0 shipped with `_FALLBACK` at 0.57.0. Its suite had run
  before the release patch, so it never saw the bump; 0.59.0 fixed it.
- In any repo, run the suite AFTER the VERSION bump when the repo has
  version-coupled tests.

**In Deli Counter, prove a test fails BEFORE `build.py --all`, not after.**
- `build_freshness.py` compares modification times, and `check.py` (the
  pre-commit hook) runs it.
- `git stash` then `git stash pop` on a file in its `GEOMETRY_SOURCES`, such
  as `presets.py`, writes the same content back with a new time. Every shell
  built before it then reads as stale, and the hook refuses the commit.
- Deli Counter 0.188.0 paid one refused hook (about ten minutes) and a
  second `build.py --all` (6.5 minutes) for it.
- So stash, prove and pop first, then rebuild once.
- Never set the time back instead. A source older than its build is the
  direction the guard's docstring calls unsafe.

## Hygiene: is everything filed where `docs/FILING.md` says?

```bash
python tools/factory_hygiene.py --check     # LOOSE at the root, untracked records, index drift; exit 1 on any
python tools/factory_index.py --write       # regenerate docs/findings, patches, tools ... READMEs after adding a file
python tools/factory_retire.py              # what the retention rule would remove (dry run); --apply removes it
```

The check runs at the end of every cold run (`cold_run.py --end` prints its
one line) and is step 8 of `docs/SHIPPING_A_CHANGE.md`. A `(undescribed)` in
an index is a file with no docstring or heading: give it one.

## GDScript, before it leaves this machine

```bash
pip install gdtoolkit
python tools/gdcheck.py <path/to/file.gd>
```

Clean output is `parses, and none of the four known traps`. What the four traps
are, and why a probe's launch mode is part of writing it, is in `CLAUDE.md`.

## A cold run

Full procedure and the rules while the clock runs: `docs/COLD_RUN.md`. The
shape, with `<id>` like `cold_9078`:

```bash
python tools/cold_run.py --selftest
python tools/cold_run.py --begin <id>
python -m level_factory -C workspaces/<ws> batch create docs/cold_runs/<id>/batch.json
python -m level_factory -C workspaces/<ws> plan <mission>
python -m level_factory -C workspaces/<ws> run <mission>
python -m level_factory -C workspaces/<ws> approve <mission> brief_approved
python -m level_factory -C workspaces/<ws> approve <mission> candidate_selected --candidate <mission>.candidate.seed_<n>
python -m level_factory -C workspaces/<ws> approve <mission> functional_shell_locked
python -m level_factory -C workspaces/<ws> run <mission> --art --gameplay
python -m level_factory -C workspaces/<ws> export <mission> --mode portable-godot
python tools/cold_run.py --end
```

**The same shape as one script: `tools/cold_drive/`.**

    python tools/cold_drive/stage_batch.py <N> <PREV> "<what this run tests>"
    bash tools/cold_drive/cold_drive.sh <N> <PREV> <mission> <seed|auto> > docs/cold_runs/cold_<N>/driver.log 2>&1
    python tools/cold_run.py --end

- **The export bakes the lights by default** (Level Factory 0.144.0).
  `EXPORT_FLAGS=--no-bake-lights` skips the bake. Runs before 0.144.0
  passed `EXPORT_FLAGS=--bake-lights`, which still parses.
- **Once per machine: `python -m level_factory setup --blender <exe>
  --godot <exe>`.** It writes `factory.local.json` at the root (ignored by
  git). Since Level Factory 0.167.0 the driver's `init` fills each run's
  `tools.local.json` from it. The driver then runs the doctor, and stops on
  a FAIL or on anything NOT_CONFIGURED. It used to copy
  `workspaces/cold-<PREV>-ws/tools.local.json`, and cold run 9194 stopped
  when that workspace had been retired. Cold run 9223 was the first run
  without the copy.
- **A mission whose last run's workspace is gone.** `stage_batch.py`
  copies `batch.json` and `briefs/` out of `docs/cold_runs/cold_<PREV>`, so
  stage from the mission's own last run. `<PREV>` now matters to the
  driver only for the findings diff. A diff against a different mission's
  workspace reads as an empty count.
- **The driver and `stage_batch.py` find the factory from their own path,**
  so they run from wherever the factory is unpacked.
- **One level without the clock:** `python -m level_factory -C <new folder>
  make <batch.json>` runs the same legs and the same pick (Level Factory
  0.169.0). It does not hash the repos, and it is not a cold run.
- **What the driver does.** It stops at the first failing leg and keeps the
  art and export legs' full output beside the batch (`art.log`,
  `export.log`). A grep that kept only success lines once threw away the one
  error a stopped export printed.
- **What it leaves to you.** It does not call `--end`; a stopped run leaves
  `_runs/cold/ACTIVE` until it is ended on purpose.
- **Stage with the script.** `stage_batch.py` sets the batch id as well as
  the description. Runs 9148 to 9151 were staged by hand-copying the
  previous `batch.json` and editing only the description, and all four ran
  as batch `cold_9147`.

`-C` names the **workspace** (the folder holding `.level_factory/`), never the
factory root. Record interventions with `--note`, identical re-runs with
`--retry`, and things you only looked at with `--observe`; the three are
reported apart on purpose.

**The clock hashes the ten tool repos only.** Verified against
`_runs/cold/<id>/before.json`: the hashed top-level directories are exactly
`deli_counter dispatch lasertag level_factory lot lux patina pipeline pixelcoat
zoo`. Editing `CLAUDE.md`, `docs/` or `PIPELINE_ROADMAP.md` at the root cannot
change the count — editing anything inside those ten can, whether or not
anybody writes it down.

## Health and grading

```bash
python -m level_factory -C workspaces/<ws> doctor     # before the clock starts
python tools/check_all.py                             # 0 clean, 1 found, 2 COULD NOT check
```

`doctor` reporting WARN on tool drift is the stale pin in
`factory.manifest.json`, not a blocker. Red is worth fixing before `--begin`;
none of that counts.

`check_all.py` answers *is the level any good*, which is a different question
from *how many hands did it take*. Both belong in a run's report and neither
substitutes for the other.

## Godot probes

A probe launched with `--script` runs AS the main loop and must
`extends SceneTree`. One that `extends Node` raises a modal dialog **on the
walker's screen** and blocks until somebody clicks OK, which reads as a hang.
Use `--headless` whenever a window is not needed; a real frame time needs one,
so open a window that measures and quits itself.

**How a probe exits, and how to check that it did.** Both have cost a
retraction (2026-09-27).

- `quit()` asks the main loop to stop at the end of the frame. It cannot
  close an in-engine modal. Every shipped probe therefore exits through
  `_exit(code)`: `quit(code)`, two `await process_frame`, then
  `OS.kill(OS.get_process_id())`. A normal exit never reaches the kill --
  the loop has stopped -- so it costs nothing on the path that works. Proven
  with a probe that skipped `quit()` entirely: the kill path ended a
  windowed engine on its own.
- **A launcher's timeout kills its direct child only.** Godot's console
  launcher spawns the real engine as a grandchild, so `subprocess.run(...,
  timeout=)` left an engine drawing to the walker's desktop with nobody
  waiting on it. `perf_stations_run.py` kills the tree (`taskkill /T` on
  Windows) and refuses with CANNOT MEASURE if any Godot it did not start is
  still up afterwards. Proven with a probe that never exits: tree gone at
  15.9 s, zero processes left.
- **Count Godot processes AFTER teardown, not at +0 ms.** A windowed
  engine freeing a 12,000-node scene and a GL context takes up to a second
  to leave, and the console launcher and the engine are two processes.
  Counting the instant a shell pipeline closed read "2 processes still
  running" on a probe that had exited correctly, and those two were then
  killed mid-teardown -- a retraction, not a hang. Wait a second, or use the
  runner, which does.
- Kill by PID, never by image name: `Get-Process Godot*` includes the
  walker's own editor.

```powershell
Start-Sleep -Milliseconds 1500; Get-Process | Where-Object { $_.ProcessName -like '*Godot*' } | Select-Object Id, StartTime
```

```bash
godot --headless --path <project> --import
godot --path <project> --script res://probe.gd -- <args>
```

**A raw export and a walk copy are two different folders** (three round
trips, 2026-10-03).

- `export` writes a package whose main scene is `mission.tscn` and which has
  no player. Copying it over a walk folder gives Godot no walk scene;
  `python tools/walk_export.py <ws>/.level_factory <mission> --out DIR` is
  what makes the walk copy (the nine underscore files plus
  `run/main_scene`).
- `_runs/perf_inner/run.py <tag> <package>` measures a RAW export. Handed a
  walk copy, the station probe never finishes: the watchdog ends it after
  ten minutes and the runner prints CANNOT MEASURE over a partial report.
  A raw package rebuilds from a walk copy by deleting the nine underscore
  files and restoring `run/main_scene="res://mission.tscn"`; the two then
  differ in nothing else.
- A fresh copy needs `godot --headless --path <copy> --import` before any
  `--script` probe that names a Lux class, or the probe fails to parse with
  `Could not find type "LuxLightRig"`.

Never leave a Godot or Blender process running when the job ends.
