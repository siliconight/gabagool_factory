#!/bin/bash
# Is the baked sun darker on the level's sunlit faces because a lightmap holds no specular?
# (roadmap 243, 2026-10-12; after backdrop_split.sh)
# backdrop_split.py put line's and up's differences on the level, and there the baked sun reads darker
# than the live one even with the backdrop's shadow taken away (up 46.9 against 59.1). A lightmap is
# diffuse only; a live sun adds Godot's default specular, which Lux never sets.
#   the ARM: a copy of 9264's package, the backdrop casting no shadow (backdrop_noshadow.py) AND the
#   live sun's specular 0 (sun_nospec.py), shot at the tier stations; backdrop_split.py then reads it
#   beside the arm with its specular (shots_arm) and 9265.
# Frames go to _scratch/frames_sun_occl/shots_arm_nospec; the copy to _scratch/spec_arm/, removed.
#
#     bash docs/findings/lux_tiers/spec_arm.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
P64="workspaces/cold-9264-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
SCR="_scratch/spec_arm"
FR="_scratch/frames_sun_occl"
OUT="docs/findings/lux_tiers"
G="C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
[ -f "$P64/mission.tscn" ] || { echo "no package at $P64"; exit 1; }
rm -rf "$SCR"
mkdir -p "$SCR" "$FR"
cp -r "$P64" "$SCR/arm" || exit 1
timeout 1800 "$G" --headless --path "$SCR/arm" --import < /dev/null > "$FR/import_spec.log" 2>&1
echo "import exit $?"
cp "$OUT/sun_casters.gd" "$SCR/arm/sun_casters.gd" || exit 1
timeout 600 "$G" --headless --path "$SCR/arm" -s res://sun_casters.gd < /dev/null > "$FR/sun_casters2.log" 2>&1
echo "census exit $?"
grep -E "^(the sun:|a top |visible shadow|  [A-Za-z_]|    [ 0-9.]+ m high|NO LuxSun|could not)|the tallest [0-9]+:$" \
  "$FR/sun_casters2.log" > "$OUT/sun_casters_9264.out.txt"
cat "$OUT/sun_casters_9264.out.txt"
rm -f "$SCR/arm/sun_casters.gd" "$SCR/arm/sun_casters.gd.uid"
python "$OUT/backdrop_noshadow.py" "$SCR/arm" || exit 1
python "$OUT/sun_nospec.py" "$SCR/arm" || exit 1
S="--station line:-60,1.8,25.5,20,6.0,26.0 --station corner:65,1.8,16,80.6,6.0,20"
S="$S --station up:-31.7,1.8,25.5,-15.1,9.0,27.27"
timeout 1800 python tools/look_shots.py "$SCR/arm" --scene mission.tscn --out "$FR/shots_arm_nospec" --json $S \
  > "$FR/shots_arm_nospec.json" 2> "$FR/shots_arm_nospec.err" < /dev/null
echo "shots exit $?"
python "$OUT/backdrop_split.py" > "$OUT/backdrop_split.out.txt" 2>&1
echo "split exit $?"
cat "$OUT/backdrop_split.out.txt"
rm -rf "$SCR"
