---
name: name-workspaces-literally-in-records
description: "docs/ scripts still write cold-NNNN-ws in full, but since 2026-10-19 (--pushed-only) a name no longer keeps a PUSHED run's workspace: keep a finding's small inputs inside the finding"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 5a87c330-6afd-4be5-9664-654ab358aa1c
  modified: 2026-10-19T11:24:20.484Z
---

Any script under docs/ (frame, price, A/B, census) that reads `workspaces/cold-N-ws` writes each
workspace's name out in full: `for ws in cold-9273-ws cold-9274-ws; do run=${ws#cold-}; run=${run%-ws}`,
a literal tuple or dict. Never `cold-$run-ws`, `"cold-%s-ws" % n` or `f"cold-{n}-ws"`.

**CHANGED 2026-10-19 — the walker said yes to `--pushed-only`.** Every cold drive's clean job now runs
`tools/factory_retire.py --apply --pushed-only` (`patches/patch_retire_pushed_only.py`): a PUSHED run's
workspace beyond the newest four goes even when a record names it. A literal name still protects an
UNPUSHED run's workspace (and still counts for the twelve-workspace rule), so keep writing names out. But a
finding that must stay re-runnable after its run is pushed keeps the small inputs it reads INSIDE the
finding — e.g. `docs/findings/drop_edges_173/gate_9318_inputs/navigation_hints.json` (10 KB instead of
pinning a 1 GB workspace) — or says it regenerates the workspace from `docs/cold_runs/cold_N/` first.

**Why:** names pinned 67 pushed workspaces and the disk filled on 2026-10-16
(`docs/findings/disk_full_2026_10_16/`); before that, on 2026-10-12, a BUILT name let the retire take
cold-9261-ws and cold-9262-ws from under four scripts (887c179 made the records literal).

**How to apply:** copying a frame or price script, keep its literal loop; when a finding will be re-read
after its run is pushed, copy the few files it needs beside it. Related: [[perf-copies-fill-the-disk]],
[[repo-hygiene-filing]], [[claim-shipping-only-from-a-package]].
