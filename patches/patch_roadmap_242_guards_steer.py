"""Roadmap 242 and 197, 2026-10-13: Laser Tag 0.31.0 -- the guards walk as the crew does, keeping to the mesh
and stepping up -- measured on the 16 lots, proven in cold run 9276, and what it leaves. 242's status clause on
the 23 rewritten and one paragraph appended after "THE ENEMY COUNT CLASSED, AND LASER TAG 0.30.0", before 243's
status; 197's "Left" rewritten -- its queued enemies answered by 0.30.0 and 0.31.0, and its door clause grounded
in the contract. The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_242_guards_steer.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S242_OLD = ("the 23 left, 21 of them at two places where the guards lack what the crew bot has -- off the mesh "
            "against a wall's end with a guard ahead (warehouse_yard_001 seed_9206, 13, its WARN 73), and against "
            "a stair ramp's low side edge that the bake joins to the floor and only a step-up crosses "
            "(crossroads_9600 seed_9600, 8) (below)")
S242_NEW = ("the guards walking as the crew does, 2026-10-13 -- Laser Tag 0.31.0 keeps them to the mesh and steps "
            "them up as the contract's player does, the crew's own code moved into one `LT_Steering`: over the 16 "
            "lots enemy stuck 23 -> 14 with the change switched off reading 0.30.0 exactly, the stair ramp's 8 "
            "gone, and cold run 9276 (0 interventions) grading restaurant_row_001 as 9275 did; left, 14 guards "
            "at one wall's end on warehouse_yard_001 seed_9206 that the physics holds, and the fights 0.31.0 "
            "moved, read on the breadth and not yet judged (below)")

S197_OLD = ("Left: the 28, enemies queued on the crew's route along the deli's west wall among a kitchen grill and "
            "a shelf run, touching no static geometry -- each enemy's destination when it stalls is the next "
            "instrument; and the recipe's three floor doors under the contract's 1.25 m, flagged by a warning "
            "nothing reads.*")
S197_NEW = ("The 28 are answered, 2026-10-13 (roadmap 242): Laser Tag 0.30.0 classes this lot's 30 under 0.29.0 as "
            "29 guards held only by other guards and one stuck, and 0.31.0 takes the one -- PASS_WITH_TUNING 80, "
            "no guard stuck. Left: the recipe's three floor doors under the contract's 1.25 m, flagged by a "
            "warning nothing reads -- and that 1.25 is derived at a 0.15 m bake cell, where the contract's own "
            "`nav_bake.cell_size_m` is 0.1, at which its formula, 2 x ceil(0.4 / cell) x cell + 2 x cell, gives "
            "1.0 (`agent_contract.json`, `clearances.derivation`), so whether the doors widen or the clearance is "
            "re-derived is a decision, and a re-derivation moves every aisle and landing built from it.*")

ANCHOR = "**THE ENEMY COUNT CLASSED, AND LASER TAG 0.30.0, 2026-10-13**"

BODY_242 = """

**THE GUARDS WALK AS THE CREW DOES: LASER TAG 0.31.0, 2026-10-13** (`docs/findings/route_snag/guard_steer_breadth.py`, `guard_steer_breadth.out.txt`; `patches/patch_lt_guards_steer.py`; `docs/cold_runs/cold_9276/`). The crew bot has stepped up as the contract's player does since 0.24.0 and kept to the mesh it plans on since 0.29.0; the guards did neither, though `agent_contract.json` says npc_standard shares the player's metrics. 0.31.0 moves the crew's two routines into `LT_Steering`, static functions both bodies call, and the guards call them: each step kept on the mesh, a step-up after the slide to the scenario's `player_max_step_up_m` (0.5). The 16 lots graded three ways under Godot Physics -- 0.30.0, 0.31.0, and 0.31.0 with the guards' steering switched off in the copy. **THE CONTROL:** switched off, 0.31.0 reads 0.30.0 exactly, every summary field, grade and score, on all 16: the move changed nothing the crew does. **Measured:** enemy stuck 23 -> 14, blocked 159 -> 143. crossroads_9600 seed_9600's 8 at the stair ramp's open side are gone (PASS_WITH_TUNING 89 -> PASS 90), and so are deli_001 seed_9191's and club_block_014 seed_9282's one each. warehouse_yard_001 seed_9206's are not: 14 stand at the same wall's end. Five touch only that wall and the floor, their velocity after the slide -- keep-to-the-mesh's correction -- pointing away from the wall, and no slide travelled 0.1 mm; four of them are off the floor, their fall speed growing to -8.49 m/s, and do not fall. A body the physics holds there, as Godot Physics held the crew at restaurant_row_001's deli counter before 0.29.0; how a guard gets 5 cm off the mesh with keep-to-the-mesh on is not measured. **The fights moved on every lot**, and the grades with them on three: warehouse_yard_001 seed_9206 WARN 73 -> PASS_WITH_TUNING 83 on OVEREXPOSED's line (mean crew survival 5.77 -> 7.34 s, one run's crew lasting 46.7 s where none had lasted 7.5), seed_9004 89 -> PASS 90 (a team wipe gone), gas_block_001 seed_9181 88 -> 87 (route 0.88 -> 0.80, a team wipe more, and two crew-stuck events where there were none -- traced in run 12, `pin_trace.py`, a crew member turning back and forth at its path's last point with its route point 0.58 m past it, a mesh and a point the lot already had). **In a real drive**, cold run 9276 (0 interventions): restaurant_row_001's three PASS 90 at route 1.00 with no stuck event as in 9275, seed_9104 picked, findings 117 -> 117, every candidate's fight moved. **Left:** the wall's end on warehouse_yard_001 seed_9206, a hold in the engine reached from off the mesh; the gas lot's route point past its path's end; and whether the fights 0.31.0 moved read better or worse -- an encounter's question this item does not answer."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE GUARDS WALK AS THE CREW DOES: LASER TAG 0.31.0" not in text, "already applied"
    for old in (S242_OLD, S197_OLD):
        assert text.count(old) == 1, ("not found once", old[:60], text.count(old))
    text = text.replace(S242_OLD, S242_NEW).replace(S197_OLD, S197_NEW)
    h = text.find("\n\n**242. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert S242_NEW in text[s:h], "242's status does not sit directly above its heading"
    h197 = text.find("\n\n**197. ")
    s197 = text.rfind("\n\n*STATUS:", 0, h197)
    assert S197_NEW in text[s197:h197], "197's status does not sit directly above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**243. ", nxt) > nxt \
        and not re.search(r"\n\n\*\*\d+\. ", text[h + 10:nxt]), "243 does not follow 242"
    a = text.rfind(ANCHOR, h, nxt)
    assert a > h and text.count(ANCHOR) == 1, "the 0.30.0 paragraph is not 242's, once"
    assert text.find("\n\n", a) == nxt, "the 0.30.0 paragraph is not 242's last"
    text = text[:nxt] + BODY_242 + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 242 and 197: statuses and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
