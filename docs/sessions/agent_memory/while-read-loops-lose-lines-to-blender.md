---
name: while-read-loops-lose-lines-to-blender
description: "A bash `while read` loop over a list file stops early when the body runs build.py/Blender, which eats stdin; use `for x in $(cat list)` and `< /dev/null` on the child"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-09T17:26:22.255Z
---

**Rule:** never feed a list to `while read` when the loop body runs Deli
Counter's `build.py`, Blender, Godot or any child that may read stdin.
- Iterate with `for sp in $(cat "$LIST")`.
- Give the child `< /dev/null`.
- Keep the list in the session scratchpad.

**Why:** 2026-10-09, rebuilding 38 refurnished shells for Deli Counter
0.204.0.
- `while read sp; do python build.py "$sp"; done < list` built a handful of
  shells and stopped. The Blender child had consumed the rest of the list.
- It printed "failures: 0", because the loop simply ran out of lines.
- `build_freshness.py` caught it: "bank_tower_a01 ... changed since this
  shell was built".
- The list file under `_scratch/` was also gone afterwards, cause not found.

**How to apply:** after any batch build, run the freshness or coverage
check that counts what was built, rather than trusting the loop's own
failure count. See [[bash-cwd-drifts-between-calls]] and
[[bash-heredoc-large-bodies-fail]].
