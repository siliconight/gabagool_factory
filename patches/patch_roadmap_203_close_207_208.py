"""Roadmap: close item 203 on cold run 9197; file 207 (a strip club's two stage
rigs refused) and 208 (the walktest walks a thinner body, not in the mission's
order), the threads 203 leaves open.

    python patch_roadmap_203_close_207_208.py

Anchored on PIPELINE_ROADMAP.md as patch_roadmap_203_step_up.py left it
(1,269,206 bytes, LF, as read 2026-10-07): 203's status line by its unique
prefix, directly above its heading, and 206's last line (the file's end).
Then run `tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_PREFIX = "*STATUS: NARROWED 2026-10-07 -- fixed in the crew, measured on cold run 9194's own candidates"
STATUS_NEW = ("*STATUS: CLOSED 2026-10-07 -- proven in a level. Laser Tag 0.24.0 gives the crew bot the agent "
              "contract's step-up (max_step_up_m 0.5, onto a top it can stand on, never a slope) and Level Factory "
              "0.154.0 carries the contract's value to it. Cold run 9197 (bank_block_001, 0 interventions, 9194's "
              "seeds): route completion on the two bank_branch_a04 candidates 0.08 -> 0.84 and 0.00 -> 0.84, "
              "`LT_ROUTE_NEVER_COMPLETED` 1 -> 0, matching the rerun on 9194's staged projects whose step-up-off "
              "control reproduced 9194 exactly (`docs/findings/stair_step_up/`); the picker took seed_9155 (1.00) on "
              "completion. The threads left open are items 208 (the walktest's body and order) and the design call "
              "on band transitions recorded below.*\n")

TAIL_206 = "- A test: no candidate's extraction is the objective building.\n"

ADD = r"""
*STATUS: OPEN 2026-10-07 -- recurring, unexplained: whenever a level places a strip club, Lux refuses two of its club anchors (`LUX_CLUB_REFUSED`, moderate, non-blocking). Cold run 9197: "Baked 42 club rig(s) from 44 club anchor(s); refused b2/main_floor_stage, b2/vip_wing_stage" (strip_club_a01); cold run 9167 (club_block_014) carried the same code. Filed nowhere until now.*

**207. A strip club's two stages are not lit.** Found 2026-10-07 attributing cold run 9197's findings (`docs/cold_runs/cold_9197/NOTES.md`): the code arrived with the picked candidate's strip_club_a01, not with the release under test.

**WHAT WAS MEASURED.** 9197's validation, seed_9155: `LUX_CLUB_REFUSED` -- 42 of 44 club anchors became rigs; the two refused are the main-floor and VIP-wing stages, the rooms a club is for. Beside it, `ZOO_FIXTURES_MARKERLESS` (info): 13 of 18 club fixtures are hardware with no emitter marker by design (club_wash, stage_light), and Lux's fixture gate counts the other 5. Cold run 9167's driver log carries `LUX_CLUB_REFUSED 0 -> 1` on club_block_014; its notes do not explain it.

**NEXT.**
- Read why Lux refuses a stage anchor (the refusal's own reason, in Lux's club rig builder), on strip_club_a01 and the other club variants.
- Then decide whether the stage is lit by its hardware (the markerless fixtures) and the refusal is correct, or a rig is missing.
- The walker's standing call applies: dens of sin are dark buildings, but a stage is where a club's light goes.

*STATUS: OPEN 2026-10-07 -- measured, not fixed: `walktest_navqa`'s walker is a thinner body than the agent contract's player (0.28 m, `AGENT_RADIUS * 0.7`, against `characters.player.radius_m` 0.35; the contract's `qa.walker_capsule_radius_m` 0.35 is read by nothing), with a 56 degree floor and a 0.5 m teleport step-up, and it walks home -> each anchor plus a chain through them, never the mission's order (spawn -> objective -> extraction). It passed cold run 9194's bank basement where the crew wedged.*

**208. The walktest walks a different body, in a different order.** Split out of item 203 on 2026-10-07, after the crew's own fix (Laser Tag 0.24.0) closed the wedge.

**WHAT WAS MEASURED** (`lot/godot/addons/heist_nav_qa/nav_qa_director.gd`, re-read 2026-10-07):
- `capsule.radius = AGENT_RADIUS * 0.7` with `AGENT_RADIUS` the bake radius (0.4, `DC_NAV_RADIUS`) -- 0.28 m. The contract's player is 0.35, and `qa.walker_capsule_radius_m` (0.35) sits in `agent_contract.json` and `agent_contract.py`'s defaults with no reader: a knob with no effect.
- Floor 56 degrees (`DC_NAV_SLOPE` + 1); a step-up that teleports up to 0.5 m with no check that it lands on a floor; a 0.072 m waypoint tolerance; up to three repaths a leg, each snapping the body back onto the navmesh within 2 m.
- Path proofs are navmesh queries that move no body; the walkers walk the anchors in marker order. On cold run 9194 the chain walked the vault to a ground-floor anchor, never the vault to the extraction.

**WHY IT MATTERS.** The walktest picks the candidate (a walktest that is not ok puts it out), and a lenient walker passes geometry the crew cannot cross: it passed the stair foot where 9194's crew wedged at 8% and 0%. A thinner body clears doors and corners the contract's player does not.

**NEXT.**
- The walker reads the contract's body: `walker_capsule_radius_m`, and the floor angle the crew stands on.
- Its step-up lands only on a floor (the rule Laser Tag 0.24.0's carries).
- It walks the mission's order as well as the chain.
- Measure first: re-walk the kept workspaces' candidates with the contract's body and count what fails, before it becomes the gate it already is.
"""


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
    assert len(data) == 1269206, "PIPELINE_ROADMAP.md is %d bytes, read at 1,269,206" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.endswith(TAIL_206) and text.count(TAIL_206) == 1, "the tail anchor is not the file's end"
    text = _replace_status(text, STATUS_PREFIX, STATUS_NEW, "**203. ") + ADD
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 203 closed, 207 and 208 appended")


if __name__ == "__main__":
    main()
