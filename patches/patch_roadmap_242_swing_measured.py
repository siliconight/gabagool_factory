"""Roadmap 242, 2026-10-13: the swing measured again, by the stoops' graders' breadth (roadmap 240,
`docs/findings/stoop_breadth/`). Replaces the "Left: the swing itself, unmeasured again" clause of 242's status
(asserted once and still directly above its heading) and appends one paragraph to its body, before 243's
status. The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_242_swing_measured.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S242_OLD = "Left: the swing itself, unmeasured again -- 9261's and 9262's lots were retired"
S242_NEW = ("The swing measured again under 0.29.0 on 2026-10-13, by the stoops' breadth (roadmap 240): a "
            "change on the far side of the street, controls holding, moved the score on 2 of 8 lots -- one grade "
            "up a notch, one a point down within its grade -- each route move a single team wipe and no stuck "
            "event within 10.9 m of the change. Left: the swing itself -- an encounter's, now, not a snag's -- "
            "9261's and 9262's lots were retired")

BODY_242 = """

**THE SWING UNDER 0.29.0, MEASURED BY THE STOOPS, 2026-10-13** (`docs/findings/stoop_breadth/`, run for roadmap 240). The stoops' breadth is this item's furniture arms in another form: eight staged lots, each graded with its rowhomes at `stoop=0` twice -- the control, identical in every field on all eight -- and with Deli Counter 0.212.0's stoops and railings, a change on the far side of the street that grows the navmesh by 115 to 297 polygons. Laser Tag 0.29.0, 25 runs a lot at `--fixed-fps 60`, Godot Physics. **Moved:** the score on 2 of 8 lots -- warehouse_yard_001 seed_9004 PASS_WITH_TUNING 89 -> PASS 90, a grade up a notch, and seed_9206 68 -> 67 within WARN; route completion on the same two, 0.96 -> 1.0 and 1.0 -> 0.96, each one team wipe in 25 runs with no timeout; enemy-stuck counts on two others; the fight fields (shots, engagement distance, survival, deaths) on seven. **Not moved:** seven grades; no player-stuck event in any arm; and of 229 stuck events none within 10.9 m of a stoop. Before 0.29.0, the lamps becoming poles moved this lot family's picked route 1.00 -> 0.64 through two snags; under 0.29.0 a change of this size moves single encounters. The swing a grade still carries is the encounter's, a point or a notch on a quarter of the lots here; no remedy is proposed."""


#: and a correction to 240's breadth paragraph, written the same day: seed_9206's GRADE did not move, only its
#: score within WARN, so seven grades held, not six
C240_OLD = ("six grades unchanged, warehouse_yard_001 seed_9004 PASS_WITH_TUNING 89 -> PASS 90 and seed_9206 "
            "WARN 68 -> 67, each route move")
C240_NEW = ("seven grades unchanged -- warehouse_yard_001 seed_9004 PASS_WITH_TUNING 89 -> PASS 90, and seed_9206's "
            "score 68 -> 67 within WARN (first written \"six grades unchanged\"; WARN held) -- each route move")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE SWING UNDER 0.29.0, MEASURED BY THE STOOPS" not in text, "already applied"
    assert text.count(C240_OLD) == 1, "240's breadth wording not found once"
    text = text.replace(C240_OLD, C240_NEW)
    assert text.count(S242_OLD) == 1, "242's status clause not found once"
    text = text.replace(S242_OLD, S242_NEW)
    h = text.find("\n\n**242. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert h > 0 and S242_NEW in text[s:h], "242's status does not sit directly above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**243. ", nxt) > nxt \
        and not re.search(r"\n\n\*\*\d+\. ", text[h + 10:nxt]), "243 does not follow 242"
    text = text[:nxt] + BODY_242 + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 242: status and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
