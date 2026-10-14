"""The cold driver's candidate picker reads Level Factory's rule instead of spelling its own (Level Factory 0.202.0).

`tools/cold_drive/pick_candidate.py` was a second spelling of the pick. Level Factory 0.169.0 moved the rule into
the tool (`packages/pipeline/pick.py`, `level-factory pick` and `make`) so that somebody making a level picks by
the rule the cold runs were graded under; this copy stayed for the driver, and on 2026-10-13 the grade tie-break
(`patch_pick_candidate_grade.py`) went into it and not into the tool, so for a day the cold runs and
`level-factory pick` picked by two rules. Level Factory 0.202.0 carries the tie-break and what a pick counts
(`docs/findings/pick_majors/`); this replaces the copy with a reader of that module -- the same arguments, the
seed on stdout, each candidate's line on stderr, and a refusal (exit 1) where the tool refuses.

The whole file is replaced; the file it replaces is pinned by its sha16 (git c868b5b), so its text is the
before. Nothing is written unless the pin matches and the new text compiles.

    python patches/patch_pick_candidate_reads_lf.py
"""
import hashlib
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
PICK = ROOT / "tools" / "cold_drive" / "pick_candidate.py"
SHA = "871792808f4bf524"

NEW = '''"""Pick a candidate on its merits, after the shell leg (cold run driver helper).

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
'''


def main():
    raw = PICK.read_bytes()
    assert b"\r\n" not in raw, "pick_candidate.py is LF"
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == SHA, ("pick_candidate.py is not the file this patch read", got)
    compile(NEW, str(PICK), "exec")
    PICK.write_bytes(NEW.encode("utf-8"))
    print("tools/cold_drive/pick_candidate.py now reads Level Factory's rule")


if __name__ == "__main__":
    main()
