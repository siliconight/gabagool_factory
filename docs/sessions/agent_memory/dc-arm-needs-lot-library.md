---
name: dc-arm-needs-lot-library
description: "A Deli Counter pricing arm must repoint the brief's lot_library, not only tools.local.json"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-27T00:22:29.328Z
---

To build a level against a Deli Counter clone, repointing `tools.local.json`'s `repositories.deli_counter` is NOT enough. Lot draws its buildings from the brief's `lot_library` (`batches/<batch>/missions/<m>/brief/brief.json`), an absolute path to the live `deli_counter/build`. On 2026-10-26 the first subject arm rebuilt seed 9205 with the clone's code, but read the live library: the supermarket's art came back `cache`, and the garage picked up an in-flight 0.273.0 build.

**Why:** an arm that silently reads the live library measures nothing, or measures the wrong change.

**How to apply:** repoint both `lot_library` and `repositories.deli_counter`. Run `build.py --all` (and `nav_gate.py --all`) in the clone first. Then check the run log for the changed shells' jobs reading `succeeded`, not `cache`. Related: [[dc-control-run-via-tools-local]], [[prices-drift-between-sessions]].
