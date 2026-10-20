---
name: enemy-inside-an-empty
description: "Roadmap 191 CLOSED (cold 9188 no regression): all 4 UNREACHABLE_SPAWN refusals 9164-9186 were an enemy Lot pushed inside an Empty; Lot 0.97.3 keeps spawns out of blockers and enemies out of the fenced band; measure placement with the COLLISION reading, not footprints"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-06T22:50:13.480Z
---

Found 2026-10-06 reading cold run 9186's refused seed_9205. The record is
`docs/findings/enemy_inside_an_empty/`.

**The defect.** Lot's `site_spawns.place_enemies` pushes route samples
sideways until `outdoors()` says open ground.
- `outdoors()` asked `footprints()`, which reads `buildings` only. Empties
  are `blockers`, so it couldn't see them.
- All four refusals are this: 9170 and 9174 seed_9061 (e15), 9179 and 9186
  seed_9205 (e9).

**Shipped in Lot 0.97.3 (b57863b):**
- `site_extent.blocker_rect`;
- `site_fences.shut_band(s)`;
- `site_spawns.solid_rects` / `shut_band_rects`;
- a fixture test on 9186's site. Suite 664 -> 669.

0.97.3 moves no enemy on 9187's or 9178's candidates. Cold run 9188 confirmed
that (identical enemies, 0 interventions), and roadmap 191 is CLOSED.

**Lesson, refuted and kept:** I first compared rules on the
declared-footprint occluder fallback (solids=None) without noticing.
- Production passes `site_collision.read_site(spec, [stage_dir])`, and with
  it 0.97.2 reproduces every shipped enemy.
- The fallback put 9186's Enemy_4 elsewhere.

**How to apply:**
- Before trusting any placement simulation, check it reproduces the shipped
  scene's positions.
- `docs/findings/enemy_inside_an_empty/place_variants.py --stage DIR` does
  this for any staged candidate.

**Still open:**
- whether an Empty should be cover to `plan_cover`;
- long band pushes (50 m on 9174).

Related: [[fence-marks-the-playable-edge]], [[empties-get-dark-interiors]].
