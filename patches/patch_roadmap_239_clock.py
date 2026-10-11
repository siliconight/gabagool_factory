"""Roadmap 239: the graders no longer wait on real seconds -- cold run 9247's measurement of the
three-wide cap, and the fixed clock with the navigation on the grader's thread (Laser Tag 0.27.0,
Level Factory 0.180.0 and 0.180.1, Lot 0.117.0). Replaces 239's status, adds the two measured
paragraphs before its open list, and rewrites the list; each anchor asserted once, nothing written
on a miss. Run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_239_clock.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD = (
    "*STATUS: NARROWED 2026-10-11 -- the graders now run three at a time (Level Factory 0.179.1, "
    "the walker's call): verdicts unchanged at three and six in every trial, a few recorded positions "
    "one 0.01 m rounding step apart from three up; the faster Laser Tag clock measured and refused. "
    "Open: that noise's cause, one import of a package instead of several, and how far Laser Tag's 4x "
    "clock (a 66.7 ms physics step) reads from the game's 60 Hz.*\n"
    "\n"
    "**239. A cold run spends 88 % of its job time in its graders.**")
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-11 -- the graders no longer wait on real seconds. Cold run 9247 "
    "measured three at a time (Level Factory 0.179.1): shell leg 15.7 -> 10.4 minutes, its floor the "
    "longest evaluation, every evaluation simulating 3.91 to 3.97 times its wall time. The navigation "
    "map now updates on the grader's own thread and the graders run under `--fixed-fps 60` (Laser Tag "
    "0.27.0, Level Factory 0.180.0 and 0.180.1, Lot 0.117.0): 9247's longest evaluation 593 s -> 21 s "
    "and its walk tests 2.1-2.6 minutes -> 4-5 s, the reports their jobs' (a walk test's map-iteration "
    "count aside); fifteen candidates over five missions repeat under any clock and load, every grade "
    "and finding held. Open: the next cold run's drive, one import of a package instead of several, and "
    "the grader's step (4x against the game's 1/60 s, the walker's call).*\n"
    "\n"
    "**239. A cold run spends 88 % of its job time in its graders.**")

OPEN_OLD = (
    "**OPEN, IN ORDER.**\n"
    "1. **One import of a package, not several.** The export imports its package to bake it, the walk "
    "copy imports it again from scratch, and each walk test imports its staged project first; Godot "
    "re-verifies a reused import cache against each source's hash, so reuse is safe by construction "
    "where the sources are the same files. Worth about 1.5 to 3 minutes a run; to be measured before "
    "built.\n"
    "2. **Jams cost wall time.** A run that ends on a stuck body plays to its 180 s limit, 45 s of wall "
    "at 4x: fixing what jams (roadmap 197, Laser Tag 0.26.0's enemy) also shortens the evaluation.\n"
    "3. **The noise's cause.** Async navigation iterations and the worker pool shared across processes "
    "are the suspects (`engine_settings_probe.gd`); pinning either would move every grader's results "
    "once and needs its own A/B.\n"
    "4. **The 4x clock's fidelity.** If Godot steps physics at 66.7 ms under Laser Tag's default, its "
    "findings are a coarser simulation than the game's 60 Hz; `realtime_ab.sh` runs one evaluation at "
    "1x beside 4x, with 0.25.0's enemy and 0.26.0's, to say how far apart they read.\n")
OPEN_NEW = (
    "**MEASURED, COLD RUN 9247** (restaurant_row_001 on 9245's lot, its three lots and walk tests "
    "byte-identical to 9245's; `docs/cold_runs/cold_9247/NOTES.md`): the shell leg 10.4 minutes "
    "against 15.7, ending with its longest evaluation (seed_9104, 9.89 minutes) as predicted; the drive "
    "24.3 minutes against 30.4; the same 31.5 job-minutes done side by side. Every evaluation in both "
    "runs simulated 3.91 to 3.97 times its job's wall time: paced by real seconds, which is why three at "
    "once ran no slower and why only a shorter evaluation could shorten the leg.\n"
    "\n"
    "**A CLOCK THAT DOES NOT WAIT: ADOPTED** (`docs/findings/grader_speed/README.md`, Lever 4). Godot's "
    "`--fixed-fps 60` runs each frame as one physics step, computed as fast as the processor allows, "
    "the step unchanged. Alone it moved seed_9104's crew stuck count 9 -> 21 (in 21 s) and failed every "
    "walk test, the map EMPTY: Godot 4.7 updates a navigation map and its regions on worker threads, so "
    "when an update lands is wall time -- the cause of the 0.01 m noise at three wide as well. With the "
    "navigation on the grader's own thread, seed_9104 read identical to its job in every field under "
    "either clock, twice and three at once; fourteen more candidates over five missions repeated "
    "exactly under the fixed clock, every grade and finding holding against their jobs and one score "
    "moving a point -- from the navigation setting, not the clock (deli_001 seed_9393: the synchronised "
    "clock with synchronous navigation read exactly what the fixed one did); and 9247's three walk tests "
    "read their jobs' reports but the director's map-iteration count, in 4.2 to 5.3 s against 122 to "
    "150. Laser Tag 0.27.0 and Lot 0.117.0 set the navigation; Level Factory 0.180.0 and Lot's "
    "`walktest.py` pass the flag, which the engine hides from scripts. **The bar moved here, and why is "
    "recorded:** the old reports could not repeat under load, so \"identical to the job\" was a "
    "comparison with a reading that did not hold still; the new standard is a report that repeats under "
    "any clock and load, with the verdicts held against the old.\n"
    "\n"
    "**OPEN, IN ORDER.**\n"
    "1. **The next cold run's drive.** The shell leg should fall from 10.4 minutes to about a minute "
    "(the longest evaluation now 21 to 39 s, the walk tests 4 to 5 s); the export and the walk copy, "
    "about 10 minutes, become most of a run.\n"
    "2. **One import of a package, not several.** The export imports its package to bake it, the walk "
    "copy imports it again from scratch, and each walk test imports its staged project first; Godot "
    "re-verifies a reused import cache against each source's hash, so reuse is safe by construction "
    "where the sources are the same files. Worth about 1.5 to 3 minutes a run; to be measured before "
    "built.\n"
    "3. **The grader's step, the walker's call.** Laser Tag steps at 4x (1/15 s); at the game's own "
    "1/60 s an evaluation now costs about a minute (62 s on seed_9104) and repeats exactly, reading "
    "seed_9104 a little apart from 4x (enemy stuck 1 against 3, crew stuck 7 against 9, crew deaths 25 "
    "against 29, the same grade and score). `realtime_ab.sh`, written for this on the waiting clock, is "
    "superseded.\n"
    "\n"
    "**ANSWERED, KEPT FOR THE RECORD.** \"Jams cost wall time\": no run of 9245's or 9247's reached its "
    "180 s limit, and under the fixed clock a stalled run costs seconds. \"The noise's cause\": the "
    "navigation's worker-thread iterations, measured above.\n")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "A CLOCK THAT DOES NOT WAIT: ADOPTED" not in text, "already applied"
    for old, what in ((STATUS_OLD, "239's status and heading"), (OPEN_OLD, "239's open list")):
        assert text.count(old) == 1, (what, text.count(old))
    text = text.replace(STATUS_OLD, STATUS_NEW).replace(OPEN_OLD, OPEN_NEW)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 239 narrowed further (the clock); now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
