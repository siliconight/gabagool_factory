"""Pick a candidate on its merits, after the shell leg (cold run driver helper).

    python tools/cold_drive/pick_candidate.py <workspace> <mission>

Prints the seed to select, and each candidate's line to stderr. THE RULE IS LEVEL FACTORY'S:
`level_factory/packages/pipeline/pick.py` (0.202.0), the one `level-factory pick` and
`level-factory make` select by -- who is out, what counts as a major, and the order after that.
This file reads it and spells none of it.

It used to spell it. Level Factory 0.169.0 moved the rule into the tool so that somebody making
a level picks by the rule the cold runs were graded under; this copy stayed for the driver, and
on 2026-10-13 the grade tie-break (`patches/patch_pick_candidate_grade.py`, the walker: "ties
should go to the higher grade") went into this copy and not into the tool, so for a day the
cold runs and `level-factory pick` picked by two rules. Nothing kept the two together, so now
there is one (`patches/patch_pick_candidate_reads_lf.py`). Where the tool refuses -- no
candidate, no validation file -- this exits 1 with its reason rather than guessing.
"""
import pathlib
import sys

F = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(F / "level_factory"))
from packages.pipeline import pick  # noqa: E402  (Level Factory's rule)

ws, mission = pathlib.Path(sys.argv[1]), sys.argv[2]
try:
    rows = pick.candidates(ws / ".level_factory", mission)
except ValueError as exc:
    sys.exit(f"pick_candidate: {exc}")
best, every_out = pick.pick(rows)
for row in rows:
    print(f"  {row.line()}", file=sys.stderr)
if every_out:
    print("  every candidate is out; taking the fewest major findings", file=sys.stderr)
print(best.seed)
