#!/bin/bash
# Cold run 9272's stoops (Deli Counter 0.211.1, Level Factory 0.196.0): 9271's stoops, now `stair` to the
# circulation gate and merged with each Empty's front. In order, nothing beside a price:
#   1. the walk again: `stoop_walk.gd` in a mirror of 9272's package -- the merge moved the stoop modules'
#      colliders under `KitCollision`, so the climb is asked again, with 9271's controls beside it
#   2. the frames, 9271 left (each stoop three modules) and 9272 right (merged): the same stations as 9271's
#      -- a merge should change no picture beyond the lightmap's re-pack
#   3. the price: Level Factory's fixed stations, 9270's package (no stoops) both controls, 9272's the
#      subject -- the whole cost of the stoops as they ship, against 9271's +22.7 draws a heading
# Every copy removed at the end.
#
#     bash docs/cold_runs/cold_9272/stoops.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
OUT="docs/cold_runs/cold_9272"
FR="_scratch/frames_9272_stoops"
SCR="_scratch/price_9272"
G="C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
PKG="LF_restaurant_row_001.portable-godot"
mkdir -p "$FR" "$OUT/price" "$SCR"

# 1. the walk
rm -rf "$SCR/walk"
mkdir -p "$SCR/walk"
cp -r "workspaces/cold-9272-ws/.level_factory/exports/$PKG" "$SCR/walk/$PKG" || exit 1
cp "$OUT/stoop_walk.gd" "$SCR/walk/$PKG/stoop_walk.gd"
timeout 1800 "$G" --headless --path "$SCR/walk/$PKG" --import < /dev/null > "$FR/walk_import.log" 2>&1
echo "walk import exit $?"
timeout 600 "$G" --headless --path "$SCR/walk/$PKG" -s res://stoop_walk.gd -- \
  res://lot/gs_empty_rowhome_a/site.tscn -1.5 "$F/$OUT/stoop_walk.out.txt" < /dev/null > "$FR/walk.log" 2>&1
echo "walk exit $?"
cat "$OUT/stoop_walk.out.txt"
rm -rf "$SCR/walk"

# 2. the frames
S="--station stoop:-8.6,1.6,28.4,-11.35,0.35,30.9 --station side:-13.9,0.8,30.7,-11.35,0.3,30.7"
S="$S --station row:-24.0,1.7,28.2,-4.0,0.9,31.2 --station hatch:-43,8.2,9.49,-51,6.6,-2.51"
# the workspaces named in full, so tools/factory_retire.py sees which ones this reads
for ws in cold-9271-ws cold-9272-ws; do
  run=${ws#cold-}; run=${run%-ws}
  pkg="workspaces/$ws/.level_factory/exports/$PKG"
  [ -f "$pkg/mission.tscn" ] || { echo "no package at $pkg"; exit 1; }
  timeout 900 python tools/look_shots.py "$pkg" --scene mission.tscn --out "$FR/shots_$run" --json $S \
    > "$FR/shots_$run.json" 2> "$FR/shots_$run.err" < /dev/null
  echo "shots $run exit $?"
done
ARGS=()
for s in stoop side row hatch; do
  ARGS+=("9271: three modules $s=$FR/shots_9271/$s.png" "9272: merged $s=$FR/shots_9272/$s.png")
  python docs/cold_runs/cold_9244/frame_diff.py "$FR/shots_9271/$s.png" "$FR/shots_9272/$s.png"
done
python docs/findings/edge_menu/sheet.py "$OUT/stoops.png" 2 "${ARGS[@]}" && echo "sheet: $OUT/stoops.png"

# 3. the price
rm -rf "$SCR/control" "$SCR/subject"
cp -r "workspaces/cold-9270-ws/.level_factory/exports/$PKG" "$SCR/control" || exit 1
cp -r "workspaces/cold-9272-ws/.level_factory/exports/$PKG" "$SCR/subject" || exit 1
python docs/findings/horizon_glow/price_glow.py "$SCR/control" "$SCR/subject" "$OUT/price" > "$OUT/price/price.txt" 2>&1
echo "price exit $?"
tail -8 "$OUT/price/price.txt"
rm -rf "$SCR/control" "$SCR/subject"
