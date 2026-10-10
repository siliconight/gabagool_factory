#!/usr/bin/env bash
# One cold run, end to end, for a batch already written at docs/cold_runs/cold_N.
# Stops at the first leg that exits non-zero; nothing here edits a tool repo.
#
#   python tools/cold_drive/stage_batch.py <N> <PREV> "<what this run tests>"
#   bash tools/cold_drive/cold_drive.sh <N> <PREV> <mission> <seed|auto> \
#       > docs/cold_runs/cold_<N>/driver.log 2>&1
#
# The export bakes the lights by default since Level Factory 0.144.0;
# EXPORT_FLAGS=--no-bake-lights skips it.
#   python tools/cold_run.py --end
#
# The shape `docs/COMMANDS.md` lists, as one script. It lived in one session's
# scratchpad for cold runs 9134 to 9151 and moved here so a later session can
# run it. `--end` is NOT called here: a stop leaves `_runs/cold/ACTIVE` until
# somebody ends the run on purpose, and the count is read after that.
set -u
N="$1"; PREV="$2"
# The factory is two directories above this script, wherever it was unpacked
# (roadmap 202). It was written in, as /c/Projects/....
cd "$(dirname "$0")/../.." || exit 2
WS=workspaces/cold-$N-ws
M="${3:-club_block_014}"
SEED="${4:-9181}"
step() { echo "== $1"; }
die() { echo "STOPPED: $1"; exit 2; }
step selftest; python tools/cold_run.py --selftest 2>&1 | tail -1 || die selftest
step begin; python tools/cold_run.py --begin cold_$N 2>&1 | tail -2
[ -f _runs/cold/ACTIVE ] || die "no ACTIVE after begin"
# `init` fills tools.local.json from factory.local.json, which `level-factory
# setup` writes once per machine (Level Factory 0.167.0). It used to be copied
# from run PREV's workspace, and cold run 9194 stopped when that workspace had
# been retired. The doctor stops the run here if a tool cannot be reached.
python -m level_factory init "$WS" --name "Cold run $N" >/dev/null 2>&1 || die init
python -m level_factory -C "$WS" doctor > "$WS/doctor.txt" 2>&1 || { tail -5 "$WS/doctor.txt"; die "doctor (run level-factory setup)"; }
# NOT_CONFIGURED passes the doctor (it is information there) and fails a run later.
! grep -q "NOT_CONFIGURED" "$WS/doctor.txt" || { grep "NOT_CONFIGURED" "$WS/doctor.txt"; die "a tool is not configured (run level-factory setup)"; }
step batch; python -m level_factory -C "$WS" batch create docs/cold_runs/cold_$N/batch.json 2>&1 | tail -1
step plan; python -m level_factory -C "$WS" plan $M >/dev/null 2>&1 || die plan
step shell; python -m level_factory -C "$WS" run $M 2>&1 | grep -E "candidates:|blockers open" | tee /tmp/cold_leg.txt; for s_ in "$WS"/.level_factory/jobs/$M.lot_assemble.candidate.seed_*; do echo "  $(basename $s_): $(ls $s_/*/out/buildings/*.glb 2>/dev/null | xargs -n1 basename | tr "
" " ")"; done; echo "  exit ${PIPESTATUS[0]} (non-zero at an approval gate is the pipeline waiting)"; grep -q "blockers open: 0" /tmp/cold_leg.txt || die "shell leg"
if [ "$SEED" = "auto" ]; then
  SEED=$(python tools/cold_drive/pick_candidate.py "$WS" "$M") || die "no candidate could be picked"
  echo "  picked seed_$SEED on the walktest and Laser Tag's route findings"
fi
step approvals
python -m level_factory -C "$WS" approve $M brief_approved >/dev/null || die approve1
python -m level_factory -C "$WS" approve $M candidate_selected --candidate $M.candidate.seed_$SEED >/dev/null || die approve2
python -m level_factory -C "$WS" approve $M functional_shell_locked >/dev/null || die approve3
step art; python -m level_factory -C "$WS" run $M --art --gameplay 2>&1 | tee docs/cold_runs/cold_$N/art.log | grep -E "blockers open" | tee /tmp/cold_leg.txt; echo "  exit ${PIPESTATUS[0]}"; grep -q "blockers open: 0" /tmp/cold_leg.txt || die "art leg"
step export; python -m level_factory -C "$WS" export $M --mode portable-godot ${EXPORT_FLAGS:-} 2>&1 | tee docs/cold_runs/cold_$N/export.log | grep -E "^exported|CLOSURE|light bake|error" | tee /tmp/cold_leg.txt; echo "  exit ${PIPESTATUS[0]}"; grep -q "^exported" /tmp/cold_leg.txt || die export
step findings
python - "$N" "$PREV" "$M" <<'PY'
import collections, json, sys
def codes(n):
    import os
    p = f"workspaces/cold-{n}-ws/.level_factory/validation/{sys.argv[3]}.json"
    if not os.path.exists(p):
        return collections.Counter()
    d = json.load(open(p, encoding="utf-8"))
    out = collections.Counter()
    def walk(o):
        if isinstance(o, dict):
            if "code" in o and isinstance(o["code"], str):
                out[o["code"]] += 1
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(d)
    return out
a, b = codes(sys.argv[2]), codes(sys.argv[1])
print("findings", sum(a.values()), "->", sum(b.values()))
for k in sorted(set(a) | set(b)):
    if a[k] != b[k]:
        print("  ", k, a[k], "->", b[k])
PY
step walk; python tools/walk_export.py "$WS/.level_factory" $M 2>&1 | tail -2
python tools/cold_drive/wire_sky.py _runs/walk_export_$M 2>&1 | tail -1
echo DONE
