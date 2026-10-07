"""The largest navmesh islands of a bake_sweep --dump, other than the
spawn's: area, height range, plan extent (level frame), and which building
footprint or Empty each lies over. Measures; names no cause.

    python navmesh_islands.py <sweep_*.json> <staged laser_tag_evaluate dir> [n]
"""
import json
import os
import sys
from collections import defaultdict

ROOT = r"C:\Projects\gabagool_studios\gabagool_factory"
sys.path.insert(0, os.path.join(ROOT, "lot"))
import site_extent  # noqa: E402


def shoelace(pts):
    return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                   for i in range(len(pts)))) / 2.0


def main():
    dump = json.load(open(sys.argv[1], encoding="utf-8"))
    st = sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    b = dump["bakes"][0]
    verts = b["verts"]
    spec = json.load(open(os.path.join(st, "site.site.drawn.json"), encoding="utf-8"))
    rects = [(x.get("archetype"), site_extent.rotated_footprint(x)) for x in spec["buildings"]]
    rects += [("Empty " + str(x.get("id")), site_extent.blocker_rect(x)) for x in spec.get("blockers", [])]
    isl = defaultdict(lambda: {"a": 0.0, "ys": [], "xs": [], "ls": [], "over": defaultdict(float)})
    for k, idx in b["polys_list"]:
        p3 = [verts[i] for i in idx]
        a = shoelace([(q[0], q[2]) for q in p3])
        d = isl[k]
        d["a"] += a
        d["ys"] += [q[1] for q in p3]
        d["xs"] += [q[0] for q in p3]
        d["ls"] += [-q[2] for q in p3]
        cx = sum(q[0] for q in p3) / len(p3)
        cl = -sum(q[2] for q in p3) / len(p3)
        hit = [name for name, r in rects if r and r[0] <= cx <= r[2] and r[1] <= cl <= r[3]]
        d["over"][hit[0] if hit else "open ground"] += a
    for k, d in sorted(isl.items(), key=lambda kv: -kv[1]["a"])[1:n + 1]:
        over = sorted(d["over"].items(), key=lambda kv: -kv[1])[:3]
        print("island %-4s %6.0f m2  height %5.1f..%5.1f m  x %6.1f..%6.1f  y %6.1f..%6.1f  over %s" % (
            k, d["a"], min(d["ys"]), max(d["ys"]), min(d["xs"]), max(d["xs"]), min(d["ls"]), max(d["ls"]),
            [(o, round(a)) for o, a in over]))


if __name__ == "__main__":
    main()
