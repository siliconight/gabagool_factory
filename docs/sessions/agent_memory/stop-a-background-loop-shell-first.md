---
name: stop-a-background-loop-shell-first
description: "Stopping a background bash loop on Windows: TaskStop leaves the grandchildren running, and killing one pass's subshell only advances the loop to its next pass; kill the loop's own bash.exe first, then its tree"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-06T18:05:11.148Z
---

On 2026-10-06 a three-pass pricing loop (`price_fabric.sh`) was stopped
with TaskStop.
- The python, perf-harness and windowed Godot processes kept running.
- Killing them ended pass one, and the loop started pass two.
- Killing that pass's bash subshell made the loop start pass three.
- Only killing the loop's own `bash.exe` (the oldest one running the
  script) stopped it.

**Why:** a windowed Godot left running on the walker's machine is exactly
what CLAUDE.md forbids, and every stray pass leaves a ~160 MB copy in
`_runs/perf_inner`.

**How to apply:**
1. List the processes with `Get-CimInstance Win32_Process`, filtering
   CommandLine on the script's or run's name.
2. Stop the earliest-created `bash.exe` that runs the script.
3. Then stop its children and grandchildren.
4. Re-list until nothing matches, and confirm no Godot is left.
5. Remove only the copies that run made, after listing them.

Related: [[perf-copies-fill-the-disk]].
