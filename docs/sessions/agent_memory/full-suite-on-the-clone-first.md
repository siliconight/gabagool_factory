---
name: full-suite-on-the-clone-first
description: "Run a tool repo's WHOLE suite on the proven clone before generating its patch; nearby tests miss cross-cutting pins"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-27T17:49:03.211Z
---

Before `gen_*.py --write`, run the repo's full suite on the clone (DC: `build.py --all`, `nav_gate.py --all`, then `DC_ZOO_ROOT=... pytest`; Zoo: `pytest -q` then the bpy half in Blender), not only the tests next to the change.

**Why:** 2026-10-27, twice in one block. Zoo 1.135.0's first apply failed `test_species_by_name` (new species unreachable by prompt — minted keywords were underscored, the parser matches spaced words). Deli Counter 0.281.0's first apply failed five tests in `test_club_fixtures`, `test_payphone_wall_form`, `test_ticket_queue` that pinned the old bank lobby's cigarettes/payphone/sofa counts. Both were caught by the apply's own gate before any commit, but each cost a revert of the real repo and a regenerate.

**How to apply:** clone proof = full suite green, then stamp, generate, dry-run, apply. A furniture/recipe change in DC ripples into library-wide count tests; a new Zoo species needs spaced keywords. Related: [[gate-commits-on-the-patch]], [[dry-run-a-patch-guards-not-anchors]].
