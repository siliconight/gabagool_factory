"""Roadmap 178: what Lot's two non-blocking instruments read today, over every cold-run site on disk.

The item (2026-09-24) counted `site_tactical.analyze`'s isolation warning on 65 of 79 site specs and its
`objective_approaches` at 0 on 38, never above 2 -- and said a gate over that graph would be wrong, because
`build_graph` saw declared paths only and not the street the buildings connect along. Lot 0.77.0 joined the
buildings that share a road. This reads the same two fields off every `site.site.gameplay.json` a `lot_assemble`
job wrote under `workspaces/`, and prints the distribution. It reports a measurement and stops.

    python lot_intel_178.py [workspaces_dir]
"""
import collections
import glob
import json
import os
import sys


def main(argv):
    root = argv[1] if len(argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                         "..", "..", "..", "workspaces")
    root = os.path.abspath(root)
    pattern = os.path.join(root, "*", ".level_factory", "jobs", "*lot_assemble*", "1", "out",
                           "site.site.gameplay.json")
    files = sorted(p.replace(os.sep, "/") for p in glob.glob(pattern))
    isolated = collections.Counter()
    approaches = collections.Counter()
    read = 0
    no_intel = 0
    workspaces = set()
    isolated_sites = []
    for f in files:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            no_intel += 1
            continue
        intel = (d.get("tactical") or {}).get("intel") or {}
        if "isolated_buildings" not in intel and "objective_approaches" not in intel:
            no_intel += 1
            continue
        read += 1
        ws = f.split("/workspaces/")[1].split("/")[0]
        workspaces.add(ws)
        k = len(intel.get("isolated_buildings") or [])
        isolated[k] += 1
        if k:
            isolated_sites.append((ws, f.split("/jobs/")[1].split("/")[0], intel["isolated_buildings"]))
        approaches[intel.get("objective_approaches")] += 1
    print(f"workspaces root: {root}")
    print(f"sites read: {read} in {len(workspaces)} workspaces; {no_intel} of {len(files)} files carry no intel")
    print("isolated buildings per site (count -> sites):", sorted(isolated.items()))
    print("objective_approaches (value -> sites):",
          sorted(approaches.items(), key=lambda kv: (kv[0] is None, kv[0] if kv[0] is not None else -1)))
    print(f"sites with an isolated building: {sum(v for k, v in isolated.items() if k)} of {read}")
    for ws, job, ids in isolated_sites[:12]:
        print(f"  {ws}  {job}  {ids}")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
