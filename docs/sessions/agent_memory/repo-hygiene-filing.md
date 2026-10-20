---
name: repo-hygiene-filing
description: "2026-10-06 hygiene pass: docs/FILING.md is the where-things-go table; tools/factory_hygiene.py --check (LOOSE/UNTRACKED/RECORDS/INDEX), factory_index.py --write (generated READMEs), factory_retire.py (dry-run retention); nothing at the root, scratch in _scratch/, records committed with the work"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-07T00:06:26.725Z
---

The walker asked (2026-10-06) for a hygiene pass and a way to iterate
without clogging the repos. The record is
`docs/findings/repo_hygiene_2026-10/`.

**The rule set, in `docs/FILING.md` and a CLAUDE.md hard rule:**
- a change = a patch under `patches/`; an investigation = a folder under
  `docs/findings/` with instruments beside its README; a cold run's record
  = `docs/cold_runs/cold_N/`; scratch = `_scratch/<date>_<topic>/`
  (ignored); one-shots = `migrations/`.
- Nothing is written to the factory root. Nothing untracked under
  `docs/` or `patches/` at the end of a block.

**The tools (factory root `tools/`):**
- `factory_hygiene.py --check`: LOOSE, UNTRACKED (tool repos), RECORDS,
  INDEX fail; UNDESCRIBED/RETIRABLE/FINDINGS are reported. `--brief` is
  printed by `cold_run.py --end`.
- `factory_index.py --write` / `--check`: generated README blocks for
  docs/findings, patches, tools, scripts, migrations, deli_counter/
  migrations, docs/proposals, docs/sessions, docs/history.
- `factory_retire.py` (dry-run; `--apply`): perf copies with a JSON, walk
  exports untouched 30 days, cold workspaces beyond the newest 12 that no
  doc names.

**What moved:** SESSION_*.md → docs/sessions; census7/film JSON →
_runs/measurements; phase reports + NEXT.md → docs/history; `Claude
outputs/` → docs/findings/claude_outputs_2026-09; 766 MB root scratchpad
and 11 never-run cold folders → `_scratch/archive/2026-10-06_hygiene/`;
rockay-ws's 228 Godot import caches untracked; `workspaces/`, `.godot/`,
`.claude/`, `.pytest_cache/` ignored. Lot 0.97.4 (root test → tests/),
DC 0.193.0 (23 one-shots → migrations/), Zoo and Lux ignore/uid fixes.

**Walker's calls:** perf copies deleted (9.2 GB); older cold workspaces
retired on the walker's later word (13, cold-9164..9176, 8.0 GB; disk 38 GB
free); DC's 21 live `migrate_*.py` stay at the root.

**Pushing:** the walker asked for a push of everything on 2026-10-06. The
tool repos pushed from here; the auto-mode classifier refused the factory
root's push ("out-of-place publication"), and the walker pushed it. Ask the
walker to push the root; never retry it from here.

**How to apply:** run `factory_hygiene.py --check` before a root commit;
`factory_index.py --write` after adding to an indexed folder; put session
output in `_scratch/`, never the root. A `(undescribed)` index entry means
a file with no docstring.
