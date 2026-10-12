#!/bin/bash
# Prove cold run 9265's sun (Lux 0.76.0: baked while the lightmap shows) in its own package against
# cold run 9264's (Lux 0.75.0: the sun live, its shadows drawn every frame), the same level and seed.
#   1. both packages copied and imported in place, once (look_shots and the price harness mirror the
#      copy and carry its import cache, so neither pays for it again);
#   2. sun_state.gd on each: the sun's bake mode and shadow as the game runs it, the power cut and
#      back -- 9264 the control, which must read dynamic and shadowed;
#   3. frames at the tier stations (docs/findings/lux_tiers/), luma.py's table, and sun_baked.png
#      (9264 left, 9265 right, a row a station);
#   4. the price: Level Factory's fixed stations through docs/findings/horizon_glow/price_glow.py,
#      control_1 (9264), the subject (9265, perf_glow.json, the harness's name), control_2 (9264).
# The copies are removed at the end. Nothing else runs beside a price.
#
#     bash docs/cold_runs/cold_9265/sun_price.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
P64="workspaces/cold-9264-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
P65="workspaces/cold-9265-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
SCR="_scratch/price_9265"
FR="_scratch/frames_9265"
OUT="docs/cold_runs/cold_9265"
G="C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
[ -f "$P64/mission.tscn" ] || { echo "no package at $P64"; exit 1; }
[ -f "$P65/mission.tscn" ] || { echo "no package at $P65"; exit 1; }
mkdir -p "$OUT/price" "$SCR" "$FR"
rm -rf "$SCR/control" "$SCR/subject"
cp -r "$P64" "$SCR/control" || exit 1
cp -r "$P65" "$SCR/subject" || exit 1
for name in control subject; do
  timeout 1800 "$G" --headless --path "$SCR/$name" --import < /dev/null > "$FR/import_$name.log" 2>&1
  echo "$name import exit $?"
  cp "$OUT/sun_state.gd" "$SCR/$name/sun_state.gd" || exit 1
  timeout 600 "$G" --headless --path "$SCR/$name" -s res://sun_state.gd < /dev/null > "$FR/sun_state_$name.log" 2>&1
  echo "$name sun_state exit $?"
  grep -E "^(vendored|frame|power|no |could)" "$FR/sun_state_$name.log" > "$OUT/sun_state_$name.out.txt"
  cat "$OUT/sun_state_$name.out.txt"
  rm -f "$SCR/$name/sun_state.gd" "$SCR/$name/sun_state.gd.uid"
done
S="--station line:-60,1.8,25.5,20,6.0,26.0 --station corner:65,1.8,16,80.6,6.0,20"
S="$S --station up:-31.7,1.8,25.5,-15.1,9.0,27.27"
for name in control subject; do
  timeout 1800 python tools/look_shots.py "$SCR/$name" --scene mission.tscn --out "$FR/shots_$name" --json $S \
    > "$FR/shots_$name.json" 2> "$FR/shots_$name.err" < /dev/null
  echo "$name shots exit $?"
done
python "$OUT/luma.py" > "$OUT/luma.out.txt" 2>&1
echo "luma exit $?"
cat "$OUT/luma.out.txt"
ARGS=()
for s in line corner up spawn objective elev_N; do
  ARGS+=("9264, Lux 0.75.0: the sun live $s=$FR/shots_control/$s.png" "9265, Lux 0.76.0: the sun baked $s=$FR/shots_subject/$s.png")
done
python docs/findings/edge_menu/sheet.py "$OUT/sun_baked.png" 2 "${ARGS[@]}" && echo "sheet: $OUT/sun_baked.png"
python docs/findings/horizon_glow/price_glow.py "$SCR/control" "$SCR/subject" "$OUT/price" > "$OUT/price/price.txt" 2>&1
echo "price exit $?"
tail -8 "$OUT/price/price.txt"
rm -rf "$SCR/control" "$SCR/subject"
