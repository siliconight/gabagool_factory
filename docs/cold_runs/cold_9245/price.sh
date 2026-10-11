#!/bin/bash
# The price of roof props (roadmap 181): 9245's package (Zoo 1.101.0's scatter on every enterable
# roof, merged one roof a species) against 9244's (the same lot, one Zoo, Deli Counter and Level
# Factory release earlier, no roof props), the horizon-glow harness's way: control_1, subject,
# control_2 at the package's fixed stations, then each heading's draws and p95 against the two
# controls' mean (`price_vs_mean.py`, 9244's copy). The anchors are compared FIRST: the stations
# come from each package's gameplay_anchors.json, and a price across two anchor sets is two
# instruments. Each package is COPIED into _scratch (the harness writes into the project) and the
# copies are deleted at the end (perf copies fill the disk).
#
#     bash docs/cold_runs/cold_9245/price.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
P44="workspaces/cold-9244-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
P45="workspaces/cold-9245-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
OUT="docs/cold_runs/cold_9245/price"
python - "$P44/gameplay_anchors.json" "$P45/gameplay_anchors.json" <<'EOF' || exit 3
import json, sys
a, b = (json.load(open(p, encoding="utf-8")) for p in sys.argv[1:3])
ka = sorted((x["anchor_type"], x["shell_id"], tuple(x["transform"]["pos"])) for x in a["anchors"])
kb = sorted((x["anchor_type"], x["shell_id"], tuple(x["transform"]["pos"])) for x in b["anchors"])
print("anchors 9244", len(ka), "9245", len(kb), "identical" if ka == kb else "DIFFER")
if ka != kb:
    for x in sorted(set(ka) ^ set(kb))[:10]: print("  ", x)
    sys.exit(3)
EOF
mkdir -p "$OUT" _scratch/price_9245
rm -rf _scratch/price_9245/control _scratch/price_9245/subject
cp -r "$P44" _scratch/price_9245/control && cp -r "$P45" _scratch/price_9245/subject || exit 4
python docs/findings/horizon_glow/price_glow.py _scratch/price_9245/control _scratch/price_9245/subject "$OUT" 2>&1 | tee "$OUT/price.txt"
cp docs/cold_runs/cold_9244/price/price_vs_mean.py "$OUT/price_vs_mean.py"
python "$OUT/price_vs_mean.py" "$OUT" 2>&1 | tee "$OUT/vs_mean.txt" | tail -8
rm -rf _scratch/price_9245/control _scratch/price_9245/subject
echo "copies removed"
