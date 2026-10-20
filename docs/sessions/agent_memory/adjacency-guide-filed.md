---
name: adjacency-guide-filed
description: "Walker's PA 1990s Building Adjacency and Level Layout guide filed 2026-10-10 as docs/reference/PA_1990S_ADJACENCY_AND_LAYOUT_GUIDE.md; roadmap 230: steps 1 (draw by cluster template, LF 0.176.0/0.176.1), 2 (pair rules as S_ADJACENCY, Lot 0.111.0) and 4 (gameplay targets as S_TARGETS, Lot 0.112.0) LANDED; cold run 9232 proves them in a shipped level; step 3 (connectors for 199) open; DATA, not a layout brain"
metadata:
  node_type: memory
  type: reference
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-10T22:57:38.571Z
---

The walker, 2026-10-10: "would this help level factory and lot in terms of
placement?" Filed verbatim (144 KB) at
`docs/reference/PA_1990S_ADJACENCY_AND_LAYOUT_GUIDE.md`. Roadmap 230.

**What it is:** a layout specification for a "layout brain": settlement
profiles, a typed adjacency vocabulary (relations, edge channels, access
classes, verdicts prefer/allow/condition/repair/reject), a 9x9 category
affinity matrix, an 84-type building catalog, 32 pair rules (P01-P32), a
connector catalog (sidewalk, local_street, rear_passage, service_lane,
shared_court, driveway, loading_apron, parking_walk, crossing, gate...),
greybox dimensions (service lane 3.5-5 m, a focal point every 20-50 m),
a dressing contract, period rules, gameplay targets (3-8 enterable,
ordinary fabric 50-75 %, >= 2 approaches, a return loop, 2-3 choices), 18
cluster templates (C01 corner services, C03 station neighbourhood, C04
industrial-residential edge, C08 roadside lodging, C11 hospital edge...),
V01-V14 checks, T01-T16 cases.

**What landed (2026-10-10/11), as data for the deterministic planners:**
- LF 0.176.0: `MissionBrief.cluster` names a template or `auto` (the
  archetype's words pick it; `packages/pipeline/cluster.py`); `pick_lot`
  draws the template's families after the anchor; a brief naming nothing
  keeps its draw byte for byte; the site spec records `cluster_resolved`.
- LF 0.176.1: the site spec builder's own `pick_lot` draw takes the
  template too (`preferred_for_brief`). Cold run 9231 found the miss: the
  art leg dressed the template's pharmacy, the site placed the old
  station, the export's closure gate stopped the run.
- Lot 0.111.0: `site_adjacency` -> `S_ADJACENCY` findings (category from
  the archetype's words, relation from geometry, the 9x9 affinity and 16
  pair rules; MED where the guide wants an explanation, INFO why a pair is
  good). First lines in 9231: P17 prefer on the deli, office and station.
- Lot 0.112.0: `site_targets` -> `S_TARGETS` INFO lines (enterable count,
  ordinary share, plate approaches + distinct first hops, road loops, the
  longest stretch between focal points on the straight legs, parking
  fields/driveways/yards). Landmarks and navmesh questions said unmeasured.

**Open:** step 3, the connectors for roadmap 199 (a rear service_lane /
rear_passage with declared owner and users is the loop every level lacks;
gates with states); the audit then counts them. The guide's numbers are
authored starting points ([[references-fill-blanks-not-override]]).

See [[walkable-city-brief-informs-lot]], [[land-use-guide-informs-lot]],
[[library-growth-reshuffles-lots]], [[authorship-guide]].
