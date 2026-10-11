#!/bin/bash
# Does Laser Tag's evaluation wait on the wall clock, and what does it read without waiting?
# Cold runs 9245 and 9247 measured every evaluation simulating 3.91 to 3.97 times its job's wall
# time -- the 4x clock less the import and the nav bake -- at two and at three side by side alike,
# so each process spends most of a job waiting for real seconds to pass. Godot's `--fixed-fps N`
# advances every frame by 1/N of a second of game time whatever the wall clock says. Three arms on
# copies of cold run 9247's staged seed_9104 evaluation (its longest, 9.89 min), one at a time:
#   B  --fixed-fps 60, time scale 4 (the job's 66.7 ms physics step, not synchronised)
#   C  --fixed-fps 60, time scale 1 (the game's 16.7 ms step, not synchronised)
#   A  the job's exact command (synchronised, 4x): the reference both are compared with
# B identical to A in every field would make the clock a speed lever with no change in what is
# measured; C says how far the game's own step reads from the 4x one. B and C run first so their
# wall times are taken on a quiet machine (they use the processor; A mostly waits). It measures
# and prints.
#
#     bash docs/findings/grader_speed/fixedfps_ab.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
G="/c/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
WS="$F/workspaces/cold-9247-ws/.level_factory"
JOB="restaurant_row_001.laser_tag_evaluate.candidate.seed_9104"
X="$F/_scratch/grader_speed/fixedfps"
rm -rf "$X" && mkdir -p "$X"
for arm in A B C; do cp -r "$WS/staging/$JOB" "$X/p_$arm"; done
run_arm() {
  local arm=$1; shift
  local s; s=$(date +%s.%N)
  timeout 2400 "$G" --headless "$@" --path "$(cygpath -w "$X/p_$arm")" -s res://addons/laser_tag_tool/runners/run_map_eval.gd -- \
    --bake-nav --map res://level.tscn --scenario res://mission_scenario.tres --runs 25 --seed 9104 $ARM_ARGS \
    --output "$(cygpath -w "$X/r_$arm.json")" < /dev/null > "$X/run_$arm.log" 2>&1
  local rc=$?
  echo "$arm: exit $rc, wall $(python -c "print(round($(date +%s.%N) - $s, 1))") s" | tee -a "$X/walls.txt"
}
ARM_ARGS="" run_arm B --fixed-fps 60
ARM_ARGS="--time-scale 1" run_arm C --fixed-fps 60
ARM_ARGS="" run_arm A
python - "$(cygpath -w "$WS")" "$(cygpath -w "$X")" "$JOB" <<'EOF'
import csv, glob, json, os, re, sys
ws, x, job = sys.argv[1], sys.argv[2], sys.argv[3]
walls = dict(re.findall(r"^(\w): exit \d+, wall ([0-9.]+) s", open(os.path.join(x, "walls.txt")).read(), re.M))
def load(path):
    d = json.load(open(path, encoding="utf-8"))
    c = os.path.splitext(path)[0] + ".csv"
    sim = sum(float(r["duration_seconds"]) for r in csv.DictReader(open(c, encoding="utf-8"))) if os.path.isfile(c) else None
    return d, sim
reports = {"job": load(glob.glob(os.path.join(ws, "jobs", job, "*", "out", "lasertag.report.json"))[0])}
for arm in "ABC":
    p = os.path.join(x, "r_%s.json" % arm)
    reports[arm] = load(p) if os.path.isfile(p) else (None, None)
ref = reports["A"][0]
for name in ("job", "A", "B", "C"):
    d, sim = reports[name]
    if d is None:
        print("%-3s NO REPORT" % name); continue
    s = d["summary"]
    wall = float(walls[name]) if name in walls else None
    print("%-3s grade %-16s score %3s  enemy stuck %3s  player stuck %3s  player deaths %3s  simulated %s min  wall %s  ratio %s" % (
        name, d["grade"], d["overall_score"], s["enemy_stuck_events"], s["player_stuck_events"], s["player_deaths"],
        "%.2f" % (sim / 60) if sim else "?", "%.1f s" % wall if wall else "(the job's)",
        "%.2f" % (sim / wall) if sim and wall else "-"))
    if ref is None or name == "A":
        continue
    differ = [k for k in ref if k != "map" and ref[k] != d.get(k)]
    print("      against A: every field identical %s%s" % (not differ, "" if not differ else " (differ: %s)" % differ))
    if ref["events"] != d["events"]:
        n = next(i for i, (a, b) in enumerate(zip(ref["events"], d["events"])) if a != b) if any(
            a != b for a, b in zip(ref["events"], d["events"])) else min(len(ref["events"]), len(d["events"]))
        print("      events %d vs A's %d, first difference at %d:" % (len(d["events"]), len(ref["events"]), n))
        print("        A:", ref["events"][n] if n < len(ref["events"]) else None)
        print("        %s:" % name, d["events"][n] if n < len(d["events"]) else None)
    sd = {k: (ref["summary"][k], d["summary"].get(k)) for k in ref["summary"] if ref["summary"][k] != d["summary"].get(k)}
    if sd:
        print("      summary fields that moved:", sd)
EOF
rm -rf "$X"/p_*
