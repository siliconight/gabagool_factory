"""Roadmap 242, 2026-10-13: the enemy count classed on the WARN lots, Laser Tag 0.30.0 shipped (a guard held
only by other bots is EnemyBlocked, uncharged), proven in cold run 9275, and the 23 events it still counts placed.
Rewrites the status's enemy-count clause and appends one paragraph after "THE ENEMY STOP, TRACED", before 243's
status. The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_242_enemy_blocked.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S242_OLD = ("an enemy-stuck count that counts a body held by a TEAMMATE -- seed_9104's three, 2026-10-13, are "
            "enemies queued single file on one path with no avoidance (below); how much of the WARN lots' 51 "
            "and 23 is the same, unmeasured")
S242_NEW = ("the enemy count's congestion, taken out 2026-10-13 -- Laser Tag 0.30.0 records a guard held only by "
            "other bots as EnemyBlocked, which the score does not charge: over the 16 lots enemy stuck 182 -> 23 "
            "with every other field identical, deli_001 seed_9393 and bank_block_001 seed_9256 WARN -> "
            "PASS_WITH_TUNING, and cold run 9275 (0 interventions) graded seed_9104's three as blocked; the 23 "
            "left, 21 of them at two places where the guards lack what the crew bot has -- off the mesh against a "
            "wall's end with a guard ahead (warehouse_yard_001 seed_9206, 13, its WARN 73), and against a stair "
            "ramp's low side edge that the bake joins to the floor and only a step-up crosses (crossroads_9600 "
            "seed_9600, 8) (below)")

ANCHOR = "**THE ENEMY STOP, TRACED, 2026-10-13**"

BODY_242 = """

**THE ENEMY COUNT CLASSED, AND LASER TAG 0.30.0, 2026-10-13** (`docs/findings/stoop_breadth/enemy_stop_trace.py --lot`, `enemy_stop_lots.out.txt`; `docs/findings/route_snag/blocked_breadth.py`, `blocked_breadth.out.txt`; `patches/patch_lt_queue_not_stuck.py`; `docs/cold_runs/cold_9275/`). The trace on the WARN lots, two runs a lot identical as its control: warehouse_yard_001 seed_9206's 51 EnemyStuck each had another guard among the closing frame's contacts, bank_block_001 seed_9256's 23 another guard (22) or a crew member (1), club_block_014 seed_9282's one the level only. **RETRACTED, KEPT:** "73 of 75 are a body held by another body" -- the sum is 74, and the census asked whether ANY contact was a body, not whether bodies were all that held it. **Laser Tag 0.30.0** asks the second as a held guard's window closes: contacts under the feet left out, all the rest bots, and it records EnemyBlocked, which NPC Pathing does not charge; any contact of the level and EnemyStuck as before; a blocked guard is handled as a stuck one -- the same state, jitter and random draws. Over the 16 lots under Godot Physics against 0.29.0 -- every other summary field identical, and on every lot the new stuck and blocked adding up to the old stuck -- enemy stuck 182 -> 23 and 159 blocked; six scores up by exactly what `_score_pathing` charged for the events taken out, none down; deli_001 seed_9393 WARN 74 -> PASS_WITH_TUNING 80, bank_block_001 seed_9256 WARN 72 -> PASS_WITH_TUNING 75, warehouse_yard_001 seed_9206 WARN 68 -> 73. **In a real drive**, cold run 9275 (0 interventions): restaurant_row_001's three PASS 90 as in 9274, seed_9104's three EnemyStuck its three EnemyBlocked -- the same runs, times, guards and positions -- and every other field and event the same. **THE 23 LEFT, PLACED** (`--lot --contacts --raw`; `enemy_stop_residue.out.txt`, `enemy_stop_residue_raw.out.txt`). 21 stand at two places. warehouse_yard_001 seed_9206's 13 at (1.50, 16.86): each guard touches the end of building b1's south wall (`ext_col_0_S_seg22`, its face at x 1.85, normal -x) and another guard. The mesh's edge there is x 1.45, so the guard stands 5 cm off the mesh. Its next path point is round the wall's end, 0.83 m away, and the other guard stands across that way. crossroads_9600 seed_9600's 8 at (44.41, 0.00, -6.63): each guard's capsule rests on the long side edge of building b2's stair ramp, 0.18 m above the floor, the contact 60 degrees from up -- the ramp itself is 37.5 degrees, and the contact's normal is reproduced from the collider's corners to two decimals. The guard's path crosses that side edge onto the ramp: its next point, 0.64 m away, lies on the ramp's top, so the bake joins the floor to the ramp across its side near the foot. A rise there lies between the body's 0.1025 m unassisted step and the bake's one-voxel climb, the band `agent_contract.json`'s `agent_max_climb_derivation` names: a transition the contract leaves to the consumer's step-up. Laser Tag's crew bot steps up to the contract's 0.5 m and has kept to the mesh since 0.29.0; its guards do neither. deli_001 seed_9191's one touches nothing but the floor, and club_block_014 seed_9282's one a cover prop. **Next:** the guards steered as the crew is -- kept to the mesh, stepping up to the contract's height -- priced on the 16 lots as 0.29.0 was."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE ENEMY COUNT CLASSED, AND LASER TAG 0.30.0" not in text, "already applied"
    assert text.count(S242_OLD) == 1, "242's status clause not found once"
    text = text.replace(S242_OLD, S242_NEW)
    h = text.find("\n\n**242. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert S242_NEW in text[s:h], "242's status does not sit directly above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**243. ", nxt) > nxt \
        and not re.search(r"\n\n\*\*\d+\. ", text[h + 10:nxt]), "243 does not follow 242"
    a = text.rfind(ANCHOR, h, nxt)
    assert a > h and text.count(ANCHOR) == 1, "the enemy-stop trace paragraph is not 242's, once"
    assert text.find("\n\n", a) == nxt, "the enemy-stop trace paragraph is not 242's last"
    text = text[:nxt] + BODY_242 + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 242: status and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
