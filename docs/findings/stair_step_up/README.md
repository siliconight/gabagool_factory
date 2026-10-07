# The crew had no step-up (roadmap 203)

2026-10-07. Cold run 9194 made the bank the score (Level Factory 0.152.0), and
on both candidates that drew `bank_branch_a04` Laser Tag's crew wedged leaving
the basement vault: route completion 8% (seed_9054, the picked one) and 0%
(seed_9256), 1,302 and 2,363 of their stuck events in one 2 m cell at the foot
of the service stair `a03_stair_bw`.

## Which instrument was wrong

`walktest_navqa` passed the same basement. A read-only survey of both movers
(re-read where it mattered) found them to be different bodies:

| | Laser Tag crew bot (0.23.2) | walktest walker |
|---|---|---|
| radius | 0.35 (the contract's) | 0.28 (`AGENT_RADIUS * 0.7`) |
| floor angle | 45 deg (engine default) | 56 deg |
| step-up | **none** | teleports up to 0.5 m |
| waypoint tolerance | 0.42 m (corner-cutting) | 0.072 m |

`deli_counter/agent_contract.json` settles it. `characters.player.
max_step_up_m` is **0.5**, and `clearances.unassisted_step_max_m` (0.1025, what
a stock capsule walks over) says a transition above it "requires the consumer
to have implemented step-up". The navmesh routes over anything up to
`nav_bake.agent_max_climb_m` (0.15, one voxel -- less disconnects the map, and
the same derivation records barriers along every flight as a rejected fix).
The ramp's open side at the wedge stands 0.118 m: inside the band the contract
hands to step-up, and the crew bot had none. The walktest's walker departs
from the contract too (it is thinner), but at this wedge Laser Tag's
departure decided.

## The fix

Laser Tag 0.24.0 gives the crew the contract's step-up: after the slide,
onto a TOP the body can stand on -- probed straight down a body-width ahead,
normal within `floor_max_angle`, lift and move both clear -- never a slope.
The top's height is tried first and the contract's full 0.5 m second, because
a ramp met from its side rises across the capsule's width. Level Factory
0.154.0 carries the contract's `max_step_up_m` into Laser Tag's scenario,
the road the radius already travels.

`lasertag/.../runners/tests/test_step_up_is_the_contracts.gd` walks the real
pill over real colliders, step-up off and on: a 0.08 m step (the control,
walked either way), a 0.118 m step and a 37.9 degree ramp met from its side
(off stops, on steps and stands on it -- feet at y 0.288 where a resting
capsule stands at 0.287), a 0.6 m box and a 50 degree slope (no step either
way).

## The measurement (`rerun_9194_with_step_up.sh`, `rerun_2026-10-07.txt`)

9194's two staged evaluation projects, copied, with the working tree's Laser
Tag and an explicit step-up; same level, seed and 25 runs:

| candidate | step-up | route completion | progress | PlayerStuck | grade |
|---|---|---|---|---|---|
| seed_9054 | off | 0.08 | 0.67 | 1,306 (1,302 in one cell) | WARN |
| seed_9054 | on | **0.84** | 0.89 | **4** | WARN |
| seed_9256 | off | 0.00 | 0.69 | 2,366 (2,363 in one cell) | PASS_WITH_TUNING |
| seed_9256 | on | **0.84** | 0.93 | **7** | PASS_WITH_TUNING |

**The control reproduces cold run 9194's own reports exactly** -- completion,
progress, stuck count and stuck cell, for both seeds -- so the evaluation is
deterministic and the step-up is the whole difference. Godot exits 1 on a
WARN grade and 0 otherwise; both of seed_9054's runs exited 1.

## Not established

- The remaining 16% of runs that do not finish were not attributed (combat is
  the likely reading; not read).
- The walktest's own body is still the thinner one; giving it the contract's
  radius (`qa.walker_capsule_radius_m`, read by nothing) is roadmap 203's other
  half.
- A consumer whose controller has no step-up still meets this edge. Whether a
  level should avoid route-critical transitions in the band is a design call
  the contract once answered with "no barriers along every flight".
