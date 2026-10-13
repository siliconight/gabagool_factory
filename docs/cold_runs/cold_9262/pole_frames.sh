#!/bin/bash
# The pole line (roadmap 240, Zoo 1.104.0 + Lot 0.118.0) beside what it replaced: the same three
# stations shot in 9261's package (steel lamps on both kerbs every 25 m) and 9262's (a utility pole
# line on one kerb, a cobra-head on every pole, a can every third or fourth), the sheet side by
# side. seed_9104 picked in both, so the stations stand in the same place. Godot coordinates
# (x, height, -plan y), eye 1.8 m over the sidewalk:
#   line    on the main road's south sidewalk at x -60, looking east along the kerb the poles take
#   across  on its north sidewalk, looking at the pole with a can at plan (-48.3, -27.27)
#   corner  at the east side road's junction, looking at its corner pole and the main road's
#
# Run AFTER the drive (nothing else runs beside a frame):
#     bash docs/cold_runs/cold_9262/pole_frames.sh
#
# CANNOT RUN AGAIN AS WRITTEN (2026-10-13): workspaces/cold-9261-ws and workspaces/cold-9262-ws were
# retired on 2026-10-12, when this loop built their names and nothing named them in a form
# tools/factory_retire.py could see. poles.png is the record, kept as shot.
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
OUT="_scratch/frames_9262_poles"
mkdir -p "$OUT"
S="--station line:-60,1.8,25.5,20,6.0,26.0 --station across:-40,1.8,15.5,-48.3,7.0,27.27 --station corner:65,1.8,16,80.6,6.0,20"
# the workspaces named in full, so tools/factory_retire.py sees which ones this reads
for ws in cold-9261-ws cold-9262-ws; do
  run=${ws#cold-}; run=${run%-ws}
  pkg="workspaces/$ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
  timeout 900 python tools/look_shots.py "$pkg" --scene mission.tscn --out "$OUT/shots_$run" --json $S \
    > "$OUT/shots_$run.json" 2> "$OUT/shots_$run.err" < /dev/null
  echo "shots $run exit $?"
done
ARGS=()
for s in line across corner; do
  ARGS+=("9261 lamps $s=$OUT/shots_9261/$s.png" "9262 poles $s=$OUT/shots_9262/$s.png")
done
python docs/findings/edge_menu/sheet.py "docs/cold_runs/cold_9262/poles.png" 2 "${ARGS[@]}" && echo "sheet: docs/cold_runs/cold_9262/poles.png"
