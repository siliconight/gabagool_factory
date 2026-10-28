---
name: ship-change-tool-and-suite-once
description: "Walker approved 2026-10-28 -- smoke first, full suite ONCE on the clone, light jobs overlap, ship via tools/ship_change.py"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-28T15:19:25.329Z
---

Asked what slowed the roadmap most, I measured: each change re-proved itself 2-3 times serially (Zoo suite 8 min on the clone + 7.7 on the real repo; DC build+gate+suite twice plus a 6.9-min commit-hook suite), and the costliest defects surfaced at the end of the chain (wooden money racks in frames; the "Delco" IP guard 14 s into the first real build). The walker said yes to all four fixes:

1. **Full suite ONCE, on the clone.** The dry run proves the applied repo byte-identical, so no real-repo suite unless the apply writes what the clone did not (build output, a migration against real specs). The repo's own commit hook still runs: `--no-verify` stays forbidden.
2. **Smoke first**: make the smallest level that exercises a change before any long suite (`tools/ship_change.py smoke`).
3. **`tools/ship_change.py`**: `clone`, `smoke`, `patch` (pinned/anchored patch from the clone's diff + double dry run), `prove-old`, `apply` (writes factory_index first and folds it into the commit, attribution check, push). Replaces hand-copied gen_*/dry_run/apply_* scripts. Written in `docs/SHIPPING_A_CHANGE.md` section 5.
4. **Light jobs overlap** (two unit suites side by side); walks, prices and level builds still run alone.

**Why:** wall clock was the bottleneck, not thinking; the walker wants the roadmap moving.
**How to apply:** default to the tool for every tool-repo change; keep `prove-old` (a test that cannot fail proves nothing). Related: [[release-reground-and-index-first]], [[full-suite-on-the-clone-first]], [[keep-it-rolling]].
