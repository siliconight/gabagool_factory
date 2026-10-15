#!/bin/bash
# The deli's basement (the walk's finding 5) at the walker's spot and the two places the fix changed, in the
# level's own light and in the inspection light, as one sheet: before against after is one run against another.
#
# An urban_row_001 package of seed_9104, which stands deli_a01 at Godot (-51, 0, -2.51), unrotated, so plan
# (x, y) is Godot (-51 + x, -(y + 2.51)) (README, "5"); the basement floor is z -3.3, an eye 1.6 m over it -1.7.
# Stations, eye then target, Godot metres:
#   basement_west   walker_74's spot, plan (-17.8, -3.6), at the divider's west end (plan x -15, y 1.0), where
#                   0.221.0 left 7 m open from x -12 to the outside wall
#   basement_east   in the utility room, plan (15, -4), at the divider's east end (plan x 15.5), where 0.221.0
#                   left the vault open to it
#   utility_door    in the corridor, plan (-3, -4), at the utility room's door 0.222.0 adds (plan x 1, y -4)
#
# NOT DURING A WALK OR A DEMO: two look_shots runs, each a Godot window for a few minutes.
#
#     bash docs/findings/walk_2026-10-14/basement_frames.sh <cold run>
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
RUN="${1:?a cold run number, its workspace an urban_row_001 run of seed_9104}"
PKG="workspaces/cold-$RUN-ws/.level_factory/exports/LF_urban_row_001.portable-godot"
OUT="docs/findings/walk_2026-10-14"
SCR="_scratch/basement_frames_$RUN"
ST="--station basement_west:-68.8,-1.7,1.1,-66.0,-2.0,-3.51 --station basement_east:-36.0,-1.7,1.49,-35.5,-2.0,-3.51"
ST="$ST --station utility_door:-54.0,-1.7,1.49,-50.0,-2.0,1.49"
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
for s in basement_west basement_east utility_door; do
  args+=("$s, the level's own light=$SCR/own/$s.png")
  args+=("$s, INSPECTION LIGHT=$SCR/inspect/INSPECT_studio_$s.png")
done
python docs/findings/edge_menu/sheet.py "$OUT/basement_${RUN}_sheet.png" 2 "${args[@]}"
