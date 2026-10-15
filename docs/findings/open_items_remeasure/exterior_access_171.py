"""Roadmap 171 re-measured: how much exterior access the library carries today.

171 (2026-09-23) counted, across 370 specs, 2 specs carrying a `fire_escapes` assembly and 3 ladders with an
exterior placement mode. Deli Counter 0.220.0 added a second way a building stands a fire escape -- a walk-up
Empty's `fire_escape_stack`, a side, Zoo's `fire_escape` a storey at a time, visual only -- so this counts both
ways and the ladders again, over every spec and over the library alone (not Level Factory's lf_ specs). Prints
the counts and the names and stops; whether any of it is an entry route is not something a spec says.

    python docs/findings/open_items_remeasure/exterior_access_171.py
"""
import collections
import glob
import json
import os
import pathlib

SPECS = pathlib.Path(__file__).resolve().parents[3] / "deli_counter" / "specs"


def main():
    files = sorted(glob.glob(str(SPECS / "*.json")))
    for label, keep in (("every spec", lambda n: True), ("the library (not lf_)", lambda n: not n.startswith("lf_"))):
        names = [f for f in files if keep(os.path.basename(f))]
        assemblies, stacks, ext_ladders = [], [], []
        modes = collections.Counter()
        ladders = 0
        for f in names:
            spec = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
            stem = os.path.basename(f)[:-5]
            if spec.get("fire_escapes"):
                assemblies.append("%s (%d)" % (stem, len(spec["fire_escapes"])))
            if spec.get("fire_escape_stack"):
                stacks.append("%s (%s)" % (stem, spec["fire_escape_stack"]))
            for lad in spec.get("ladders") or []:
                ladders += 1
                mode = lad.get("placement_mode") or "(none)"
                modes[mode] += 1
                if mode in ("exterior_wall", "platform"):
                    ext_ladders.append("%s:%s (%s)" % (stem, lad.get("id"), mode))
        print("== %s: %d specs" % (label, len(names)))
        print("  fire_escapes assemblies: %d spec(s): %s" % (len(assemblies), ", ".join(assemblies) or "none"))
        print("  fire_escape_stack sides: %d spec(s): %s" % (len(stacks), ", ".join(stacks) or "none"))
        print("  specs with either: %d" % len({a.split(" ")[0] for a in assemblies} | {s.split(" ")[0] for s in stacks}))
        print("  ladders: %d, by placement_mode %s" % (ladders, dict(sorted(modes.items()))))
        print("  exterior ladders: %d: %s" % (len(ext_ladders), ", ".join(ext_ladders) or "none"))


if __name__ == "__main__":
    main()
