---
name: probes-off-round-coordinates
description: "A ray or capsule placed on a round coordinate lands where generated pieces meet; offset the probe's lattice (LF 0.219.0 uses 3.1/2.3 mm)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-19T19:30:20.715Z
---

When writing an engine probe that samples a grid (rays, capsules, shape queries), lay the grid a few odd millimetres off round coordinates, or expect seam artefacts. Generated pieces meet on round coordinates, and float32 rounding plus exact-boundary rules decide the answer there, not the geometry.

**Why:** roadmap 173's drop-edge gate refused cold run 9333 on a 1.7 um float32 gap between a slab cut and a plate authored flush at x -64.0, a lattice line. Its A/B on six packages found four more lattice artefacts: a ray in a face's plane, a capsule exactly its radius from a face (Godot calls touching an overlap), zero-normal hits from a ray starting on a box's side, and a slope read millimetres apart. Level Factory 0.219.0 fixed the gate by shifting the grid origin (`SEAM_NUDGE_X/Z`, 3.1/2.3 mm: not multiples of 0.5 mm, over 35 float32 steps within 1 km). Findings in `docs/findings/breadth_sweep_2026-10-19/`.

**How to apply:** for a new probe, offset every query point, or reuse walkable_edge.gd's constants. When a probe's answer flips between two nearby points, print the floats at the boundary (CLAUDE.md) before reasoning about it. Related: [[corner-pin-is-godot-physics]].
