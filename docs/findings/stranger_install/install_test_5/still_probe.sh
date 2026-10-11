#!/bin/bash
# Is install test 5's Ladder_ladder_0_base "fighting" depth or time? The walk's own shot bot
# twice (the camera moved 1 mm between its two frames, as shipped) and the same bot with the move
# set to 0 (shot_bot_still.gd), on the stranger's walk preview. A still camera cannot z-fight:
# whatever it counts is the scene changing between two frames.
G='C:\Godot\4.7\Godot_v4.7-stable_win64.exe'
P='C:\stranger_202_5\gabagool\levels\.level_factory\preview\restaurant_row_001_walk'
O=/c/Projects/gabagool_studios/gabagool_factory/_scratch/install_202_5/still
mkdir -p "$O"
OW=$(cygpath -w "$O")
for run in moved_1 still_1 moved_2 still_2; do
  script="res://shot_bot.gd"; case "$run" in still*) script="res://shot_bot_still.gd";; esac
  timeout 600 "$G" --rendering-driver opengl3 --path "$P" --script "$script" -- "$OW\\$run.json" "$OW\\shots_$run" res://mission.tscn > "$O/$run.log" 2>&1 < /dev/null
  echo "$run exit $?"
done
python - "$O" <<'PY'
import json, sys, pathlib
o = pathlib.Path(sys.argv[1])
for run in ("moved_1", "still_1", "moved_2", "still_2"):
    p = o / f"{run}.json"
    if not p.exists():
        print(run, "NO VERDICT"); continue
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = d.get("stations") or d.get("shots") or []
    print(run, [(r.get("station"), r.get("jitter_pct"), r.get("fight_pct")) for r in rows])
PY
