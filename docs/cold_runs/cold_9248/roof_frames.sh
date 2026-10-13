#!/bin/bash
# The roofs by building, fewer (Zoo 1.102.0, the walker's call on 9245's roofs): the same two
# stations as `docs/cold_runs/cold_9245/roof_frames.sh`, shot in 9245's package (Zoo 1.101.0: 17
# props on every enterable roof) and 9248's (1.102.0: a profile's counts per roof), the sheet side
# by side. The lot is 9245's (seed_9104 picked in both), so the stations stand in the same place:
# `hatch` a body's eye above the deli's roof at its ladder's top, looking across the roof; `street`
# across the street from the extraction point, looking up at the deli's roof edge.
#
# Run AFTER the drive (nothing else runs beside a frame):
#     bash docs/cold_runs/cold_9248/roof_frames.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
OUT="_scratch/frames_9248_roofs"
mkdir -p "$OUT"
S="--station hatch:-43,8.2,9.49,-51,6.6,-2.51 --station street:-45,1.6,30,-51,7.0,11.5"
# the workspaces named in full, so tools/factory_retire.py sees which ones this reads
for ws in cold-9245-ws cold-9248-ws; do
  run=${ws#cold-}; run=${run%-ws}
  pkg="workspaces/$ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
  timeout 900 python tools/look_shots.py "$pkg" --scene mission.tscn --out "$OUT/shots_$run" --json $S \
    > "$OUT/shots_$run.json" 2> "$OUT/shots_$run.err" < /dev/null
  echo "shots $run exit $?"
done
ARGS=()
for s in hatch street; do
  ARGS+=("9245 $s=$OUT/shots_9245/$s.png" "9248 $s=$OUT/shots_9248/$s.png")
  python docs/cold_runs/cold_9244/frame_diff.py "$OUT/shots_9245/$s.png" "$OUT/shots_9248/$s.png"
done
python docs/findings/edge_menu/sheet.py "docs/cold_runs/cold_9248/roofs.png" 2 "${ARGS[@]}" && echo "sheet: docs/cold_runs/cold_9248/roofs.png"
