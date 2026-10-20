---
name: claim-shipping-only-from-a-package
description: "A capability that crosses repos (DC -> Lot -> LF staging -> Dispatch -> package) is shipped only when a real package shows it; LF's stage_dispatch_inputs is a whitelist that silently drops new gameplay keys"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-19T01:52:42.738Z
---

Three times a nav capability was claimed "in the package" after each repo's own tests passed, and the package
did not carry it: ladders on cold runs 9075 and 9076 (roadmap 172), and the declared-drop links on cold run 9320
(roadmap 173; the root's 02c1b06 said "the declared set now ships in the package"). Every time the break was
Level Factory's `packages/staging/dispatch_inputs.py` `stage_dispatch_inputs`, which PROJECTS each gameplay
manifest into a literal dict of named keys — a key it does not name vanishes exactly as if upstream never sent
it. LF 0.216.1 added `vertical_links`, and `tests/unit/test_drop_links_staged.py` `DISPATCH_READS` now lists
every key Dispatch's importers read (`up_axis, anchors, props, interactives, ladders, vertical_links`).

**Why:** the per-repo tests each test one hop; only a package tests the chain. The drop-edge gate (LF 0.216.0)
caught it by refusing 9320's export — see [[open-work-2026-10-09]].

**How to apply:** when Dispatch learns to read a new gameplay key, add it to the staging AND to `DISPATCH_READS`
in the same change. Never write "ships in the package" until a cold run's `navigation_hints.json` (or the
package file in question) has been read and shows it; trace a missing record hop by hop through the workspace
(build record -> lot_assemble site.site.gameplay.json -> temp/<m>/dispatch_inputs -> dispatch_handoff out).
