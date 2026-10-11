#!/bin/bash
# The shell leg's six graders at once: cold run 9246's three Laser Tag evaluations AND three walk
# tests, all started together from copies of their staged projects with each job's exact command,
# every report compared with the job's own. `concurrency_ab.sh` proved three evaluations side by
# side; a shell leg at a raised `godot_headless` cap puts the walk tests up with them, so this is
# the load the cap would actually allow. Identical reports are what license the cap; anything
# else refuses it. It measures and prints.
#
#     bash docs/findings/grader_speed/sixwide_ab.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
G="/c/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
PY="C:\\Users\\Brannen\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe"
WS="$F/workspaces/cold-9246-ws/.level_factory"
X="$F/_scratch/grader_speed/sixwide"
rm -rf "$X" && mkdir -p "$X"
for seed in 9191 9292 9393; do
  cp -r "$WS/staging/deli_001.laser_tag_evaluate.candidate.seed_$seed" "$X/lt_$seed"
  cp -r "$WS/staging/deli_001.walktest_navqa.candidate.seed_$seed" "$X/wt_$seed"
  mkdir -p "$X/wt_out_$seed"
done
s=$(date +%s.%N)
for seed in 9191 9292 9393; do
  ( timeout 1200 "$G" --headless --path "$(cygpath -w "$X/lt_$seed")" -s res://addons/laser_tag_tool/runners/run_map_eval.gd -- \
      --bake-nav --map res://level.tscn --scenario res://mission_scenario.tres --runs 25 --seed $seed \
      --output "$(cygpath -w "$X/lt_$seed.json")" < /dev/null > "$X/lt_$seed.log" 2>&1
    echo "laser tag $seed: exit $? at $(python -c "print(round($(date +%s.%N) - $s, 1))") s" ) &
  ( cd "$F/lot" && LOT_GODOT="C:\\Godot\\4.7\\Godot_v4.7-stable_win64_console.exe" timeout 1200 "$PY" "$(cygpath -w "$F/lot/walktest.py")" \
      "$(cygpath -w "$X/wt_$seed")" site_navqa.tscn --require --report-dir "$(cygpath -w "$X/wt_out_$seed")" < /dev/null > "$X/wt_$seed.log" 2>&1
    echo "walk test $seed: exit $? at $(python -c "print(round($(date +%s.%N) - $s, 1))") s" ) &
done
wait
echo "all six done, wall $(python -c "print(round($(date +%s.%N) - $s, 1))") s"
python - "$(cygpath -w "$WS")" "$(cygpath -w "$X")" <<'EOF'
import json, os, sys, glob
ws, x = sys.argv[1], sys.argv[2]
def job(stage, seed, name):
    return json.load(open(glob.glob(os.path.join(ws, "jobs", "deli_001.%s.candidate.seed_%d" % (stage, seed), "*", "out", name))[0], encoding="utf-8"))
for seed in (9191, 9292, 9393):
    a = job("laser_tag_evaluate", seed, "lasertag.report.json")
    b = json.load(open(os.path.join(x, "lt_%d.json" % seed), encoding="utf-8"))
    same = {k: a[k] == b[k] for k in a if k != "map"}
    print("laser tag %d: %d events vs the job's %d; every field identical %s%s" % (
        seed, len(b["events"]), len(a["events"]), all(same.values()),
        "" if all(same.values()) else " (differ: %s)" % [k for k, v in same.items() if not v]))
    if a["events"] != b["events"]:
        idx = [i for i, (e, f) in enumerate(zip(a["events"], b["events"])) if e != f]
        multiset = sorted(json.dumps(e, sort_keys=True) for e in a["events"]) == sorted(json.dumps(e, sort_keys=True) for e in b["events"])
        print("    %d events differ (first at %s); the same events in another order: %s" % (len(idx), idx[:8], multiset))
        for i in idx[:4]:
            print("      job %4d %s" % (i, json.dumps(a["events"][i])[:200]))
            print("      new %4d %s" % (i, json.dumps(b["events"][i])[:200]))
    a = job("walktest_navqa", seed, "site_navqa.walktest.json")
    p = os.path.join(x, "wt_out_%d" % seed, "site_navqa.walktest.json")
    if not os.path.isfile(p):
        print("walk test %d: NO REPORT" % seed); continue
    b = json.load(open(p, encoding="utf-8"))
    same = {k: a.get(k) == b.get(k) for k in set(a) | set(b)}
    print("walk test %d: ok %s vs the job's %s; every field identical %s%s" % (
        seed, b.get("ok"), a.get("ok"), all(same.values()),
        "" if all(same.values()) else " (differ: %s)" % sorted(k for k, v in same.items() if not v)))
EOF
# the copied PROJECTS only: `lt_9*` also matches the reports beside them, and the first run of
# this script deleted the one report that differed (2026-10-11)
for seed in 9191 9292 9393; do rm -rf "$X/lt_$seed" "$X/wt_$seed"; done
