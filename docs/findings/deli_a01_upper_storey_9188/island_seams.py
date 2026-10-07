"""Where two navmesh islands come closest, in a building's own frame, beside
that building's interior doors. Measures; names no cause.

    python island_seams.py <sweep.json> <site.site.drawn.json> <archetype> <islandA> <islandB> <height_m> [band_m]

Polygons of each island whose mean height is within `band_m` (default 0.6)
of `height_m` are compared edge to edge in plan. Prints the closest pairs of
edges (level frame and building frame, which differ by the building's `at`;
rot 0 only, anything else refuses), then every door-like opening on the
matching story with its distance to the closest seam point.
"""
import json
import math
import sys


def seg_seg(a, b, c, d):
    """Plan distance between segments ab and cd, and the midpoint of the closest pair."""
    def pd(p, a, b):
        ax, ay = a
        bx, by = b
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
        q = (ax + t * dx, ay + t * dy)
        return math.hypot(p[0] - q[0], p[1] - q[1]), q
    best = None
    for p, s, e in ((a, c, d), (b, c, d), (c, a, b), (d, a, b)):
        dist, q = pd(p, s, e)
        if best is None or dist < best[0]:
            best = (dist, ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2))
    return best


def main():
    dump = json.load(open(sys.argv[1], encoding="utf-8"))
    spec = json.load(open(sys.argv[2], encoding="utf-8"))
    arch, ia, ib = sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
    hz = float(sys.argv[6])
    band = float(sys.argv[7]) if len(sys.argv) > 7 else 0.6
    bld = [x for x in spec["buildings"] if x.get("archetype") == arch]
    assert len(bld) == 1
    bld = bld[0]
    if float(bld.get("rot", 0) or 0) != 0.0:
        raise SystemExit("rot %s: only rot 0 is handled" % bld.get("rot"))
    ax, ay = bld["at"]
    b = dump["bakes"][0]
    verts = b["verts"]
    edges = {ia: [], ib: []}
    for k, idx in b["polys_list"]:
        if k not in edges:
            continue
        p3 = [verts[i] for i in idx]
        h = sum(q[1] for q in p3) / len(p3)
        if abs(h - hz) > band:
            continue
        pts = [(q[0], -q[2]) for q in p3]
        # only polygons over this building
        cx = sum(p[0] for p in pts) / len(pts) - ax
        cy = sum(p[1] for p in pts) / len(pts) - ay
        fx, fy = bld["_footprint"]
        if abs(cx) > fx / 2 + 1 or abs(cy) > fy / 2 + 1:
            continue
        for i in range(len(pts)):
            edges[k].append((pts[i], pts[(i + 1) % len(pts)]))
    print("edges near h %.2f +- %.2f over %s: island %d %d, island %d %d" % (hz, band, arch, ia, len(edges[ia]), ib, len(edges[ib])))
    if not edges[ia] or not edges[ib]:
        print("one side has no polygons in the band; nothing to compare")
        return
    pairs = []
    for a, b2 in edges[ia]:
        for c, d in edges[ib]:
            dist, mid = seg_seg(a, b2, c, d)
            pairs.append((dist, mid))
    pairs.sort(key=lambda t: t[0])
    seen = []
    print("closest approaches (distinct within 1.5 m):")
    for dist, mid in pairs:
        if any(math.hypot(mid[0] - s[0], mid[1] - s[1]) < 1.5 for s in seen):
            continue
        seen.append(mid)
        print("   %.2f m at level (%.2f, %.2f) = building (%.2f, %.2f)" % (dist, mid[0], mid[1], mid[0] - ax, mid[1] - ay))
        if len(seen) >= 6:
            break
    g = json.load(open(bld["gameplay"], encoding="utf-8"))
    print("door-like openings, building frame, distance to the nearest seam point above:")
    for o in g["openings"]:
        if o["kind"] not in ("door", "breach"):
            continue
        dmin = min(math.hypot(o["x"] - (s[0] - ax), o["y"] - (s[1] - ay)) for s in seen)
        print("   story %2s %-7s %-24s wall %-9s (%6.2f, %6.2f) w %.2f   %.2f m from a seam" % (
            o["story"], o["kind"], o.get("tag"), o["wall"], o["x"], o["y"], o["width"], dmin))


if __name__ == "__main__":
    main()
