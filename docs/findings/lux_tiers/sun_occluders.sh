#!/bin/bash
# Which shadows does the live sun cast that the baked one cannot? (roadmap 243, 2026-10-12)
#
# Cold run 9265 (Lux 0.76.0, the sun baked with its shadows) lights facades that 9264's live sun
# leaves dark, while arm A (the live sun unshadowed, sun_variants.py) lights the same ones: the two
# agree on which faces the sun reaches and disagree on what stands in its way. Level Factory bakes
# `bake.tscn` -- the presentation scene and its LightmapGI -- and the game's `mission.tscn` also loads
# the dressing and `site_backdrop.tscn`, which the bake never sees.
#   1. a copy of 9264's package, imported once; sun_casters.gd counts the shadow casters the bake
#      holds and the ones it does not (sun_casters_9264.out.txt);
#   2. the ARM: the same copy with the backdrop casting no shadow (backdrop_noshadow.py), the sun
#      live as 9264 shipped it, shot at the tier stations;
#   3. luma: 9264 as shipped, the arm, 9265 -- if the arm reads as 9265 where 9264 is dark, the
#      backdrop's shadow is the difference; if not, something else is (sun_occluders_luma.out.txt);
#   4. sun_occluders.png: 9264 | the arm | 9265, a row a station.
# Frames go to _scratch/frames_sun_occl/; the copy to _scratch/sun_occl/, removed at the end.
#
#     bash docs/findings/lux_tiers/sun_occluders.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
P64="workspaces/cold-9264-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
SCR="_scratch/sun_occl"
FR="_scratch/frames_sun_occl"
F65="_scratch/frames_9265"
OUT="docs/findings/lux_tiers"
G="C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
[ -f "$P64/mission.tscn" ] || { echo "no package at $P64"; exit 1; }
[ -f "$F65/shots_control/line.png" ] && [ -f "$F65/shots_subject/line.png" ] \
  || { echo "no 9264/9265 frames under $F65 (docs/cold_runs/cold_9265/sun_price.sh makes them)"; exit 1; }
rm -rf "$SCR"
mkdir -p "$SCR" "$FR"
cp -r "$P64" "$SCR/arm" || exit 1
timeout 1800 "$G" --headless --path "$SCR/arm" --import < /dev/null > "$FR/import.log" 2>&1
echo "import exit $?"
cp "$OUT/sun_casters.gd" "$SCR/arm/sun_casters.gd" || exit 1
timeout 600 "$G" --headless --path "$SCR/arm" -s res://sun_casters.gd < /dev/null > "$FR/sun_casters.log" 2>&1
echo "census exit $?"
grep -E "^(the sun:|a top |visible shadow|  [A-Za-z_]|    top |NO LuxSun|could not)|the tallest [0-9]+:$" \
  "$FR/sun_casters.log" > "$OUT/sun_casters_9264.out.txt"
cat "$OUT/sun_casters_9264.out.txt"
rm -f "$SCR/arm/sun_casters.gd" "$SCR/arm/sun_casters.gd.uid"
python "$OUT/backdrop_noshadow.py" "$SCR/arm" || exit 1
S="--station line:-60,1.8,25.5,20,6.0,26.0 --station corner:65,1.8,16,80.6,6.0,20"
S="$S --station up:-31.7,1.8,25.5,-15.1,9.0,27.27"
timeout 1800 python tools/look_shots.py "$SCR/arm" --scene mission.tscn --out "$FR/shots_arm" --json $S \
  > "$FR/shots_arm.json" 2> "$FR/shots_arm.err" < /dev/null
echo "arm shots exit $?"
python - "$F65/shots_control" "$FR/shots_arm" "$F65/shots_subject" > "$OUT/sun_occluders_luma.out.txt" <<'PY'
import sys
from PIL import Image, ImageChops, ImageStat
names = ("9264 live", "no backdrop shadow", "9265 baked")
print("mean luma 0-255; in brackets the mean absolute difference from 9265's frame")
print("%-10s" % "station" + "".join("%22s" % n for n in names))
for shot in ("line", "corner", "up", "spawn", "objective", "elev_N"):
    ims = [Image.open("%s/%s.png" % (d, shot)).convert("L") for d in sys.argv[1:4]]
    cells = ["%8.1f (%5.1f)" % (ImageStat.Stat(im).mean[0], ImageStat.Stat(ImageChops.difference(im, ims[2])).mean[0])
             for im in ims]
    print("%-10s" % shot + "".join("%22s" % c for c in cells))
PY
echo "luma exit $?"
cat "$OUT/sun_occluders_luma.out.txt"
ARGS=()
for s in line corner up spawn objective elev_N; do
  ARGS+=("9264: the sun live $s=$F65/shots_control/$s.png" "9264, the backdrop casting no shadow $s=$FR/shots_arm/$s.png"
         "9265: the sun baked $s=$F65/shots_subject/$s.png")
done
python docs/findings/edge_menu/sheet.py "$OUT/sun_occluders.png" 3 "${ARGS[@]}" && echo "sheet: $OUT/sun_occluders.png"
rm -rf "$SCR"
