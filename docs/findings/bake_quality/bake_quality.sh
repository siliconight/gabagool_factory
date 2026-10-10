#!/bin/bash
# Roadmap 224: re-bake one walk copy at each LightmapGI quality and shoot the box truck's shaded side.
#
#     bash docs/findings/bake_quality/bake_quality.sh <walk copy> <out dir> [qualities...]
#
# For each quality: `tools/lux_rebake.py --bake-quality Q` (Level Factory's own bake, Lux's
# preset, the shipped spawned set), its report kept as rebake_qQ.json; then `tools/look_shots.py`
# at the truck's side station, shots_qQ/. `blotch.py` reads the frames. Quality 0 is Level
# Factory's own, so its copy is the control: it must reproduce the shipped frame.
F=/c/Projects/gabagool_studios/gabagool_factory
cd "$F" || exit 1
SRC="$1"; OUT="$2"; shift 2
QS="${*:-0 1 2}"
mkdir -p "$OUT"
for q in $QS; do
  DEST="$OUT/copy_q$q"
  python tools/lux_rebake.py "$SRC" "$DEST" --bake-quality "$q" > "$OUT/rebake_q$q.json" 2> "$OUT/rebake_q$q.err" < /dev/null
  echo "q$q rebake exit $?"
  python tools/look_shots.py "$DEST" --out "$OUT/shots_q$q" --json \
    --station "truck_side:-31.9,1.7,-4.5,-39.9,1.7,-4.5" \
    > "$OUT/shots_q$q.json" 2> "$OUT/shots_q$q.err" < /dev/null
  echo "q$q shots exit $?"
  rm -rf "$DEST"              # 290 MB a copy; the report and the frames are what is kept
done
echo done
