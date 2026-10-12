#!/bin/bash
# Price cold run 9263's wires (roadmap 240's third build, Lot 0.119.0) against its own package with
# the wires hidden (wires_off.py): every other draw identical, the same bake, the same stations.
# Level Factory's fixed-station harness through docs/findings/horizon_glow/price_glow.py: control_1
# (wires hidden), the subject (as built; the harness's name for it is "glow", so perf_glow.json is
# the package AS BUILT), control_2 (wires hidden again). Per heading, draw calls and p95 frame time
# against the two controls' mean; the controls' spread is the noise floor.
#
# The instrument's own control: the wires are one draw a visible 32 m cell (7 on the picked lot), so
# a heading that sees wires must read +1 to +7 draws and one that sees none +0. A price whose draws
# do not move where wires are in view has not seen them.
#
# Then the frames: the same copies shot at the stations below (Godot frame: x, height, -plan y), the
# sheet control left, subject right. Nothing else runs beside a price. The poles they look at are
# the run's own (wire_spans.py on its themed drawn spec); eye 1.8 m over the sidewalk:
#   line    9262's: the main road's south sidewalk at x -60, looking east along the line
#   across  9262's: the north sidewalk, looking at the pole with a can at plan (-48.3, -27.27)
#   corner  9262's: the east junction, its corner pole and the tie across the side street's mouth
#   west    the west junction from the south sidewalk: 0.118.1's corner pole and the tie across the
#           main road to the main line's Pole_22 at plan (-15.1, -27.27)
#   up      under the main line's span west of Pole_22, looking up at its crossarm: the sag
#
#     bash docs/cold_runs/cold_9263/wires_price.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
PKG="workspaces/cold-9263-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
SCR="_scratch/price_9263"
FR="_scratch/frames_9263"
OUT="docs/cold_runs/cold_9263"
[ -f "$PKG/mission.tscn" ] || { echo "no package at $PKG"; exit 1; }
mkdir -p "$OUT/price" "$SCR" "$FR"
rm -rf "$SCR/control" "$SCR/subject"
cp -r "$PKG" "$SCR/subject" || exit 1
cp -r "$PKG" "$SCR/control" || exit 1
python "$OUT/wires_off.py" "$SCR/control" > "$OUT/price/wires_off.txt" 2>&1 || { cat "$OUT/price/wires_off.txt"; exit 1; }
tail -1 "$OUT/price/wires_off.txt"
S="--station line:-60,1.8,25.5,20,6.0,26.0 --station across:-40,1.8,15.5,-48.3,7.0,27.27"
S="$S --station corner:65,1.8,16,80.6,6.0,20 --station west:-2,1.8,25.5,-25.6,7.0,16.0"
S="$S --station up:-31.7,1.8,25.5,-15.1,9.0,27.27"
for name in control subject; do
  timeout 900 python tools/look_shots.py "$SCR/$name" --scene mission.tscn --out "$FR/shots_$name" --json $S \
    > "$FR/shots_$name.json" 2> "$FR/shots_$name.err" < /dev/null
  echo "$name shots exit $?"
done
ARGS=()
for tok in $S; do
  case "$tok" in
    --station) ;;
    *) s="${tok%%:*}"; ARGS+=("wires hidden $s=$FR/shots_control/$s.png" "9263 as built $s=$FR/shots_subject/$s.png") ;;
  esac
done
python docs/findings/edge_menu/sheet.py "$OUT/wires.png" 2 "${ARGS[@]}" && echo "sheet: $OUT/wires.png"
python docs/findings/horizon_glow/price_glow.py "$SCR/control" "$SCR/subject" "$OUT/price" > "$OUT/price/price.txt" 2>&1
echo "price exit $?"
tail -8 "$OUT/price/price.txt"
