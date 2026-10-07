"""Which navmesh island lies on each side of a building's doors, in a
bake_sweep --dump. Measures; names no cause.

    python door_islands.py <sweep.json> <site.site.drawn.json> <archetype> [step_m ...]

FRAMES. The dump's verts are Godot [x, height, z]; the level frame is
(x, y) with y = -z, the frame the site spec's `at` is written in. A
building's gameplay.json opening (x, y) is in the building's own frame,
centred on its footprint; rot 0 places it at at + (x, y). Only rot 0 is
handled, and anything else REFUSES rather than guessing a rotation sense.

For each door-like opening (door, breach) at each step distance either side
of the wall, along the wall's outward normal: the island and polygon whose
plan contains the point, its height there, or -- when no polygon contains
it -- the nearest polygon's island and the plan distance to it.
"""
import json
import math
import sys
from collections import Counter


def point_in(px, py, pts):
    inside = False
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if (y1 > py) != (y2 > py):
            xc = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            if px < xc:
                inside = not inside
    return inside


def seg_dist(px, py, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def main():
    dump = json.load(open(sys.argv[1], encoding="utf-8"))
    spec = json.load(open(sys.argv[2], encoding="utf-8"))
    arch = sys.argv[3]
    steps = [float(s) for s in sys.argv[4:]] or [0.5, 1.5, 3.0]
    b = dump["bakes"][0]
    verts = b["verts"]
    polys = []
    for k, idx in b["polys_list"]:
        p3 = [verts[i] for i in idx]
        polys.append((k, [(q[0], -q[2]) for q in p3], [q[1] for q in p3]))
    area = Counter()
    for k, pts, _h in polys:
        area[k] += abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                           for i in range(len(pts)))) / 2.0
    big = area.most_common(3)
    print("islands by area (level frame m2): %s; home point %s" % (
        ", ".join("%s=%.0f" % kv for kv in big), b.get("points", {}).get("home")))
    bld = [x for x in spec["buildings"] if x.get("archetype") == arch]
    assert len(bld) == 1, "want one %s, got %d" % (arch, len(bld))
    bld = bld[0]
    if float(bld.get("rot", 0) or 0) != 0.0:
        raise SystemExit("rot %s: only rot 0 is handled; refusing to guess" % bld.get("rot"))
    ax, ay = bld["at"]
    g = json.load(open(bld["gameplay"], encoding="utf-8"))
    normals = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}
    for o in g["openings"]:
        if o["kind"] not in ("door", "breach"):
            continue
        side = o["wall"].rsplit("_", 1)[-1]
        if side not in normals:
            print("  %-8s %-6s story %s wall %s: not an exterior side, skipped" % (o["kind"], o.get("tag"), o["story"], o["wall"]))
            continue
        nx, ny = normals[side]
        cx, cy = ax + o["x"], ay + o["y"]
        print("%s %s story %s wall %s at level (%.2f, %.2f), width %.2f, sill %.2f" % (
            o["kind"], o.get("tag"), o["story"], o["wall"], cx, cy, o["width"], o.get("sill", 0)))
        for s in sorted(set([-x for x in steps] + steps)):
            px, py = cx + nx * s, cy + ny * s
            hit = [(k, pts, h) for k, pts, h in polys if point_in(px, py, pts)]
            where = "outside" if s > 0 else "inside "
            if hit:
                desc = "; ".join("island %s h %.2f" % (k, sum(h) / len(h)) for k, pts, h in hit)
                print("   %s %+5.1f m: IN  %s" % (where, s, desc))
            else:
                best = min(((min(seg_dist(px, py, pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))), k, sum(h) / len(h))
                            for k, pts, h in polys), key=lambda t: t[0])
                print("   %s %+5.1f m: no polygon; nearest island %s at %.2f m, h %.2f" % (where, s, best[1], best[0], best[2]))


if __name__ == "__main__":
    main()
