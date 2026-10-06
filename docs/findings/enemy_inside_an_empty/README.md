# An enemy pushed into an Empty

Found 2026-10-06, investigating cold run 9186's seed_9205, which Laser Tag
refused in 2 s: "Enemy_5 could not path to the player spawn"
(`UNREACHABLE_SPAWN`, `NO_RUNS`).

## What was measured

**Every refusal is the same defect** (`unreachable_spawns.py`,
`unreachable_spawns.txt`). Laser Tag refused four candidates in cold runs 9164
to 9186 on `UNREACHABLE_SPAWN`. In each, Enemy_5 stood inside an Empty:

| run | candidate | Enemy_5 (level x, y north) | inside |
|---|---|---|---|
| 9170 | seed_9061 | (31.67, -44.24) | e15, `gs_empty_rowhome_i` |
| 9174 | seed_9061 | (31.67, -44.24) | e15, `gs_empty_rowhome_i` |
| 9179 | seed_9205 | (-17.70, -35.46) | e9, `gs_empty_rowhome_l` |
| 9186 | seed_9205 | (-17.70, -35.46) | e9, `gs_empty_rowhome_l` |

- **The control:** the other 17 enemies of 9186's three candidates stand in
  the open, and so do all 18 of 9187's. The instrument can say "open".
- An Empty is a house with its doors shut (Level Factory 0.143.0). Nothing
  inside one can reach the street.

**How it got there.**
- Lot's `site_spawns.place_enemies` spreads the enemies along the route
  spawn -> objective -> extraction. It pushes a sample perpendicular to the
  route until `outdoors()` calls it open ground.
- `outdoors()` asked `footprints()`, which reads `site_spec["buildings"]`.
  An Empty is a blocker, so `outdoors()` could not see it.
- 9186's Enemy_5 is 24.00 m perpendicular to the route's last leg. That is
  Lot's own `LOT_ENEMY_SPAWN_PUSHED` figure for the run: "furthest move
  24.0 m".
- **Reproduced:** run on 9186's inputs with the collision reading Lot
  passes, Lot 0.97.2's `place_enemies` puts all six enemies where the shipped
  scene has them, Enemy_5 inside e9 (`place_variants.py`, variant A). It does
  the same on all three of 9174's candidates.

**Why the fence did not catch it.** `site_fences.plan_fences` leaves a row
open rather than strand a mission marker behind its front line ("NEVER
ENCLOSE A MARKER"). It skips a marker that stands inside a house, so the
fence went up around an enemy already shut in.

## Keeping the Empties out is not enough

`place_variants.py` places a candidate's enemies under three rules:
- A, buildings only (0.97.2);
- B, buildings and the blockers;
- C, buildings, the blockers and the band behind each Empty row's front
  line.

The band is the ground the row's end fences shut off out to the plate's
edge. Occluders are Lot's collision reading, under which rule A equals the
shipped scene on every candidate checked.

| candidate | rule | the enemies that differ |
|---|---|---|
| 9186 seed_9205 | A | Enemy_5 inside e9, pushed 24.0 m |
| | B | Enemy_5 1.33 m clear of the band, pushed 19.5 m |
| | C | the same as B |
| 9174 seed_9061 | A | Enemy_5 inside e15, pushed 40.0 m; Enemy_4 0.34 m clear of the band |
| | B | Enemy_4 (35.14, -43.77) and Enemy_5 (34.13, -48.01), **both behind the front line** |
| | C | Enemy_4 (-8.67, 36.89) and Enemy_5 (-14.76, 26.95), open, pushed 50.0 and 45.0 m |

- On 9186 the Empties alone are enough. On 9174 they are not: B moves both
  enemies onto shut ground.
- C's moves on 9174 are large, to the far side of the route. They are what
  the cheapest open, fair place costs there, and `LOT_ENEMY_SPAWN_PUSHED`
  reports them.
- Outputs: `place_variants_0972.txt` and `place_variants_9174_seed_9061.txt`.

**On the runs that matter now:** with the collision reading, C moves no
enemy on any candidate of cold runs 9187 and 9178.

**The fallback.** `--footprints` measures on the declared-footprint
occluders `place_enemies` falls back to when the collision reading is
incomplete (`place_variants_0972_footprints.txt`). On 9186 it puts Enemy_4
inside e13 under A and behind the row under B (10.38, -47.04, pushed
39.5 m). The Lot test runs on this fallback.

**Refuted, kept.**
- The first run of this comparison used the fallback without saying so,
  and it patched `footprints()` wholesale. On 0.97.2 that also feeds the
  fallback's occluders (`margin=0.0`), so it credited the Empties and the
  band as cover.
- Its figures were quoted as Lot's placement: "Enemy_4 pushed through its
  house", "18.5 and 12.5 m". That was in the first draft of the Lot patch's
  docstring and in this README.
- Under the collision reading Lot passes, 9186's Enemy_4 never moves.
- Separating the two calls changed no figure on the fallback. Changing the
  occluder model changed the answer.

## What shipped

Lot 0.97.3:
- `site_extent.blocker_rect` is one reader for a blocker's plan rect, used by
  the ground, the fences and the spawns. There had been three copies of the
  rule.
- `site_fences.shut_band` / `shut_bands` is the band `plan_fences` computed
  inline, now a function.
- `site_spawns.solid_rects` (footprints and blockers) is asked by the crew's
  spawns and the enemies. The enemies also ask `shut_band_rects`.
- `tests/test_spawns_keep_out_of_empties.py` runs on 9186's site as drawn
  (`tests/fixtures/restaurant_row_001_seed_9205.site.json`).

**Not changed, and open:** `plan_cover` measures sightlines against
`footprints()` alone, so an Empty is not cover to the cover planner. Whether
it should be is a different question, with a visible effect.

## Roadmap 185, answered

185 recorded seed_9061's refusal in 9170 and 9174 as "not traced to
`setback_demo`". It was an enemy inside e15.

## Files

- `unreachable_spawns.py` reads every refused Laser Tag evaluation in the
  cold-run workspaces. For each, it reports the enemy's position and which
  declared rect contains it. Output: `unreachable_spawns.txt`.
- `place_variants.py [--stage DIR] [--lot DIR] [--footprints]` places a
  staged candidate's enemies under the three rules. The default candidate is
  9186's seed_9205.
  - `place_variants_0972.txt`: 9186, Lot 0.97.2, collision reading.
  - `place_variants_0972_footprints.txt`: the same on the fallback.
  - `place_variants_9174_seed_9061.txt`: 9174's seed_9061.
  - `place_variants_0973.txt`: 9186 on 0.97.3, its rule C run unpatched.
