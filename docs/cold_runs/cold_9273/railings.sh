#!/bin/bash
# Cold run 9273's railings (Zoo 1.105.0, Deli Counter 0.212.0, Level Factory 0.197.0): an iron railing on each
# side of every rowhome Empty's stoop. In order, nothing beside a price:
#   1. the walk: `rail_walk.gd` in a mirror of 9272's package -- the same stoop with no railings, the control
#      that the instrument sees a body leave a stoop at all -- and of 9273's: the way up as it was, and a
#      body on the landing or the flight driven sideways
#   2. the frames, 9272 left and 9273 right: 9272's four stations, and a front view from the sidewalk of
#      blocker_10's stoop (gs_empty_rowhome_a, its landing's centre at (-11.35, 0.533, 31.215), read off
#      9272's site.tscn: turned 180, its facade at z 31.665, its ramp's foot at 29.927)
#   3. the price: Level Factory's fixed stations, 9272's package both controls, 9273's the subject -- the
#      whole cost of the railings as they ship
# Every copy removed at the end.
#
#     bash docs/cold_runs/cold_9273/railings.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
OUT="docs/cold_runs/cold_9273"
FR="_scratch/frames_9273_railings"
SCR="_scratch/price_9273"
G="C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
PKG="LF_restaurant_row_001.portable-godot"
mkdir -p "$FR" "$OUT/price" "$SCR"

# 1. the walk, on each package
for run in 9272 9273; do
  rm -rf "$SCR/walk"
  mkdir -p "$SCR/walk"
  cp -r "workspaces/cold-$run-ws/.level_factory/exports/$PKG" "$SCR/walk/$PKG" || exit 1
  cp "$OUT/rail_walk.gd" "$SCR/walk/$PKG/rail_walk.gd"
  timeout 1800 "$G" --headless --path "$SCR/walk/$PKG" --import < /dev/null > "$FR/walk_import_$run.log" 2>&1
  echo "walk import $run exit $?"
  timeout 600 "$G" --headless --path "$SCR/walk/$PKG" -s res://rail_walk.gd -- \
    res://lot/gs_empty_rowhome_a/site.tscn -1.5 "$F/$OUT/rail_walk_$run.out.txt" < /dev/null > "$FR/walk_$run.log" 2>&1
  echo "walk $run exit $?"
  cat "$OUT/rail_walk_$run.out.txt"
  rm -rf "$SCR/walk"
done

# 2. the frames
S="--station stoop:-8.6,1.6,28.4,-11.35,0.35,30.9 --station side:-13.9,0.8,30.7,-11.35,0.3,30.7"
S="$S --station row:-24.0,1.7,28.2,-4.0,0.9,31.2 --station hatch:-43,8.2,9.49,-51,6.6,-2.51"
S="$S --station front:-9.6,1.55,27.6,-11.35,0.75,30.6"
for run in 9272 9273; do
  pkg="workspaces/cold-$run-ws/.level_factory/exports/$PKG"
  [ -f "$pkg/mission.tscn" ] || { echo "no package at $pkg"; exit 1; }
  timeout 900 python tools/look_shots.py "$pkg" --scene mission.tscn --out "$FR/shots_$run" --json $S \
    > "$FR/shots_$run.json" 2> "$FR/shots_$run.err" < /dev/null
  echo "shots $run exit $?"
done
ARGS=()
for s in front side stoop row hatch; do
  ARGS+=("9272: no railings $s=$FR/shots_9272/$s.png" "9273: railings $s=$FR/shots_9273/$s.png")
  python docs/cold_runs/cold_9244/frame_diff.py "$FR/shots_9272/$s.png" "$FR/shots_9273/$s.png"
done
python docs/findings/edge_menu/sheet.py "$OUT/railings.png" 2 "${ARGS[@]}" && echo "sheet: $OUT/railings.png"

# 3. the price
rm -rf "$SCR/control" "$SCR/subject"
cp -r "workspaces/cold-9272-ws/.level_factory/exports/$PKG" "$SCR/control" || exit 1
cp -r "workspaces/cold-9273-ws/.level_factory/exports/$PKG" "$SCR/subject" || exit 1
python docs/findings/horizon_glow/price_glow.py "$SCR/control" "$SCR/subject" "$OUT/price" > "$OUT/price/price.txt" 2>&1
echo "price exit $?"
tail -8 "$OUT/price/price.txt"
rm -rf "$SCR/control" "$SCR/subject"
