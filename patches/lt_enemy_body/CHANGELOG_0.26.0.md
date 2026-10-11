## [0.26.0] - an enemy is the contract's body too

### Why now

Roadmap 197: cold run 9191's generated corner deli failed
`ENEMY_PATHING_BROKEN` on every candidate, 165 of seed_9191's 177
enemy-stuck events at one rear door, and nobody had said why. Re-measured
on today's tools (cold run 9246, the same brief and seeds), the deli's
enemies still jam -- 49 on seed_9191, 19 on seed_9393 -- now at two other
openings, and reading the harness found the reason a narrow opening jams
an enemy and not the crew:

- **`_apply_body` builds only the crew.** Every enemy kept
  `LT_EnemyPill.tscn`'s capsule of radius 0.40. That is the BAKE's agent
  radius, and `deli_counter/agent_contract.json` says of it "NOT a body
  radius and nothing should be built from it"; npc_standard is 0.35. A
  navmesh eroded by 0.40 leaves a 0.40 body no clearance at any corner
  it rounds.
- **The enemy kept the scene's `path_desired_distance` 0.8**, the value
  0.18.0 measured cutting corners and jamming the crew (route completion
  0.0 and 38 stuck, four runs of four, against 1.0 and 0 derived).
  0.18.0's note said the 0.8 stayed "as the authored fallback ... nothing in
  this repo's own evaluation path uses it any more". That was true of
  players; `_configure_enemy` never called anything that set it, and no
  test looked at an enemy.

### What changed

- **`LT_Const.arrival_radius(radius, speed, ticks, cell_height)`**: the
  0.18.0 formula in one place. `LT_BotPlayerController._align_agent_to_mesh`
  calls it; the crew's number is the same to the bit.
- **`_configure_enemy` applies `_apply_body`**: the enemy's capsule, mesh
  and agent take the scenario's radius and height, the crew's fields,
  because npc_standard shares the player's metrics until a distinct class
  ships (the reason the enemy's eye already reads one field).
- **`LT_EnemyMovement._align_agent_to_mesh`**, on the first destination:
  the path height offset and the arrival radius from the body and the
  map, as the crew's controller has done since 0.18.0.

The pill scenes keep 0.40 and 0.8 as the fallback for a pill dropped into
a map by hand; the harness now overrides both for every body it spawns.

### Measured

Cold run 9246's seed_9191 -- the generated corner deli, evaluated by Laser Tag 0.25.0 in the job's own staged project -- three times unpatched: the job's report, then twice more on a quiet machine (`docs/findings/grader_speed/`), identical in every field, all 1,943 events. The evaluation is deterministic, so a difference is the patch's and nothing else's. Drafted onto a copy of that staged project, the five files the only difference, the same 25 runs at the same seed: enemy-stuck events 49 -> 28, the grade WARN 68 -> PASS_WITH_TUNING 76, `INSTANT_CONTACT` WARN -> `CONTACT_TIMING` PASS (first contact 2.67 -> 3.13 s), route completion 25 of 25 and enemy deaths 150 both ways, player deaths 34 -> 33. The 42 events at one end of a 1.2 m shelf run beside the deli's alley door became 24 at its other end, and the 7 at the loading bay's partition neck became 3: what remains is the shell's geometry (roadmap 197), not the body

### Tests

`runners/tests/test_enemy_is_the_contracts.gd`, 9 checks: one derivation for every body (`LT_Const.arrival_radius` is the 0.18.0 formula, 0.4350 on 0.18.0's own figures, and the crew's controller calls it); the harness builds an enemy from the scenario (capsule radius 0.35 where the scene's was 0.40, its height, the agent's radius); an enemy that sets out derives its arrival radius and path height offset from its body and the map. On 0.25.0 the script fails before its first check: `arrival_radius` does not exist. Every test in `runners/tests` -- 18 with the new one -- exits 0 under Godot 4.7, headless, in the repository; in a clone outside the factory `test_nav_bake_is_the_contract` cannot reach `../deli_counter` and `test_one_eye_per_body` fails the same way on 0.25.0 and 0.26.0
