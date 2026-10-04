#!/usr/bin/env bash
# Parking fields, measured: each brief's shell leg built in a fresh workspace
# by today's tools (Lot 0.94.0, Level Factory 0.134.0), against the builds of
# patches/lot_yards/before_after.sh's "after" (Lot 0.93.0, Level Factory
# 0.133.0) as the before; every other tool the same. Then the land-use census
# on every candidate, and the findings diffed. Writes nothing to a tool repo.
#   bash before_after.sh
set -u
R=/c/Projects/gabagool_studios/gabagool_factory
cd "$R" || exit 3
echo "Lot: $(cat lot/VERSION)  LF: $(cat level_factory/VERSION)"
leg() {  # leg <mission> <batch dir>
  local m=$1 b=$2 ws=$R/workspaces/fields-after-$1-ws
  rm -rf "$ws"
  (cd "$R" && python -m level_factory init "$ws" --name "fields after $m" >/dev/null 2>&1) || { echo "$m: init failed"; return; }
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
    if [ $v = before ]; then ws=workspaces/yards-after-$m-ws; else ws=workspaces/fields-after-$m-ws; fi
    for j in $ws/.level_factory/jobs/$m.lot_assemble.candidate.seed_*; do
      seed=${j##*seed_}
      python tools/landuse_census.py "$ws" $m $seed 2>/dev/null | python -c "
import json, sys
d = json.load(sys.stdin)
a = d['areas']
print('%-7s %-16s %s  parking %7.1f m2  yard %5.1f  remainder %.4f (%7.1f m2)  largest piece %7.1f m2' % ('$v', '$m', '$seed', a['parking'], a['yard'], d['shares']['remainder'], a['remainder'], d['remainder_largest_blob']))
" || echo "$v $m $seed: census failed"
      python -c "
import json, sys
g = json.load(open(sys.argv[1], encoding='utf-8'))
fp = g.get('field_plan') or {}
fs = fp.get('placed') or []
print('        fields %d (%s), cars %d; pads %d' % (len(fs), ', '.join('road %d %s %d bays' % (f['road'], f['side'], f['bays']) for f in fs),
      len(fp.get('cars') or []), len((g.get('yard_plan') or {}).get('placed') or [])))
" "$j/out/site.site.gameplay.json"
    done
  done
done
echo "== findings $(date +%T)"
python - <<'PY'
import collections, json
for m in ("gas_block_001", "club_block_014", "crossroads_9600"):
    cs = {}
    for v, ws in (("before", f"workspaces/yards-after-{m}-ws"), ("after", f"workspaces/fields-after-{m}-ws")):
        d = json.load(open(f"{ws}/.level_factory/validation/{m}.json", encoding="utf-8"))
        cs[v] = collections.Counter((i.get("code"), (i.get("candidate_id") or "")[-4:]) for i in d["issues"])
    print(m, sum(cs["before"].values()), "->", sum(cs["after"].values()))
    print("   gained", dict(cs["after"] - cs["before"]))
    print("   lost  ", dict(cs["before"] - cs["after"]))
PY
echo "== done $(date +%T)"
