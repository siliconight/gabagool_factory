#!/usr/bin/env bash
# A bank lobby's teller-line queue framed in one package by tools/look_shots.py, in the inspection light (what is there)
# and the level's own light (how it is lit):
#
#     bash docs/findings/teller_queue_275/shots.sh <package dir> <out dir> <label> [building]
#
# STATIONS in bank_branch_a02's own frame (x east, y north, h up; metres), turned into the package's site frame by
# stations.py from the building's placement in its site.tscn. bank_branch_a02's counter: x -6..6 at y -2, its public
# face at y -2.4; Deli Counter 0.244.0's queue in front of it: four lines at y -4.678, -6.234, -7.79, -9.346, x 0.4..4.4
# or 1.6..5.6, letting out at x 0.4..1.6 toward the counter.
#   lobby_entry   from inside the street door, at the counter and the queue
#   queue_side    from the queue's east end, along its lanes
#   queue_exit    from where the last lane lets out, at the counter
#   lane_inside   in the middle lane, along it
#   wide          from the lobby's west end
#   counter_line  along the counter, over the queue's head
set -e
cd "$(dirname "$0")/../../.."
PKG="$1"; OUT="$2"; LABEL="$3"; B="${4:-bank_branch_a02}"
ST=$(python docs/findings/teller_queue_275/stations.py "$PKG" "$B" lobby_entry:-3,-10,1.6,2.5,-4,0.9 \
    queue_side:8.5,-6.5,1.6,0,-6,0.8 queue_exit:1.0,-4.0,1.6,1.0,-2.0,1.2 lane_inside:5.2,-7.0,1.6,0,-7,0.9 \
    wide:-13,-9,1.7,3,-5,0.8 counter_line:-5.5,-3.2,1.6,5.5,-4.5,0.9 | grep -v '^#')
python tools/look_shots.py "$PKG" --out "$OUT/${LABEL}_inspect" --inspect studio $ST > "$OUT/${LABEL}_inspect.log" 2>&1; echo "inspect exit $?"
python tools/look_shots.py "$PKG" --out "$OUT/${LABEL}_lit" $ST > "$OUT/${LABEL}_lit.log" 2>&1; echo "lit exit $?"
