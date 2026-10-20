"""Deli Counter's circulation gate (`circulation.check_shell`) on two builds of the same specs, side by side.

A probe: prints what it measured and stops. For each spec it reads `build/<spec>.glb`, `.slots.json` and
`.gameplay.json` from each repo, runs that repo's own `check_shell`, and prints both summaries and every conflict the
second has that the first has not. The GLBs are not tracked: build each repo's specs first (`python build.py
specs/<spec>.json` in each).

    python docs/findings/hole_causes_265/circ_ab.py <deli_counter A> <deli_counter B> <spec> [<spec> ...]
"""
import importlib
import json
import os
import sys

a_dir, b_dir, specs = sys.argv[1], sys.argv[2], sys.argv[3:]


def run(repo, name):
    sys.path.insert(0, repo)
    for m in ("circulation", "zfight_gate"):
        sys.modules.pop(m, None)
    circ = importlib.import_module("circulation")
    b = os.path.join(repo, "build")
    slots = json.load(open(os.path.join(b, name + ".slots.json"), encoding="utf-8"))
    gp = json.load(open(os.path.join(b, name + ".gameplay.json"), encoding="utf-8"))
    out = circ.check_shell(os.path.join(b, name + ".glb"), slots, gp)
    sys.path.remove(repo)
    return out


def brief(r):
    return {k: (len(r[k]) if isinstance(r[k], list) else r[k]) for k in sorted(r)}


for s in specs:
    ra, rb = run(os.path.abspath(a_dir), s), run(os.path.abspath(b_dir), s)
    print("==", s)
    print("   A", brief(ra))
    print("   B", brief(rb))
    for k in rb:
        if isinstance(rb[k], list) and rb[k] != ra.get(k):
            for x in [x for x in rb[k] if x not in (ra.get(k) or [])][:8]:
                print("   B+", k, x)
