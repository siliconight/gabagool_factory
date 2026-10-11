#!/bin/bash
# Zoo 1.99.0's container roof, seen: look_shots' default stations -- the four elevated views among
# them, where 9226 saw a container's top as a bright flat slab floating over a storefront -- shot
# in 9226's package (Zoo 1.78-era set, the roof at full paint) and this run's (the roof at the
# walls' valley shade). The two packages differ in every release since 9226, so the sheet is the
# roof's look, not its price; the price is the census's (no primitive added). Frames to
# _scratch/frames_9240_roof/, the sheet to docs/cold_runs/cold_9240/roof.png (9226 beside 9240,
# the four elevated views).
#
#     bash docs/cold_runs/cold_9240/roof_frames.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
PKG_C="workspaces/cold-9226-ws/.level_factory/exports/LF_warehouse_yard_001.portable-godot"
PKG_S="workspaces/cold-9240-ws/.level_factory/exports/LF_warehouse_yard_001.portable-godot"
OUT="_scratch/frames_9240_roof"
mkdir -p "$OUT"
for run in 9226 9240; do
  pkg="$PKG_C"; [ "$run" = 9240 ] && pkg="$PKG_S"
  timeout 900 python tools/look_shots.py "$pkg" --scene mission.tscn --out "$OUT/shots_$run" --json \
    > "$OUT/shots_$run.json" 2> "$OUT/shots_$run.err" < /dev/null
  echo "shots $run exit $?"
done
ARGS=()
for s in elev_W elev_E elev_N elev_S; do
  ARGS+=("9226 $s=$OUT/shots_9226/$s.png" "9240 $s=$OUT/shots_9240/$s.png")
done
python docs/findings/edge_menu/sheet.py "docs/cold_runs/cold_9240/roof.png" 2 "${ARGS[@]}" && echo "sheet: docs/cold_runs/cold_9240/roof.png"
