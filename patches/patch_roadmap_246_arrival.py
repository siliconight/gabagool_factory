"""Roadmap 246, 2026-10-14: CLOSED -- traced in a run and fixed in Laser Tag 0.32.0, proven by the breadth and cold run
9293. The status line is rewritten with its evidence, and one body paragraph is appended (246 is the roadmap's last
item). The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

Cold run 9293's result is read from its own driver log and the patch refuses until the run has ended.

    python patches/patch_roadmap_246_arrival.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD = "*STATUS: OPEN 2026-10-13 -- found by 245's census and not fixed; Laser Tag's to fix, bounded.*"
TAIL = ("**THE FIX** is Laser Tag's: an arrival only within `LT_Const.arrival_radius` of the route point itself. Prove "
        "it on 9185's candidate, whose completion should fall, with the factory's lots replayed as the control. "
        "Bounded: the walker has said Laser Tag work should not become a rabbit hole.\n")


def _result(n):
    log = (ROOT / "docs" / "cold_runs" / f"cold_{n}" / "driver.log").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"INTERVENTIONS: (\d+)\s+\(journal (\d+), unattributed files (\d+)\)", log)
    assert m and "DONE" in log, f"cold run {n} has not ended"
    return f"{m.group(1)} interventions"


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "TRACED AND FIXED, 2026-10-14" not in text, "already applied"
    assert text.count(STATUS_OLD) == 1, ("246's status", text.count(STATUS_OLD))
    assert text.count(TAIL) == 1 and text.endswith(TAIL), "246's FIX paragraph is not the roadmap's end"
    r9293 = _result(9293)
    status_new = (
        "*STATUS: CLOSED 2026-10-14 -- traced in a run and fixed. Laser Tag 0.32.0 (a277dd9) counts an arrival only "
        "where the bot's path reaches the route point (`LT_BotPlayerController.path_reaches_point`, Godot's own "
        "`is_target_reachable()` question). Traced first on 0.31.0 (`docs/findings/lt_arrival/arrival_trace.py`): on "
        "cold run 9185's restaurant_row_001 seed_9003 every crew bot \"arrived\" 61.2 m from its stranded objective, "
        "`is_target_reached()` false, and the route read 1.00 completed. Over the sixteen lots 0.32.0 reads 0.31.0 "
        "exactly -- every summary field, grade and score -- and 9185's seed_9003 reads route completion 1.000 -> "
        "0.000, PASS 90 -> PASS_WITH_TUNING 81, no other field moving (`arrival_breadth.py`); cold run 9293 on "
        "0.32.0, " + r9293 + ".*")
    body = (
        "\n**TRACED AND FIXED, 2026-10-14** (`docs/findings/lt_arrival/`; `patches/patch_lt_arrival_at_point.py`; "
        "`docs/cold_runs/cold_9293/`). **The trace** ran a copy of 9185's staged evaluation on 0.31.0 with one print "
        "at the arrival. Over two runs, all eight crew bots counted route point 1, the objective at Godot (-54.0, "
        "3.3, 12.47), reached while standing at (-8.3, 0.0, -28.2), 61.2 m from it and 2.5 m from their spawn. At "
        "that moment `is_target_reached()` read false and `get_final_position()` read (-8.55, 0.0, -28.05). The "
        "reachable points arrived 0.00 to 0.93 m away, their paths ending 0.00 to 0.15 m from them. The reading "
        "filed above was right, and it is now measured. **THE FIX AS FILED** said within `LT_Const.arrival_radius` "
        "of the point. It was built on Godot's own question instead: the path's end within "
        "`target_desired_distance` of the point, which is `is_target_reachable()`, as a static "
        "`path_reaches_point` the test calls with the trace's numbers. A point whose path stops short is passed as "
        "a jammed one is, its arrival uncounted, and logged as `RoutePointUnreachable`. **The breadth** "
        "(`arrival_breadth.py`, 0.31.0 exported against 0.32.0, 25 runs a lot) is its own control: the sixteen lots, "
        "every point reachable, read identically, and only 9185's stranded candidate moves, in its completion and "
        "progress alone. `runners/tests/test_an_arrival_is_at_the_point.gd` does not load on 0.31.0, and all 27 "
        "test scripts exit 0 on 0.32.0. **What it changes:** route completion, the picker's second key, now counts "
        "real arrivals throughout. A stranded candidate was already out on its walk test, and Laser Tag no longer "
        "says otherwise.\n")
    for line in body.splitlines():
        assert not re.match(r"\*\*\d+\.", line), ("a body line would parse as an item", line[:40])
    text = text.replace(STATUS_OLD, status_new) + body
    h = text.find("\n\n**246. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert text[s + 2:].startswith("*STATUS: CLOSED 2026-10-14 -- traced in a run and fixed"), "246's status moved"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 246 CLOSED; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
