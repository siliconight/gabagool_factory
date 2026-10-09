#!/usr/bin/env bash
# Cold run 9214 resumed at its export leg after a recorded --retry: the driver's
# own commands from `== export` on (tools/cold_drive/cold_drive.sh), unchanged.
set -u
N=9214; PREV=9203
cd /c/Projects/gabagool_studios/gabagool_factory
WS=workspaces/cold-$N-ws
M=bank_block_001
step() { echo "== $1"; }
die() { echo "STOPPED: $1"; exit 2; }
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
