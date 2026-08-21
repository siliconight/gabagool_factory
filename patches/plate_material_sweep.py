"""Which module stems cover more than one material, and how many files move.

THE DEFECT. `kit.plan_kit` puts `slot_material` in the bucket KEY (kit.py
~306), so two slots with identical geometry and different materials become
TWO distinct modules. `kit.module_stem` does NOT put material in the
filename. Two modules, one name. They build differently -- `dna.resolve_
module_plan` reads `module["material"]` as an override -- so one file wins
and the other zone gets the wrong surface, and with it the wrong collider.

This is the same shape as `_d` for plate depth, `_v` for stairwells, `_o` for
apertures and `_h` for props: the key knows something the filename does not.

Reports only. No Blender, nothing written.

    python plate_material_sweep.py [--root <factory dir>] [--show 20]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

DEFAULT_ROOT = r"C:\Projects\gabagool_studios\gabagool_factory"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--show", type=int, default=20)
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

    collisions = []            # (building, stem, role, [materials])
    by_role = collections.Counter()
    role_totals = collections.Counter()
    buildings = set()
    total_modules = 0
    changed_names = 0          # stems that would gain _m<material>
    with_material = 0

    for path in manifests:
        try:
            man = json.load(open(path, encoding="utf-8"))
            plan = kit.plan_kit(man, theme="delco", style=1)
        except Exception as exc:
            print("  SKIP %s (%s: %s)"
                  % (os.path.basename(path), type(exc).__name__, exc))
            continue
        mods = plan.get("modules", [])
        if not mods:
            continue
        bid = plan.get("building_id") or os.path.basename(path)
        total_modules += len(mods)

        by_stem = collections.defaultdict(set)
        role_of = {}
        for m in mods:
            role_of[m["stem"]] = m.get("type")
            role_totals[m.get("type")] += 1
            mat = m.get("material")
            if mat:
                with_material += 1
                changed_names += 1
            by_stem[m["stem"]].add(mat)

        for stem, mats in sorted(by_stem.items()):
            if len(mats) > 1:
                collisions.append((bid, stem, role_of[stem],
                                   sorted(str(x) for x in mats)))
                by_role[role_of[stem]] += 1
                buildings.add(bid)

    print("distinct modules planned: %d" % total_modules)
    print("modules carrying a slot material: %d" % with_material)
    print()

    print("=== STEMS COVERING MORE THAN ONE MATERIAL")
    print("  buildings affected: %d" % len(buildings))
    print("  colliding stems:    %d" % len(collisions))
    if by_role:
        print("  by role:")
        for role, n in by_role.most_common():
            print("    %-14s %4d   (of %d modules of that role)"
                  % (role, n, role_totals[role]))
    print()
    for bid, stem, role, mats in collisions[:a.show]:
        print("    %-30s %-42s %s" % (bid[:30], stem, " vs ".join(mats)))
    if len(collisions) > a.show:
        print("    ... and %d more" % (len(collisions) - a.show))
    print()

    print("=== IS IT ONLY PLATES?")
    plate = {"floor", "ceiling", "roof"}
    non_plate = sorted({r for r in by_role if r not in plate})
    if non_plate:
        print("  NO -- these non-plate roles collide too: %s" % non_plate)
        print("  The bucket key carries slot_material for EVERY role, so any")
        print("  role with two material zones at one size collides. A fix")
        print("  scoped to plates would leave these.")
    else:
        print("  yes -- only floor/ceiling/roof collide in this data.")
        print("  NOTE that is a property of the DATA, not of the code: the")
        print("  bucket key carries slot_material for every role, so a wall")
        print("  with two material zones at one width would collide too.")
    print()

    print("=== BLAST RADIUS of adding _m<material> to the stem")
    print("  %d module filenames would change (every module whose slot names"
          % changed_names)
    print("  a material). Modules with no slot material keep their name.")
    print("  Both repos construct the stem and NEITHER parses it, so Zoo and")
    print("  Deli Counter must change together -- kit.module_stem and")
    print("  themed_tscn.module_stem.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
