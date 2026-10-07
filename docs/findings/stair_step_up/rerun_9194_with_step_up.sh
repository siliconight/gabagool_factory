#!/usr/bin/env bash
# Re-run Laser Tag on cold run 9194's two bank_branch_a04 candidates with the
# step-up bot (Laser Tag 0.24.0), and with step-up OFF as the control
# (roadmap 203).
#
#     bash docs/findings/stair_step_up/rerun_9194_with_step_up.sh
#
# Each candidate's staged evaluation project is COPIED into _scratch, never
# touched in place: those are cold run 9194's record. The copy gets the working
# tree's Laser Tag addon and an explicit `player_max_step_up_m` (0.5 on, 0.0
# off) appended to its mission scenario; everything else -- the level, the
# baked navigation's inputs, the seed, 25 runs -- is what 9194's job ran:
#
#     run_map_eval.gd -- --bake-nav --map res://level.tscn
#         --scenario res://mission_scenario.tres --runs 25 --seed <seed>
#
# The four evaluations run in parallel; physics ticks are fixed-step, so wall
# time is not an input. Prints what it measured and nothing else.
set -u
cd /c/Projects/gabagool_studios/gabagool_factory
GODOT="C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
OUT=_scratch/stair_step_up
mkdir -p "$OUT"
run_one() {
  local seed=$1 mode=$2
  local src=workspaces/cold-9194-ws/.level_factory/staging/bank_block_001.laser_tag_evaluate.candidate.seed_$seed
  local dst=$OUT/seed_${seed}_$mode
  rm -rf "$dst"
  cp -r "$src" "$dst"
  rm -rf "$dst/addons/laser_tag_tool"
  cp -r lasertag/addons/laser_tag_tool "$dst/addons/laser_tag_tool"
  local step=0.5
  [ "$mode" = off ] && step=0.0
  printf 'player_max_step_up_m = %s\n' "$step" >> "$dst/mission_scenario.tres"
  timeout 1800 "$GODOT" --headless --path "$dst" \
    -s res://addons/laser_tag_tool/runners/run_map_eval.gd -- \
    --bake-nav --map res://level.tscn --scenario res://mission_scenario.tres \
    --runs 25 --seed "$seed" \
    --output "C:/Projects/gabagool_studios/gabagool_factory/$dst/lasertag.report.json" \
    > "$dst.log" 2>&1
  echo "seed_$seed step-up $mode: godot exit $?"
}
for seed in 9054 9256; do
  for mode in on off; do
    run_one "$seed" "$mode" &
  done
done
wait
python - <<'EOF'
import json, os, collections
for seed in (9054, 9256):
    for mode in ("on", "off"):
        p = "_scratch/stair_step_up/seed_%d_%s/lasertag.report.json" % (seed, mode)
        if not os.path.exists(p):
            print("seed_%d %-3s NO REPORT" % (seed, mode))
            continue
        r = json.load(open(p, encoding="utf-8"))
        s = r["summary"]
        cells = collections.Counter(
            (round(e["position"][0] / 2) * 2, round(e["position"][2] / 2) * 2)
            for e in r["events"] if e.get("event") == "PlayerStuck")
        top = cells.most_common(1)[0] if cells else None
        print("seed_%d step-up %-3s completion %.2f  progress %.2f  PlayerStuck %5d  grade %-16s  top stuck cell %s"
              % (seed, mode, s["route_completion_rate"], s["route_progress_rate"],
                 s["player_stuck_events"], r.get("grade"), top))
EOF
echo "engines left: $(tasklist 2>/dev/null | grep -i -c godot)"
