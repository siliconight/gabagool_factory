---
name: perf-stations-follow-package-anchors
description: "The perf harness's stations and look_shots' cameras come from the package's gameplay_anchors.json -- LF 0.156.0/0.158.0 changed those anchors, so frame times across them compare different stations"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-08T17:57:25.891Z
---

`level_factory/tools/perf_stations.gd` takes up to 12 stations from the
package's `gameplay_anchors.json` (round-robin across 8 anchor types), and
`tools/look_shots.py` derives its spawn/objective/extraction cameras from the
same file; `tools/walk_export.py` stands its body at the package's
`player_start`.

**Why:** 2026-10-08, Level Factory 0.156.0 added the van's start/exit and the
responder anchors and removed the synthesized centroid start; 0.158.0 dropped
the unplaced Deli Counter shell's anchors (68 -> 33 on bank_block_001). Every
station-based number across those releases is measured from different places.

**How to apply:** when pricing a change, run "on", "off" and the control on
packages built by the SAME Level Factory version; never compare a price taken
before 0.158.0 with one after it as if the stations were the same. Read the
station list (`rows[].station`) before comparing two reports. Related:
[[cover-draws-roadmap-180]], [[performance-beats-graphics]].
