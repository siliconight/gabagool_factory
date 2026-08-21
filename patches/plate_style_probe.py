"""Why is every plate slot style=1? Ask skin_style itself.

floors.py:231/240 and roofs.py:81 DO pass style=skin_style.style_for(...),
so the mechanism is wired. Every plate slot in every shipped manifest is
nevertheless style=1, which means style_for is RETURNING 1 for all of them.

    style_for: surface material -> default material -> 1

So either the spec's `materials` list is empty, or the plate's material is
absent from it and the default_material collapses everything onto the same
index. This runs the real function against the real specs and prints the
answer per material.

Two PowerShell attempts at this question were wrong -- one filtered specs on
a path that does not exist, one gated on a field the specs do not carry, and
BOTH printed a clean "hypothesis is wrong" while having read zero specs. This
one counts what it read and refuses to conclude from nothing.

    python plate_style_probe.py [--root <factory dir>] [--show 12]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys


def find_specs(dc_root):
    """Spec JSONs: carry a `materials` list, are not a derived artefact."""
    skip = (".slots.json", ".manifest.json", ".lights.json", ".navgate.json",
            ".navigation.json", ".gameplay.json", ".combat_audit.json")
    out = []
    for dirpath, dirnames, files in os.walk(dc_root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        for f in files:
            if not f.endswith(".json") or f.endswith(skip):
                continue
            p = os.path.join(dirpath, f)
            try:
                d = json.load(open(p, encoding="utf-8"))
            except Exception:
                continue
            if isinstance(d, dict) and d.get("materials"):
                out.append((p, d))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=r"C:\Projects\gabagool_studios\gabagool_factory")
    ap.add_argument("--show", type=int, default=12)
    a = ap.parse_args()
    dc = os.path.join(os.path.abspath(a.root), "deli_counter")
    sys.path.insert(0, dc)
    import skin_style

    specs = find_specs(dc)
    print("specs carrying a materials list: %d" % len(specs))
    if not specs:
        print("  READ NOTHING -- this proves nothing. Fix the finder.")
        return 1

    # slots by building name, so a spec can be paired with its manifest
    slots = {}
    for dirpath, dirnames, files in os.walk(dc):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        for f in files:
            if f.endswith(".slots.json"):
                slots[f[:-len(".slots.json")]] = os.path.join(dirpath, f)
    print("slots manifests: %d" % len(slots))
    print()

    PLATES = ("floor", "ceiling", "roof")
    shown = 0
    style_hist = collections.Counter()
    unmapped = collections.Counter()
    paired = 0

    for path, spec in sorted(specs):
        name = os.path.basename(path)[:-len(".json")]
        sl = slots.get(name)
        if not sl:
            continue
        paired += 1
        try:
            man = json.load(open(sl, encoding="utf-8"))
        except Exception:
            continue

        ids = [m.get("id", m) if isinstance(m, dict) else m
               for m in spec.get("materials", [])]
        mapping = skin_style.material_styles(ids)
        default = spec.get("default_material")

        mats = sorted({s.get("material") for s in man.get("slots", [])
                       if s.get("role") in PLATES and s.get("material")})
        if not mats:
            continue

        rows = []
        for mat in mats:
            st = skin_style.style_for(mat, mapping, default)
            style_hist[st] += 1
            if mat not in mapping:
                unmapped[mat] += 1
            rows.append((mat, st, "in list" if mat in mapping else "NOT in list"))

        if shown < a.show:
            shown += 1
            print("=== %s" % name)
            print("    spec materials : %s" % ",".join(ids))
            print("    default_material: %r" % default)
            for mat, st, why in rows:
                print("      %-14s -> style %-3d  (%s)" % (mat, st, why))
            styles = {r[1] for r in rows}
            if len(styles) == 1 and len(rows) > 1:
                print("      ^^ %d materials, ONE style -- these stems collide"
                      % len(rows))
            print()

    print("specs paired with a slots manifest: %d" % paired)
    if not paired:
        print("  PAIRED NOTHING -- proves nothing.")
        return 1
    print()
    print("=== style distribution over every (building, plate material)")
    for st, n in sorted(style_hist.items()):
        print("    style %-3d %5d" % (st, n))
    print()
    print("=== plate materials NOT in their spec's materials list")
    if not unmapped:
        print("    none -- every plate material is mapped, so the collapse")
        print("    onto style 1 has some other cause.")
    else:
        for mat, n in unmapped.most_common():
            print("    %-16s %d building(s)" % (mat, n))
        print()
        print("    These fall through to default_material, and if that is")
        print("    also the FIRST entry they land on style 1 alongside it --")
        print("    which is exactly the observed collision.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
