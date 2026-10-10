## 0.112.0 - the guide's gameplay targets in the site audit

**Roadmap 230, the fourth adoption.** The walker's adjacency and layout guide
closes with "editable gameplay targets", starting numbers for a small
cooperative mission that are "to tune in playtests, not minimum content
quotas". 0.111.0 put the guide's pair rules in the audit; this puts its
numbers beside them, so a reviewer reads what the level measures against
what the guide suggests in one report.

- **`site_targets.py`,** pure, from the drawn spec alone: the enterable
  buildings against 3 to 8; the ordinary fabric (every Empty instance and
  every lot building but the objective, over all of them) against 50 to
  75 %; the road ends that reach the plate's edge and the distinct first
  hops to the objective across the site graph (`site_tactical`'s number,
  the one `S_ONE_APPROACH` grades at 1) against 2 meaningful approaches;
  the loops of the road graph (edges less nodes plus components over the
  axis-aligned roads' junctions) against the preferred return loop; the
  longest stretch between focal points along the straight legs spawn to
  objective and objective to extraction (the leg's ends, the lot buildings
  and the junctions within 20 m of the line) against 20 to 50 m traveled,
  said as a floor on the real gap; the parking fields and bays, driveways
  and dumpster yards for the buildings they serve.
- **`S_TARGETS` in the site audit,** every line INFO: the measure, the
  range, and what the gap means ("the terrace outnumbers the level's
  buildings", "the way back is the way in, and the guide prefers a return
  loop", "wants a corner, a threshold or a landmark view").
- **Not measured, and said so:** landmarks (the spec carries signs, the
  brief the landmark), simultaneous choices at a decision, regrouping
  room, and anything that needs the navmesh.

**Tests:** 6 in `tests/test_site_targets.py`. **Suite:** RESULT_SUITE.
