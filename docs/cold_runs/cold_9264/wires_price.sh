#!/bin/bash
# Price cold run 9264's wires (Lot 0.119.1: held to a pixel by a vertex shader, faded by coverage, so
# drawn in the transparent pass) the way 9263's 0.119.0 wires were priced: the run's own package
# against a copy with every wire node hidden (docs/cold_runs/cold_9263/wires_off.py), Level Factory's
# fixed stations through docs/findings/horizon_glow/price_glow.py -- control_1 (hidden), the subject
# as built (perf_glow.json, the harness's name), control_2 (hidden again). Then the frames at 9263's
# five wire stations, and two sheets: wires.png (hidden left, as built right) and against_9263.png
# (9263's 0.119.0 wires left, 9264's 0.119.1 right, then the far end of `line` enlarged three times).
# Nothing else runs beside a price.
#
#     bash docs/cold_runs/cold_9264/wires_price.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
PKG="workspaces/cold-9264-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
SCR="_scratch/price_9264"
FR="_scratch/frames_9264"
OUT="docs/cold_runs/cold_9264"
[ -f "$PKG/mission.tscn" ] || { echo "no package at $PKG"; exit 1; }
[ -d "_scratch/frames_9263/shots_subject" ] || { echo "no 9263 frames at _scratch/frames_9263/shots_subject"; exit 1; }
mkdir -p "$OUT/price" "$SCR" "$FR"
rm -rf "$SCR/control" "$SCR/subject"
cp -r "$PKG" "$SCR/subject" || exit 1
cp -r "$PKG" "$SCR/control" || exit 1
python docs/cold_runs/cold_9263/wires_off.py "$SCR/control" > "$OUT/price/wires_off.txt" 2>&1 \
  || { cat "$OUT/price/wires_off.txt"; exit 1; }
tail -1 "$OUT/price/wires_off.txt"
S="--station line:-60,1.8,25.5,20,6.0,26.0 --station across:-40,1.8,15.5,-48.3,7.0,27.27"
S="$S --station corner:65,1.8,16,80.6,6.0,20 --station west:-2,1.8,25.5,-25.6,7.0,16.0"
S="$S --station up:-31.7,1.8,25.5,-15.1,9.0,27.27"
for name in control subject; do
  timeout 900 python tools/look_shots.py "$SCR/$name" --scene mission.tscn --out "$FR/shots_$name" --json $S \
    > "$FR/shots_$name.json" 2> "$FR/shots_$name.err" < /dev/null
  echo "$name shots exit $?"
done
python - <<'PY'
from PIL import Image
for run in ("9263", "9264"):
    im = Image.open("_scratch/frames_%s/shots_subject/line.png" % run).crop((560, 300, 880, 420))
    im.resize((im.width * 3, im.height * 3), Image.NEAREST).save("_scratch/frames_%s/shots_subject/line_far.png" % run)
PY
ARGS=()
B=()
for s in line across corner west up; do
  ARGS+=("wires hidden $s=$FR/shots_control/$s.png" "9264 as built $s=$FR/shots_subject/$s.png")
  B+=("9263 (0.119.0) $s=_scratch/frames_9263/shots_subject/$s.png" "9264 (0.119.1) $s=$FR/shots_subject/$s.png")
done
B+=("9263 (0.119.0) line_far=_scratch/frames_9263/shots_subject/line_far.png" "9264 (0.119.1) line_far=$FR/shots_subject/line_far.png")
python docs/findings/edge_menu/sheet.py "$OUT/wires.png" 2 "${ARGS[@]}" && echo "sheet: $OUT/wires.png"
python docs/findings/edge_menu/sheet.py "$OUT/against_9263.png" 2 "${B[@]}" && echo "sheet: $OUT/against_9263.png"
python docs/findings/horizon_glow/price_glow.py "$SCR/control" "$SCR/subject" "$OUT/price" > "$OUT/price/price.txt" 2>&1
echo "price exit $?"
tail -8 "$OUT/price/price.txt"
