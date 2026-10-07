"""Roadmap: the walker's answers of 2026-10-07 (items 200 and 202), what the
agent contract says about item 203's wedge, and item 206 -- the extraction is
the getaway vehicle.

    python patch_roadmap_walker_answers.py

Anchored on PIPELINE_ROADMAP.md as patch_roadmap_200_203_205.py left it
(1,260,951 bytes, LF, as read 2026-10-07). A status line is found by its
unique prefix and must sit directly above its own item's heading. Then run
`tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_200_PREFIX = "*STATUS: NARROWED 2026-10-07 -- Level Factory 0.153.0 wires the dial"
STATUS_200_OLD_TAIL = ("Open, the walker's: what `target_minutes` means (a session needs a combat term; a structural "
                       "route is overstated about tenfold), and what route_shape, objective_hypotheses, "
                       "extraction_relationship, verticality and landmark should drive.*")
STATUS_200_NEW_TAIL = ("The walker, 2026-10-07: `target_minutes` is not a hard rule now -- a real length counts "
                       "fighting and acquiring the score (\"the drilling\"), which the estimate does not. Open: that "
                       "term, and what route_shape, objective_hypotheses, extraction_relationship, verticality and "
                       "landmark should drive.*")

DECISIONS_202 = ("**OPEN DECISIONS (the walker's).**\n"
                 "- Does the collaborator make levels (a zip at the certified tags is enough) or change tools (they "
                 "need the remotes and `docs/SHIPPING_A_CHANGE.md`)?\n"
                 "- What is their machine? A Mac turns this item into a port: the drivers are bash and PowerShell "
                 "over Windows paths.\n")
DECISIONS_202_NEW = ("**DECISIONS (the walker's, answered 2026-10-07).**\n"
                     "- The collaborator will \"likely just be making levels\", and a tool change \"will likely be a "
                     "fork from this repo\". So the deliverable is a zip at the certified tags with the install page, "
                     "not access to the remotes.\n"
                     "- Their machines: \"Windows and Linux\". Every driver and setup step must run on Linux too: the "
                     "cold drive is bash with a hardcoded `/c/` root, and the 23 developer scripts that carry this "
                     "machine's paths are Windows PowerShell.\n"
                     "- *As first filed:* \"Does the collaborator make levels ... or change tools?\" and \"What is "
                     "their machine? A Mac turns this item into a port.\"\n")

NEXT_203 = ("**NEXT.**\n"
            "- Give the walktest the crew's body: the contract's `walker_capsule_radius_m`,")
NEXT_203_NEW = ("**WHAT THE AGENT CONTRACT SAYS** (`deli_counter/agent_contract.json`, read 2026-10-07 after the "
                "survey). It settles which mover departs from the player it is meant to be:\n"
                "- `characters.player.max_step_up_m` is **0.5**: the contract's player lifts itself over a 0.5 m step. "
                "`clearances.unassisted_step_max_m` (0.1025) is what a capsule walks over with no step-up, and the "
                "contract says a transition above it \"requires the consumer to have implemented step-up "
                "themselves\".\n"
                "- `nav_bake.agent_max_climb_m` is 0.15, one voxel: it was 0.5 until walkers parked against a "
                "staircase's open lateral edge on walkup_siege (2026-07-28), and asking for less quantises to zero "
                "and disconnects the map. The same derivation records a REJECTED fix: \"enforcing lateral "
                "containment on every flight\", a barrier along every staircase's sides.\n"
                "- So the 0.118 m edge at the wedge sits in the band the contract hands to the consumer's step-up, "
                "and **Laser Tag's crew bot has no step-up at all** (no step code in `LT_BotPlayerController.gd`). "
                "The walktest's walker carries the contract's 0.5 m step-up but a thinner body (0.28 m, not 0.35). "
                "Each departs from the contract's player in one way; at this wedge, Laser Tag's departure is the "
                "one that decides.\n"
                "\n"
                "**NEXT, revised.**\n"
                "- Laser Tag's crew gets the contract's step-up (`max_step_up_m`), gated on the top surface being "
                "walkable (CLAUDE.md: step-up must not try to rescue a slope); re-run bank_block_001's two "
                "bank_branch_a04 candidates.\n"
                "- The walktest's walker gets the contract's body (`qa.walker_capsule_radius_m`, read by nothing "
                "today) and walks the mission's order.\n"
                "- Whether a level should carry route-critical transitions in the band at all -- for a consumer "
                "whose controller lacks step-up -- is a design call: the contract rejected barriers along every "
                "flight; a flared ramp foot would remove the band at the foot only.\n"
                "\n"
                "**NEXT, as first filed.**\n"
                "- Give the walktest the crew's body: the contract's `walker_capsule_radius_m`,")

TAIL_205 = "- Re-run gas_block_001 cold.\n"

ADD = r"""
*STATUS: OPEN 2026-10-07 -- the walker's default, not yet built: the crew leaves the score building and returns to the getaway vehicle to leave the scene. Today the extraction is a seeded draw among the buildings that are not the spawn, and it is the score building itself on 43 of 136 multi-building candidate specs on disk and on 2 of cold run 9195's 3 candidates.*

