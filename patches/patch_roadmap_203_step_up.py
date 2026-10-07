"""Roadmap: item 203 narrowed -- Laser Tag 0.24.0 gives the crew the contract's
step-up, Level Factory 0.154.0 carries it, measured on cold run 9194's own
candidates against a control.

    python patch_roadmap_203_step_up.py

Anchored on PIPELINE_ROADMAP.md as patch_roadmap_205_close.py left it
(1,267,407 bytes, LF, as read 2026-10-07). The status line is found by its
unique prefix and must sit directly above its item's heading. Then run
`tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_PREFIX = "*STATUS: OPEN 2026-10-07 -- found by cold run 9194: with the score now the bank (item 201)"
STATUS_NEW = ("*STATUS: NARROWED 2026-10-07 -- fixed in the crew, measured on cold run 9194's own candidates, a cold "
              "run to come: Laser Tag 0.24.0 gives the crew bot the agent contract's step-up (max_step_up_m 0.5, onto "
              "a top it can stand on, never a slope) and Level Factory 0.154.0 carries the contract's value to it. "
              "Re-run on 9194's two bank_branch_a04 evaluation projects: route completion 0.08 -> 0.84 and 0.00 -> "
              "0.84, PlayerStuck 1,306 -> 4 and 2,366 -> 7; the step-up-off control reproduces 9194's reports "
              "exactly (`docs/findings/stair_step_up/`). Open: the walktest's own body (0.28 m, not the contract's "
              "0.35) and the mission's order; and whether a level should avoid band transitions for a consumer "
              "with no step-up.*\n")

NEXT = "**NEXT, revised.**\n"
NEXT_NEW = ("**FIXED IN THE CREW: Laser Tag 0.24.0 and Level Factory 0.154.0** (`patches/patch_lt_step_up_tests.py`, "
            "`patches/patch_lt_step_up.py`, `patches/patch_lf_step_up_tests.py`, `patches/patch_lf_step_up.py`).\n"
            "- `LT_BotPlayerController` steps up after the slide when it is on the floor and walking into a wall: a "
            "ray straight down a body-width ahead must find a TOP within `max_step_up` whose normal is inside the "
            "body's `floor_max_angle`, and the lift and the move onto it must both test clear. The top's height is "
            "tried first and the contract's full lift second, because a ramp met from its open side rises across "
            "the capsule's width -- the first draft took no step there for exactly that reason.\n"
            "- `LT_TestScenario.player_max_step_up_m` (0.5), handed to the bot by the harness; Level Factory maps "
            "`characters.player.max_step_up_m` into it beside the radius.\n"
            "- `runners/tests/test_step_up_is_the_contracts.gd`: the real pill, step-up off and on, over a 0.08 m "
            "step (the control), a 0.118 m step, a 37.9 degree ramp met from its side (on: stands on it, feet at "
            "y 0.288 where a resting capsule stands at 0.287), a 0.6 m box and a 50 degree slope (never climbed).\n"
            "\n"
            "**MEASURED** (`docs/findings/stair_step_up/rerun_9194_with_step_up.sh`): 9194's two staged evaluation "
            "projects, copied, same level, seed and 25 runs --\n"
            "\n"
            "| candidate | step-up | completion | progress | PlayerStuck |\n"
            "|---|---|---|---|---|\n"
            "| seed_9054 | off | 0.08 | 0.67 | 1,306 (1,302 in one cell) |\n"
            "| seed_9054 | on | 0.84 | 0.89 | 4 |\n"
            "| seed_9256 | off | 0.00 | 0.69 | 2,366 (2,363 in one cell) |\n"
            "| seed_9256 | on | 0.84 | 0.93 | 7 |\n"
            "\n"
            "The control reproduces cold run 9194's own reports exactly, so the evaluation is deterministic and "
            "the step-up is the whole difference. Not attributed: the 16% of runs that still do not finish.\n"
            "\n"
            "**NEXT, revised.**\n")


def _replace_status(text, prefix, new_line, heading):
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hits) == 1, "status prefix found %d times" % len(hits)
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2].startswith(heading), "status not above %r" % heading
    lines[i] = new_line.rstrip("\n")
    return "\n".join(lines)


def main():
    data = RM.read_bytes()
    assert len(data) == 1267407, "PIPELINE_ROADMAP.md is %d bytes, read at 1,267,407" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.count(NEXT) == 1, "NEXT anchor found %d times" % text.count(NEXT)
    text = _replace_status(text, STATUS_PREFIX, STATUS_NEW, "**203. ")
    text = text.replace(NEXT, NEXT_NEW)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 203 narrowed")


if __name__ == "__main__":
    main()
