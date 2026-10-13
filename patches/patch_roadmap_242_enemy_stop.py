"""Roadmap 242, 2026-10-13: restaurant_row_001 seed_9104's enemy stop, looked at -- not geometry, not a fight
(`docs/findings/stoop_breadth/`, `enemy_pin_probe.gd`). Adds the enemy's destination to the "Left:" of 242's
status (asserted once and still directly above its heading) and appends one paragraph to its body, before
243's status. The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_242_enemy_stop.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S242_OLD = ("the encounter and not the traversal; the engine, the game's choice.*")
S242_NEW = ("the encounter and not the traversal; an enemy-stuck count that cannot tell a body standing in the "
            "open with nowhere to go from a stuck one (seed_9104's, 2026-10-13, below); the engine, the game's "
            "choice.*")

BODY_242 = """

**SEED_9104'S ENEMY STOP, LOOKED AT, 2026-10-13** (`docs/findings/stoop_breadth/`; `enemy_pin_probe.gd`, `enemy_pin.txt`). Since the stoops reshaped its navmesh (cold run 9271), restaurant_row_001 seed_9104's Laser Tag report carries three EnemyStuck events where 9270's carried none: LT_Enemy_02 at (-2.05, 0.02, 12.24) at t 9.07 in runs 10 and 15, LT_Enemy_04 at (-2.75, 0.02, 12.24) at t 15.07 in run 10 -- 18 m from any stoop. **Not geometry:** on 9274's staged level, a capsule of the contract's player size on either point overlaps nothing; the only solid within 6 m at waist height is building b1's south wall, 0.58 m to the south (0.23 m clear of the body). **Not a fight:** the report has no sighting and no shot from either enemy in the six seconds before its stuck event. Laser Tag counts an enemy stuck when it still has a destination and has moved under the threshold over the window (`LT_EnemyMovement._update_stuck`), with no test for what it is doing; the same place at the same time in two runs, before any contact, reads as a destination the body cannot reach -- the path ending at a wall. **Unmeasured:** the enemy's destination at that moment, which is the next instrument; the crew's count had the same blind spot until 0.28.0 and 0.28.1."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "SEED_9104'S ENEMY STOP, LOOKED AT" not in text, "already applied"
    h = text.find("\n\n**242. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert text[s + 2:h].count(S242_OLD) == 1 and text.count(S242_OLD) == 1, "242's status end not found once"
    text = text.replace(S242_OLD, S242_NEW)
    h = text.find("\n\n**242. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert text[s + 2:h].endswith(S242_NEW), "242's status does not sit directly above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**243. ", nxt) > nxt \
        and not re.search(r"\n\n\*\*\d+\. ", text[h + 10:nxt]), "243 does not follow 242"
    text = text[:nxt] + BODY_242 + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 242: status and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
