---
name: rowhouse-stoops-roadmap-240
description: "roadmap 240 stoops + iron railings SHIPPED 2026-10-13 -- DC 0.211.x/0.212.0, LF 0.195-0.197, Zoo 1.105.0; cold 9271-9273 0 interventions; walker: 3 risers, concrete, both sides; graders' breadth run after: no snag"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-13T14:05:17.088Z
---

Every rowhome Empty stands three steps up on a concrete stoop with a black iron railing on each side. The design is `docs/proposals/ROWHOUSE_STOOP.md`, whose taste calls are now answered. Root commits: 20940c8 (stoops) and d85e0a5 (railings).

- **The stoop:** 7 in risers on 11 in treads, a 0.9 m landing, 1.5 m wide, 1.74 m deep.
  - The door and window are raised by a 0.3834 m sill.
  - It is walked on one collision ramp that rides the nosings at 32.5°.
- **The railings:** Zoo's `stoop_railing`, in level and flight forms drawn from the slot box, with no collision of its own.
  - Two slots a side, 5 cm inside the stoop's side, at `rot_y` 270.
  - DC writes the colliders: a box and a tilted slab.
- **The walker's calls, 2026-10-13:** "3 risers, concrete, railings both sides".
- **Proof:** 9273's `rail_walk.gd`. A body driven sideways off the landing or the flight stops after 0.312 m; on 9272's package it walks off.
- **Cost:** +8.0 draws a heading for the railings (the stoops cost +6.5). p95 sat at the noise floor in two prices.

**Things learned the hard way:**
- **The terrace reads a shell's extent from its COLLIDERS.** Any collider in front of an Empty moves the whole row back unless its name is in LF's `street_line.STOOP_COLLIDERS`. The railings would have moved the row 1.41 m.
- **`merge_empties.gd` merges only slots whose names give a side.** `stoop_*` maps to S since LF 0.196.0.
- **The composer's z-fight gate reads each module as its AABB and skips pairs under 0.05 m².**
  - A flush thin prop beside a step sat 0.3 cm² under that floor.
  - Test with `zfight_gate.visible_fights(boxes, area_min=0.0)`, plus a flush control.
- **`godot_basis(rot_y)` is Ry(−t):** 270 sends module +X to Godot −Z (Blender +Y). A thin module ties 90 and 270, and the composer keeps the slot's own turn.
- **DC's circulation gate starts a doorway volume at wall bottom + sill,** 0.15 m low. Recorded, not fixed.
- **A Zoo module carries a box collider unless its genome says `collision: false`.** The slot's `fit.collision` is ignored.
- **One heading's p95 spike with a wide pass spread can be a disturbance.** 9273's +2.61 ms read +0.02 ms when re-measured. Re-price before believing a single heading.
- **DC's commit hook runs `check.py` with the Godot nav gate:** expect about 10 minutes per commit.

**The graders' breadth, run after shipping** (`docs/findings/stoop_breadth/`, root 7e47728):
- **Method:** A/B on 8 staged lots with rowhomes, swapping in today's DC shells with `stoop=0` against the shells as built, plus a control.
- **Results:** the walk test is unchanged on all eight. No Laser Tag stuck event falls within 10.9 m of a stoop (229 events). The fights move both ways: one grade up a notch, one score down 1, and each route move is one team wipe.
- **Lesson:** any navmesh change re-plays the seeded fights. Judge a geometry change by stuck events located against it, not by the grade.
- **Lesson:** a staged walk-test director older than Lot 0.117.0 can't settle under today's clock, so sync today's addon, as `main()` does.
- **The seed_9104 enemy-stuck spot, TRACED:** enemies queued behind enemies (no avoidance, the destination re-set every frame), 18 m from any stoop. It is congestion, not geometry; see [[corner-pin-is-godot-physics]].

**Queued for the walker:** `cold_9273/railings.png`.

**Why:** the walker's comps, roadmap 240's rowhouse front.

**How to apply:** next on the front: dishes and parged fronts; then the rear ells. See [[philly-street-comps]] and [[lightmap-atlas-repacks-on-new-users]].
