# Where things go

The factory root tracks coordination data; each tool is its own repo. This
is the table for "I have made a thing -- where does it live", and the four
rules that keep the answer true as the work goes on. `CLAUDE.md` points
here; `tools/factory_hygiene.py --check` fails when the table is not
followed.

## The table

| the thing | where it lives | tracked? | notes |
|---|---|---|---|
| a change to a tool | `patches/patch_<repo>_<topic>.py` at the root, anchored, asserting its targets | yes | the only record of how the source came to be; never deleted. A release is `patch_<repo>_<version>_release.py`. |
| the change's record | the tool's `CHANGELOG.md` and `VERSION`; a roadmap item (`tools/roadmap_status.py --write`, then `--check`) | yes | `docs/SHIPPING_A_CHANGE.md` has the order |
| an investigation | `docs/findings/<topic>/README.md`, with its instruments (`.py`, `.gd`) and their outputs (`.txt`, `.json`) beside it | yes | a frame only when a sentence needs it; a refuted instrument stays, marked |
| a cold run | `docs/cold_runs/cold_N/`: `batch.json`, `briefs/`, `driver.log`, `art.log`, `export.log`, `NOTES.md` | yes | the workspace `workspaces/cold-N-ws/` is regenerable from it and is ignored; the clock's journal is `_runs/cold/` |
| a measurement worth keeping on its own | `_runs/measurements/` (`git add -f`: the folder is ignored, its files are tracked) or the finding that made it | yes | a census, a price, a probe's JSON |
| session scratch, output you are still looking at, a package copy | `_scratch/<date>_<topic>/` | no, ignored | never the root, never a `scratchpad/` |
| a one-shot that already ran | `migrations/` at the root, `<repo>/migrations/` in a tool | yes | kept: see the first row |
| a standing tool | `tools/` at the root, with a docstring whose first line says what it does | yes | that line is what the index shows |
| a runbook | `scripts/` (`.ps1`) | yes | |
| a design or proposal | `docs/proposals/` | yes | |
| a session's notes or handoff | `docs/sessions/` | yes | |
| a report from a phase that is over | `docs/history/` | yes | |
| a perf price copy | `_runs/perf_inner/<name>/` until `<name>.json` exists, then deleted | no | `tools/factory_retire.py` does the deleting |
| a walk export | `_runs/walk_export_<mission>/` | no | the newest per mission is kept, older ones retired |

What a tool repo's root holds: the generator, its gates, its tests where
the repo's `check.py` collects them, `README.md`, `CHANGELOG.md`,
`VERSION`. One-shots go under its `migrations/`. Deli Counter's root is the
measured exception: 120 `test_*.py` live there because `check.py` collects
them there, and COMMANDS.md says so.

## The four rules

1. **A file says what it is.** A `.py` has a module docstring, a `.md` a
   heading, a `.gd` or `.ps1` a first comment line. `tools/factory_index.py`
   reads that line into the folder's `README.md`; a file without one is
   listed as `(undescribed)`, which is a to-do.
2. **The record ships with the work.** At the end of a block of work
   nothing is untracked under `docs/` or `patches/`, and the roadmap and
   the indexes pass `--check`. Eleven cold-run folders and ten patches sat
   untracked for weeks before 2026-10-06; that is the state this rule
   forbids.
3. **Output lands where the table says, by the tool's default.** A probe
   takes `--out` and defaults to its finding's folder; a price run deletes
   its package copy once the JSON is written; a session's scratch goes to
   `_scratch/`. Nothing writes to the root.
4. **Regenerable output is retired, not kept.** `tools/factory_retire.py`
   (dry-run by default, `--apply` to act) retires perf copies that have
   their JSON, walk exports older than a mission's newest, and cold-run
   workspaces older than the last twelve that no finding reads.

## The checks

```bash
python tools/factory_hygiene.py --check      # LOOSE at the root, untracked records, index drift, retirable bulk
python tools/factory_index.py --check        # every generated index matches its folder
python tools/factory_retire.py               # what the retention rule would remove; --apply removes it
```

`factory_hygiene.py --check` is step 7 of `docs/SHIPPING_A_CHANGE.md`, and
`tools/cold_run.py --end` prints its one-line summary after the
intervention count.

## For somebody new

Read in this order: `README.md` (the front door), `USING_THE_FACTORY.md`
(which tool owns which domain), this file (where things go),
`docs/COMMANDS.md` (how to run anything), then the generated indexes:
`docs/findings/README.md`, `patches/README.md`, `tools/README.md`.
`PIPELINE_MAP.md` is the architecture, `PIPELINE_ROADMAP.md` the open
questions, `docs/GLOSSARY.md` the words.
