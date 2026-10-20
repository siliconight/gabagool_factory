---
name: dry-run-a-patch-guards-not-anchors
description: "A patch's dry check must run its whole main() in memory, every final assert included -- counting anchors is not enough"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-19T19:30:14.745Z
---

Dry-check a patch by running its full transformation in memory, including the guards that run after the anchors (e.g. "stairwell still reads the lint"), and parse the results. Counting each anchor's matches is not a dry run.

**Why:** 2026-10-19, Deli Counter 0.233.0 (`patches/patch_dc_lint_out_of_the_build.py`) was "dry-checked OK" by anchor counts in the session before, then refused on its first real apply: a docstring line in stairwell still named `layout_lint.DOOR_APPROACH_M`, and the patch's post-replacement guard caught it. Nothing was written, because the guard ran before any write. That is the backstop working, and it is still a round trip.

**How to apply:** before applying any anchored patch, import it with importlib and replay main()'s reads, `_once` calls and final asserts against the live files without the writes, then `ast.parse` each result. Keep every guard ahead of the first write, as [[gate-commits-on-the-patch]] keeps commits behind the patch.
