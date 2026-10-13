#!/bin/bash
# The rowhome Empties' roofs in tar (Deli Counter 0.210.0, the walker's call of 2026-10-12: "tar now,
# coating later"; docs/reference/ROWHOUSE_ROOFS.md): cold run 9267's package (the Empties roofed in
# `concrete`, skinned concrete_delco) against 9268's (tar, tar_neutral), the same lot -- seed_9104
# picked in both -- so the stations stand in the same place. The twelve Empties stand in one row along
# Godot z 37.8, x -78.5 to -6.4, about 10 m tall:
#   over    24 m up in front of the row, looking down onto the roofs
#   along   18 m up past the row's west end, looking east along the roofs
#   hatch, street   cold run 9248's two roof stations (the deli's roof, already tar), the control: a
#                   frame that moves there moved for some other reason
# Then frame_diff on each pair and a sheet, 9267 left, 9268 right.
#
# Run AFTER the drive (nothing else runs beside a frame):
#     bash docs/cold_runs/cold_9268/roof_frames.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
OUT="_scratch/frames_9268_roofs"
mkdir -p "$OUT"
S="--station over:-42,24,18,-42,9,40 --station along:-88,18,30,-30,8,40"
S="$S --station hatch:-43,8.2,9.49,-51,6.6,-2.51 --station street:-45,1.6,30,-51,7.0,11.5"
# the workspaces named in full, so tools/factory_retire.py sees which ones this reads
for ws in cold-9267-ws cold-9268-ws; do
  run=${ws#cold-}; run=${run%-ws}
  pkg="workspaces/$ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
  [ -f "$pkg/mission.tscn" ] || { echo "no package at $pkg"; exit 1; }
  timeout 900 python tools/look_shots.py "$pkg" --scene mission.tscn --out "$OUT/shots_$run" --json $S \
    > "$OUT/shots_$run.json" 2> "$OUT/shots_$run.err" < /dev/null
  echo "shots $run exit $?"
done
ARGS=()
for s in over along hatch street; do
  ARGS+=("9267: concrete $s=$OUT/shots_9267/$s.png" "9268: tar $s=$OUT/shots_9268/$s.png")
  python docs/cold_runs/cold_9244/frame_diff.py "$OUT/shots_9267/$s.png" "$OUT/shots_9268/$s.png"
done
python docs/findings/edge_menu/sheet.py "docs/cold_runs/cold_9268/roofs.png" 2 "${ARGS[@]}" && echo "sheet: docs/cold_runs/cold_9268/roofs.png"
