"""Dress every shell in a Deli Counter build folder with two Patina checkouts and compare the dressing orders.
Prints per shell the cover counts that differ (A -> B) and a total; shells whose orders are identical print nothing.
Measures only.

    python docs/findings/parapet_flush/plane_census.py <dc build dir> <patina A> <patina B> [limit]
"""
import collections
import glob
import json
import os
import subprocess
import sys
import tempfile

PY = r"C:\Projects\gabagool_studios\gabagool_factory\.venv\Scripts\python.exe"
build, pa, pb = (os.path.abspath(a) for a in sys.argv[1:4])
limit = int(sys.argv[4]) if len(sys.argv) > 4 else None
shells = sorted(p for p in glob.glob(os.path.join(build, "*.glb")) if os.path.exists(p[:-4] + ".slots.json"))
if limit:
    shells = shells[:limit]


def orders(patina, glb, tmp):
    out = os.path.join(tmp, os.path.basename(glb)[:-4] + ".patina.glb")
    r = subprocess.run([PY, "-m", "patina.cli", glb, "--mode", "vertex-color", "--out", out, "--theme", "default",
                        "--dressing", "--anchors", "--gutters"], cwd=patina, capture_output=True, text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    if r.returncode != 0:
        print("  %s: %s" % (os.path.basename(glb), (r.stderr or r.stdout).strip()[-300:]))
        return None
    d = json.load(open(out[:-4] + ".dressing.json", encoding="utf-8"))
    return [json.dumps({k: o[k] for k in ("cover", "pos", "normal", "size") if k in o}, sort_keys=True)
            for o in d["orders"]], d.get("counts", {})


changed = same = failed = 0
for glb in shells:
    with tempfile.TemporaryDirectory() as ta, tempfile.TemporaryDirectory() as tb:
        a, b = orders(pa, glb, ta), orders(pb, glb, tb)
    name = os.path.basename(glb)[:-4]
    if a is None or b is None:
        failed += 1
        print(name, "FAILED", "A" if a is None else "", "B" if b is None else "")
        continue
    if sorted(a[0]) == sorted(b[0]):
        same += 1
        continue
    changed += 1
    kinds = sorted(set(a[1]) | set(b[1]))
    diff = {k: (a[1].get(k, 0), b[1].get(k, 0)) for k in kinds if a[1].get(k, 0) != b[1].get(k, 0)}
    moved = len(collections.Counter(a[0]) - collections.Counter(b[0]))
    print(name, "orders", len(a[0]), "->", len(b[0]), "differing", moved, diff)
print("shells", len(shells), "identical", same, "changed", changed, "failed", failed)
