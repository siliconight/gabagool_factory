---
name: dc-control-run-via-tools-local
description: "A Deli Counter \"before\" cold run without touching the real repo -- clone, build AND nav-gate it, pre-write the workspace's tools.local.json"
metadata:
  node_type: memory
  type: reference
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-21T10:20:09.752Z
---

Level Factory reads Deli Counter's buildings from `<deli_counter repo>/build/` (glb, gameplay, slots, lights AND
`<id>.navgate.json`), and the repo path comes from the workspace's `tools.local.json`
(`repositories.deli_counter`). `level_factory init` KEEPS a `tools.local.json` already in the workspace folder (it
only refuses a folder with `factory.project.json`). So a same-level control for a Deli Counter change:

1. `git clone deli_counter <scratch>/dc_lib_<ver>` and check out the old commit.
2. In the clone: `python build.py --all` (about 25 min) AND `python nav_gate.py --all` -- the commit hook runs the
   gate on the real repo; without it every shell's fitness is "absent" and `run` refuses: "a themed lot of 3 needs
   3 fit families and the library offers 0" (cold run 9367, 2026-10-21, stopped at its shell leg for exactly this).
3. `mkdir workspaces/cold-N-ws` and write its `tools.local.json` (copy a recent run's, change only
   `repositories.deli_counter` to the clone), then run `cold_drive.sh` unchanged.
4. `before.json` hashes the REAL repos, so it names the real Deli Counter: the NOTES must say which one the run
   read; the doctor's `tool:deli_counter v... @ <sha>` line is the evidence.

Lot reads one file from the real sibling repo regardless (`agent_contract.json`); fine while it is unchanged.
A walk copy left at `_runs/walk_export_<mission>` must be renamed first (2026-10-21: a factory 1.40.0 release
check's, renamed `_runs/walk_release140_restaurant_row_001_s9205`). Related: [[never-edit-tool-repos-during-a-cold-run]].
