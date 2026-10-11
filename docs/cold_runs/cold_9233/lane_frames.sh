#!/bin/bash
# Roadmap 199 / 230 step 3's evidence: the service lane behind the row, shot from both ends
# (tools/lane_stations.py on the themed drawn spec), in cold run 9233's package; and the same
# edge stations and elevated views as 9232's level, for the second side street's end. Frames to
# _scratch/frames_9233_lane/, the sheet to docs/cold_runs/cold_9233/lane.png.
#
#     bash docs/cold_runs/cold_9233/lane_frames.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
PKG="workspaces/cold-9233-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
DRAWN="workspaces/cold-9233-ws/.level_factory/jobs/restaurant_row_001.themed_site_assemble/1/out/site.site.drawn.json"
OUT="_scratch/frames_9233_lane"
mkdir -p "$OUT"
S=$(python tools/lane_stations.py "$DRAWN" 2> "$OUT/stations.txt")
cat "$OUT/stations.txt"
[ -n "$S" ] || { echo "no lane station"; exit 2; }
timeout 900 python tools/look_shots.py "$PKG" --scene mission.tscn --out "$OUT/shots" --json $S \
  > "$OUT/shots.json" 2> "$OUT/shots.err" < /dev/null
echo "shots exit $?"
ARGS=()
for tok in $S; do
  case "$tok" in
    --station) ;;
    *) s="${tok%%:*}"; ARGS+=("9233 $s=$OUT/shots/$s.png") ;;
  esac
done
python docs/findings/edge_menu/sheet.py "docs/cold_runs/cold_9233/lane.png" 2 "${ARGS[@]}" && echo "sheet: docs/cold_runs/cold_9233/lane.png"
