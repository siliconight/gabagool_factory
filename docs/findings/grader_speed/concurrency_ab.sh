#!/bin/bash
# Do Laser Tag's evaluations come out the same when the candidates run side by side? (the walker,
# 2026-10-11, on making cold runs faster without losing certainty.) Level Factory runs at most two
# godot_headless jobs at once (`scheduler.DEFAULT_CONCURRENCY`), so a run's three candidates'
# graders queue. This copies cold run 9246's three staged evaluation projects and runs all three AT
# THE SAME TIME with each job's exact command, then compares each report with the job's own, event
# for event. Identical reports under three-wide load are what would let the cap rise; anything else
# refuses it. It measures and prints.
#
#     bash docs/findings/grader_speed/concurrency_ab.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
G="/c/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
WS="$F/workspaces/cold-9246-ws/.level_factory"
X="$F/_scratch/grader_speed/concurrent"
rm -rf "$X" && mkdir -p "$X"
for seed in 9191 9292 9393; do
  cp -r "$WS/staging/deli_001.laser_tag_evaluate.candidate.seed_$seed" "$X/p_$seed"
done
s=$(date +%s.%N)
for seed in 9191 9292 9393; do
  ( timeout 1200 "$G" --headless --path "$(cygpath -w "$X/p_$seed")" -s res://addons/laser_tag_tool/runners/run_map_eval.gd -- \
      --bake-nav --map res://level.tscn --scenario res://mission_scenario.tres --runs 25 --seed $seed \
      --output "$(cygpath -w "$X/r_$seed.json")" < /dev/null > "$X/run_$seed.log" 2>&1
    echo "seed $seed: exit $? at $(python -c "print(round($(date +%s.%N) - $s, 1))") s" ) &
done
wait
echo "all three done, wall $(python -c "print(round($(date +%s.%N) - $s, 1))") s"
python - "$(cygpath -w "$WS")" "$(cygpath -w "$X")" <<'EOF'
import json, os, sys, glob
ws, x = sys.argv[1], sys.argv[2]
for seed in (9191, 9292, 9393):
    job = glob.glob(os.path.join(ws, "jobs", "deli_001.laser_tag_evaluate.candidate.seed_%d" % seed, "*", "out", "lasertag.report.json"))[0]
    a = json.load(open(job, encoding="utf-8"))
    b = json.load(open(os.path.join(x, "r_%d.json" % seed), encoding="utf-8"))
    fields = {k: a[k] == b[k] for k in a if k != "map"}
    print("seed %d: events %d vs the job's %d, identical %s; every field identical %s%s" % (
        seed, len(b["events"]), len(a["events"]), a["events"] == b["events"], all(fields.values()),
        "" if all(fields.values()) else " (differ: %s)" % [k for k, v in fields.items() if not v]))
EOF
rm -rf "$X"/p_*
