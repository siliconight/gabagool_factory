#!/bin/bash
# Do Laser Tag 0.27.0's runtime setters do what the project settings did? `syncnav_ab.sh` and
# `breadth_ab.py` made the navigation synchronous with two lines in each copy's project.godot; the
# release does it in `run_map_eval.gd` with `LT_Const.synchronous_navigation`, at run time. Three
# arms under `--fixed-fps 60` on copies of cold run 9246's deli seed_9393 -- the candidate where
# the navigation setting moved the report (`clock_or_nav_ab.sh`) -- each with Laser Tag 0.26.0's
# addon swapped in, so all three run the same code but for the change:
#   c  0.26.0, no settings: the asynchronous control, which must DIFFER from a (or this candidate
#      cannot tell the setters from nothing, and another is needed)
#   a  0.26.0 with the project settings: synchronous, as the earlier A/Bs ran it
#   b  the 0.27.0 draft (`_scratch/lt_draft`, `patch_lt_sync_nav.py --draft`), no settings
# b = a is the release doing what was measured. Then cold run 9247's seed_9104 with the draft
# against its job, which every earlier arm matched. It measures and prints.
#
#     bash docs/findings/grader_speed/runtime_setters_ab.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
G="/c/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
X="$F/_scratch/grader_speed/runtime_setters"
DELI="$F/workspaces/cold-9246-ws/.level_factory/staging/deli_001.laser_tag_evaluate.candidate.seed_9393"
ROW="$F/workspaces/cold-9247-ws/.level_factory/staging/restaurant_row_001.laser_tag_evaluate.candidate.seed_9104"
OLD="$F/lasertag/addons/laser_tag_tool"
NEW="$F/_scratch/lt_draft/addons/laser_tag_tool"
[ -f "$NEW/scripts/core/LT_Const.gd" ] && grep -q "func synchronous_navigation" "$NEW/scripts/core/LT_Const.gd" || { echo "no 0.27.0 draft at $NEW"; exit 2; }
grep -q "func synchronous_navigation" "$OLD/scripts/core/LT_Const.gd" && { echo "the repo is not 0.26.0"; exit 2; }
rm -rf "$X" && mkdir -p "$X"
stage() {   # stage <arm> <source project> <addon>
  cp -r "$2" "$X/p_$1"
  rm -rf "$X/p_$1/addons/laser_tag_tool"
  cp -r "$3" "$X/p_$1/addons/laser_tag_tool"
}
stage c "$DELI" "$OLD"
stage a "$DELI" "$OLD"
printf '\n[navigation]\n\nworld/map_use_async_iterations=false\nworld/region_use_async_iterations=false\n' >> "$X/p_a/project.godot"
stage b "$DELI" "$NEW"
stage r "$ROW" "$NEW"
run_arm() {   # run_arm <arm> <seed>
  local s; s=$(date +%s.%N)
  timeout 1200 "$G" --headless --fixed-fps 60 --path "$(cygpath -w "$X/p_$1")" -s res://addons/laser_tag_tool/runners/run_map_eval.gd -- \
    --bake-nav --map res://level.tscn --scenario res://mission_scenario.tres --runs 25 --seed "$2" \
    --output "$(cygpath -w "$X/r_$1.json")" < /dev/null > "$X/run_$1.log" 2>&1
  echo "$1: exit $?, wall $(python -c "print(round($(date +%s.%N) - $s, 1))") s; $(grep -m1 '\[LT\] navigation' "$X/run_$1.log" || echo 'no navigation line')"
}
run_arm c 9393
run_arm a 9393
run_arm b 9393
run_arm r 9104
python - "$(cygpath -w "$F")" <<'EOF'
import glob, json, os, sys
f = sys.argv[1]
x = os.path.join(f, "_scratch", "grader_speed", "runtime_setters")
def load(p):
    return json.load(open(p, encoding="utf-8")) if os.path.isfile(p) else None
r = {k: load(os.path.join(x, "r_%s.json" % k)) for k in "cabr"}
r["job_9104"] = load(sorted(glob.glob(os.path.join(f, "workspaces", "cold-9247-ws", ".level_factory", "jobs",
    "restaurant_row_001.laser_tag_evaluate.candidate.seed_9104", "*", "out", "lasertag.report.json")))[-1])
for name, d in r.items():
    if d is None:
        print("%-9s NO REPORT" % name); continue
    s = d["summary"]
    print("%-9s grade %-16s score %3s  enemy stuck %3s  player stuck %3s  player deaths %3s  events %4d" % (
        name, d["grade"], d["overall_score"], s["enemy_stuck_events"], s["player_stuck_events"], s["player_deaths"], len(d["events"])))
for a, b, want in (("b", "a", "identical"), ("a", "c", "different (the control)"), ("r", "job_9104", "identical")):
    if r[a] is None or r[b] is None:
        print("%s vs %s: NO REPORT" % (a, b)); continue
    differ = [k for k in r[a] if k != "map" and r[a][k] != r[b].get(k)]
    print("%s vs %s (want %s): %s" % (a, b, want, "identical in every field" if not differ else "differ in %s" % differ))
EOF
rm -rf "$X"/p_*
