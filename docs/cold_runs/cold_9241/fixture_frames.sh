#!/bin/bash
# Zoo 1.98.1's dome, seen: the deli's apartment hideout's fixtures (`tools/fixture_stations.py
# --type dome` on 9241's site lights manifest, 3 m off each row's first lamp inside the room),
# shot in three packages of the same lot -- 9238 (troffers), 9239 (Zoo 1.98.0's dome, its glass
# hung up into the ceiling) and 9241 (1.98.1's, the glass under the canopy) -- a station a row.
# The dome keeps the troffer's id and position, so one set of stations serves all three. Frames
# to _scratch/frames_9241_fixtures/, the sheet to docs/cold_runs/cold_9241/fixtures.png.
#
# Run AFTER the price (nothing else runs beside a perf measurement):
#     bash docs/cold_runs/cold_9241/fixture_frames.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
JOB="jobs/restaurant_row_001.themed_site_assemble/1/out"
LIGHTS="workspaces/cold-9241-ws/.level_factory/$JOB/site.site.lights.json"
OUT="_scratch/frames_9241_fixtures"
mkdir -p "$OUT"
S=$(python tools/fixture_stations.py "$LIGHTS" --type dome --max 6 2> "$OUT/stations.txt")
cat "$OUT/stations.txt"
[ -n "$S" ] || { echo "no dome station"; exit 2; }
# the workspaces named in full, so tools/factory_retire.py sees which ones this reads
for ws in cold-9238-ws cold-9239-ws cold-9241-ws; do
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
       ARGS+=("9238 $s=$OUT/shots_9238/$s.png" "9239 $s=$OUT/shots_9239/$s.png" "9241 $s=$OUT/shots_9241/$s.png") ;;
  esac
done
python docs/findings/edge_menu/sheet.py "docs/cold_runs/cold_9241/fixtures.png" 3 "${ARGS[@]}" && echo "sheet: docs/cold_runs/cold_9241/fixtures.png"
