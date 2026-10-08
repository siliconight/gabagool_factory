"""Table the re-walks: each distinct staged walk test, recorded verdict against every variant run.

    python summarize.py [--out summary.txt]

Reads `results_<variant>.json` beside this file (written by `rewalk.py`) for
the variants in VARIANTS, in that order, skipping any not run. One row a
label: the recorded verdict, then each variant's -- `ok`, `FAIL n` (n
walkers not ok), `NO REPORT` (a timeout or a crash), or `-` (not walked).
Then every walker that is not ok in any variant, with its status, so a
failure can be placed. A refuted run (`*_refuted.json`) is not read.

Prints what it measured and stops. A results file without the fields this
reads FAILS rather than printing a short table.
"""
import argparse
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
VARIANTS = ["as_run", "crew_body", "crew_full", "radius_only", "floor_only"]

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=str(HERE / "summary.txt"))
a = ap.parse_args()

runs = {}
for v in VARIANTS:
    p = HERE / f"results_{v}.json"
    if p.exists():
        runs[v] = json.loads(p.read_text(encoding="utf-8"))
labels = sorted({lab for r in runs.values() for lab in r})
lines = []


def cell(row):
    if row is None:
        return "-"
    w = row.get("walked", "MISSING")
    if w == "MISSING":
        raise SystemExit("a results row without 'walked': not the shape rewalk.py writes")
    if w is None:
        return "NO REPORT"
    if "ok" not in w or "walkers" not in w:
        raise SystemExit("a walked summary without 'ok' and 'walkers'")
    return "ok" if w["ok"] else f"FAIL {not_ok(w)}"


def not_ok(summary):
    """Walkers not ok, from their statuses: the director writes a walker that
    climbed a ladder as `ok(N vertical leg(s) via ladder)`, which is ok."""
    return sum(1 for s in summary["walkers"].values() if s != "ok" and not s.startswith("ok("))


head = f"{'staged walk':38s} {'recorded':9s} " + " ".join(f"{v:12s}" for v in runs)
lines.append(head)
for lab in labels:
    rec = None
    for r in runs.values():
        if lab in r:
            rec = r[lab]["recorded"]
            break
    rec_s = "ok" if rec and rec["ok"] else f"FAIL {not_ok(rec)}" if rec else "?"
    lines.append(f"{lab:38s} {rec_s:9s} " + " ".join(f"{cell(runs[v].get(lab)):12s}" for v in runs))
counts = []
for v, r in runs.items():
    walked = [row for row in r.values() if row.get("walked") is not None]
    failed = [row for row in walked if not row["walked"]["ok"]]
    counts.append(f"{v}: {len(failed)} of {len(walked)} failed, {len(r) - len(walked)} no report")
lines.append("")
lines.extend(counts)
lines.append("")
lines.append("walkers not ok:")
for lab in labels:
    for v, r in runs.items():
        row = r.get(lab)
        if not row or not row.get("walked"):
            continue
        for name, status in sorted(row["walked"]["walkers"].items()):
            if status != "ok" and not status.startswith("ok("):
                lines.append(f"  {lab:38s} {v:12s} {name:10s} {status}")
text = "\n".join(lines) + "\n"
print(text, end="")
pathlib.Path(a.out).write_text(text, encoding="utf-8")
