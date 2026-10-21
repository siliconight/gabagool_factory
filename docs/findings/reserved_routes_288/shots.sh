#!/usr/bin/env bash
# deli_a03's market aisles -- where Deli Counter 0.250.0 reserves its routes before its rows are laid -- and two
# controls that must not move, its kitchen and the office's ground bullpen, in one restaurant_row_001 package, framed
# by tools/look_shots.py in the level's own light and the inspection light. Copied from
# docs/findings/denser_rooms_148/shots.sh, its rooms changed:
#
#     bash docs/findings/reserved_routes_288/shots.sh <workspace> <walk copy> <out dir> <label>
#
# STATIONS from tools/room_stations.py, read off the run's own workspace, as that script's header says.
set -e
cd "$(dirname "$0")/../../.."
WS="$1"; PKG="$2"; OUT="$3"; LABEL="$4"
mkdir -p "$OUT"
KEEP="market_aisles kitchen ground_bullpen"
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
