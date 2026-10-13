#!/bin/bash
# Roof props, seen (roadmap 181): two stations shot in 9244's package (no roof props) and 9245's
# (Zoo 1.101.0's scatter on every enterable roof), the sheet side by side. Stations in look_shots'
# Godot frame (x, up, -y), from 9244's gameplay_anchors.json: the deli's roof ladder `lot:ladder_0`
# tops out at (-43, 0, 9.49) on a roof 6.6 m up, so `hatch` stands a body's eye (1.6 m) above the
# roof at the hatch and looks across the roof to the building's centre (-51, 6.6, -2.51); `street`
# stands across the street from the extraction point (-45, 0, 13.49) and looks up at the deli's
# roof edge, the view a player on the ground gets of what the roof carries.
#
# Run AFTER the price (nothing else runs beside a perf measurement):
#     bash docs/cold_runs/cold_9245/roof_frames.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
OUT="_scratch/frames_9245_roofs"
mkdir -p "$OUT"
S="--station hatch:-43,8.2,9.49,-51,6.6,-2.51 --station street:-45,1.6,30,-51,7.0,11.5"
# the workspaces named in full, so tools/factory_retire.py sees which ones this reads
for ws in cold-9244-ws cold-9245-ws; do
  run=${ws#cold-}; run=${run%-ws}
  pkg="workspaces/$ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
  timeout 900 python tools/look_shots.py "$pkg" --scene mission.tscn --out "$OUT/shots_$run" --json $S \
    > "$OUT/shots_$run.json" 2> "$OUT/shots_$run.err" < /dev/null
  echo "shots $run exit $?"
done
ARGS=()
for s in hatch street; do
  ARGS+=("9244 $s=$OUT/shots_9244/$s.png" "9245 $s=$OUT/shots_9245/$s.png")
  python docs/cold_runs/cold_9244/frame_diff.py "$OUT/shots_9244/$s.png" "$OUT/shots_9245/$s.png"
done
python docs/findings/edge_menu/sheet.py "docs/cold_runs/cold_9245/roofs.png" 2 "${ARGS[@]}" && echo "sheet: docs/cold_runs/cold_9245/roofs.png"
