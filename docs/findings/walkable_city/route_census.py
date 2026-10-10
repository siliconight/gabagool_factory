"""Route census of drawn sites (roadmap 199): the road graph, its approaches and loops, the hub's place.

    python docs/findings/walkable_city/route_census.py <site.site.drawn.json> [...]
    python docs/findings/walkable_city/route_census.py --cold        # every cold workspace's themed spec

For each spec: the plate; the roads (count, total length); the junctions between them, a road
ending on another being a T and a road crossing another an X; the road ends that reach the
plate's edge (the approaches a player, a responder or a getaway can use); the cycles in the road
graph (a loop a route can go round: edges - nodes + components); the buildings, the objective and
the distance from its position to the nearest junction (the brief's hub is central in movement,
not geometry; the junction is where movement meets); the paths (building-to-building walks); and
what explains the edge (fenced runs, backdrop pieces). It prints a row a spec and stops; whether
a layout is good is the brief's question (`docs/reference/DYNAMIC_WALKABLE_CITY_LEVEL_DESIGN_BRIEF.md`),
answered in the README beside this.
"""
import glob
import json
import math
import sys
from pathlib import Path

FACTORY = Path(__file__).resolve().parents[3]


def _seg_hit(r, s):
    """Where road r meets road s, for axis-aligned roads: the point, and whether it lies at an
    end of r / of s (within half a width), else None."""
    (ax, ay), (bx, by) = r["a"], r["b"]
    (cx, cy), (dx, dy) = s["a"], s["b"]
    rw, sw = float(r.get("width", 10.0)) / 2.0, float(s.get("width", 10.0)) / 2.0
    r_h, s_h = abs(by - ay) < 1e-6, abs(dy - cy) < 1e-6
    if r_h == s_h:
        return None                     # parallel; a shared end would be a corner, not seen here
    if r_h:
        px, py = cx, ay
        if not (min(ax, bx) - rw <= px <= max(ax, bx) + rw and min(cy, dy) - sw <= py <= max(cy, dy) + sw):
            return None
    else:
        px, py = ax, cy
        if not (min(ay, by) - rw <= py <= max(ay, by) + rw and min(cx, dx) - sw <= px <= max(cx, dx) + sw):
            return None
    r_end = min(math.hypot(px - ax, py - ay), math.hypot(px - bx, py - by)) <= rw + sw
    s_end = min(math.hypot(px - cx, py - cy), math.hypot(px - dx, py - dy)) <= rw + sw
    return (px, py), r_end, s_end


def census(d):
    g = d.get("ground") or {}
    sx, sy = float(g.get("size_x", 0)), float(g.get("size_y", 0))
    roads = d.get("roads") or []
    length = sum(math.hypot(r["b"][0] - r["a"][0], r["b"][1] - r["a"][1]) for r in roads)
    junctions, kinds = [], []
    for i, r in enumerate(roads):
        for j, s in enumerate(roads):
            if j <= i:
                continue
            hit = _seg_hit(r, s)
            if hit is None:
                continue
            p, r_end, s_end = hit
            junctions.append(p)
            kinds.append("T" if (r_end or s_end) else "X")
    # approaches: road ends within a width of the plate's edge
    approaches = []
    for i, r in enumerate(roads):
        w = float(r.get("width", 10.0))
        for end in (r["a"], r["b"]):
            ex, ey = end
            if abs(ex + sx / 2) <= w or abs(ex - sx / 2) <= w or abs(ey + sy / 2) <= w or abs(ey - sy / 2) <= w:
                approaches.append((round(ex, 1), round(ey, 1)))
    # the road graph: nodes are road ends and junctions, edges the pieces between them
    nodes = {}
    def node(p):
        key = (round(p[0], 2), round(p[1], 2))
        return nodes.setdefault(key, len(nodes))
    edges = 0
    for r in roads:
        pts = [tuple(r["a"]), tuple(r["b"])] + [p for p in junctions if _on(r, p)]
        along = sorted(set((round(p[0], 2), round(p[1], 2)) for p in pts))
        for p in along:
            node(p)
        edges += max(0, len(along) - 1)
    # components by union-find over the edges
    parent = list(range(len(nodes)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for r in roads:
        pts = [tuple(r["a"]), tuple(r["b"])] + [p for p in junctions if _on(r, p)]
        along = sorted(set((round(p[0], 2), round(p[1], 2)) for p in pts))
        for p, q in zip(along, along[1:]):
            a, b = find(node(p)), find(node(q))
            if a != b:
                parent[a] = b
    comps = len({find(i) for i in range(len(nodes))}) if nodes else 0
    cycles = edges - len(nodes) + comps
    buildings = d.get("buildings") or []
    objective = d.get("objective")
    hub = next((b for b in buildings if b.get("id") == objective), None)
    hub_at = None
    if hub is not None:
        at = hub.get("at")
        if isinstance(at, dict):
            hub_at = (float(at.get("x", 0)), float(at.get("y", 0)))
        elif isinstance(at, (list, tuple)) and len(at) >= 2:
            hub_at = (float(at[0]), float(at[1]))
    hub_to_junction = (min(math.hypot(hub_at[0] - p[0], hub_at[1] - p[1]) for p in junctions)
                       if hub_at and junctions else None)
    paths = d.get("paths") or []
    return {
        "name": d.get("name") or d.get("site_id"),
        "plate": (sx, sy),
        "shape": (d.get("site_shape_resolved") or {}).get("got", d.get("site_shape")),
        "grammar": (d.get("road_grammar_resolved") or {}).get("got", d.get("road_grammar")),
        "route_shape": d.get("route_shape"),
        "roads": len(roads), "road_m": round(length, 1),
        "junctions": "".join(sorted(kinds)) or "-",
        "approaches": len(approaches), "approach_pts": approaches,
        "cycles": cycles,
        "buildings": len(buildings), "objective": objective,
        "hub_to_junction_m": None if hub_to_junction is None else round(hub_to_junction, 1),
        "paths": len(paths), "paths_drawn": sum(1 for p in paths if p.get("drawn")),
        "driveways": len(d.get("driveways") or []),
        "fenced_runs": (d.get("perimeter") or {}).get("fenced_runs"),
        "backdrop": len(d.get("backdrop") or []),
        "surroundings": d.get("surroundings"),
    }


def _on(r, p):
    (ax, ay), (bx, by) = r["a"], r["b"]
    w = float(r.get("width", 10.0)) / 2.0
    return (min(ax, bx) - w <= p[0] <= max(ax, bx) + w) and (min(ay, by) - w <= p[1] <= max(ay, by) + w) \
        and (abs(by - ay) < 1e-6 and abs(p[1] - ay) <= w or abs(bx - ax) < 1e-6 and abs(p[0] - ax) <= w)


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    if argv == ["--cold"]:
        files = sorted(glob.glob(str(FACTORY / "workspaces" / "cold-*-ws" / ".level_factory" / "jobs"
                                     / "*.themed_site_assemble" / "1" / "out" / "site.site.drawn.json")))
        labels = [Path(f).parts[-7] for f in files]
    else:
        files, labels = argv, argv
    cols = ("plate", "shape", "grammar", "route_shape", "roads", "road_m", "junctions", "approaches",
            "cycles", "buildings", "objective", "hub_to_junction_m", "paths", "paths_drawn", "driveways",
            "fenced_runs", "backdrop", "surroundings")
    print("workspace | " + " | ".join(cols))
    for label, f in zip(labels, files):
        c = census(json.load(open(f, encoding="utf-8")))
        print(label + " | " + " | ".join(str(c[k]) for k in cols))


if __name__ == "__main__":
    main(sys.argv[1:])
