#!/bin/bash
# Cold run 9274's reflection atlas (Level Factory 0.198.0, roadmap 238): the package's project.godot sizes the
# atlas to the package's probes. In order, nothing beside a price:
#   1. what the package says: its `[rendering]` atlas lines, and its probe count in the scene text
#   2. what it holds: `texture_split_probe.gd -- mission` on an imported copy (9273's read 314.6 MiB)
#   3. the frames, 9273 left and 9274 right: look_shots' derived stations and twelve interiors
#   4. the price: Level Factory's fixed stations, 9273's package both controls, 9274's the subject
# Every copy removed at the end.
#
#     bash docs/cold_runs/cold_9274/atlas.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
OUT="docs/cold_runs/cold_9274"
FR="_scratch/frames_9274_atlas"
SCR="_scratch/price_9274"
G="C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
PKG="LF_restaurant_row_001.portable-godot"
P74="workspaces/cold-9274-ws/.level_factory/exports/$PKG"
P73="workspaces/cold-9273-ws/.level_factory/exports/$PKG"
mkdir -p "$FR" "$OUT/price" "$SCR"

# 1. what the package says
echo "project.godot [rendering] reflection lines:"
grep -n "reflection" "$P74/project.godot"
echo "ReflectionProbe nodes in the package's scene text: $(grep -rho 'type="ReflectionProbe"' "$P74" --include=*.tscn | wc -l)"

# 2. what it holds
rm -rf "$SCR/mem"
cp -r "$P74" "$SCR/mem" || exit 1
cp docs/findings/texture_memory/texture_split_probe.gd "$SCR/mem/"
timeout 1800 "$G" --headless --path "$SCR/mem" --import < /dev/null > "$FR/mem_import.log" 2>&1
echo "memory import exit $?"
timeout 600 "$G" --path "$SCR/mem" -s res://texture_split_probe.gd -- mission < /dev/null > "$OUT/memory.txt" 2>&1
echo "memory exit $?"
grep "^\[split\]" "$OUT/memory.txt"
rm -rf "$SCR/mem"

# 3. the frames
for run in 9273 9274; do
  pkg="workspaces/cold-$run-ws/.level_factory/exports/$PKG"
  timeout 900 python tools/look_shots.py "$pkg" --scene mission.tscn --interiors 12 --out "$FR/shots_$run" --json \
    > "$FR/shots_$run.json" 2> "$FR/shots_$run.err" < /dev/null
  echo "shots $run exit $?"
done
for p in "$FR"/shots_9273/*.png; do
  s=$(basename "$p" .png)
  [ -f "$FR/shots_9274/$s.png" ] && python docs/cold_runs/cold_9244/frame_diff.py "$p" "$FR/shots_9274/$s.png"
done
W="in_drywall_delco_1997_2"; C="in_concrete_delco_1997"
python docs/findings/edge_menu/sheet.py "$OUT/atlas.png" 2 \
  "9273: atlas 64 x 256 $W=$FR/shots_9273/$W.png" "9274: atlas 32 x 64 $W=$FR/shots_9274/$W.png" \
  "9273 $C=$FR/shots_9273/$C.png" "9274 $C=$FR/shots_9274/$C.png" \
  "9273 overview=$FR/shots_9273/overview.png" "9274 overview=$FR/shots_9274/overview.png" \
  && echo "sheet: $OUT/atlas.png"

# 4. the price
rm -rf "$SCR/control" "$SCR/subject"
cp -r "$P73" "$SCR/control" || exit 1
cp -r "$P74" "$SCR/subject" || exit 1
python docs/findings/horizon_glow/price_glow.py "$SCR/control" "$SCR/subject" "$OUT/price" > "$OUT/price/price.txt" 2>&1
echo "price exit $?"
tail -8 "$OUT/price/price.txt"
rm -rf "$SCR/control" "$SCR/subject"
