#!/usr/bin/env bash
# Price the blended chain-link fabric (Zoo 1.78.0) against the alpha test it
# replaced, on cold run 9185's package: the shipped package twice (the
# control: same bytes) around a copy whose fence fabric alone is MASK 0.5.
# Each harness copy is deleted the moment its report exists, and the variant
# when the three are done.
#
#     bash docs/cold_runs/cold_9185/price_fabric.sh > price_fabric.log 2>&1
#     python docs/cold_runs/cold_9185/compare_prices.py _runs/perf_inner/fabric_blend_a.json \
#         _runs/perf_inner/fabric_blend_b.json _runs/perf_inner/fabric_mask.json
#
# Started once on 2026-10-06 and stopped in its first pass for a pause; no
# report came back. Stopping it needs the loop shell killed FIRST: killing a
# pass's subshell only moves the loop on to the next pass.
set -u
cd /c/Projects/gabagool_studios/gabagool_factory
PB=workspaces/cold-9185-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot
PM=_runs/perf_inner/src_9185_mask
python docs/cold_runs/cold_9185/fabric_mask_variant.py "$PB" "$PM" M_Skin_chain_link_delco_1997 MASK 0.5 || exit 1
for pair in "fabric_blend_a:$PB" "fabric_mask:$PM" "fabric_blend_b:$PB"; do
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
rm -rf "$PM"
echo "== done $(date +%T)"
