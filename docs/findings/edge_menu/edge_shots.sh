#!/bin/bash
# Shoot the edge stations on one copy of the walked level: bash edge_shots.sh <project> <out name>
# Plan (x, y) -> Godot (x, up, -y). Road 0 runs east-west at plan y -24.15; road 1 north from it at
# x 42 to y 32.5; the plate is x +-102, y +-51; the empty rowhomes face road 0 from the south.
F=/c/Projects/gabagool_studios/gabagool_factory
cd "$F" || exit 1
P="$1"; OUT="_scratch/edge_menu/shots_$2"
rm -rf "$OUT"
timeout 900 python tools/look_shots.py "$P" --out "$OUT" --json \
  --station "west_end:-70,1.7,24.15,-102,2.2,24.15" \
  --station "east_end:70,1.7,24.15,102,2.2,24.15" \
  --station "north_road1:42,1.7,0,42,2.2,-51" \
  --station "north_lot:3,1.7,-25,3,2.2,-51" \
  --station "south_rows:0,1.7,22,0,6.0,51" \
  > "$OUT.json" 2> "$OUT.err" < /dev/null
echo "exit $?"
