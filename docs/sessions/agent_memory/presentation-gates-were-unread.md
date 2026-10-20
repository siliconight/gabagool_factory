---
name: presentation-gates-were-unread
description: "presentation_compose's gates were read for 1 building of 16 and its circulation gate could never pass (merged cover boxes); fixed DC 0.191.0 + LF 0.149.0 (3acaefc); PROVEN cold 9188 (compose exit 0, ZFIGHT 1->3, roadmap 192); job.log shows only the LAST building"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-06T22:19:20.443Z
---

Found 2026-10-06 checking roadmap 177 against the runs since. The record is
`docs/findings/presentation_gates/`.

**What was wrong:**
- LF `adapters/presentation.normalize_validation` read `next(...)` of 16
  manifests, which is lot/deli_a01's. In 9187, office's and rail_station's
  z-fight fails went unrecorded.
- No branch read `circulation_check`.
- The driver printed "0 conflicts across ? volumes" from the wrong level of
  DC's two-arm schema.
- DC's dressing arm boxed whole nodes. Since Zoo 1.68.0 merged covers per
  side per material, every box was building-sized, so every building with
  covers failed on every run from 9164 to 9187, and each run was counted
  clean.

**Fixed:**
- DC 0.191.0 (117b61a4): per-part boxes, welded and index-connected, and a
  stair's own guards excused. A planted crate is still caught.
- LF 0.149.0: every placed building is read and named, and there is a
  PRESENTATION_CIRCULATION finding (moderate).

**How to apply:**
- The compose `job.log` keeps only the LAST command's lines. Read
  `presentation/lot/*/compose.summary.json` for each building.
- Expect PRESENTATION_ZFIGHT to count 1 per failing building now.
- **Open:** twin_a01's stoop and porch deck read as doorway conflicts, a
  walkable-piece false positive.

Related: [[stale-pieces-l23]].
