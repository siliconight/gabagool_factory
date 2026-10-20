---
name: prices-drift-between-sessions
description: "The perf harness's evening draws, p95 and buffer memory move between sessions on identical bytes; texture memory does not -- price every arm in one session, read texture_mem_bytes for memory"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-20T20:18:09.983Z
---

Measured 2026-10-20 (cold run 9355, `docs/cold_runs/cold_9355/NOTES.md`, "The price"): byte-identical packages priced
at ~12:40/14:10 and again at ~16:00 read differently. 9351's render bytes: 92 fewer draws at two evening headings
(1,316 -> 1,224); the morning package: +0.61 ms p95 a heading (floor 0.10); buffer memory 61.6 MB -> 44.6-48.8 MB,
and it also moved between two runs of one package (noon: 57.4 / 59.5 MB). `texture_mem_bytes` was identical on
identical bytes every time, and day draws held (23,609 both sessions). Cause NOT attributed (window/display, shadow
allocation, the machine's other use once the walker is back -- none measured).

**Why:** the first read of 9355 against 9351's stored price showed -184 draws, +0.7-1.0 ms and -14 MiB video memory
for a texture-only change, all three the session's. A rebuilt control (9355's package with the old booths swapped
back, `docs/cold_runs/cold_9355/make_hybrid.py`) priced in the same session read 9355's draws exactly.

**How to apply:** never price an arm against a stored JSON from another session; when the old package is gone,
rebuild it by swapping the changed files into the new package (module_diff.py lists them) and price both in turn,
alone. For a package's memory read `geometry.texture_mem_bytes`, not the summed video memory. Related:
[[perf-stations-follow-package-anchors]], [[perf-copies-fill-the-disk]].
