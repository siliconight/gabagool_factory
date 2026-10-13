#!/bin/bash
# Price cold run 9268's tar roofs (Deli Counter 0.210.0) against 9267's concrete ones: Level Factory's
# fixed stations through docs/findings/horizon_glow/price_glow.py -- control_1 (9267's package), the
# subject (9268's, perf_glow.json, the harness's name), control_2 (9267's again), per heading against
# the two controls' mean, their spread the noise floor. The same lot in both (seed_9104), so the
# stations stand in the same place. The copies are removed at the end. Nothing else runs beside a price.
#
#     bash docs/cold_runs/cold_9268/roof_price.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
P67="workspaces/cold-9267-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
P68="workspaces/cold-9268-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
SCR="_scratch/price_9268"
OUT="docs/cold_runs/cold_9268"
[ -f "$P67/mission.tscn" ] || { echo "no package at $P67"; exit 1; }
[ -f "$P68/mission.tscn" ] || { echo "no package at $P68"; exit 1; }
mkdir -p "$OUT/price" "$SCR"
rm -rf "$SCR/control" "$SCR/subject"
cp -r "$P67" "$SCR/control" || exit 1
cp -r "$P68" "$SCR/subject" || exit 1
python docs/findings/horizon_glow/price_glow.py "$SCR/control" "$SCR/subject" "$OUT/price" > "$OUT/price/price.txt" 2>&1
echo "price exit $?"
tail -8 "$OUT/price/price.txt"
rm -rf "$SCR/control" "$SCR/subject"
