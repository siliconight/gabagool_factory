#!/bin/bash
# Roadmap 229's evidence: the same rooms photographed in cold run 9225's package (Deli Counter
# 0.205.0, one row a room) and 9229's (0.206.0, rows laid to the work), from the interior
# stations tools/room_stations.py derives for the deli (b0) and the office (b1), the ceiling in
# frame. Frames to _scratch/frames_9229_rooms/, the sheet to docs/cold_runs/cold_9229/.
#
#     bash docs/cold_runs/cold_9229/room_frames.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
BEFORE="workspaces/cold-9225-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
AFTER="workspaces/cold-9229-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
OUT="_scratch/frames_9229_rooms"
mkdir -p "$OUT"
# the stations come from 9229's workspace; the buildings stand where 9225's did (same seed lines)
S0=$(python tools/room_stations.py workspaces/cold-9229-ws restaurant_row_001 b0 --rooms 4 2> "$OUT/stations_b0.txt")
S1=$(python tools/room_stations.py workspaces/cold-9229-ws restaurant_row_001 b1 --rooms 2 2> "$OUT/stations_b1.txt")
cat "$OUT/stations_b0.txt" "$OUT/stations_b1.txt"
for name in before after; do
  if [ "$name" = before ]; then P="$BEFORE"; else P="$AFTER"; fi
  timeout 900 python tools/look_shots.py "$P" --scene mission.tscn --out "$OUT/shots_$name" --json $S0 $S1 \
    > "$OUT/shots_$name.json" 2> "$OUT/shots_$name.err" < /dev/null
  echo "$name shots exit $?"
done
ARGS=()
for tok in $S0 $S1; do
  case "$tok" in
    --station) ;;
    *) s="${tok%%:*}"; ARGS+=("9225 $s=$OUT/shots_before/$s.png" "9229 $s=$OUT/shots_after/$s.png") ;;
  esac
done
python docs/findings/edge_menu/sheet.py "docs/cold_runs/cold_9229/rooms_before_after.png" 2 "${ARGS[@]}" && echo "sheet: docs/cold_runs/cold_9229/rooms_before_after.png"
