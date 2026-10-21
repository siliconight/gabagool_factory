#!/usr/bin/env bash
# The parked cars of bank_block_001 at seed 9082 framed by tools/look_shots.py, in the inspection light (what is there)
# and the level's own light (how it is lit):
#
#     bash docs/findings/car_wear_44/shots.sh <walk copy> <out dir> <label>
#
# STATIONS in the site's own frame (Godot: x, y up, z; metres), the same in cold runs 9364, 9365 and 9366 -- one level,
# Zoo the only tool that moved -- read off the walk copy's site.tscn:
#   cover_133, the compact that Zoo 1.120.x draws as a silver beater: at (30.1, 0.72, -10.87), unturned, so its nose
#     looks along +z, its tail along -z and its kerb side along -x;
#   cover_2, a tan SUV 1.120.x drives (its one sticker): at (46.05, 0.86, -11.59), unturned.
#   beater_rear  behind the beater on the driver's side: the bumper's stickers and a rear arch
#   beater_kerb  along the beater's kerb side from the sidewalk: the primer and the kerb side's arches
#   beater_roof  over the beater's roof: the lost clear coat
#   suv_rear     behind the SUV: its sticker and its dust
#   lane         down the parking lane past the beater: the street's mix
set -e
cd "$(dirname "$0")/../../.."
PKG="$1"; OUT="$2"; LABEL="$3"
ST="--station beater_rear:31.9,1.45,-15.6,30.1,0.55,-12.4 --station beater_kerb:27.8,1.40,-10.3,30.1,0.75,-10.6 \
--station beater_roof:31.4,4.0,-8.3,30.1,1.35,-10.9 --station suv_rear:47.8,1.5,-16.6,46.05,0.65,-13.9 \
--station lane:31.8,1.6,-21.0,30.4,0.9,4.0"
python tools/look_shots.py "$PKG" --out "$OUT/${LABEL}_inspect" --inspect studio $ST > "$OUT/${LABEL}_inspect.log" 2>&1; echo "inspect exit $?"
python tools/look_shots.py "$PKG" --out "$OUT/${LABEL}_lit" $ST > "$OUT/${LABEL}_lit.log" 2>&1; echo "lit exit $?"
