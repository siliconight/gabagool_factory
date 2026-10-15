"""Roadmap 173: sort every drop edge `tools/walkable_edge.gd` reports on a package into what it stands beside.

The rule the item wants -- every drop edge is either GUARDED, or DECLARED as a one-way reachability, or a
defect -- needs the declared and the architectural ones named before anything can refuse the rest. This reads
the instrument's JSON (`edges[]`: x, y, z in Godot metres, `drop_m`, `indoors`) and the package's own records,
and puts each edge in the first class that claims it:

    site_edge    nothing below at all (`drop_m` >= 1e8): the plate's edge, the playable boundary
    stair        inside a mission building's stair footprint (gameplay `stair_systems[].footprint_polygon`,
                 in the building's frame, carried to the world by the site's transform), plus MARGIN -- the open
                 side of a flight, which the contract calls architecture
    hatch        within HATCH_R of a `hatch` or `ladder` marker of a mission building: the ladder's own hole
    floor_hole   within HATCH_R of a `floor_hole` / `hatch` vertical link at its storey: a drop the spec declared
    roof_rim     on a building's roof level, within RIM of its footprint's edge: a parapet's job, or its absence
    storey_rim   at a storey level inside a footprint, not a stair: a mezzanine lip, a cut slab's collar -- the
                 class the item was filed on
    prop_top     outside every footprint, above the ground by more than a kerb: standing on a car, a dumpster,
                 a bench, a stoop; the drop is the thing's own height
    ground       outside every footprint at ground level: a kerb band, a yard wall, a dock
    other        none of the above

Buildings come from the package's `site.tscn` (ext_resource lot ids and the `b<n>` transforms) and their
records from Deli Counter's library (`build/<id>.gameplay.json`, `specs/<id>.json`). The frame: a building's
spec (x, y, z up) stands in Godot as (x, z, -y) at the site node's origin, unrotated on this site (the basis is
checked and refused otherwise). Prints the sort and the rows of the classes that matter, and stops.

    python sort_edges.py <edges.json> <package_dir>
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FACTORY = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
DC = os.path.join(FACTORY, "deli_counter")

MARGIN = 0.6        # m; a stair footprint claims this far around itself (the walk-off past a landing)
HATCH_R = 1.6       # m; a hatch hole is 1.5 m square: its edge plus a cell
RIM = 1.0           # m; a roof or storey rim is this close to the footprint's edge
LEVEL_TOL = 0.35    # m; a surface this close to a storey level is that storey
KERB = 0.3          # m; above this the ground is a thing a body stood on
WALL_LINE = 0.3     # m; a cell this close to a footprint's edge sits on the exterior wall's own line


def _buildings(pkg):
    text = open(os.path.join(pkg, "site.tscn"), encoding="utf-8").read()
    ext = dict(re.findall(r'\[ext_resource type="PackedScene" path="lot/([A-Za-z0-9_]+)/site\.tscn" id="([^"]+)"\]',
                          text))
    ext = {v: k for k, v in ext.items()}           # id -> lot id
    out = []
    for m in re.finditer(r'\[node name="(b\d+)" parent="\." instance=ExtResource\("([^"]+)"\)\]\s*\ntransform = '
                         r'Transform3D\(([^)]+)\)', text):
        vals = [float(v) for v in m.group(3).split(",")]
        basis = vals[:9]
        if any(abs(a - b) > 1e-6 for a, b in zip(basis, [1, 0, 0, 0, 1, 0, 0, 0, 1])):
            raise SystemExit(f"{m.group(1)} is rotated ({basis}); this sorter assumes an unrotated site")
        out.append({"node": m.group(1), "id": ext[m.group(2)], "origin": vals[9:12]})
    return out


def _record(bid):
    gp = os.path.join(DC, "build", f"{bid}.gameplay.json")
    sp = os.path.join(DC, "specs", f"{bid}.json")
    g = json.load(open(gp, encoding="utf-8")) if os.path.exists(gp) else {}
    s = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else {}
    return g, s


def _inside(px, pz, poly):
    """Point in polygon (ray cast), polygon in world (x, z)."""
    inside = False
    n = len(poly)
    for i in range(n):
        x0, z0 = poly[i]
        x1, z1 = poly[(i + 1) % n]
        if (z0 > pz) != (z1 > pz):
            xi = x0 + (pz - z0) * (x1 - x0) / (z1 - z0)
            if px < xi:
                inside = not inside
    return inside


def _dist_to_rect_edge(px, pz, rect):
    x0, z0, x1, z1 = rect
    if x0 <= px <= x1 and z0 <= pz <= z1:
        return min(px - x0, x1 - px, pz - z0, z1 - pz)
    dx = max(x0 - px, 0.0, px - x1)
    dz = max(z0 - pz, 0.0, pz - z1)
    return -((dx * dx + dz * dz) ** 0.5)


def _grow(poly, m):
    """Expand a convex-ish polygon by m along the axes (rects in practice)."""
    xs = [p[0] for p in poly]
    zs = [p[1] for p in poly]
    return [(min(xs) - m, min(zs) - m), (max(xs) + m, min(zs) - m), (max(xs) + m, max(zs) + m),
            (min(xs) - m, max(zs) + m)]


def main(argv):
    edges_path, pkg = argv[1], argv[2]
    rep = json.load(open(edges_path, encoding="utf-8"))
    rows = rep.get("edges") or []
    blds = _buildings(pkg)
    frames = []
    for b in blds:
        g, s = _record(b["id"])
        ox, oy, oz = b["origin"]
        fp = g.get("footprint")
        if isinstance(fp, dict):
            fx, fy = float(fp.get("x") or 0.0), float(fp.get("y") or 0.0)
        elif isinstance(fp, list) and len(fp) == 2 and all(isinstance(v, (int, float)) for v in fp):
            fx, fy = float(fp[0]), float(fp[1])           # [size_x, size_y]
        elif isinstance(fp, list) and fp and isinstance(fp[0], (list, tuple)):
            xs = [float(p[0]) for p in fp]
            ys = [float(p[1]) for p in fp]
            fx, fy = max(xs) - min(xs), max(ys) - min(ys)  # a polygon's bounds
        else:
            fx, fy = 0.0, 0.0
        fx = fx or float(s.get("footprint_x") or 0.0)
        fy = fy or float(s.get("footprint_y") or 0.0)
        # spec (x, y) -> world (ox + x, oz - y)
        rect = (ox - fx / 2, oz - fy / 2, ox + fx / 2, oz + fy / 2)
        stairs = []
        for ss in g.get("stair_systems") or []:
            poly = [(ox + float(p[0]), oz - float(p[1])) for p in ss.get("footprint_polygon") or []]
            if poly:
                stairs.append((ss.get("id"), _grow(poly, MARGIN)))
        hatches = [(ox + float(m["x"]), oz - float(m["y"])) for m in g.get("markers") or []
                   if m.get("type") in ("hatch", "ladder") and "x" in m and "y" in m]
        # DECLARED DROPS, in the item's own sense: a `floor_hole` or `hatch` vertical link is the
        # spec saying "a body goes down here" (`_vertical_links`: "describe a vertical angle or drop
        # point"). The cut is 1.5 m square by default; the record carries its point and storey.
        holes = [(ox + float(v["x"]), oz - float(v["y"]),
                  oy + float(v.get("story") or 0) * float(s.get("story_height") or 0.0))
                 for v in g.get("vertical_links") or []
                 if v.get("kind") in ("floor_hole", "hatch") and v.get("x") is not None]
        n = int(s.get("n_stories") or 0)
        h = float(s.get("story_height") or 0.0)
        base = -1 if s.get("has_basement") else 0
        levels = [oy + k * h for k in range(base, n + 1)]       # floors, and the roof at n * h
        frames.append({"id": b["id"], "node": b["node"], "rect": rect, "stairs": stairs,
                       "hatches": hatches, "holes": holes, "levels": levels,
                       "roof": oy + n * h if n else None})

    classes = {k: [] for k in ("site_edge", "wall_line", "stair", "hatch", "floor_hole", "roof_rim", "storey_rim",
                               "prop_top", "ground", "other")}
    for e in rows:
        x, y, z, drop = float(e["x"]), float(e["y"]), float(e["z"]), float(e.get("drop_m", 0))
        cls = None
        # The instrument writes a bottomless drop as 1e9 and snaps it; it arrives as 999.0.
        if drop >= 999.0 and not any(abs(_dist_to_rect_edge(x, z, f["rect"])) <= WALL_LINE for f in frames):
            cls = "site_edge"
        else:
            for f in frames:
                d = _dist_to_rect_edge(x, z, f["rect"])
                if d < -RIM:
                    continue                       # well outside this building
                # A CELL ON THE FOOTPRINT'S OWN LINE. The instrument's headroom ray starts
                # inside the exterior wall there and sees no hit, so a floor slab's edge under
                # a wall reads as a standable surface, and the cell beyond the wall as a drop.
                # Named before any class, because it is the instrument's, not the level's.
                if abs(d) <= WALL_LINE:
                    cls = "wall_line"
                    break
                if any(_inside(x, z, poly) for _sid, poly in f["stairs"]):
                    cls = "stair"
                    break
                if any(((x - hx) ** 2 + (z - hz) ** 2) ** 0.5 <= HATCH_R for hx, hz in f["hatches"]):
                    cls = "hatch"
                    break
                if any(((x - hx) ** 2 + (z - hz) ** 2) ** 0.5 <= HATCH_R and abs(y - hy) <= LEVEL_TOL
                       for hx, hz, hy in f["holes"]):
                    cls = "floor_hole"
                    break
                if d >= -RIM:
                    if f["roof"] is not None and abs(y - f["roof"]) <= LEVEL_TOL and d <= RIM:
                        cls = "roof_rim"
                        break
                    if d >= 0 and any(abs(y - lv) <= LEVEL_TOL for lv in f["levels"]):
                        cls = "storey_rim"
                        break
                    if d >= 0:
                        cls = "prop_top" if y > KERB else "ground"
                        break
            if cls is None:
                cls = "prop_top" if y > KERB else "ground"
        e["class"] = cls
        classes[cls].append(e)

    print(f"edges {len(rows)}  (report: standable {rep.get('standable_cells')}, drop edges "
          f"{rep.get('drop_edges')}, unguarded {rep.get('unguarded')}, unguarded indoors "
          f"{rep.get('unguarded_indoors')}; rows capped at the instrument's MAX_ROWS)")
    for k, v in classes.items():
        ind = sum(1 for e in v if e.get("indoors"))
        print(f"  {k:12s} {len(v):5d}   indoors {ind:5d}   drop max {max((float(e['drop_m']) for e in v if float(e['drop_m']) < 1e8), default=0):.2f}")
    for k in ("storey_rim", "other", "hatch"):
        print(f"-- {k}: the first rows")
        for e in classes[k][:12]:
            print(f"   ({e['x']:7.2f}, {e['y']:6.2f}, {e['z']:7.2f})  drop {float(e['drop_m']):6.2f}  indoors {e.get('indoors')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
