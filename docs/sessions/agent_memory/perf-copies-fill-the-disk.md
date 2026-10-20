---
name: perf-copies-fill-the-disk
description: "Price-run package copies (~250 MB) AND Godot's per-level shader cache (AppData app_userdata, 2-3 GB a level) fill C:; 9163 died of copies, 2026-10-12 hit 149 MB from caches (13 GB cleared with a yes)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-12T20:39:06.470Z
---

`_runs/perf_inner/run.py <tag> <pkg>` copies the whole package (plus a fresh
import cache) into `_runs/perf_inner/<tag>/` and leaves it there: 230 to
290 MB a run. On 2026-10-05, 42 such copies plus three experiment packages
took C: to 0.14 GB free. Cold run 9163's laser-tag report was then created
but written as 0 bytes, the run died mid-shell-leg, and it had to be run
again as 9164.

**Why:** the drive is small for this work (465 GB, 454 used even after
cleanup), and every cold-run workspace keeps another 0.6 to 0.75 GB.

**How to apply:**
- After a price set, `rm -rf _runs/perf_inner/<tag>/` for each tag once its
  `<tag>.json` exists. The JSON and `.log` are the record; the copy is not.
- The same goes for experiment copies (`_runs/merged_*`, `_runs/noempties_*`)
  and big scratch repo copies.
- Check free space (`Get-PSDrive C`) before starting a cold run after a heavy
  measuring session.
- A cold run that stops on a 0-byte file: suspect the disk first.
- Pruning old cold-run workspaces is the walker's call, not mine. Done
  2026-10-05 at the walker's word: cold-9081 to cold-9163 were moved to E:
  (verified file-for-file; I may not hard-delete), then the walker deleted
  them there the same evening (confirmed gone). They exist nowhere now:
  notes naming `workspaces/cold-NNNN-ws/...` paths point at nothing, and
  `docs/cold_runs/` is the record. Only 9164 and 9165 remain on C:; the cold
  driver reads only `cold-$PREV-ws` (its tools.local.json and validation
  JSON). An empty `E:\gabagool_archive` folder is left. Afterwards: C: 43 GB
  free, E: 63 GB free.

- 2026-10-06: about 9.6 GB of older copies are still in `_runs/perf_inner`.
  They date from 2026-09-30 to 2026-10-03 and each has its JSON; none was
  made this session. They were reported to the walker and not deleted.
  C: had 27 GB free.

- 2026-10-12: C: hit 149 MB free mid-measurement (a re-bake died on
  ENOSPC, a Laser Tag breadth run read an empty report). The hidden grower:
  Godot's GL Compatibility SHADER CACHE, one folder a project NAME under
  AppData\Roaming\Godot\app_userdata\<level> (shell)\shader_cache -- every
  package copy of a level shares it, and it grew to 2-3 GB a level (13.25 GB
  in all). The walker said yes; only those shader_cache folders were
  deleted (regenerable, a few seconds of compile next run). factory_retire.py
  does not know about them -- a candidate rule, the walker's call (AppData).
  Each fresh package copy also re-imports ~500 models (~13 min): reuse ONE
  imported copy across arms, edit it between them.

Related: [[never-edit-tool-repos-during-a-cold-run]], [[stop-a-background-loop-shell-first]].
