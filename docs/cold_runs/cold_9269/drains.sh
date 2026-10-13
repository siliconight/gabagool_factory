#!/bin/bash
# Cold run 9269's drains (Lot 0.120.0, factory roadmap 179) against 9268's package, which has none: the
# same lot (seed_9104, cold run 9262's roads), so the stations stand in the same place. Godot
# coordinates (x, height, -plan y); the pieces from `site_drains.plan` on these roads:
#   corner    the main road's north kerb at the west T's west corner: the inlet at (-26.35, 16.97), the
#             lid behind it at (-26.35, 15.92), the throat in the kerb face
#   junction  the cover at that T's centre, (-19.99, 21.67)
#   lane      the side street's kerb at the lane's mouth: inlets at (-15.29, -23.33) and (-15.29, -31.04)
#   up, hatch the controls -- a facade and the deli's roof, no drain in either: a frame that moves
#             there moved for another reason
# Then frame_diff on each pair and a sheet (9268 left, 9269 right); then the price: Level Factory's
# fixed stations, 9268's package both controls, 9269's the subject. Copies removed at the end; nothing
# else runs beside a price.
#
#     bash docs/cold_runs/cold_9269/drains.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
OUT="docs/cold_runs/cold_9269"
FR="_scratch/frames_9269_drains"
SCR="_scratch/price_9269"
mkdir -p "$FR" "$OUT/price" "$SCR"
S="--station corner:-31.5,1.7,20.5,-25.0,0.0,16.5 --station junction:-26.0,1.7,26.5,-20.0,0.0,21.67"
S="$S --station lane:-10.5,1.7,-19.0,-15.5,0.0,-24.0"
S="$S --station up:-31.7,1.8,25.5,-15.1,9.0,27.27 --station hatch:-43,8.2,9.49,-51,6.6,-2.51"
for run in 9268 9269; do
  pkg="workspaces/cold-$run-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
  [ -f "$pkg/mission.tscn" ] || { echo "no package at $pkg"; exit 1; }
  timeout 900 python tools/look_shots.py "$pkg" --scene mission.tscn --out "$FR/shots_$run" --json $S \
    > "$FR/shots_$run.json" 2> "$FR/shots_$run.err" < /dev/null
  echo "shots $run exit $?"
done
ARGS=()
for s in corner junction lane up hatch; do
  ARGS+=("9268: no drains $s=$FR/shots_9268/$s.png" "9269: the drains $s=$FR/shots_9269/$s.png")
  python docs/cold_runs/cold_9244/frame_diff.py "$FR/shots_9268/$s.png" "$FR/shots_9269/$s.png"
done
python docs/findings/edge_menu/sheet.py "$OUT/drains.png" 2 "${ARGS[@]}" && echo "sheet: $OUT/drains.png"
rm -rf "$SCR/control" "$SCR/subject"
cp -r "workspaces/cold-9268-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot" "$SCR/control" || exit 1
cp -r "workspaces/cold-9269-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot" "$SCR/subject" || exit 1
python docs/findings/horizon_glow/price_glow.py "$SCR/control" "$SCR/subject" "$OUT/price" > "$OUT/price/price.txt" 2>&1
echo "price exit $?"
tail -8 "$OUT/price/price.txt"
rm -rf "$SCR/control" "$SCR/subject"
