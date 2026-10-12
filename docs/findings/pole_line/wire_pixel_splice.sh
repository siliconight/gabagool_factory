#!/bin/bash
# The look at Lot 0.119.1's wires before the release (wire_pixel_splice.py): cold run 9263's package
# with a drafted Lot's wire files and material spliced in, shot at cold run 9263's five wire stations
# (docs/cold_runs/cold_9263/wires_price.sh), beside 9263 as built. The sheet: 0.119.0 left, the splice
# right, a row a station, then the far end of `line` enlarged three times from both.
#
#     LOT_ROOT=<drafted Lot copy> bash docs/findings/pole_line/wire_pixel_splice.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
[ -n "${LOT_ROOT:-}" ] || { echo "set LOT_ROOT to the drafted Lot copy"; exit 2; }
PKG="workspaces/cold-9263-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
DRAWN="workspaces/cold-9263-ws/.level_factory/jobs/restaurant_row_001.themed_site_assemble/1/out/site.site.drawn.json"
SCR="_scratch/splice_9263"
FR="_scratch/frames_9263"
OUT="docs/findings/pole_line"
[ -d "$FR/shots_subject" ] || { echo "no 9263 frames at $FR/shots_subject (run wires_price.sh first)"; exit 1; }
rm -rf "$SCR"
cp -r "$PKG" "$SCR" || exit 1
python "$OUT/wire_pixel_splice.py" "$SCR" "$DRAWN" > "$OUT/wire_pixel_splice.out.txt" 2>&1 \
  || { cat "$OUT/wire_pixel_splice.out.txt"; exit 1; }
cat "$OUT/wire_pixel_splice.out.txt"
S="--station line:-60,1.8,25.5,20,6.0,26.0 --station across:-40,1.8,15.5,-48.3,7.0,27.27"
S="$S --station corner:65,1.8,16,80.6,6.0,20 --station west:-2,1.8,25.5,-25.6,7.0,16.0"
S="$S --station up:-31.7,1.8,25.5,-15.1,9.0,27.27"
timeout 900 python tools/look_shots.py "$SCR" --scene mission.tscn --out "$FR/shots_pixel" --json $S \
  > "$FR/shots_pixel.json" 2> "$FR/shots_pixel.err" < /dev/null
echo "splice shots exit $?"
grep -i -E "shader error|error:.*shader|SHADER" "$FR/shots_pixel.err" | head -5
python - "$FR" <<'PY'
import sys
from PIL import Image
fr = sys.argv[1]
for name in ("subject", "pixel"):
    im = Image.open("%s/shots_%s/line.png" % (fr, name)).crop((560, 300, 880, 420))
    im.resize((im.width * 3, im.height * 3), Image.NEAREST).save("%s/shots_%s/line_far.png" % (fr, name))
PY
ARGS=()
for s in line across corner west up line_far; do
  ARGS+=("0.119.0 $s=$FR/shots_subject/$s.png" "0.119.1 $s=$FR/shots_pixel/$s.png")
done
python docs/findings/edge_menu/sheet.py "$OUT/wire_pixel.png" 2 "${ARGS[@]}" && echo "sheet: $OUT/wire_pixel.png"
rm -rf "$SCR"
