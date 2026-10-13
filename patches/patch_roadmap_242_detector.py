"""Roadmap 242, 2026-10-12 night: the corner pin fixed in Laser Tag (0.29.0) and the stuck detector's two
false positives found and fixed on the way (0.28.0, 0.28.1), proven in cold runs 9266 and 9267
(`docs/findings/route_snag/`). Replaces 242's status (asserted once and still above its heading) and
appends one paragraph to its body. The index is NOT touched here: run `python tools/roadmap_status.py
--write` then `--check`.

    python patches/patch_roadmap_242_detector.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S242_OLD_HEAD = "*STATUS: NARROWED 2026-10-12 -- the snag found: a body pinned at a corner the crew bot cuts "
S242_OLD_TAIL = ("Left: Laser Tag's bot keeps the path's clearance at corners (the fix, whichever engine the game "
                 "ships); the engine, the game's choice, the default standing until it is made; the second place, "
                 "beside a meter at (35, -17).*")
S242_NEW = ("*STATUS: NARROWED 2026-10-12 -- the pin fixed in Laser Tag, and the grader's stuck count corrected "
            "twice on the way (`docs/findings/route_snag/`). The crew bot cut corners into the bake's clearance, "
            "where Godot Physics pinned it at restaurant_row_001's deli counter and Jolt at other corners: Laser "
            "Tag 0.29.0 keeps it to the mesh it plans on. Measuring that fix found `_update_stuck` counting two "
            "things that are not stuck, each costing a candidate 10 points and its crew a skipped route point -- "
            "a bot standing to fight (0.28.0; under this morning's 0.27.0, 23 of 108 events under Godot Physics "
            "and 28 of 60 under Jolt) and a round trip to a route point inside one window (0.28.1). Over 16 lots "
            "in seven families, each lot's two Godot Physics passes identical: player-stuck 108 -> 0 and 60 -> 0. "
            "Cold runs 9266 and 9267 (0 interventions each) graded the generator's own candidates as the breadth "
            "did: restaurant_row_001's three all PASS 90 at route 1.00 with no stuck event, the picked seed_9104 "
            "from PASS_WITH_TUNING 78 at route 0.72. Left: the swing itself, unmeasured again -- 9261's and "
            "9262's lots were retired (9263's reads route 1.00 under 0.29.0); two routes a run shorter under "
            "0.29.0, not attributed; the engine, the game's choice.*")

BODY_242 = """

**THE STUCK DETECTOR COUNTED FIGHTS AND ROUND TRIPS, AND THE PIN IS FIXED, 2026-10-12 night** (`docs/findings/route_snag/`: "The stuck detector counts fights" and the sections after it). The keep-on-mesh draft -- the fix the engine breadth pointed at -- first measured as a mixed result: stuck 108 -> 45 under Godot Physics and 60 -> 44 under Jolt, with five lots worse. `pin_trace.py` (census, `--why`, `trace`, `--wide`; each copy's first stuck event the census's, the control) took them apart. `_update_stuck` closes a 4 s window and records PlayerStuck when the body moved under 0.5 m and no enemy is in sight AT THAT INSTANT: 18 of the 21 added events were crew bots standing to fight (`advance_while_engaging` off), an enemy in sight in 59 or 60 of the window's 60 frames, counted as their enemy left sight on the last. Under the shipped 0.27.0, `why_breadth.py` (32 of 32 rows the same as `engine_breadth.out.txt`, the control) found 23 of 108 and 28 of 60 such, 7 of 32 lot-engine rows owing their whole -10 to them. Laser Tag 0.28.0 (`patches/patch_lt_fight_not_stuck.py`) restarts the window on a stand to fight: 18 rows up, 3 down -- and the 3 were the detector's second false positive, traced: a body out to its route point and back inside one window, ending where it began, which net displacement reads as stuck (**RETRACTED, KEPT** in the findings: "real non-progress 0.27.0 did not count"). Laser Tag 0.28.1 (`patches/patch_lt_arrival_not_stuck.py`) restarts it on an arrival too: against 0.28.0 11 rows up and none down, stuck 92 -> 70 and 24 -> 3, what was left the deli counter's one real pin and three events on crossroads_9600 seed_9600. Laser Tag 0.29.0 (`patches/patch_lt_keep_on_mesh.py`, held until then; on 0.28.0 its own "pins" were round trips timed to the millimetre by the bot's fixed speed -- the breadth's pinned count cannot tell them from geometry) then read stuck 70 -> 0 and 3 -> 0, scores up on 4 rows and down a point on 3, the same on 25. Cold run 9266 (0.28.0) and 9267 (0.28.1 and 0.29.0), 0 interventions each, graded restaurant_row_001's candidates as the breadth did. Each release's test fails on the release before it (`test_a_fight_is_not_stuck.gd`, `test_an_arrival_is_not_stuck.gd`, `test_bot_keeps_to_the_mesh.gd`); all 24 Laser Tag tests exit 0."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE STUCK DETECTOR COUNTED FIGHTS AND ROUND TRIPS" not in text, "already applied"
    i = text.find(S242_OLD_HEAD)
    assert i >= 0 and text.count(S242_OLD_HEAD) == 1, "242's status not found once"
    j = text.find(S242_OLD_TAIL, i)
    assert j > i and text.find("\n", i) > j, "242's status end not on its line"
    text = text[:i] + S242_NEW + text[j + len(S242_OLD_TAIL):]
    h = text.find("\n\n**242. ")
    assert h > 0 and text[h - len(S242_NEW):h] == S242_NEW, "242's status does not sit above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**243. ", nxt) > nxt, "243 does not follow 242"
    text = text[:nxt] + BODY_242 + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 242: status and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
