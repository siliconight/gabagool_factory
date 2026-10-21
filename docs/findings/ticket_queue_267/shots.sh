#!/usr/bin/env bash
# The box office's queue framed in one package by tools/look_shots.py, in the inspection light (what is there) and the
# level's own light (how it is lit):
#
#     bash docs/findings/ticket_queue_267/shots.sh <package dir> <out dir> <label>
#
# STATIONS in site metres, Godot's frame (X east, Y up, Z south), eye then target. arena_a02 stands unturned at site
# (-2, 0, -4.01) in club_block_014 seed 9014 (cold runs 9358 to 9361), so a building point (x, y) at height h is site
# (x - 2, h, -y - 4.01). Deli Counter 0.243.0's queue in building metres: the ticket window at (-15.5, 5.9), 1.0 to
# 2.1 m up; four lines 4.8 m long at y 4.572, 3.016, 1.46, -0.096, from x -14.9 or -16.1 to -10.1 or -11.3.
#   queue_front     from the event floor, 9 m south of the queue, at the window and the lanes
#   queue_entrance  from the queue's east end, the way in, looking west along it to the window
#   window_close    from the floor in front of the window, at the window
#   lane_inside     in the middle lane, looking along it
#   far_view        from across the event floor
#   barrier_line    9359's far_line station: where the four barricades stood
set -e
cd "$(dirname "$0")/../../.."
PKG="$1"; OUT="$2"; LABEL="$3"
ST='--station queue_front:-15.1,1.6,0.99,-16.5,0.9,-8.01 --station queue_entrance:-9.6,1.6,-5.01,-17.5,0.9,-7.81 --station window_close:-17.0,1.6,-7.61,-17.5,1.5,-9.91 --station lane_inside:-12.6,1.6,-6.25,-18.0,0.9,-6.25 --station far_view:-6.0,1.7,4.99,-15.1,0.8,-6.71 --station barrier_line:-2.0,1.7,12.5,-2.0,0.6,1.99'
python tools/look_shots.py "$PKG" --out "$OUT/${LABEL}_inspect" --inspect studio $ST > "$OUT/${LABEL}_inspect.log" 2>&1; echo "inspect exit $?"
python tools/look_shots.py "$PKG" --out "$OUT/${LABEL}_lit" $ST > "$OUT/${LABEL}_lit.log" 2>&1; echo "lit exit $?"
