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
# Each step's line carries the clock time it began, and DONE the time the drive ended,
# so a run's record says where its minutes went: the legs had no time of their own
# anywhere (the journal holds the start, the index the jobs, not the legs).
step() { echo "== $1 ($(date +%H:%M:%S))"; }
die() { echo "STOPPED: $1"; exit 2; }
# PROFILE_LEGS=1 runs the shell, art and export legs under cProfile and keeps each
# profile beside the run's journal (_runs/cold/cold_N/<leg>.prof, not in the record).
# A leg's in-process time is covered by no job's `duration=`: cold run 9248's
# presentation_compose took 63.7 s of which its command was 1.6 s, and only a
# profile says where the rest went. Off, the legs run exactly as before.
# (`profile_leg.py`, not `python -m cProfile`, which swallows the leg's exit code:
# 9250's art leg printed exit 0 where it exits 1 at the approval gate.)
lf() { if [ -n "${PROFILE_LEGS:-}" ]; then python tools/cold_drive/profile_leg.py "_runs/cold/cold_$N/$1.prof" "${@:2}"; else python -m level_factory "${@:2}"; fi; }
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
step shell; lf shell -C "$WS" run $M 2>&1 | grep -E "candidates:|blockers open" | tee /tmp/cold_leg.txt; for s_ in "$WS"/.level_factory/jobs/$M.lot_assemble.candidate.seed_*; do echo "  $(basename $s_): $(ls $s_/*/out/buildings/*.glb 2>/dev/null | xargs -n1 basename | tr "
" " ")"; done; echo "  exit ${PIPESTATUS[0]} (non-zero at an approval gate is the pipeline waiting)"; grep -q "blockers open: 0" /tmp/cold_leg.txt || die "shell leg"
if [ "$SEED" = "auto" ]; then
  SEED=$(python tools/cold_drive/pick_candidate.py "$WS" "$M") || die "no candidate could be picked"
  echo "  picked seed_$SEED on the walktest and Laser Tag's route findings"
fi
# THE SEED NAMES ONE OF THIS BATCH'S CANDIDATES, or the run stops here and says so. Cold run 9362 named seed 9281
# against a batch whose seed_base was 9054 (candidates 9054, 9155, 9256): Level Factory's `approve candidate_selected`
# took a candidate no job had built, and the functional lock refused it a step later as "THIS LOCK PROTECTS NOTHING"
# -- true, and no help. Name a seed the batch builds: set batch.json's seed_base to it.
ls -d "$WS"/.level_factory/jobs/$M.*.candidate.seed_$SEED >/dev/null 2>&1 || die "seed_$SEED is not one of this batch's candidates ($(ls -d "$WS"/.level_factory/jobs/$M.*.candidate.seed_* 2>/dev/null | sed 's/.*seed_//' | sort -u | tr '\n' ' ')) -- set batch.json's seed_base to it"
step approvals
python -m level_factory -C "$WS" approve $M brief_approved >/dev/null || die approve1
python -m level_factory -C "$WS" approve $M candidate_selected --candidate $M.candidate.seed_$SEED >/dev/null || die approve2
python -m level_factory -C "$WS" approve $M functional_shell_locked >/dev/null || die approve3
step art; lf art -C "$WS" run $M --art --gameplay 2>&1 | tee docs/cold_runs/cold_$N/art.log | grep -E "blockers open" | tee /tmp/cold_leg.txt; echo "  exit ${PIPESTATUS[0]}"; grep -q "blockers open: 0" /tmp/cold_leg.txt || die "art leg"
step export; lf export -C "$WS" export $M --mode portable-godot ${EXPORT_FLAGS:-} 2>&1 | tee docs/cold_runs/cold_$N/export.log | grep -E "^exported|CLOSURE|light bake|error" | tee /tmp/cold_leg.txt; echo "  exit ${PIPESTATUS[0]}"; grep -q "^exported" /tmp/cold_leg.txt || die export
# A package asked to bake that ships unbaked STOPS the run (cold run 9242: the export
# warned, the drive went on, and the run counted zero). The bake's own report decides.
if [[ "${EXPORT_FLAGS:-}" != *--no-bake-lights* ]]; then
  python -c "import json,sys; sys.exit(0 if json.load(open(sys.argv[1], encoding='utf-8')).get('ok') else 1)" \
    "$WS/.level_factory/exports/LF_$M.portable-godot/light_bake.json" 2>/dev/null \
    || die "light bake: the package ships unbaked (light_bake.json ok is not true)"
fi
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
# THE LIGHT CHECK (2026-10-23, the walker's walk of cold run 9383): every room and every opening's landing, under the
# level's own preset, held to its floor (`tools/light_check.py`). It failed three rooms of 9383 that nobody had run it
# on. Its frames stay in the run's scratch, its verdict goes in the record, and a FAIL is reported, not a stop.
step light; python tools/light_check.py _runs/walk_export_$M --slots own --out _runs/cold/cold_$N/light_check \
    > _runs/cold/cold_$N/light_check.log 2>&1
echo "light check exit $? -- $(grep -m1 -E '^  (FAIL|PASS|WARN|EXEMPT|REPORT) ' _runs/cold/cold_$N/light_check/light_check.txt 2>/dev/null || echo 'no verdict written')"
cp _runs/cold/cold_$N/light_check/light_check.txt docs/cold_runs/cold_$N/light_check.txt 2>/dev/null || true
# THE PACKAGE CLEAN JOB (2026-10-11): what a pushed record makes regenerable goes --
# workspaces beyond the newest four, release and test zips, test unpacks. This run's
# own workspace stays: its record is not pushed yet. Never fatal to the run.
# --pushed-only (2026-10-19, the walker): a pushed run's workspace goes even when a
# record names it -- the disk filled on 2026-10-16 with 67 of them kept that way.
step retire; python tools/factory_retire.py --apply --pushed-only 2>&1 | tail -1 || true
echo "DONE ($(date +%H:%M:%S))"
