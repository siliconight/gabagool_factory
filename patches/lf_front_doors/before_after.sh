#!/usr/bin/env bash
# Doors to the street, measured: each brief's shell leg built twice in fresh
# workspaces, once by Level Factory 0.131.0 (a git worktree at fa3968e) and
# once by 0.132.0, every other tool the same, then the land-use census on
# every candidate. Writes nothing to a tool repo.
#   bash before_after.sh
set -u
R=/c/Projects/gabagool_studios/gabagool_factory
OLD=$R/_runs/lf_0131
cd "$R" || exit 3
if [ ! -d "$OLD/level_factory" ]; then
  mkdir -p "$OLD"
  git -C level_factory worktree add "$OLD/level_factory" fa3968e >/dev/null 2>&1 || { echo "no worktree"; exit 4; }
fi
echo "old LF: $(cat $OLD/level_factory/VERSION)  new LF: $(cat level_factory/VERSION)"
leg() {  # leg <variant> <mission> <batch dir> <lf parent dir>
  local v=$1 m=$2 b=$3 lfp=$4 ws=$R/workspaces/fronts-$1-$2-ws
  rm -rf "$ws"
  (cd "$lfp" && python -m level_factory init "$ws" --name "fronts $v $m" >/dev/null 2>&1) || { echo "$v $m: init failed"; return; }
  cp "$R/workspaces/cold-9140-ws/tools.local.json" "$ws/tools.local.json"
  (cd "$lfp" && python -m level_factory -C "$ws" batch create "$R/$b/batch.json" 2>&1 | tail -1)
  (cd "$lfp" && python -m level_factory -C "$ws" plan $m >/dev/null 2>&1) || { echo "$v $m: plan failed"; return; }
  (cd "$lfp" && python -m level_factory -C "$ws" run $m 2>&1 | grep -E "candidates:|blockers open" | sed "s/^/  $v $m: /")
}
for spec in "gas_block_001 docs/cold_runs/cold_9140" "club_block_014 docs/cold_runs/cold_9134" "crossroads_9600 docs/experiments/crossroads_9600"; do
  m=${spec%% *}; b=${spec#* }
  echo "== $m $(date +%T)"
  leg before $m $b "$OLD" &
  leg after $m $b "$R" &
  wait
done
echo "== census $(date +%T)"
for v in before after; do
  for m in gas_block_001 club_block_014 crossroads_9600; do
    ws=workspaces/fronts-$v-$m-ws
    for j in $ws/.level_factory/jobs/$m.lot_assemble.candidate.seed_*; do
      seed=${j##*seed_}
      python tools/landuse_census.py "$ws" $m $seed 2>/dev/null | python -c "
import json, sys
d = json.load(sys.stdin)
fr = [f for r in d['roads'] for f in r['fronting']]
sp = [r['setback_spread'] for r in d['roads'] if len(r['fronting']) > 1]
print('%-7s %-16s %s  door-to-road %d/%d  remainder %.2f  line spread %.1f' % ('$v', '$m', '$seed', sum(1 for f in fr if f['door_faces_road']), len(fr), d['shares']['remainder'], max(sp) if sp else 0.0))
" || echo "$v $m $seed: census failed"
      grep -c "LOT_PATH_END_OFF_DOOR" $j/*/out/*.json 2>/dev/null | awk -F: '{s+=$2} END {print "        walks to a doorless wall (findings in the job out): " s}'
    done
  done
done
echo "== done $(date +%T)"
