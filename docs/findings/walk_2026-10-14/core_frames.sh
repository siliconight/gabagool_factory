#!/bin/bash
# The office's stair core (the walk's findings 7-9) at the walker's own three positions, in the level's own
# light and in the inspection light, as one sheet for the walker before any fix is built.
#
# Cold run 9310's package (restaurant_row_001); the office stands at Godot (54, 0, -0.49), unrotated, so plan
# (x, y) is Godot (54 + x, -(y + 0.49)) (README, "7, 8 and 9"). Stations, eye then target, Godot metres:
#   core_gap        walker_75's spot, plan (-2.5, 5.6), at the first flight's stepped side through the north slot
#   core_mouth      walker_76's spot, plan (0.2, -4.2), up the core from its mouth toward the slab it reached
#   core_underside  finding 9's spot, plan (2.6, -3.2), at the second flight's fill bottom over the slot
#
# NOT DURING A WALK OR A DEMO: two look_shots runs, each a Godot window for a few minutes.
#
#     bash docs/findings/walk_2026-10-14/core_frames.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
# the workspace named in full, so tools/factory_retire.py sees which one this reads
PKG="workspaces/cold-9310-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
OUT="docs/findings/walk_2026-10-14"
SCR="_scratch/core_frames"
ST="--station core_gap:51.5,1.6,-6.1,54.0,1.7,-1.79 --station core_mouth:54.2,1.6,3.7,54.2,6.9,-10.37"
ST="$ST --station core_underside:56.6,1.6,2.7,53.2,3.6,0.51"
[ -f "$PKG/mission.tscn" ] || { echo "no package at $PKG"; exit 1; }
rm -rf "$SCR"
mkdir -p "$SCR"
timeout 1500 python tools/look_shots.py "$PKG" --scene mission.tscn --out "$SCR/own" --json --timeout 1400 $ST \
  > "$SCR/own.json" 2> "$SCR/own.err" < /dev/null
echo "own light exit $?"
timeout 1500 python tools/look_shots.py "$PKG" --scene mission.tscn --out "$SCR/inspect" --json --timeout 1400 \
  --inspect studio $ST > "$SCR/inspect.json" 2> "$SCR/inspect.err" < /dev/null
echo "inspection light exit $?"
args=()
for s in core_gap core_mouth core_underside; do
  args+=("$s, the level's own light=$SCR/own/$s.png")
  args+=("$s, INSPECTION LIGHT=$SCR/inspect/INSPECT_studio_$s.png")
done
python docs/findings/edge_menu/sheet.py "$OUT/core_9310_sheet.png" 2 "${args[@]}"
