#!/bin/bash
# Level Factory 0.178.3's shot bot (still frames masking animation) on the stranger's walk
# preview from install test 5, and on the shot bot's own z-fight control (two quads 0.01 mm
# apart, docs/findings/shotbot_sparkle/zfight_control.tscn): the level's ladder base must pass
# with its flicker reported as animated, the control must still fail.
G='C:\Godot\4.7\Godot_v4.7-stable_win64.exe'
P='C:\stranger_202_5\gabagool\levels\.level_factory\preview\restaurant_row_001_walk'
PP=/c/stranger_202_5/gabagool/levels/.level_factory/preview/restaurant_row_001_walk
F=/c/Projects/gabagool_studios/gabagool_factory
O=$F/_scratch/install_202_5/masked
mkdir -p "$O"
OW=$(cygpath -w "$O")
cp "$F/_scratch/lf_draft7/assets/godot/shot_bot.gd" "$PP/shot_bot_masked.gd"
cp "$F/docs/findings/shotbot_sparkle/zfight_control.tscn" "$PP/zfight_control.tscn"
for run in level_masked control_masked control_shipped; do
  script="res://shot_bot_masked.gd"; scene="res://mission.tscn"
  case "$run" in control_*) scene="res://zfight_control.tscn";; esac
  case "$run" in *_shipped) script="res://shot_bot.gd";; esac
  timeout 600 "$G" --rendering-driver opengl3 --path "$P" --script "$script" -- "$OW\\$run.json" "$OW\\shots_$run" "$scene" > "$O/$run.log" 2>&1 < /dev/null
  echo "$run exit $?"
done
python - "$O" <<'PY'
import json, sys, pathlib
o = pathlib.Path(sys.argv[1])
for run in ("level_masked", "control_masked", "control_shipped"):
    p = o / f"{run}.json"
    if not p.exists():
        print(run, "NO VERDICT"); continue
    d = json.loads(p.read_text(encoding="utf-8"))
    print(run, [(r.get("station"), r.get("ok"), r.get("jitter_pct"), r.get("fight_pct"), r.get("animated_pct")) for r in d.get("stations") or []])
PY
