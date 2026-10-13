#!/bin/bash
# Cold run 9270's grates (Lot 0.120.1) against 9269's (0.120.0), the same lot (seed_9104): the paint
# first -- 9269's drain_paint.py on this package, which read four of 9269's eight grates over a
# crosswalk bar -- then the frames. Godot coordinates (x, height, -plan y):
#   corner   9269's station: the main road's north kerb at the west T's west corner, where 0.120.0
#            stood a grate over the crosswalk's bar (plan -26.345, -16.970) and 0.120.1 stands it past
#            the last bar (plan -28.495, -16.970); both places are in the frame
#   up, hatch the controls, as in 9269 -- a facade and the deli's roof, no drain in either
# No price: the same eight meshes and triangles, four grates and two lids moved 2.15 m along a kerb.
#
#     bash docs/cold_runs/cold_9270/drains.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
OUT="docs/cold_runs/cold_9270"
FR="_scratch/frames_9270_drains"
mkdir -p "$FR"
P="workspaces/cold-9270-ws/.level_factory"
python docs/cold_runs/cold_9269/drain_paint.py "$P/exports/LF_restaurant_row_001.portable-godot" \
  "$P/jobs/restaurant_row_001.themed_site_assemble/1/out" site > "$OUT/drain_paint.out.txt" 2>&1
echo "drain_paint exit $?"
tail -3 "$OUT/drain_paint.out.txt"
S="--station corner:-31.5,1.7,20.5,-25.0,0.0,16.5"
S="$S --station up:-31.7,1.8,25.5,-15.1,9.0,27.27 --station hatch:-43,8.2,9.49,-51,6.6,-2.51"
for run in 9269 9270; do
  pkg="workspaces/cold-$run-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
  [ -f "$pkg/mission.tscn" ] || { echo "no package at $pkg"; exit 1; }
  timeout 900 python tools/look_shots.py "$pkg" --scene mission.tscn --out "$FR/shots_$run" --json $S \
    > "$FR/shots_$run.json" 2> "$FR/shots_$run.err" < /dev/null
  echo "shots $run exit $?"
done
ARGS=()
for s in corner up hatch; do
  ARGS+=("9269: 0.120.0 $s=$FR/shots_9269/$s.png" "9270: 0.120.1 $s=$FR/shots_9270/$s.png")
  python docs/cold_runs/cold_9244/frame_diff.py "$FR/shots_9269/$s.png" "$FR/shots_9270/$s.png"
done
python docs/findings/edge_menu/sheet.py "$OUT/drains.png" 2 "${ARGS[@]}" && echo "sheet: $OUT/drains.png"