**206. The extraction is the getaway vehicle.** The walker, 2026-10-07: "On extraction, I would think the default is they have to leave the building and return to the 'getaway' car or vehicle to leave the scene."

**WHAT THE FACTORY DOES TODAY.**
- `site_variation.site_placements` draws the extraction among the buildings other than the spawn, so it can be the objective building (Level Factory 0.152.0 fixed the objective; the extraction draw is unchanged). Lot then stands the extraction at that building's first extraction marker, else its origin.
- Measured with `docs/findings/brief_pacing_mode/heist_gate_census.py`: the extraction is the objective building on 43 of 136 multi-building specs on disk; on cold run 9195, 2 of 3 candidates, whose pacing reads `travel b0->b0 0.0` -- no second half to the heist.
- 159 of 181 cold-run briefs ask for `extraction_relationship: "crew_start_backtrack"`, which nothing builds from (item 200). Lot's `site_audit` warns against exactly that shape (`S_BACKTRACK`, "the exfil rewinds the entry").
- The package carries three extraction anchors on cold run 9194's level (`lot:EXIT`, `lot:STREET`, `lot:STREET_25`), none marked as the mission's (item 204).

**NEXT.**
- The extraction becomes a point, not a building: a getaway vehicle on the street, outside the score building, never in it.
- Where it stands is a design question to weigh against `S_BACKTRACK`: at the crew's start (the briefs' "backtrack") or a different edge of the site (Lot's audit).
- A choice of several vehicle spots is replayability's first step, and the package marks the live one (item 204).
- A test: no candidate's extraction is the objective building.
"""


def _replace_in_status(text, prefix, old_tail, new_tail, heading):
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hits) == 1, "status prefix found %d times" % len(hits)
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2].startswith(heading), "status not above %r" % heading
    assert lines[i].count(old_tail) == 1 and lines[i].endswith(old_tail), "status tail not found"
    lines[i] = lines[i][: -len(old_tail)] + new_tail
    return "\n".join(lines)


def main():
    data = RM.read_bytes()
    assert len(data) == 1260951, "PIPELINE_ROADMAP.md is %d bytes, read at 1,260,951" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for old in (DECISIONS_202, NEXT_203):
        assert text.count(old) == 1, "anchor found %d times: %r" % (text.count(old), old[:70])
    assert text.endswith(TAIL_205) and text.count(TAIL_205) == 1, "the tail anchor is not the file's end"
    text = _replace_in_status(text, STATUS_200_PREFIX, STATUS_200_OLD_TAIL, STATUS_200_NEW_TAIL, "**200. ")
    text = text.replace(DECISIONS_202, DECISIONS_202_NEW).replace(NEXT_203, NEXT_203_NEW) + ADD
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 200 and 202 answered, 203 contract, 206 appended")


if __name__ == "__main__":
    main()
