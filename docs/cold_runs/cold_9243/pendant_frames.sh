#!/bin/bash
# Zoo 1.100.0's fixture merge, seen: the merge re-packs a pendant's cord and socket into one mesh
# and changes no triangle, so the picture should not move. Stations at the lot's pendant rows
# (`tools/fixture_stations.py --type pendant` on 9243's site lights manifest, 3 m off each row's
# first lamp inside its room), shot in 9241's package (unmerged) and 9243's (merged), a station a
# row, and each pair's mean absolute difference printed by `frame_diff.py` -- a failing tube's
# flicker moves pixels in both, so a difference is read beside the frames, not alone. Frames to
# _scratch/frames_9243_pendants/, the sheet to docs/cold_runs/cold_9243/pendants.png.
#
# Run AFTER the price (nothing else runs beside a perf measurement):
#     bash docs/cold_runs/cold_9243/pendant_frames.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
JOB="jobs/restaurant_row_001.themed_site_assemble/1/out"
LIGHTS="workspaces/cold-9243-ws/.level_factory/$JOB/site.site.lights.json"
OUT="_scratch/frames_9243_pendants"
mkdir -p "$OUT"
S=$(python tools/fixture_stations.py "$LIGHTS" --type pendant --max 6 2> "$OUT/stations.txt")
cat "$OUT/stations.txt"
[ -n "$S" ] || { echo "no pendant station"; exit 2; }
# the workspaces named in full, so tools/factory_retire.py sees which ones this reads
for ws in cold-9241-ws cold-9243-ws; do
  run=${ws#cold-}; run=${run%-ws}
  pkg="workspaces/$ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
  timeout 900 python tools/look_shots.py "$pkg" --scene mission.tscn --out "$OUT/shots_$run" --json $S \
    > "$OUT/shots_$run.json" 2> "$OUT/shots_$run.err" < /dev/null
  echo "shots $run exit $?"
done
ARGS=()
for tok in $S; do
  case "$tok" in
    --station) ;;
    *) s="${tok%%:*}"
       ARGS+=("9241 $s=$OUT/shots_9241/$s.png" "9243 $s=$OUT/shots_9243/$s.png")
       python docs/cold_runs/cold_9243/frame_diff.py "$OUT/shots_9241/$s.png" "$OUT/shots_9243/$s.png" ;;
  esac
done
python docs/findings/edge_menu/sheet.py "docs/cold_runs/cold_9243/pendants.png" 2 "${ARGS[@]}" && echo "sheet: docs/cold_runs/cold_9243/pendants.png"
