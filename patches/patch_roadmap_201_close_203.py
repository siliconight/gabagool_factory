"""Roadmap: close item 201 on cold run 9194, and file item 203 (the crew
wedges leaving the bank's vault).

    python patch_roadmap_201_close_203.py

Anchored on PIPELINE_ROADMAP.md as patch_roadmap_202.py left it (1,245,542
bytes, LF, as read 2026-10-07): 201's status line, the seam between 201's
last line and 202's status, and 202's last line (the file's end). Then run
`tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_201 = ("*STATUS: OPEN 2026-10-07 -- found by the level standard's capability sweep and re-read in the code: "
              "`site_variation.site_placements` draws the spawn and the objective building independently from the "
              "seed (`ids[next(rng) % count]`, twice), so the score is not the archetype's building, not the one "
              "holding the objective rooms, and can be the spawn building itself.*\n")
CLOSED_201 = ("*STATUS: CLOSED 2026-10-07 -- proven in a level. Level Factory 0.152.0: "
              "`building_library.score_building` names b0 when a library family answers to the archetype "
              "(`pick_lot` places it first), `site_placements(..., objective=)` draws the spawn among the other "
              "buildings, and the site spec records `objective_from`. Cold run 9194 (bank_block_001, 0 "
              "interventions): all three candidates' objective is b0, a bank (bank_branch_a04, bank_tower_a01, "
              "bank_branch_a04), `objective_from: archetype`, spawn and extraction each another building, and the "
              "walk scene's objective point is the bank's basement vault. It exposed item 203: on both "
              "bank_branch_a04 candidates the crew wedges at a service stair's foot on the way out.*\n")

SEAM = ("- A test pins it, and a cold run of a library brief shows the score where the brief put it.\n"
        "\n"
        "*STATUS: OPEN 2026-10-07 -- measured, not started:")
SEAM_NEW = ("- A test pins it, and a cold run of a library brief shows the score where the brief put it.\n"
            "\n"
            "**PROVEN, cold run 9194** (`docs/cold_runs/cold_9194/NOTES.md`). Level Factory 0.152.0 "
            "(`building_library.score_building`, `site_placements(..., objective=)`, `objective_from` in the site "
            "spec; `tests/unit/test_score_building.py`, 10 of 11 failing on 0.151.0). On bank_block_001 all three "
            "candidates put the score in b0, a bank; the spawn and the extraction are each another building; the "
            "objective point is the bank's `OBJECTIVE_A` in its basement `vault_room`. Lot moved that point 0.25 m "
            "off a desk prop on bank_branch_a04 (`LOT_DESTINATION_RESOLVED`, minor). The companions differ from "
            "9168's because the library grew between the runs, so the finding counts (63 -> 66) are not "
            "attributed to this change. What the change exposed is item 203.\n"
            "\n"
            "*STATUS: OPEN 2026-10-07 -- measured, not started:")

TAIL = ("- What is their machine? A Mac turns this item into a port: the drivers are bash and PowerShell over "
        "Windows paths.\n")

ADD = r"""
*STATUS: OPEN 2026-10-07 -- found by cold run 9194: with the score now the bank (item 201), Laser Tag's crew leaves bank_branch_a04's basement vault and wedges at one building-local point, (-16.88, -6.89) on the basement floor, 0.31 m off the lower landing of the service stair `a03_stair_bw` -- on both candidates that drew that bank (seed_9054, the picked one, 8% route completion, 1,302 of 1,306 PlayerStuck there; seed_9256 0%, 2,363 of 2,366). `walktest_navqa`'s walkers leave the same basement, so whether the stair foot or the crew controller is wrong is not established. The driver's picker took seed_9054 over seed_9155 (100%) because it read major findings, not completion; fixed in the same commit.*

**203. The crew wedges leaving the bank's vault.** Found 2026-10-07 by cold run 9194 (`docs/cold_runs/cold_9194/NOTES.md`), the first run in which the score is the bank.

