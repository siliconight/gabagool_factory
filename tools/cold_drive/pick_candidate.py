"""Pick a candidate on its merits, after the shell leg (cold run driver helper).

    python tools/cold_drive/pick_candidate.py <workspace> <mission>

Prints the seed to select. A candidate is out when its nav walktest is not
ok, or when Laser Tag raised a MAJOR route or pathing finding against it
(LT_ROUTE_NEVER_COMPLETED, LT_MAP_ENEMY_PATHING_BROKEN). Among the rest the
fewest major findings wins, then the highest route completion Laser Tag
measured, then the lowest seed. If every candidate is out, the one with the
fewest major findings is printed and the reason goes to stderr: the run still
needs a selection, and a pick that says it is the least bad is better than one
that says nothing.

ROUTE COMPLETION (2026-10-07, roadmap 203). Cold run 9194 picked seed_9054,
whose crew finished the route in 8% of Laser Tag's runs, over seed_9155 at
100%: both had zero major findings, because Laser Tag raises
LT_ROUTE_NEVER_COMPLETED only at 0%, and the tie went to the lower seed.
Completion is read from each candidate's `lasertag.report.json`
(`summary.route_completion_rate`); a candidate without one sorts last and
says so.
"""
import collections
import glob
import json
import os
import re
import sys

ws, mission = sys.argv[1], sys.argv[2]
lf = os.path.join(ws, ".level_factory")
seeds = sorted(int(re.search(r"seed_(\d+)$", p).group(1))
               for p in glob.glob(os.path.join(lf, "jobs", f"{mission}.lot_assemble.candidate.seed_*")))
assert seeds, "no candidates"
with open(os.path.join(lf, "validation", f"{mission}.json"), encoding="utf-8") as f:
    issues = json.load(f)["issues"]
major = collections.Counter()
out = collections.defaultdict(list)
for i in issues:
    m = re.search(r"seed_(\d+)$", str(i.get("candidate_id") or ""))
    if not m:
        continue
    seed = int(m.group(1))
    if i.get("severity") in ("major", "critical", "blocker"):
        major[seed] += 1
    if i.get("code") in ("LT_ROUTE_NEVER_COMPLETED", "LT_MAP_ENEMY_PATHING_BROKEN") \
            and i.get("severity") in ("major", "critical", "blocker"):
        out[seed].append(i["code"])
for seed in seeds:
    wt = glob.glob(os.path.join(lf, "jobs", f"{mission}.walktest_navqa.candidate.seed_{seed}", "*", "out",
                                "*.walktest.json"))
    if not wt:
        out[seed].append("no walktest")
        continue
    with open(wt[-1], encoding="utf-8") as f:
        if not json.load(f).get("ok"):
            out[seed].append("walktest not ok")
completion = {}
for seed in seeds:
    rep = glob.glob(os.path.join(lf, "jobs", f"{mission}.laser_tag_evaluate.candidate.seed_{seed}", "*", "out",
                                 "lasertag.report.json"))
    try:
        with open(rep[-1], encoding="utf-8") as f:
            completion[seed] = float(json.load(f)["summary"]["route_completion_rate"])
    except (IndexError, OSError, ValueError, KeyError, TypeError) as exc:
        completion[seed] = None
        print(f"  seed {seed}: no route completion read ({type(exc).__name__}); it sorts last",
              file=sys.stderr)
for seed in seeds:
    rc = "?" if completion[seed] is None else f"{completion[seed]:.2f}"
    print(f"  seed {seed}: {major[seed]} major, route completion {rc}, out for {out[seed] or 'nothing'}",
          file=sys.stderr)
good = [s for s in seeds if not out[s]]
pool = good or seeds
if not good:
    print("  every candidate is out; taking the fewest major findings", file=sys.stderr)
print(sorted(pool, key=lambda s: (major[s], -(completion[s] if completion[s] is not None else -1.0), s))[0])
