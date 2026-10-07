"""Roadmap: item 200 narrowed by Level Factory 0.153.0 and cold run 9195; item
203's two movers, re-read in the code; item 205, gas_station_a02's cooler run.

    python patch_roadmap_200_203_205.py

Anchored on PIPELINE_ROADMAP.md as patch_roadmap_202_deps_204.py left it
(1,255,627 bytes, LF, as read 2026-10-07). A status line is found by its
unique prefix, must occur once, and must sit directly above its own item's
heading. Then run `tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_200_PREFIX = ("*STATUS: OPEN 2026-10-07 -- found writing the level standard (`docs/LEVEL_STANDARD.md`, "
                     "Appendix A): four mission-brief fields reach nothing")
STATUS_200_NEW = ("*STATUS: NARROWED 2026-10-07 -- Level Factory 0.153.0 wires the dial, seen in cold run 9195's shell "
                  "leg: every candidate's pacing is a heist (travel counted) judged against the brief's 25-35 min, "
                  "reads 2.8-3.4 min \"likely TOO SHORT\", and Level Factory raised one non-blocking "
                  "`LOT_PACING_OUTSIDE_TARGET` each; the heist gate the mode switches on passed all three (and all 144 "
                  "candidate specs on disk); `batch create` names the brief fields nothing builds from. Open, the "
                  "walker's: what `target_minutes` means (a session needs a combat term; a structural route is "
                  "overstated about tenfold), and what route_shape, objective_hypotheses, extraction_relationship, "
                  "verticality and landmark should drive.*\n")

SEAM_200 = ("- Decide, with the walker, what each of the other three should drive -- or retire them from the schema.\n"
            "\n"
            "*STATUS: CLOSED 2026-10-07 -- proven in a level. Level Factory 0.152.0:")
SEAM_200_NEW = ("- Decide, with the walker, what each of the other three should drive -- or retire them from the schema.\n"
                "\n"
                "**SHIPPED: Level Factory 0.153.0** (`patches/patch_lf_brief_pacing_tests.py`, "
                "`patches/patch_lf_brief_pacing.py`; census in `docs/findings/brief_pacing_mode/`). Three "
                "disconnections, not two: besides the window and the mode, the Lot adapter matched \"outside target\" "
                "in Lot's status, which only the straddle case carries, so \"likely TOO SHORT\" and \"likely TOO "
                "LONG\" never surfaced -- and Level Factory's fake Lot wrote only the straddle status, so no test "
                "could see it. Now: the site spec carries `mode` (`mission_mode`, which Deli Counter's spec reads "
                "too) and `pacing.target_minutes`; the adapter names Lot's four statuses (a test reads Lot's source "
                "and fails when they differ) and reports an unknown status or a missing block as "
                "`LOT_PACING_UNREAD`; `batch create` prints the fields in `UNBUILT_BRIEF_FIELDS`. And the search "
                "widened the list from three to six: `route_shape`, `objective_hypotheses` and `seed_policy` build "
                "nothing either -- the first five are read only by `functional_signature`, so changing one re-locks "
                "a mission and changes no geometry. Tests: 13, 10 failing on 0.152.0. Seen in cold run 9195 "
                "(`docs/cold_runs/cold_9195/NOTES.md`), whose art leg stopped on item 205.\n"
                "\n"
                "*STATUS: CLOSED 2026-10-07 -- proven in a level. Level Factory 0.152.0:")

STATUS_203_PREFIX = ("*STATUS: OPEN 2026-10-07 -- found by cold run 9194: with the score now the bank (item 201), "
                     "Laser Tag's crew leaves bank_branch_a04's basement vault")
STATUS_203_NEW = ("*STATUS: OPEN 2026-10-07 -- found by cold run 9194: with the score now the bank (item 201), Laser "
                  "Tag's crew leaves bank_branch_a04's basement vault and wedges at one building-local point, "
                  "(-16.88, -6.89) on the basement floor, 0.31 m off the lower landing of the service stair "
                  "`a03_stair_bw` -- on both candidates that drew that bank (seed_9054, the picked one, 8% route "
                  "completion; seed_9256 0%). The walktest passes there because it walks a different body: a 0.28 m "
                  "capsule with a 56 degree floor, a 0.5 m step-up and teleport recovery, against the crew's 0.35 m, "
                  "45 degrees and none. The contract's `qa.walker_capsule_radius_m` (0.35) is read by nothing. The "
                  "driver's picker now reads route completion.*\n")

NEXT_203 = ("**NEXT.**\n"
            "- Settle which instrument is wrong at the stair foot: a frame there, then the walktest's walker against "
            "Laser Tag's crew controller (radius, steering, step) on the vault -> extraction leg.\n")
NEXT_203_NEW = ("**THE TWO MOVERS ARE DIFFERENT BODIES** (a read-only survey of both, its load-bearing lines re-read "
                "2026-10-07):\n"
                "- **Laser Tag's crew bot** (`lasertag/addons/laser_tag_tool/scripts/player/"
                "LT_BotPlayerController.gd`): a stock `CharacterBody3D` of the contract's radius 0.35, the engine's "
                "45 degree floor, no step-up; a `NavigationAgent3D` whose `path_desired_distance` is "
                "`sqrt((max(0.05, r) + speed/ticks)^2 + (cell_h/2)^2)` -- 0.42 m on the 0.15 m-cell bake -- so it "
                "takes a corner waypoint 0.42 m early with 0.05 m of clearance (0.40 bake radius minus 0.35). Its "
                "own comment derives 0.44 on a 0.25 m cell; Laser Tag 0.23.1 moved to 0.1 m cells. Stuck is under "
                "0.5 m in 4 s with no enemy in sight, and it never moves the body to recover.\n"
                "- **The walktest's walker** (`lot/godot/addons/heist_nav_qa/nav_qa_director.gd`): "
                "`capsule.radius = AGENT_RADIUS * 0.7` with `AGENT_RADIUS` defaulting to 0.4 -- 0.28 m -- a 56 "
                "degree floor, a step-up that teleports up to 0.5 m, a 0.072 m waypoint tolerance, and up to three "
                "repaths a leg, each first snapping the body back onto the navmesh within 2 m.\n"
                "- **The contract has the right number and nothing reads it:** `agent_contract.json`'s "
                "`qa.walker_capsule_radius_m` is 0.35 (also in `agent_contract.py`'s defaults); nothing in Lot reads "
                "it.\n"
                "- **Not yet established:** the survey's own computation from the staged glb puts the ramp's open "
                "north edge 0.31 m from the wedge point, about 0.2 m high where a 0.35 m capsule meets it -- a wall "
                "at 45 degrees with no step-up, a step for the walker. Consistent with the wedge; not measured in "
                "the engine.\n"
                "\n"
                "**NEXT.**\n"
                "- Give the walktest the crew's body: the contract's `walker_capsule_radius_m`, the crew's floor "
                "angle, no teleport step -- a knob that exists and is read by nothing -- and walk the vault -> "
                "extraction leg with it. If it wedges at the same point, the walktest was the wrong instrument and "
                "the geometry (the ramp's open edge) is the defect.\n"
                "- Settle which instrument is wrong at the stair foot: a frame there, then the walktest's walker "
                "against Laser Tag's crew controller (radius, steering, step) on the vault -> extraction leg.\n")

TAIL_204 = "- A test on a library-lot package: no anchor from a shell the lot does not place.\n"

ADD = r"""
*STATUS: OPEN 2026-10-07 -- found by cold run 9195, which stopped at the art leg on it: gas_station_a02's greybox lays a cooler run 25.442 m long and the composer placed the theme's 3.28 m module on it (`PRESENTATION_PLACEMENT_MISMATCH`, blocker; 166 of 167 modules aligned). The same mismatch is in cold run 9184's compose manifest, where Level Factory 0.147.0 never read it; 0.149.0 reads every placed building's package, and no run since had placed this building.*

