"""The cold-run driver's candidate picker: a tie goes to the higher grade (the walker, 2026-10-13: "yes, ties should
go to the higher grade").

`tools/cold_drive/pick_candidate.py` took the fewest major findings, then the highest route completion, then the
lowest seed, and read no grade. The breadth sweep of 2026-10-13 (`docs/findings/breadth_sweep_2026-10-13/`) found
cold run 9283 picking card_block_001's seed_9061 at PASS_WITH_TUNING 77 over seed_9263 at 89: one major each,
route completion 1.00 each, and the lower seed won. Now the higher Laser Tag `overall_score` breaks that tie
before the seed. Laser Tag's grade is a pure function of the score (`LT_ScoreCalculator.GRADE_BANDS`, the
trivial-encounter cap lowering the score itself), so the higher score is the higher grade and orders within one.
A candidate whose report carries no score sorts last among its ties and says so, as a missing completion does.

Anchored edits, each asserted exactly once and the file's sha16 pinned, nothing written until all matched.

    python patches/patch_pick_candidate_grade.py
"""
import hashlib
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
PICK = ROOT / "tools" / "cold_drive" / "pick_candidate.py"
SHA = "a9ec2cc8457729d7"

EDITS = [
    ("fewest major findings wins, then the highest route completion Laser Tag\n"
     "measured, then the lowest seed. If every candidate is out, the one with the\n",
     "fewest major findings wins, then the highest route completion Laser Tag\n"
     "measured, then the higher Laser Tag score, then the lowest seed. If every\n"
     "candidate is out, the one with the\n"),
    ("(`summary.route_completion_rate`); a candidate without one sorts last and\n"
     "says so.\n"
     "\"\"\"\n",
     "(`summary.route_completion_rate`); a candidate without one sorts last and\n"
     "says so.\n"
     "\n"
     "THE GRADE (2026-10-13, the walker: \"ties should go to the higher grade\").\n"
     "Cold run 9283 picked card_block_001's seed_9061 at PASS_WITH_TUNING 77 over\n"
     "seed_9263 at 89: one major each, completion 1.00 each, and the lower seed\n"
     "won. The report's `overall_score` now breaks that tie before the seed.\n"
     "Laser Tag's grade is a pure function of it (`GRADE_BANDS`; the trivial-\n"
     "encounter cap lowers the score itself), so the higher score is the higher\n"
     "grade. A report without one sorts last among its ties and says so.\n"
     "\"\"\"\n"),
    ("completion = {}\n"
     "for seed in seeds:\n",
     "completion = {}\n"
     "score = {}\n"
     "grade = {}\n"
     "for seed in seeds:\n"),
    ("        with open(rep[-1], encoding=\"utf-8\") as f:\n"
     "            completion[seed] = float(json.load(f)[\"summary\"][\"route_completion_rate\"])\n"
     "    except (IndexError, OSError, ValueError, KeyError, TypeError) as exc:\n"
     "        completion[seed] = None\n"
     "        print(f\"  seed {seed}: no route completion read ({type(exc).__name__}); it sorts last\",\n"
     "              file=sys.stderr)\n",
     "        with open(rep[-1], encoding=\"utf-8\") as f:\n"
     "            report = json.load(f)\n"
     "        completion[seed] = float(report[\"summary\"][\"route_completion_rate\"])\n"
     "    except (IndexError, OSError, ValueError, KeyError, TypeError) as exc:\n"
     "        completion[seed] = None\n"
     "        report = None\n"
     "        print(f\"  seed {seed}: no route completion read ({type(exc).__name__}); it sorts last\",\n"
     "              file=sys.stderr)\n"
     "    try:\n"
     "        score[seed] = int(report[\"overall_score\"])\n"
     "        grade[seed] = str(report[\"grade\"])\n"
     "    except (ValueError, KeyError, TypeError) as exc:\n"
     "        score[seed] = None\n"
     "        grade[seed] = \"?\"\n"
     "        print(f\"  seed {seed}: no grade read ({type(exc).__name__}); it sorts last among its ties\",\n"
     "              file=sys.stderr)\n"),
    ("    print(f\"  seed {seed}: {major[seed]} major, route completion {rc}, out for {out[seed] or 'nothing'}\",\n"
     "          file=sys.stderr)\n",
     "    sc = \"?\" if score[seed] is None else score[seed]\n"
     "    print(f\"  seed {seed}: {major[seed]} major, route completion {rc}, grade {grade[seed]} {sc}, \"\n"
     "          f\"out for {out[seed] or 'nothing'}\", file=sys.stderr)\n"),
    ("print(sorted(pool, key=lambda s: (major[s], -(completion[s] if completion[s] is not None else -1.0), s))[0])\n",
     "print(sorted(pool, key=lambda s: (major[s], -(completion[s] if completion[s] is not None else -1.0),\n"
     "                                  -(score[s] if score[s] is not None else -1), s))[0])\n"),
]


def main():
    raw = PICK.read_bytes()
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == SHA, ("pick_candidate.py is not the file this patch read", got)
    assert b"\r\n" not in raw, "pick_candidate.py is LF"
    text = raw.decode("utf-8")
    for old, new in EDITS:
        assert text.count(old) == 1, ("anchor", text.count(old), old[:60])
        text = text.replace(old, new)
    compile(text, str(PICK), "exec")
    PICK.write_bytes(text.encode("utf-8"))
    print("pick_candidate.py: a tie goes to the higher grade")


if __name__ == "__main__":
    main()
