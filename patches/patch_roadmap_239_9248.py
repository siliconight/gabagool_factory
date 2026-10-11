"""Roadmap 239: cold run 9248 measured the fixed clock in a real drive -- the open item that asked
for it closes, and the status says what is left. Each anchor asserted once, nothing written on a
miss. Run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_239_9248.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S_OLD = ("count aside); fifteen candidates over five missions repeat under any clock and load, every "
         "grade and finding held. Open: the next cold run's drive, one import of a package instead of "
         "several, and the grader's step (4x against the game's 1/60 s, the walker's call).*\n")
S_NEW = ("count aside); fifteen candidates over five missions repeat under any clock and load, every "
         "grade and finding held. Cold run 9248 measured it in a real drive: 24.3 -> 14.3 minutes, the "
         "shell leg 10.40 -> 1.08, every Laser Tag report identical to 9247's in every field. Open: one "
         "import of a package instead of several (the export is now half the drive), and the grader's "
         "step (4x against the game's 1/60 s, the walker's call).*\n")
O_OLD = ("**OPEN, IN ORDER.**\n"
         "1. **The next cold run's drive.** The shell leg should fall from 10.4 minutes to about a minute "
         "(the longest evaluation now 21 to 39 s, the walk tests 4 to 5 s); the export and the walk copy, "
         "about 10 minutes, become most of a run.\n"
         "2. **One import of a package, not several.**")
O_NEW = ("**MEASURED, COLD RUN 9248** (9245's lot again, the five releases above; "
         "`docs/cold_runs/cold_9248/NOTES.md`): 0 interventions, the drive 14.3 minutes against 9247's "
         "24.3, the shell leg 1.08 minutes against 10.40 -- Laser Tag's jobs 14.4 to 21.7 s against 256.6 "
         "to 593.2, the walk tests 9.0 to 9.3 s with their import against 125.8 to 154.0 -- and every "
         "Laser Tag report identical to 9247's in every field, every walk test its 9247 job's but the "
         "map-iteration count. The export, 7.0 minutes, is now half the drive.\n"
         "\n"
         "**OPEN, IN ORDER.**\n"
         "1. **One import of a package, not several.**")
N_OLD = "3. **The grader's step, the walker's call.**"
N_NEW = "2. **The grader's step, the walker's call.**"


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**MEASURED, COLD RUN 9248**" not in text, "already applied"
    for old, what in ((S_OLD, "239's status tail"), (O_OLD, "239's open item 1"), (N_OLD, "239's item 3")):
        assert text.count(old) == 1, (what, text.count(old))
    text = text.replace(S_OLD, S_NEW).replace(O_OLD, O_NEW).replace(N_OLD, N_NEW)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 239 records cold run 9248; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