**205. A 25 m cooler run.** Found 2026-10-07 by cold run 9195 (`docs/cold_runs/cold_9195/NOTES.md`), gas_block_001, seed_9080.

**WHAT WAS MEASURED.** `presentation/lot/gas_station_a02/portable_resource_manifest.json`, `placement_check`: 167 checked, 166 matched, 1 mismatched, `ok: false`; the mismatch is slot `cooler_run`, `greybox_extent` [25.442, 2.2, 0.9], `placed_extent` [3.28, 2.2, 0.9], stem `prop_cooler_run_delco_1997_04_w328_d90_h220`, `fit_rot` 0. The theme's kit bundles two cooler runs, 3.28 m (`w328`) and 8.00 m (`w800`). 9184's manifest for the same building reads the same, field for field.

**WHY IT STOPPED A RUN NOW.** Level Factory 0.147.0 (9184) read one placed building's compose manifest of many; 0.149.0 reads all of them (its CHANGELOG: "Every placed building's package is read"). The defect is at least as old as 9184; 0.149.0 made it a blocker, correctly, and gas_block_001 cannot ship until it is fixed.

**NEXT.**
- Read where the 25.442 m comes from: the recipe's cooler run in Deli Counter (a run sized to its wall?), and what a gas station's store holds in the land-use and art guides.
- Decide where the fix lands: a shorter run in Deli Counter, or a composer that fills a long run with the kit's modules (8.00 m x 3 + a 3.28 m, or a module grown to fit). One owner, not both: `USING_THE_FACTORY.md`'s routing table says which repo owns the domain.
- Re-run gas_block_001 cold.
"""


def _replace_status(text, prefix, new_line, heading):
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hits) == 1, "status prefix found %d times: %r" % (len(hits), prefix[:60])
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2].startswith(heading), \
        "status at line %d is not directly above %r" % (i + 1, heading)
    lines[i] = new_line.rstrip("\n")
    return "\n".join(lines)


def main():
    data = RM.read_bytes()
    assert len(data) == 1255627, "PIPELINE_ROADMAP.md is %d bytes, read at 1,255,627" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for old in (SEAM_200, NEXT_203):
        assert text.count(old) == 1, "anchor found %d times: %r" % (text.count(old), old[:70])
    assert text.endswith(TAIL_204) and text.count(TAIL_204) == 1, "the tail anchor is not the file's end"
    text = _replace_status(text, STATUS_200_PREFIX, STATUS_200_NEW, "**200. ")
    text = _replace_status(text, STATUS_203_PREFIX, STATUS_203_NEW, "**203. ")
    text = text.replace(SEAM_200, SEAM_200_NEW).replace(NEXT_203, NEXT_203_NEW) + ADD
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 200 narrowed, 203 movers, 205 appended")


if __name__ == "__main__":
    main()
