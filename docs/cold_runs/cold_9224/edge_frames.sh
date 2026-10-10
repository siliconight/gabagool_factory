#!/bin/bash
# Cold run 9224's edge, before and after: the same stations on 9223's package (Lot 0.106.0, Lux
# 0.72.0: the pale wall, no glow) and 9224's (Lot 0.107.0's fence with the wall unseen, Lux
# 0.73.0's glow), through tools/look_shots.py.
#
#     bash docs/cold_runs/cold_9224/edge_frames.sh <control package> <subject package> <out dir>
#
# restaurant_row_001's plate is 196 x 100 m (x +-98, y +-50, plan); road 0 runs east-west at
# plan y -23.165 from x -88.5 to 88.5, road 1 north from it at x -26.49 to y 31.5. Plan (x, y) ->
# Godot (x, up, -y). The stations look down each road to the plate's edge and up road 1 to the
# north edge; look_shots adds its own elevated cameras over the plate.
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
CTL="$1"; SUB="$2"; OUT="$3"
STATIONS="--station west_end:-55,1.7,23.165,-98,2.2,23.165 --station east_end:55,1.7,23.165,98,2.2,23.165 --station north_road1:-26.49,1.7,0,-26.49,2.2,-50 --station road0_mid_north:0,1.7,23.165,0,2.2,-50"
for name in control subject; do
  if [ "$name" = control ]; then P="$CTL"; else P="$SUB"; fi
  # a package has no *_walk.tscn (that is the walk copy's); its entry scene is the level
  timeout 900 python tools/look_shots.py "$P" --scene mission.tscn --out "$OUT/shots_$name" --json $STATIONS \
    > "$OUT/shots_$name.json" 2> "$OUT/shots_$name.err" < /dev/null
  echo "$name shots exit $?"
done
