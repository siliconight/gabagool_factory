#!/usr/bin/env bash
# One building line a street, measured: each brief's shell leg built in fresh
# workspaces by Level Factory 0.134.0 (a git worktree at its commit) and by
# 0.135.0, every other tool the same (Lot 0.96.0, Zoo 1.59.0, Patina 0.23.0,
# Laser Tag 0.23.2), then the land-use census on every candidate and the
# findings diffed. Writes nothing to a tool repo.
#   bash before_after.sh
set -u
R=/c/Projects/gabagool_studios/gabagool_factory
OLD=$R/_runs/lf_0134
cd "$R" || exit 3
if [ ! -d "$OLD/level_factory" ]; then
  mkdir -p "$OLD"
  git -C level_factory worktree add "$OLD/level_factory" 70dcdf0 >/dev/null 2>&1 || { echo "no worktree"; exit 4; }
fi
echo "old LF: $(cat $OLD/level_factory/VERSION)  new LF: $(cat level_factory/VERSION)"
leg() {  # leg <variant> <mission> <batch dir> <lf parent dir>
  local v=$1 m=$2 b=$3 lfp=$4 ws=$R/workspaces/line-$1-$2-ws
  rm -rf "$ws"
  (cd "$lfp" && python -m level_factory init "$ws" --name "line $v $m" >/dev/null 2>&1) || { echo "$v $m: init failed"; return; }
  cp "$R/workspaces/cold-9144-ws/tools.local.json" "$ws/tools.local.json"
  (cd "$lfp" && python -m level_factory -C "$ws" batch create "$R/$b/batch.json" 2>&1 | tail -1)
  (cd "$lfp" && python -m level_factory -C "$ws" plan $m >/dev/null 2>&1) || { echo "$v $m: plan failed"; return; }
  (cd "$lfp" && python -m level_factory -C "$ws" run $m 2>&1 | grep -E "candidates:|blockers open|Error|refus" | sed "s/^/  $v $m: /")
}
for spec in "gas_block_001 docs/cold_runs/cold_9144" "club_block_014 docs/cold_runs/cold_9134" "crossroads_9600 docs/experiments/crossroads_9600"; do
  m=${spec%% *}; b=${spec#* }
  echo "== $m $(date +%T)"
  leg before $m $b "$OLD" &
  leg after $m $b "$R" &
  wait
done
echo "== census $(date +%T)"
for v in before after; do
  for m in gas_block_001 club_block_014 crossroads_9600; do
    ws=workspaces/line-$v-$m-ws
    for j in $ws/.level_factory/jobs/$m.lot_assemble.candidate.seed_*; do
      seed=${j##*seed_}
      python tools/landuse_census.py "$ws" $m $seed 2>/dev/null | python -c "
import json, sys
d = json.load(sys.stdin)
fr = [f for r in d['roads'] for f in r['fronting']]
through = d['roads'][0]
print('%-7s %-16s %s  through-road line spread %5.1f m (%d fronting)  door-to-road %d/%d  remainder %.3f  parking %6.1f' % (
    '$v', '$m', '$seed', through['setback_spread'], len(through['fronting']),
    sum(1 for f in fr if f['door_faces_road']), len(fr), d['shares']['remainder'], d['areas'].get('parking', 0.0)))
" || echo "$v $m $seed: census failed"
    done
  done
done
echo "== findings $(date +%T)"
python - <<'PY'
import collections, json
for m in ("gas_block_001", "club_block_014", "crossroads_9600"):
    cs = {}
    for v in ("before", "after"):
        d = json.load(open(f"workspaces/line-{v}-{m}-ws/.level_factory/validation/{m}.json", encoding="utf-8"))
        cs[v] = collections.Counter((i.get("code"), (i.get("candidate_id") or "")[-4:]) for i in d["issues"])
    print(m, sum(cs["before"].values()), "->", sum(cs["after"].values()))
    print("   gained", dict(sorted((cs["after"] - cs["before"]).items())))
    print("   lost  ", dict(sorted((cs["before"] - cs["after"]).items())))
PY
echo "== done $(date +%T)"
