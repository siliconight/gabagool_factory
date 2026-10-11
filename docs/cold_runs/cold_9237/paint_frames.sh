#!/bin/bash
# Roadmap 231's second lever and the paint's cells, seen: the plate families under the 32 m baked
# tile and the road paint one mesh a colour a 32 m cell (Lot 0.115.0) beside 9236's one mesh a
# colour on 8 m tiles, at the same stations in both packages -- `tools/paint_stations.py` on
# 9237's themed drawn spec and markings manifest (the lot is 9233's, as 9236's; the script refuses
# if the two manifests differ), down each street, short of each first crosswalk and off the first
# bay ticks -- plus the lane stations 9233's and 9236's records shot. Frames to
# _scratch/frames_9237_paint/, the sheets to docs/cold_runs/cold_9237/paint.png (9236 beside
# 9237, a station a row) and lane.png (9237's lane from both ends).
#
# Run AFTER the price (nothing else runs beside a perf measurement):
#     bash docs/cold_runs/cold_9237/paint_frames.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
JOB="jobs/restaurant_row_001.themed_site_assemble/1/out"
PKG_C="workspaces/cold-9236-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
PKG_S="workspaces/cold-9237-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
DRAWN="workspaces/cold-9237-ws/.level_factory/$JOB/site.site.drawn.json"
OUT="_scratch/frames_9237_paint"
mkdir -p "$OUT"
cmp -s "workspaces/cold-9236-ws/.level_factory/$JOB/site.markings.json" \
       "workspaces/cold-9237-ws/.level_factory/$JOB/site.markings.json" \
  || { echo "the two manifests differ: not the same paint, not the same stations"; exit 2; }
P=$(python tools/paint_stations.py "$DRAWN" 2> "$OUT/paint_stations.txt")
L=$(python tools/lane_stations.py "$DRAWN" 2> "$OUT/lane_stations.txt")
cat "$OUT/paint_stations.txt" "$OUT/lane_stations.txt"
[ -n "$P" ] || { echo "no paint station"; exit 2; }
for run in 9236 9237; do
  pkg="$PKG_C"; [ "$run" = 9237 ] && pkg="$PKG_S"
  timeout 900 python tools/look_shots.py "$pkg" --scene mission.tscn --out "$OUT/shots_$run" --json $P $L \
    > "$OUT/shots_$run.json" 2> "$OUT/shots_$run.err" < /dev/null
  echo "shots $run exit $?"
done
ARGS=()
for tok in $P; do
  case "$tok" in
    --station) ;;
    *) s="${tok%%:*}"; ARGS+=("9236 $s=$OUT/shots_9236/$s.png" "9237 $s=$OUT/shots_9237/$s.png") ;;
  esac
done
python docs/findings/edge_menu/sheet.py "docs/cold_runs/cold_9237/paint.png" 2 "${ARGS[@]}" && echo "sheet: docs/cold_runs/cold_9237/paint.png"
LARGS=()
for tok in $L; do
  case "$tok" in
    --station) ;;
    *) s="${tok%%:*}"; LARGS+=("9237 $s=$OUT/shots_9237/$s.png") ;;
  esac
done
[ ${#LARGS[@]} -gt 0 ] && python docs/findings/edge_menu/sheet.py "docs/cold_runs/cold_9237/lane.png" 2 "${LARGS[@]}" && echo "sheet: docs/cold_runs/cold_9237/lane.png"
