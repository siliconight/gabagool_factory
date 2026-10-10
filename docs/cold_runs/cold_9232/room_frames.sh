#!/bin/bash
# Roadmap 229's evidence for the second step: the deli's rooms photographed in cold run 9229's
# package (Deli Counter 0.206.0, rows laid to the work across the room) and 9232's (0.207.0, rows
# over the aisles between the shelf runs, the home rule on the hideout), from the interior stations
# tools/room_stations.py derives for the deli (b0) in EACH workspace -- the deli stands at x -58 in
# 9229 and x -51 in 9232 (the lot was drawn by a template), so the stations are the same rooms at
# the same relative eye, not the same world points. Frames to _scratch/frames_9232_rooms/, the
# sheet to docs/cold_runs/cold_9232/.
#
#     bash docs/cold_runs/cold_9232/room_frames.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
BEFORE="workspaces/cold-9229-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
AFTER="workspaces/cold-9232-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
OUT="_scratch/frames_9232_rooms"
mkdir -p "$OUT"
SB=$(python tools/room_stations.py workspaces/cold-9229-ws restaurant_row_001 b0 --rooms 4 2> "$OUT/stations_before.txt")
SA=$(python tools/room_stations.py workspaces/cold-9232-ws restaurant_row_001 b0 --rooms 4 2> "$OUT/stations_after.txt")
cat "$OUT/stations_before.txt" "$OUT/stations_after.txt"
timeout 900 python tools/look_shots.py "$BEFORE" --scene mission.tscn --out "$OUT/shots_before" --json $SB \
  > "$OUT/shots_before.json" 2> "$OUT/shots_before.err" < /dev/null
echo "before shots exit $?"
timeout 900 python tools/look_shots.py "$AFTER" --scene mission.tscn --out "$OUT/shots_after" --json $SA \
  > "$OUT/shots_after.json" 2> "$OUT/shots_after.err" < /dev/null
echo "after shots exit $?"
ARGS=()
for tok in $SA; do
  case "$tok" in
    --station) ;;
    *) s="${tok%%:*}"; ARGS+=("9229 $s=$OUT/shots_before/$s.png" "9232 $s=$OUT/shots_after/$s.png") ;;
  esac
done
python docs/findings/edge_menu/sheet.py "docs/cold_runs/cold_9232/rooms_before_after.png" 2 "${ARGS[@]}" && echo "sheet: docs/cold_runs/cold_9232/rooms_before_after.png"
