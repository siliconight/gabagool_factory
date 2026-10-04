#!/usr/bin/env bash
# Service pads, measured: each brief's shell leg built in a fresh workspace by
# today's tools (Lot 0.93.0, Level Factory 0.133.0), against the builds of
# patches/lf_front_doors/before_after.sh's "after" (Lot 0.92.0, Level Factory
# 0.132.0) as the before; every other tool the same. Then the land-use census
# on every candidate. Writes nothing to a tool repo.
#   bash before_after.sh
set -u
R=/c/Projects/gabagool_studios/gabagool_factory
cd "$R" || exit 3
echo "Lot: $(cat lot/VERSION)  LF: $(cat level_factory/VERSION)"
leg() {  # leg <mission> <batch dir>
  local m=$1 b=$2 ws=$R/workspaces/yards-after-$1-ws
  rm -rf "$ws"
  (cd "$R" && python -m level_factory init "$ws" --name "yards after $m" >/dev/null 2>&1) || { echo "$m: init failed"; return; }
  cp "$R/workspaces/cold-9140-ws/tools.local.json" "$ws/tools.local.json"
  (cd "$R" && python -m level_factory -C "$ws" batch create "$R/$b/batch.json" 2>&1 | tail -1)
  (cd "$R" && python -m level_factory -C "$ws" plan $m >/dev/null 2>&1) || { echo "$m: plan failed"; return; }
  (cd "$R" && python -m level_factory -C "$ws" run $m 2>&1 | grep -E "candidates:|blockers open" | sed "s/^/  after $m: /")
}
echo "== build $(date +%T)"
leg gas_block_001 docs/cold_runs/cold_9140 &
leg club_block_014 docs/cold_runs/cold_9134 &
leg crossroads_9600 docs/experiments/crossroads_9600 &
wait
echo "== census $(date +%T)"
for v in before after; do
  for m in gas_block_001 club_block_014 crossroads_9600; do
    if [ $v = before ]; then ws=workspaces/fronts-after-$m-ws; else ws=workspaces/yards-after-$m-ws; fi
    for j in $ws/.level_factory/jobs/$m.lot_assemble.candidate.seed_*; do
      seed=${j##*seed_}
      python tools/landuse_census.py "$ws" $m $seed 2>/dev/null | python -c "
import json, sys
d = json.load(sys.stdin)
a = d['areas']
print('%-7s %-16s %s  yard %6.1f m2  remainder %.4f (%7.1f m2)  largest piece %7.1f m2' % ('$v', '$m', '$seed', a['yard'], d['shares']['remainder'], a['remainder'], d['remainder_largest_blob']))
" || echo "$v $m $seed: census failed"
      gp=$j/out/site.site.gameplay.json
      python -c "
import json, sys
g = json.load(open(sys.argv[1], encoding='utf-8'))
yp = g.get('yard_plan') or {}
fs = [f.get('code') for f in (g.get('tactical') or {}).get('findings', [])] if isinstance(g.get('tactical'), dict) else []
print('        pads %d, no room %d; dumpsters %d' % (len(yp.get('placed') or []), len(yp.get('findings') or []),
      sum(1 for p in (g.get('furniture_plan') or {}).get('placed', []) if p.get('species') == 'dumpster')))
" "$gp"
    done
  done
done
echo "== done $(date +%T)"
