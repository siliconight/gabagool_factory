#!/bin/bash
# Roadmap 229's species step, seen: a home's room hangs a dome where it hung an office troffer
# (Deli Counter 0.208.0, Zoo 1.98.0, Lux 0.75.0). The stations are `tools/fixture_stations.py` on
# 9239's site lights manifest, one at each `dome` anchor (the deli's apartment hideout on this lot),
# 3 m off its row inside the room; the dome keeps the troffer's id and position, so the same
# stations shoot 9238's package (troffers) and 9239's (domes), a station a row. Frames to
# _scratch/frames_9239_fixtures/, the sheet to docs/cold_runs/cold_9239/fixtures.png.
#
# Run AFTER the price (nothing else runs beside a perf measurement):
#     bash docs/cold_runs/cold_9239/fixture_frames.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
JOB="jobs/restaurant_row_001.themed_site_assemble/1/out"
PKG_C="workspaces/cold-9238-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
PKG_S="workspaces/cold-9239-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
LIGHTS="workspaces/cold-9239-ws/.level_factory/$JOB/site.site.lights.json"
OUT="_scratch/frames_9239_fixtures"
mkdir -p "$OUT"
S=$(python tools/fixture_stations.py "$LIGHTS" --type dome --max 6 2> "$OUT/stations.txt")
cat "$OUT/stations.txt"
[ -n "$S" ] || { echo "no dome station"; exit 2; }
for run in 9238 9239; do
  pkg="$PKG_C"; [ "$run" = 9239 ] && pkg="$PKG_S"
  timeout 900 python tools/look_shots.py "$pkg" --scene mission.tscn --out "$OUT/shots_$run" --json $S \
    > "$OUT/shots_$run.json" 2> "$OUT/shots_$run.err" < /dev/null
  echo "shots $run exit $?"
done
ARGS=()
for tok in $S; do
  case "$tok" in
    --station) ;;
    *) s="${tok%%:*}"; ARGS+=("9238 $s=$OUT/shots_9238/$s.png" "9239 $s=$OUT/shots_9239/$s.png") ;;
  esac
done
python docs/findings/edge_menu/sheet.py "docs/cold_runs/cold_9239/fixtures.png" 2 "${ARGS[@]}" && echo "sheet: docs/cold_runs/cold_9239/fixtures.png"
