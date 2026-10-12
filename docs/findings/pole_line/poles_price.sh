#!/bin/bash
# Price the pole line itself (roadmap 240's builds 1 and 2, Zoo 1.104.0 + Lot 0.118.0): cold run 9261's
# package (steel lamps on both kerbs of the band roads, every 25 m) as the control, cold run 9262's
# (one pole line a street, a cobra-head on every pole, a can every third or fourth) as the subject.
# The same lot (seed_9104 picked in both), the same Level Factory stations: the two packages'
# gameplay_anchors.json are byte for byte the same (sha256 6a56ba31d6464f09...), so the harness stands
# at the same 53 headings in both. Two builds, two bakes: everything that differs between the runs
# is in the difference, which is the street's furniture and its light (9262's NOTES.md).
#
# Level Factory's fixed-station harness through docs/findings/horizon_glow/price_glow.py: control_1
# (9261), the subject (9262; the harness's name for it is "glow", so perf_glow.json is 9262), control_2
# (9261 again). Per heading against the controls' mean; the controls' spread is the noise floor.
# The copies go to _scratch/price_poles/ and are deleted once the JSONs exist (about 250 MB each).
# Nothing else runs beside a price.
#
#     bash docs/findings/pole_line/poles_price.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
OUT="docs/findings/pole_line/price_9261_9262"
SCR="_scratch/price_poles"
mkdir -p "$OUT" "$SCR"
rm -rf "$SCR/control" "$SCR/subject"
for pair in control:9261 subject:9262; do
  name="${pair%%:*}"; run="${pair##*:}"
  pkg="workspaces/cold-$run-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
  [ -f "$pkg/mission.tscn" ] || { echo "no package at $pkg"; exit 1; }
  cp -r "$pkg" "$SCR/$name" || exit 1
done
cmp -s "$SCR/control/gameplay_anchors.json" "$SCR/subject/gameplay_anchors.json" \
  || { echo "THE STATIONS DIFFER: gameplay_anchors.json is not the same file in both"; exit 1; }
python docs/findings/horizon_glow/price_glow.py "$SCR/control" "$SCR/subject" "$OUT" > "$OUT/price.txt" 2>&1
echo "price exit $?"
tail -8 "$OUT/price.txt"
