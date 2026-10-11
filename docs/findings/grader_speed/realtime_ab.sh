#!/bin/bash
# What does Laser Tag report at the game's own physics step? `run_map_eval.gd` sets
# `Engine.time_scale` 4 by default, and Godot scales the PHYSICS STEP by it: 4x simulates at 1/15 s
# where the game steps at 1/60 s. `timescale_ab.sh` measured the findings moving with it -- cold run
# 9246's seed_9191 read 49 enemy-stuck events at 4x, 2 at 8x, 0 at 16x -- so the default is a
# modelling choice, not only a speed. This runs the same evaluation at time scale 1 with Laser Tag
# 0.25.0's enemy (A) and 0.26.0's (B), beside the 4x figures, to say how far the shipped clock sits
# from real time. Four times slower than 4x by construction. It measures and prints.
#
#     bash docs/findings/grader_speed/realtime_ab.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
G="/c/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
X="$F/_scratch/grader_speed"
mkdir -p "$X"
for v in A B; do
  P="$F/_scratch/ab_9246/$v"
  [ -d "$P" ] || { echo "no staged copy $P"; exit 2; }
  s=$(date +%s.%N)
  timeout 2400 "$G" --headless --path "$(cygpath -w "$P")" -s res://addons/laser_tag_tool/runners/run_map_eval.gd -- \
    --bake-nav --map res://level.tscn --scenario res://mission_scenario.tres --runs 25 --seed 9191 \
    --time-scale 1 --output "$(cygpath -w "$X/ts1_$v.json")" < /dev/null > "$X/ts1_$v.log" 2>&1
  echo "$v at time-scale 1: exit $?, wall $(python -c "print(round($(date +%s.%N) - $s, 1))") s"
done
python - "$(cygpath -w "$F")" <<'EOF'
import json, os, sys, collections
F = sys.argv[1]
rows = [("A 4x (0.25.0)", r"_scratch\ab_9246\out_A\lasertag.report.json"),
        ("B 4x (0.26.0)", r"_scratch\ab_9246\out_B\lasertag.report.json"),
        ("A 1x (0.25.0)", r"_scratch\grader_speed\ts1_A.json"),
        ("B 1x (0.26.0)", r"_scratch\grader_speed\ts1_B.json")]
for name, rel in rows:
    p = os.path.join(F, rel)
    if not os.path.isfile(p):
        print(name, "NO REPORT"); continue
    d = json.load(open(p, encoding="utf-8")); s = d["summary"]
    k = collections.Counter(e.get("event") for e in d["events"])
    st = [e for e in d["events"] if e.get("event") == "EnemyStuck"]
    cells = collections.Counter((round(e["position"][0] - 6.0, 1) // 1, round(-e["position"][2], 1) // 1) for e in st)
    print("%-14s grade %-16s score %3s  enemy stuck %3s  objective %2s  enemy deaths %3s  player deaths %2s  first contact %s  survival %s" % (
        name, d["grade"], d["overall_score"], s["enemy_stuck_events"], k.get("ObjectiveReached", 0),
        s["enemy_deaths"], k.get("PlayerKilled", 0), s["avg_time_to_first_contact"], s["avg_player_survival_seconds"]))
    if st:
        print("               stuck, building metre cells:", cells.most_common(4))
EOF
