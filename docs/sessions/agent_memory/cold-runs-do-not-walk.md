---
name: cold-runs-do-not-walk
description: "a cold run's 0 never ran the walk bot -- cold_drive's walk step builds the copy without the self-check; install tests walk"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-20T23:35:53.257Z
---

A cold run's `INTERVENTIONS: 0` says nothing about the walk: `tools/cold_drive/cold_drive.sh` calls `tools/walk_export.py`, which builds `_runs/walk_export_<M>` and never runs the walk bot or shot bot. Only `level_factory walk <mission>` does (install tests run it). Level Factory 0.223.0's buildings' merge (2026-10-20 10:17) removed every building's `Ladders` and `Markers`; eight cold runs (9349-9356) passed every gate; install test 11's walk printed "walk bot: no ladder_area3d in scene". Fixed in LF 0.227.0 (`docs/findings/merge_ladders_227/`); the gate that would have caught it is roadmap 272.

**Why:** a check that cannot fail on a loss reads like one that passed (CLAUDE.md, unused-parameter rule).

**How to apply:** when a change touches what the walk reads -- ladders, markers, anything found by group -- run `python -m level_factory -C workspaces/cold-N-ws walk <mission>` after `--end` and read its self-check lines (about 4.6 min). Related: [[open-work-2026-10-09]], [[walktest-crew-body-measurement]], [[presentation-gates-were-unread]].
