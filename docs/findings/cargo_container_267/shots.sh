#!/usr/bin/env bash
# The freight terminal's four shipping containers framed in one package by tools/look_shots.py, in the inspection
# light (what is there) and the level's own light (how it is lit):
#
#     bash docs/findings/cargo_container_267/shots.sh <package dir> <out dir> <label> [building]
#
# STATIONS in freight_terminal_a01's own frame (x east, y north, h up; metres), turned into the package's site frame by
# docs/findings/teller_queue_275/stations.py from the building's placement in its site.tscn. The containers, each
# 6.0 x 2.4 x 2.6 standing on the floor, long in x: container_0 at (-8, -6), container_1 at (1, 6), container_2 at
# (10, -6), container_3 at (19, 6), all in cross_dock (x -16..27, y -16..16, 6 m to its roof). Every eye stands more
# than a metre from every volume of the spec.
#   row_west     from the dock's west end, east between the two rows
#   c0_side      container_0's south side, from 6.5 m
#   c0_west_end  container_0's west end, from 3 m
#   c0_east_end  container_0's east end, from 3.5 m
#   c1_side      container_1's south side, from 5.5 m
#   dock_high    the whole dock from its south-west corner, 5 m up
set -e
cd "$(dirname "$0")/../../.."
PKG="$1"; OUT="$2"; LABEL="$3"; B="${4:-freight_terminal_a01}"
ST=$(python docs/findings/teller_queue_275/stations.py "$PKG" "$B" row_west:-14.5,0,1.7,12,0,1.3 \
    c0_side:-8,-12.5,1.6,-8,-6,1.3 c0_west_end:-14,-6,1.6,-8,-6,1.3 c0_east_end:-1.5,-6,1.6,-8,-6,1.3 \
    c1_side:1,0.5,1.6,1,6,1.3 dock_high:-15,-15,5.0,5,0,1.0 | grep -v '^#')
python tools/look_shots.py "$PKG" --out "$OUT/${LABEL}_inspect" --inspect studio $ST > "$OUT/${LABEL}_inspect.log" 2>&1; echo "inspect exit $?"
python tools/look_shots.py "$PKG" --out "$OUT/${LABEL}_lit" $ST > "$OUT/${LABEL}_lit.log" 2>&1; echo "lit exit $?"
