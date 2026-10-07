"""Laser Tag 0.24.0's release: VERSION and the CHANGELOG entry.

    python patch_lt_0240_release.py

Anchored on VERSION (b'Laser Tag 0.23.2') and on CHANGELOG.md's head (47,998
bytes, LF, as read 2026-10-07).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LT = ROOT / "lasertag"

HEAD = "# Changelog\n\n## [0.23.2] - a named event is logged at the position it carries\n"
ENTRY = """## [0.24.0] - the crew takes the contract's step-up

Cold run 9194 made a bank the score, and on both candidates that drew
`bank_branch_a04` the crew wedged leaving the basement vault:
- route completion 8% (seed_9054) and 0% (seed_9256);
- 1,302 and 2,363 of their PlayerStuck events in one 2 m cell, at the foot of
  the service stair, 0.31 m off the ramp's lower landing.

Level Factory's walktest passed the same basement.

**The two movers were different bodies, and the agent contract says which one
departed.** `deli_counter/agent_contract.json` gives the player
`max_step_up_m` 0.5. It says a transition above
`clearances.unassisted_step_max_m` (0.1025, what a stock capsule walks over at
a 45 degree floor) "requires the consumer to have implemented step-up". The
navmesh routes over anything up to `agent_max_climb_m` (0.15). The ramp's open
side at the wedge stands 0.118 m, inside that band. `LT_BotPlayerController`
had no step-up at all. The walktest's walker teleports up to 0.5 m (and is
thinner, 0.28 m against 0.35).

**The step-up.**
- `LT_BotPlayerController.max_step_up` (0.5) acts after `move_and_slide`,
  when the body is on the floor and pushing into a wall.
- A ray straight down, a body-width ahead, must find a TOP within the limit
  whose normal is inside the body's own `floor_max_angle`. A step is a top
  the body can stand on; a slope steeper than the floor is never one. This
  follows CLAUDE.md's rule that step-up must not try to rescue a slope.
- The lift and the move onto the top must both test clear.
- The top's height is tried first, and the contract's full lift second. A
  ramp met from its open side rises across the capsule's width, so a lift
  sized to the centre leaves the uphill side inside the ramp.
- `steps_taken` counts what it did.
- `LT_TestScenario.player_max_step_up_m` (0.5) is the field.
  `LT_MapEvalHarness._apply_body` hands it to the bot, and Level Factory
  0.154.0 fills it from the contract.

**Measured on 9194's two staged evaluation projects** (copied: same level, seed
and 25 runs), with step-up off as the control:

| candidate | step-up | completion | progress | PlayerStuck |
|---|---|---|---|---|
| seed_9054 | off | 0.08 | 0.67 | 1,306 |
| seed_9054 | on | 0.84 | 0.89 | 4 |
| seed_9256 | off | 0.00 | 0.69 | 2,366 |
| seed_9256 | on | 0.84 | 0.93 | 7 |

The control reproduces 9194's own reports exactly, stuck cell included. So the
evaluation is deterministic, and the step-up is the whole difference.

**Tests:** `runners/tests/test_step_up_is_the_contracts.gd` walks the real pill
over real colliders, with step-up off and on.
- **0.08 m step (the control):** walked either way, with no step taken.
- **0.118 m step:** off stops; on steps.
- **37.9 degree ramp met from its side:** off stops. On steps, walks across
  it and stands on it: feet at y 0.288, where a resting capsule stands at
  0.287, derived.
- **0.6 m box:** not climbed, and no step taken.
- **50 degree slope:** not climbed, no step taken, and the body not thrown.

It carries a watchdog: its first run, on 0.23.2, errored inside a case and
then hung for 300 s, because the error kept `quit()` from being reached.
All 16 test scripts exit 0.

"""


def main():
    v = (LT / "VERSION").read_bytes()
    assert v == b"Laser Tag 0.23.2", repr(v)
    c = (LT / "CHANGELOG.md").read_bytes()
    assert len(c) == 47998 and b"\r\n" not in c, len(c)
    text = c.decode("utf-8")
    assert text.startswith(HEAD) and text.count(HEAD) == 1
    (LT / "VERSION").write_bytes(b"Laser Tag 0.24.0")
    title = "# Changelog\n\n"
    out = title + ENTRY + text[len(title):]
    (LT / "CHANGELOG.md").write_bytes(out.encode("utf-8"))
    print("Laser Tag 0.24.0: VERSION and CHANGELOG written")


if __name__ == "__main__":
    main()
