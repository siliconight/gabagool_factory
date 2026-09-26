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

```bash
godot --headless --path <project> --import
godot --path <project> --script res://probe.gd -- <args>
```

Never leave a Godot or Blender process running when the job ends.