**WHAT WAS MEASURED.** Laser Tag, 25 runs a candidate:
- seed_9054 (bank_branch_a04, picked): route completion 0.08, progress 0.67, 1,306 PlayerStuck, grade WARN.
- seed_9155 (bank_tower_a01): 1.00, 0.99, 5, PASS.
- seed_9256 (bank_branch_a04): 0.00, 0.69, 2,366, PASS_WITH_TUNING; `LT_ROUTE_NEVER_COMPLETED` (major).

**WHERE.** Both bank_branch_a04 candidates stick at the same building-local point (both b0 at rot 0): (-16.88, -6.89) at the basement floor (-4.20), in `vault_antechamber`, 0.31 m north of `a03_stair_bw`'s lower landing (rect x -17.9..-16.7, y -8.8..-7.2, from `deli_counter/build/bank_branch_a04.gameplay.json`'s `stair_systems`), 0.36 m from the corner of the stair's solid block (x -16.7, y -7.2).

**WHEN.** On the way out. seed_9054's crew reaches the vault about 30 s in and first sticks about 44 s in; of the 49 player-runs that stuck, 45 had already reached the vault. The extraction is east at (52, 0, 13); the stair is 25 m west of the vault, where the navmesh routes the exit.

**THE INSTRUMENTS DISAGREE, and neither is yet known to be the wrong one.** `walktest_navqa` passes all three candidates. Its chain walks the vault (proxy_3, (-54, -4.2, -12)) to a ground-floor anchor (proxy_4, (-56, 0, 12)) -- path proof ok, walkers 12 of 12 -- so a navmesh walker leaves this basement and Laser Tag's crew does not. The walktest's chain never walks the mission's own order (vault to extraction, proxy_3 to proxy_12); `LT_ROUTE_NEVER_COMPLETED`'s text says the walktest "walks the same spine", which holds for its anchors and not for their order.

**WHY IT MATTERS.** Every bank brief whose draw puts bank_branch_a04 at b0 now sends the crew into that basement; before Level Factory 0.152.0 the score was usually another building (9168's heist pointed at b2), so nothing walked there. And the run counted 0 interventions while shipping the 8% candidate -- the gates measure traversal, and this one passed between them.

**THE PICKER, FIXED.** `tools/cold_drive/pick_candidate.py` dropped a candidate only for a failed walktest or a MAJOR route finding, then took the fewest majors and the lowest seed. Laser Tag raises `LT_ROUTE_NEVER_COMPLETED` only at 0%, so seed_9054's 8% carried no major, tied seed_9155 at zero and won on its seed. It now reads `summary.route_completion_rate` from each candidate's `lasertag.report.json` after the majors. Re-run on 9194's workspace it picks seed_9155; on 9193's it still picks seed_9104, the pick that run made.

**NEXT.**
- Settle which instrument is wrong at the stair foot: a frame there, then the walktest's walker against Laser Tag's crew controller (radius, steering, step) on the vault -> extraction leg.
- Have `walktest_navqa` walk the mission's order (spawn -> objective -> extraction), so a leg the crew needs is a leg the walktest proves.
- Whether Laser Tag's route finding should be major below some completion short of zero is Laser Tag's call; the 8% case is the evidence for it.
"""


def main():
    data = RM.read_bytes()
    assert len(data) == 1245542, "PIPELINE_ROADMAP.md is %d bytes, read at 1,245,542" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for old in (STATUS_201, SEAM):
        assert text.count(old) == 1, "anchor found %d times: %r" % (text.count(old), old[:70])
    assert text.endswith(TAIL) and text.count(TAIL) == 1, "the tail anchor is not the file's end"
    text = text.replace(STATUS_201, CLOSED_201).replace(SEAM, SEAM_NEW) + ADD
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 201 closed, 203 appended")


if __name__ == "__main__":
    main()
