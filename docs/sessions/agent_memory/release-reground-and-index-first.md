---
name: release-reground-and-index-first
description: "Before certifying a factory release, reground LF's contracts.GROUNDED and commit factory_index's tool-repo output before the tool's release commit"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-28T12:37:58.813Z
---

Two steps a factory release owes BEFORE its install test, each missed once on 2026-10-28 and each costing a corrective release (1.42.0 -> 1.42.1):

1. **Reground Level Factory's `contracts.GROUNDED`** for every tool that moved (a `patch_lf_reground_<release>.py`, the 1.41.0 / 1.42.1 pattern: smoke before shows exactly those rows DRIFT, after all green, then the suite). The doctor reads THAT table, not `factory.manifest.json`; promoting the manifest does not clear `drift vs certified` lines. Install test 13 read 5 drift lines and I wrongly wrote "which this promotion clears".
2. **Run `tools/factory_index.py --write` before a tool's release commit** (or fold its tool-repo output into that commit). It writes into tool repos (e.g. `deli_counter/migrations/README.md`); committed after the tag, it makes the tool STALE in `verify-manifest --strict` and HEAD != tag, which the `-Tag` packager refuses.

**Why:** the install test's claim must be 0 drift lines, and the tagged set must be what was tested.
**How to apply:** at the start of any release, check `python -c "from packages.tools import contracts; contracts.stale_source(...)"` and every tool's `git describe --exact-match HEAD` before running the install test. Related: [[release-1-42-0-plan]], [[github-push-and-releases]].
