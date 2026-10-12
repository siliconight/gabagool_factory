#!/bin/bash
# Where in the frame does the live sun differ from the baked one: on the backdrop, or on the level?
# (roadmap 243, 2026-10-12; after sun_occluders.sh, whose arm did not bring the live frames to 9265's)
#   1. a copy of cold run 9265's package (the sun baked), imported, the backdrop hidden
#      (backdrop_hidden.py), shot at the tier stations: where its frames differ from 9265's is where
#      the backdrop draws;
#   2. backdrop_split.py: 9264's difference from 9265 split into the backdrop's pixels and the level's
#      (backdrop_split.out.txt).
# Frames go to _scratch/frames_sun_occl/; the copy to _scratch/backdrop_split/, removed at the end.
#
#     bash docs/findings/lux_tiers/backdrop_split.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
P65="workspaces/cold-9265-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
SCR="_scratch/backdrop_split"
FR="_scratch/frames_sun_occl"
OUT="docs/findings/lux_tiers"
G="C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
[ -f "$P65/mission.tscn" ] || { echo "no package at $P65"; exit 1; }
rm -rf "$SCR"
mkdir -p "$SCR" "$FR"
cp -r "$P65" "$SCR/arm" || exit 1
timeout 1800 "$G" --headless --path "$SCR/arm" --import < /dev/null > "$FR/import_split.log" 2>&1
echo "import exit $?"
python "$OUT/backdrop_hidden.py" "$SCR/arm" || exit 1
S="--station line:-60,1.8,25.5,20,6.0,26.0 --station corner:65,1.8,16,80.6,6.0,20"
S="$S --station up:-31.7,1.8,25.5,-15.1,9.0,27.27"
timeout 1800 python tools/look_shots.py "$SCR/arm" --scene mission.tscn --out "$FR/shots_9265_nobackdrop" --json $S \
  > "$FR/shots_9265_nobackdrop.json" 2> "$FR/shots_9265_nobackdrop.err" < /dev/null
echo "shots exit $?"
python "$OUT/backdrop_split.py" > "$OUT/backdrop_split.out.txt" 2>&1
echo "split exit $?"
cat "$OUT/backdrop_split.out.txt"
rm -rf "$SCR"
