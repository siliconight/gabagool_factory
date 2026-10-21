#!/usr/bin/env bash
# The rooms the look review of 2026-10-19 framed -- deli_a03's market aisles, kitchen and stockroom, pharmacy_a01's
# retail floor, counter and vault rooms, the office's bullpen and lobby -- in one restaurant_row_001 package, framed by
# tools/look_shots.py in the level's own light and the inspection light:
#
#     bash docs/findings/denser_rooms_148/shots.sh <workspace> <walk copy> <out dir> <label>
#
# STATIONS from tools/room_stations.py, read off the run's own workspace (the building's placement in the drawn spec,
# the rooms in its gameplay manifest): the eye 1.6 m over the floor a third of the way down the room's long axis,
# looking at the far end 2.8 m up. The same buildings at the same seed give the same stations in both packages, and
# they are the stations the review's frames used. The three buildings are the drawn spec's b0, b1 and b2.
set -e
cd "$(dirname "$0")/../../.."
WS="$1"; PKG="$2"; OUT="$3"; LABEL="$4"
mkdir -p "$OUT"
# the review's seven rooms and the market aisles' neighbour, and the two rooms of these buildings the count fix
# (0.246.0) moved that have a station: the office's floor_1 (storey 1) and deli_a03's server_room
KEEP="market_aisles kitchen stockroom_loading retail_floor rx_counter rx_vault ground_bullpen lobby floor_1 server_room"
ST=""
for b in b0 b1 b2; do
  for s in $(python tools/room_stations.py "$WS" restaurant_row_001 "$b" --rooms 12 2>/dev/null | tr ' ' '\n' | grep -v -- "^--station$"); do
    room="${s%%:*}"
    for k in $KEEP; do if [ "$room" = "$k" ]; then ST="$ST --station $s"; fi; done
  done
done
echo "stations:$ST" > "$OUT/${LABEL}_stations.txt"
# each exit said, not swallowed: under `set -e` a failing `cmd; echo $?` stops before the echo
rc=0; python tools/look_shots.py "$PKG" --out "$OUT/${LABEL}_lit" $ST > "$OUT/${LABEL}_lit.log" 2>&1 || rc=$?
echo "lit exit $rc"
rc=0; python tools/look_shots.py "$PKG" --out "$OUT/${LABEL}_inspect" --inspect studio $ST > "$OUT/${LABEL}_inspect.log" 2>&1 || rc=$?
echo "inspect exit $rc"
