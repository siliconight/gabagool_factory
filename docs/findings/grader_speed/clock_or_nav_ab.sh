#!/bin/bash
# Is it the clock or the navigation setting that moves a report? `breadth_ab.py` ran fourteen staged
# evaluations under `--fixed-fps 60` with the navigation map's iterations synchronous: every one read
# the same twice, restaurant_row_001's matched their jobs in every field, and the others differed
# from their jobs -- by a few 0.01 m positions, and on cold run 9246's deli seed_9393 by a cascade
# from run 1 that moved the score. Laser Tag times everything by physics steps (its `_now` is the
# run's accumulated physics delta, its brains and bodies run in `_physics_process`), so either the
# synchronous navigation or the frame structure of the clock is what differs. Two arms on copies of
# seed_9393's staged project, both on the job's own synchronised 4x clock, one at a time on a quiet
# machine:
#   A  as the job ran (asynchronous navigation): does the job reproduce at all?
#   E  synchronous navigation: E = the fixed-clock run would put the difference on the navigation
#      setting, E = the job on the clock.
# It measures and prints.
#
#     bash docs/findings/grader_speed/clock_or_nav_ab.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
G="/c/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
WS="$F/workspaces/cold-9246-ws/.level_factory"
JOB="deli_001.laser_tag_evaluate.candidate.seed_9393"
X="$F/_scratch/grader_speed/clock_or_nav"
rm -rf "$X" && mkdir -p "$X"
for arm in A E; do cp -r "$WS/staging/$JOB" "$X/p_$arm"; done
printf '\n[navigation]\n\nworld/map_use_async_iterations=false\nworld/region_use_async_iterations=false\n' >> "$X/p_E/project.godot"
for arm in A E; do
  s=$(date +%s.%N)
  timeout 1800 "$G" --headless --path "$(cygpath -w "$X/p_$arm")" -s res://addons/laser_tag_tool/runners/run_map_eval.gd -- \
    --bake-nav --map res://level.tscn --scenario res://mission_scenario.tres --runs 25 --seed 9393 \
    --output "$(cygpath -w "$X/r_$arm.json")" < /dev/null > "$X/run_$arm.log" 2>&1
  echo "$arm: exit $?, wall $(python -c "print(round($(date +%s.%N) - $s, 1))") s"
done
python - "$(cygpath -w "$WS")" "$(cygpath -w "$F")" "$JOB" <<'EOF'
import glob, json, os, sys
ws, f, job = sys.argv[1], sys.argv[2], sys.argv[3]
def load(p):
    return json.load(open(p, encoding="utf-8")) if os.path.isfile(p) else None
r = {"job": load(sorted(glob.glob(os.path.join(ws, "jobs", job, "*", "out", "lasertag.report.json")))[-1]),
     "A": load(os.path.join(f, "_scratch", "grader_speed", "clock_or_nav", "r_A.json")),
     "E": load(os.path.join(f, "_scratch", "grader_speed", "clock_or_nav", "r_E.json")),
     "fixed": load(os.path.join(f, "_scratch", "grader_speed", "breadth", "r_cold-9246-ws_deli_001_9393_1.json"))}
for name, d in r.items():
    if d is None:
        print("%-6s NO REPORT" % name); continue
    s = d["summary"]
    print("%-6s grade %-16s score %3s  enemy stuck %3s  player stuck %3s  player deaths %3s  events %4d" % (
        name, d["grade"], d["overall_score"], s["enemy_stuck_events"], s["player_stuck_events"], s["player_deaths"], len(d["events"])))
for a, b in (("A", "job"), ("E", "job"), ("E", "fixed"), ("A", "fixed")):
    if r[a] is None or r[b] is None:
        print("%s vs %s: NO REPORT" % (a, b)); continue
    differ = [k for k in r[a] if r[a][k] != r[b].get(k)]
    n = sum(1 for x, y in zip(r[a]["events"], r[b]["events"]) if x != y)
    print("%s vs %s: %s" % (a, b, "identical in every field" if not differ else "differ in %s (%d events)" % (differ, n)))
EOF
rm -rf "$X"/p_*
