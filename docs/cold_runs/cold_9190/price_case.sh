#!/usr/bin/env bash
# Price Zoo 1.81.0's deli case against the box it replaced, on cold run 9190's
# package: the shipped package twice (the control: the same bytes, so any
# difference between them is the instrument's) around a copy whose deli_a01
# stands 9189's box in the case's place (`case_box_variant.py`). Each harness
# copy is deleted the moment its report exists, and the variant when the
# three are done.
#
#     bash docs/cold_runs/cold_9190/price_case.sh > docs/cold_runs/cold_9190/price_case.log 2>&1
#     python docs/cold_runs/cold_9185/compare_prices.py _runs/perf_inner/case_a.json \
#         _runs/perf_inner/case_b.json _runs/perf_inner/case_box.json
#
# The box is the CHANGE in compare_prices' columns, so its "chg - mean(a,b)"
# reads as the case's cost with the sign turned over.
set -u
cd /c/Projects/gabagool_studios/gabagool_factory
PC=workspaces/cold-9190-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot
BOX=workspaces/cold-9189-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot/lot/deli_a01/art/zoo/prop_delco_1997_03_w700_d110_h130_mglass.glb
PV=_runs/perf_inner/src_9190_box
python docs/cold_runs/cold_9190/case_box_variant.py "$PC" "$PV" "$BOX" || exit 1
for pair in "case_a:$PC" "case_box:$PV" "case_b:$PC"; do
  tag=${pair%%:*}; pkg=${pair#*:}
  echo "== $tag $(date +%T)"
  python _runs/perf_inner/run.py "$tag" "$pkg" 2>&1 | tail -6
  if [ -f "_runs/perf_inner/$tag.json" ]; then
    rm -rf "_runs/perf_inner/$tag"
    echo "   report kept, copy removed"
  else
    echo "   NO REPORT for $tag; copy kept for a look"
  fi
done
rm -rf "$PV"
echo "== done $(date +%T)"
