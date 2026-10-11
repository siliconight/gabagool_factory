#!/bin/bash
# Is Laser Tag's evaluation the same at a faster simulation clock? (the walker, 2026-10-11:
# "is there anything intelligent we can do to make our cold runs faster without losing any
# certainty of quality".) Laser Tag runs at `Engine.time_scale` 4 by default (`run_map_eval.gd`,
# `--time-scale`), physics at fixed ticks. This reruns ONE staged evaluation -- cold run 9246's
# seed_9191, Laser Tag 0.25.0 as the job ran it -- at time scales 4 (the control, which must equal
# the job's own report), 8 and 16, and compares each report to the job's, event for event. It
# measures and prints; whether a faster clock may ship is the README's call, and it may ship only
# on identical reports.
#
#     bash docs/findings/grader_speed/timescale_ab.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
G="/c/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
P="$F/_scratch/ab_9246/A"
X="$F/_scratch/grader_speed"
JOB="$F/workspaces/cold-9246-ws/.level_factory/jobs/deli_001.laser_tag_evaluate.candidate.seed_9191/1/out/lasertag.report.json"
mkdir -p "$X"
[ -d "$P" ] || { echo "no staged copy at $P"; exit 2; }
for ts in 4 8 16; do
  O=$(cygpath -w "$X/ts_$ts.json")
  s=$(date +%s.%N)
  timeout 900 "$G" --headless --path "$(cygpath -w "$P")" -s res://addons/laser_tag_tool/runners/run_map_eval.gd -- \
    --bake-nav --map res://level.tscn --scenario res://mission_scenario.tres --runs 25 --seed 9191 \
    --time-scale $ts --output "$O" < /dev/null > "$X/ts_$ts.log" 2>&1
  rc=$?
  e=$(date +%s.%N)
  echo "time-scale $ts: exit $rc, wall $(python -c "print(round($e - $s, 1))") s"
done
python - "$(cygpath -w "$JOB")" "$(cygpath -w "$X")" <<'EOF'
import json, os, sys
job = json.load(open(sys.argv[1], encoding="utf-8"))
for ts in (4, 8, 16):
    p = os.path.join(sys.argv[2], "ts_%d.json" % ts)
    if not os.path.isfile(p):
        print("time-scale %d: NO REPORT" % ts); continue
    d = json.load(open(p, encoding="utf-8"))
    same_events = d["events"] == job["events"]
    first = next((i for i, (a, b) in enumerate(zip(d["events"], job["events"])) if a != b), None)
    print("time-scale %2d: events %d vs the job's %d, identical %s%s; summary identical %s; grade %s %s; enemy_stuck %s" % (
        ts, len(d["events"]), len(job["events"]), same_events,
        "" if same_events else " (first difference at event %s)" % first,
        d["summary"] == job["summary"], d["grade"], d["overall_score"], d["summary"]["enemy_stuck_events"]))
EOF
