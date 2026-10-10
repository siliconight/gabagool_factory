"""Roadmap 221: read a Patina dressing manifest the way Zoo will, and count what faces where.

    python docs/findings/patina_cover_normals/replay_dressing.py <name>.patina.dressing.json [...]

For every order Zoo builds (`zoo_keeper.core.dressing.plan_dressing`, which also puts each one in
Blender's frame and gives it a side with `cover_side`), and by cover kind:
  - wall-facing orders (a horizontal normal): how many point AWAY from the footprint's centre;
  - how many Zoo files on the side the order stands on (the side its position is nearest,
    measured as `cover_side` measures an up-facing one);
  - how many stand inside the building's outline by more than 0.1 m.
Positions are Blender Z-up metres. It prints what it measured and stops.
"""
import json
import os
import sys
from collections import defaultdict

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "zoo"))
from zoo_keeper.core import dressing, genome  # noqa: E402


def main(paths):
    g = genome.load_species("dress_cover")
    for path in paths:
        manifest = dressing.load_manifest(path)
        plan = dressing.plan_dressing(manifest, g, "delco", "replay")
        plans = plan["plans"]
        box = dressing.footprint([p["order"]["pos"] for p in plans])
        cx, cy, hx, hy = box
        rows = defaultdict(lambda: [0, 0, 0, 0, 0])   # all, wall-facing, outward, on own side, inside
        for p in plans:
            o = p["order"]
            nx, ny, nz = (float(v) for v in o["normal"])
            px, py = float(o["pos"][0]), float(o["pos"][1])
            r = rows[o["cover"]]
            r[0] += 1
            if max(abs(nx), abs(ny)) > 1e-6 and max(abs(nx), abs(ny)) >= abs(nz):
                r[1] += 1
                if nx * (px - cx) + ny * (py - cy) > 0:
                    r[2] += 1
                stands = dressing.cover_side((0.0, 0.0, 1.0), (px, py, 0.0), box)
                if p["side"] == stands:
                    r[3] += 1
                if abs(px - cx) < hx - 0.1 and abs(py - cy) < hy - 0.1:
                    r[4] += 1
        print("%s: %d orders, footprint centre (%.2f, %.2f), half-size %.2f x %.2f"
              % (os.path.basename(path), len(plans), cx, cy, hx, hy))
        print("  %-14s %5s %6s %8s %9s %7s" % ("cover", "all", "walled", "outward", "own side", "inside"))
        for k in sorted(rows):
            a, w, o_, s, i = rows[k]
            print("  %-14s %5d %6d %8d %9d %7d" % (k, a, w, o_, s, i))


if __name__ == "__main__":
    main(sys.argv[1:])
