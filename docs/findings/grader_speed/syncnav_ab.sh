#!/bin/bash
# Is the navigation map's asynchronous update what ties Laser Tag's evaluation to the wall clock?
# `fixedfps_ab.sh` ran cold run 9247's seed_9104 evaluation with Godot's `--fixed-fps 60` at the
# job's own 66.7 ms step: 21 s of wall against the job's 9.89 min, the same grade and score, and
# every figure within a shot or two of the job's but the crew's stuck events, 21 against 9. The
# staged projects update their navigation maps on worker threads
# (`navigation/world/map_use_async_iterations` and `region_use_async_iterations`, both true), so
# when an update lands is a matter of real time -- which a synchronised 4x clock has plenty of
# between steps and an unsynchronised one has almost none of. Each arm below runs on a copy whose
# project.godot turns both off, read back by `engine_settings_probe.gd` first (the dial confirmed):
#   D1, D2  --fixed-fps 60, time scale 4, one at a time (is it deterministic?)
#   L1-L3   the same, three at once (does load move it?)
#   E       the job's synchronised 4x clock (does the clock still move it?)
#   G1, G2  --fixed-fps 60 at time scale 1, the game's own 16.7 ms step (deterministic there too?)
# D1 = D2 = L* = E would make the evaluation independent of the wall clock with the iterations
# synchronous; E against `fixedfps_ab.sh`'s A is what turning them off moves at today's clock.
# It measures and prints.
#
#     bash docs/findings/grader_speed/syncnav_ab.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
G="/c/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
WS="$F/workspaces/cold-9247-ws/.level_factory"
JOB="restaurant_row_001.laser_tag_evaluate.candidate.seed_9104"
X="$F/_scratch/grader_speed/syncnav"
PROBE="$F/docs/findings/grader_speed/engine_settings_probe.gd"
rm -rf "$X" && mkdir -p "$X"
for arm in D1 D2 L1 L2 L3 E G1 G2; do
  cp -r "$WS/staging/$JOB" "$X/p_$arm"
  printf '\n[navigation]\n\nworld/map_use_async_iterations=false\nworld/region_use_async_iterations=false\n' >> "$X/p_$arm/project.godot"
done
cp "$PROBE" "$X/p_D1/engine_settings_probe.gd"
"$G" --headless --path "$(cygpath -w "$X/p_D1")" -s res://engine_settings_probe.gd < /dev/null 2>&1 | grep "\[settings\] navigation" | tee "$X/dial.txt"
rm -f "$X/p_D1/engine_settings_probe.gd"
grep -q "map_use_async_iterations = false" "$X/dial.txt" || { echo "THE DIAL DID NOT TAKE: async iterations still on"; exit 3; }
run_arm() {
  local arm=$1; shift
  local s; s=$(date +%s.%N)
  timeout 2400 "$G" --headless "$@" --path "$(cygpath -w "$X/p_$arm")" -s res://addons/laser_tag_tool/runners/run_map_eval.gd -- \
    --bake-nav --map res://level.tscn --scenario res://mission_scenario.tres --runs 25 --seed 9104 $ARM_ARGS \
    --output "$(cygpath -w "$X/r_$arm.json")" < /dev/null > "$X/run_$arm.log" 2>&1
  echo "$arm: exit $?, wall $(python -c "print(round($(date +%s.%N) - $s, 1))") s" | tee -a "$X/walls.txt"
}
run_arm D1 --fixed-fps 60
run_arm D2 --fixed-fps 60
run_arm L1 --fixed-fps 60 & run_arm L2 --fixed-fps 60 & run_arm L3 --fixed-fps 60 & wait
ARM_ARGS="--time-scale 1" run_arm G1 --fixed-fps 60
ARM_ARGS="--time-scale 1" run_arm G2 --fixed-fps 60
ARM_ARGS="" run_arm E
python - "$(cygpath -w "$WS")" "$(cygpath -w "$F")" "$JOB" <<'EOF'
import csv, glob, json, os, sys
ws, f, job = sys.argv[1], sys.argv[2], sys.argv[3]
x = os.path.join(f, "_scratch", "grader_speed")
def load(path):
    if not os.path.isfile(path):
        return None
    return json.load(open(path, encoding="utf-8"))
r = {"job": load(glob.glob(os.path.join(ws, "jobs", job, "*", "out", "lasertag.report.json"))[0]),
     "A (async, 4x synced)": load(os.path.join(x, "fixedfps", "r_A.json")),
     "B (async, fixed-fps)": load(os.path.join(x, "fixedfps", "r_B.json")),
     "C (async, fixed-fps, 1x)": load(os.path.join(x, "fixedfps", "r_C.json"))}
for arm in ("D1", "D2", "L1", "L2", "L3", "E", "G1", "G2"):
    r[arm] = load(os.path.join(x, "syncnav", "r_%s.json" % arm))
for name, d in r.items():
    if d is None:
        print("%-22s NO REPORT" % name); continue
    s = d["summary"]
    print("%-22s grade %-16s score %3s  enemy stuck %3s  player stuck %3s  player deaths %3s  shots %4s  events %4d" % (
        name, d["grade"], d["overall_score"], s["enemy_stuck_events"], s["player_stuck_events"],
        s["player_deaths"], s["shots_fired"], len(d["events"])))
def same(a, b):
    if r.get(a) is None or r.get(b) is None:
        return "NO REPORT"
    differ = [k for k in r[a] if k != "map" and r[a][k] != r[b].get(k)]
    return "identical in every field" if not differ else "differ in %s" % differ
for a, b in (("D1", "D2"), ("D1", "L1"), ("D1", "L2"), ("D1", "L3"), ("D1", "E"), ("G1", "G2"),
             ("E", "A (async, 4x synced)"), ("A (async, 4x synced)", "job"), ("G1", "C (async, fixed-fps, 1x)")):
    print("%s vs %s: %s" % (a, b, same(a, b)))
EOF
rm -rf "$X"/p_*
