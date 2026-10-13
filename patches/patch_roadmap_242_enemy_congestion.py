"""Roadmap 242, 2026-10-13: seed_9104's enemy stop TRACED -- enemies queued behind enemies, not an unreachable
destination (`docs/findings/stoop_breadth/enemy_stop_trace.py`). Corrects the status's clause written the same
day, keeping what it said in the body, and appends one paragraph after the enemy-stop paragraph, before 243's
status. The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_242_enemy_congestion.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S242_OLD = ("an enemy-stuck count that cannot tell a body standing in the open with nowhere to go from a stuck one "
            "(seed_9104's, 2026-10-13, below)")
S242_NEW = ("an enemy-stuck count that counts a body held by a TEAMMATE -- seed_9104's three, 2026-10-13, are "
            "enemies queued single file on one path with no avoidance (below); how much of the WARN lots' 51 "
            "and 23 is the same, unmeasured")

BODY_242 = """

**THE ENEMY STOP, TRACED, 2026-10-13** (`docs/findings/stoop_breadth/enemy_stop_trace.py`, `enemy_stop_trace.out.txt`). **RETRACTED, KEPT ABOVE:** "a destination the body cannot reach -- the path ending at a wall". A copy of 9274's staged evaluation, its `LT_EnemyBrain._on_stuck` printing the agent's state and nothing more, runs the job's 25 runs -- THE CONTROL: its summary and its three EnemyStuck events are the job's. At each event the enemy's target is reachable, the crew member it seeks about 36 m east, its 49-point path at index 1 with that corner 1.84 m (2.55 m) away on flat ground; its velocity after `move_and_slide` is zero; and that frame's one slide collision is ANOTHER ENEMY -- LT_Enemy_02 against LT_Enemy_06 standing just east of it (runs 10 and 15), LT_Enemy_04 against LT_Enemy_02 (run 10). Three enemies queue single file along b1's south wall: in SEEK the brain re-sets the destination every physics frame, the enemies steer with no avoidance, and `_update_stuck` counts a body held by a teammate. **So the stoops' 0 -> 3 is congestion** -- their navmesh change lined three enemies up on one path -- the class of count 0.28.0 and 0.28.1 took out of the crew's. **Next:** the same trace on the WARN lots (warehouse_yard_001 seed_9206's 51, bank_block_001 seed_9256's 23), and, if congestion is much of it, a count that asks what holds the body, priced on the breadth as 0.28.0 was."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE ENEMY STOP, TRACED, 2026-10-13" not in text, "already applied"
    assert text.count(S242_OLD) == 1, "242's status clause not found once"
    text = text.replace(S242_OLD, S242_NEW)
    h = text.find("\n\n**242. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert S242_NEW in text[s:h], "242's status does not sit directly above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**243. ", nxt) > nxt \
        and not re.search(r"\n\n\*\*\d+\. ", text[h + 10:nxt]), "243 does not follow 242"
    assert text.rfind("**SEED_9104'S ENEMY STOP, LOOKED AT, 2026-10-13**", h, nxt) > h, "the enemy-stop paragraph is not 242's last"
    text = text[:nxt] + BODY_242 + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 242: status and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
