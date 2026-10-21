"""Cold run 9374 (Deli Counter 0.252.0) against cold run 9373 (0.251.0), on what 0.252.0 touched in that level.

Of the three buildings restaurant_row_001 draws at seed 9003 only office.glb moved: its exec_suite's chairless desk
taken away (`rooms_moved.out.txt`). So:

- the validation record (`.level_factory/validation/<mission>.json`), finding for finding by code, candidate and
  message, each side counted by code;
- the export's light bake, its models and users (`docs/cold_runs/cold_<N>/export.log`), where one baked mesh fewer
  would show.

9373's workspace goes at the next run's `--end` (`factory_retire.py --pushed-only`), so its record is read from a copy
when the workspace is gone (argv[1]). Prints what it compared; writes `cold_compare.out.txt` beside this file. A file
missing on either side is a refusal, not a match.

    python patches/dc_table_chairs/cold_compare.py [copy of 9373's validation record]
"""
import collections
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[1]
OLD, NEW, MISSION = "9373", "9374", "restaurant_row_001"
lines = ["== cold run %s (Deli Counter 0.252.0) against %s (0.251.0), %s" % (NEW, OLD, MISSION)]


def record(run):
    p = F / "workspaces" / ("cold-%s-ws" % run) / ".level_factory" / "validation" / ("%s.json" % MISSION)
    if not p.is_file() and run == OLD and len(sys.argv) > 1:
        p = pathlib.Path(sys.argv[1])
    if not p.is_file():
        sys.exit("REFUSED: no validation record for cold run %s at %s" % (run, p))
    issues = json.loads(p.read_text(encoding="utf-8")).get("issues")
    if not isinstance(issues, list):
        sys.exit("REFUSED: %s has no issues list" % p)
    return issues


records = {run: record(run) for run in (OLD, NEW)}
key = lambda i: (i.get("code"), i.get("candidate_id"), i.get("message"))  # noqa: E731
for run in (OLD, NEW):
    lines.append("cold %s: %d findings; by code %s" % (run, len(records[run]),
                                                        sorted(collections.Counter(i.get("code")
                                                                                   for i in records[run]).items())))
a, b = collections.Counter(map(key, records[OLD])), collections.Counter(map(key, records[NEW]))
lines.append("findings identical by code, candidate and message: %s (only %s: %d, only %s: %d)"
             % (a == b, OLD, sum((a - b).values()), NEW, sum((b - a).values())))
for run, only in ((OLD, a - b), (NEW, b - a)):
    for k in list(only.elements())[:12]:
        lines.append("  only %s: %s %s %s" % (run, k[0], k[1], str(k[2])[:140]))
BAKE = re.compile(r"light bake: (\d+) model\(s\) and (\d+) primitive mesh\(es\) lightmapped.*?; (\d+) users")
for run in (OLD, NEW):
    p = F / "docs" / "cold_runs" / ("cold_%s" % run) / "export.log"
    m = BAKE.search(p.read_text(encoding="utf-8", errors="replace")) if p.is_file() else None
    if not m:
        sys.exit("REFUSED: no light-bake line in %s" % p)
    lines.append("cold %s's bake: %s models and %s primitive meshes lightmapped, %s users" % ((run,) + m.groups()))
txt = "\n".join(lines) + "\n"
(HERE / "cold_compare.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
