#!/bin/bash
# The dark lane's design call, seen: Lot 0.116.0 stands the street's own lamp along the service
# lane. The lane's two stations (`tools/lane_stations.py`: 6 m in from each end, looking at the
# far end) and one station at each of 9238's lane lamps (`tools/lane_lamp_stations.py`: on the
# lane's centre line 12 m short of the pole, looking past it), shot in 9237's package (no lane
# lamps) and 9238's, a station a row. Frames to _scratch/frames_9238_lane/, the sheet to
# docs/cold_runs/cold_9238/lane.png.
#
# Run AFTER the price (nothing else runs beside a perf measurement):
#     bash docs/cold_runs/cold_9238/lane_frames.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
JOB="jobs/restaurant_row_001.themed_site_assemble/1/out"
PKG_C="workspaces/cold-9237-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
PKG_S="workspaces/cold-9238-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
DRAWN="workspaces/cold-9238-ws/.level_factory/$JOB/site.site.drawn.json"
OUT="_scratch/frames_9238_lane"
mkdir -p "$OUT"
L=$(python tools/lane_stations.py "$DRAWN" 2> "$OUT/lane_stations.txt")
P=$(python tools/lane_lamp_stations.py "$DRAWN" 2> "$OUT/lamp_stations.txt")
cat "$OUT/lane_stations.txt" "$OUT/lamp_stations.txt"
[ -n "$L" ] || { echo "no lane station"; exit 2; }
for run in 9237 9238; do
  pkg="$PKG_C"; [ "$run" = 9238 ] && pkg="$PKG_S"
  timeout 900 python tools/look_shots.py "$pkg" --scene mission.tscn --out "$OUT/shots_$run" --json $L $P \
    > "$OUT/shots_$run.json" 2> "$OUT/shots_$run.err" < /dev/null
  echo "shots $run exit $?"
done
ARGS=()
for tok in $L $P; do
  case "$tok" in
    --station) ;;
    *) s="${tok%%:*}"; ARGS+=("9237 $s=$OUT/shots_9237/$s.png" "9238 $s=$OUT/shots_9238/$s.png") ;;
  esac
done
python docs/findings/edge_menu/sheet.py "docs/cold_runs/cold_9238/lane.png" 2 "${ARGS[@]}" && echo "sheet: docs/cold_runs/cold_9238/lane.png"
