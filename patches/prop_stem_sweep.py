"""What does the 0.90.0 prop-stem change actually rename, and is the new
name unique? Measured over every slots.json in the factory. No Blender.

WHY THIS RUNS BEFORE ANY REBUILD. `kit.module_stem` used to identify a prop
by WIDTH alone. A prop is free on all three axes, so two solids of different
depth or height collapsed onto one filename and the second silently reused
the first one's geometry. 0.39.0/0.90.0 added `_d<cm>` and `_h<cm>`.

That fix was verified as 9,185/9,185 slots agreeing across the Zoo and Deli
Counter mirrors -- which proves the two tools AGREE, not that the resulting
name is UNIQUE. Those are different claims. This measures the second one:
for every building, whether two prop slots with different dims still land on
the same stem.

    python prop_stem_sweep.py [--root <factory dir>]

Exit 0 always -- this reports, it does not gate.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

DEFAULT_ROOT = r"C:\Projects\gabagool_studios\gabagool_factory"
# prop_<theme>_<style>[_w..][_d..][_h..] -- the OLD form carries no _d/_h
OLD_FORM = re.compile(r"^prop_.+_\d{2}_w\d+$")
NEW_FORM = re.compile(r"^prop_.+_\d{2}_w\d+_d\d+_h\d+")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--show", type=int, default=12)
    a = ap.parse_args()
    root = os.path.abspath(a.root)

    sys.path.insert(0, os.path.join(root, "zoo"))
    from zoo_keeper.core import kit

    manifests = []
    for dirpath, dirnames, files in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        for f in files:
            if f.endswith(".slots.json"):
                manifests.append(os.path.join(dirpath, f))
    manifests.sort()
    print("slots.json found: %d" % len(manifests))

    n_with_props = 0
    total_prop_slots = 0
    total_new_modules = 0
    old_collisions = []          # (building, stem, [dims...]) under width-only
    new_collisions = []          # (building, stem, [dims...]) under w+d+h
    per_building = []

    for path in manifests:
        try:
            man = json.load(open(path, encoding="utf-8"))
        except Exception as exc:
            print("  UNREADABLE %s (%s)" % (os.path.basename(path), exc))
            continue
        try:
            plan = kit.plan_kit(man, theme="delco", style=1, roles={"prop"})
        except Exception as exc:
            print("  PLAN FAILED %s (%s: %s)"
                  % (os.path.basename(path), type(exc).__name__, exc))
            continue

        mods = plan.get("modules", [])
        if not mods:
            continue
        n_with_props += 1
        bid = plan.get("building_id") or os.path.basename(path)
        slots = sum(m.get("count", 1) for m in mods)
        total_prop_slots += slots
        total_new_modules += len(mods)

        # NEW scheme: does any stem cover two different dim triples?
        by_new = collections.defaultdict(set)
        # OLD scheme: width alone. Reconstruct it from dims, not from a
        # remembered string, so this does not depend on old code being present.
        by_old = collections.defaultdict(set)
        for m in mods:
            d = m.get("dims") or []
            if len(d) < 3:
                continue
            trip = tuple(round(float(x), 4) for x in d[:3])
            by_new[m["stem"]].add(trip)
            by_old[int(round(d[0] * 100))].add(trip)

        for stem, trips in sorted(by_new.items()):
            if len(trips) > 1:
                new_collisions.append((bid, stem, sorted(trips)))
        for w, trips in sorted(by_old.items()):
            if len(trips) > 1:
                old_collisions.append((bid, "w%d" % w, sorted(trips)))

        per_building.append((bid, len(mods), slots,
                             sum(1 for _, t in by_old.items() if len(t) > 1)))

    print("buildings with prop slots: %d" % n_with_props)
    print("distinct prop modules planned (new scheme): %d" % total_new_modules)
    print("prop slots they dress: %d" % total_prop_slots)
    print()

    print("=== WOULD THE OLD WIDTH-ONLY NAME HAVE COLLIDED?")
    print("  buildings affected: %d"
          % len({b for b, _, _ in old_collisions}))
    print("  colliding names:    %d" % len(old_collisions))
    for bid, w, trips in old_collisions[:a.show]:
        print("    %-34s %-8s %s" % (bid, w,
              " vs ".join("x".join("%.2f" % v for v in t) for t in trips)))
    if len(old_collisions) > a.show:
        print("    ... and %d more" % (len(old_collisions) - a.show))
    print()

    print("=== IS THE NEW NAME UNIQUE? (the claim the 9,185/9,185 check did NOT make)")
    if not new_collisions:
        print("  YES -- no stem covers two different dim triples, in any building.")
    else:
        print("  NO -- %d stem(s) still cover more than one solid:" % len(new_collisions))
        for bid, stem, trips in new_collisions[:a.show]:
            print("    %-34s %-30s %s" % (bid, stem,
                  " vs ".join("x".join("%.2f" % v for v in t) for t in trips)))
    print()

    print("=== PROP GLBs ON DISK")
    old, new, other = [], [], []
    for dirpath, dirnames, files in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        for f in files:
            if f.startswith("prop_") and f.endswith(".glb"):
                stem = f[:-4]
                (old if OLD_FORM.match(stem) else
                 new if NEW_FORM.match(stem) else other).append(
                     os.path.relpath(os.path.join(dirpath, f), root))
    print("  old-form (width only, STALE): %d" % len(old))
    print("  new-form (w+d+h):             %d" % len(new))
    print("  neither:                      %d" % len(other))
    for p in old[:5]:
        print("    stale  " + p)
    for p in other[:5]:
        print("    ?      " + p)
    print()
    print("Every old-form file is unreachable by the current resolver: it asks")
    print("for a stem carrying _d and _h, and these carry neither. They are not")
    print("wrong geometry, they are unaddressable geometry.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
