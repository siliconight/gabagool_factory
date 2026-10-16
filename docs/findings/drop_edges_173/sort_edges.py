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
    slab_cut     within SLAB_MARGIN of a hole the builder cut in that slab (a floor or roof slot's `fit.voids`,
                 in the built slots): the cut's own lip -- a stair well, a ladder hatch, a floor hole
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
SLAB_MARGIN = 0.6   # m; an edge this close to a slab's cut, at its level, is the cut's own lip


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


def _tail(owners, i):
    """The last two components of an owner path: `GreyboxBase/slab_col_1`, `cover_3/SimpleCar`."""
    return "none" if i is None or int(i) < 0 else "/".join(owners[int(i)].split("/")[-2:])


def _floor_like(tail):
    """A surface a body WALKS on, by what owns its collider in this toolchain's packages: Deli Counter's
    floor and basement slabs (`GreyboxBase/slab_col_<n>`), a roof (`roof_footprint/Roof`, an Empty's
    `KitCollision/Roof`), a stair's ramps and landings (`GreyboxBase/stair<n>...`, never `stair_guard_rail`),
    and Lot's own surfaces, which are the site node's direct children (`Site/Ground`, `Site/road_1`,
    `Site/sidewalk_1L_2`, `Site/frontage_0L_1`, `Site/path_1`, `Site/yard_1`; `Site/perim_*` is the fence
    and is claimed before this is asked). Everything else is a thing's top."""
    return (tail.startswith("Site/") or re.match(r"GreyboxBase/slab_col_-?\d+$", tail) is not None
            or tail.endswith("/Roof") or re.match(r"GreyboxBase/stair\d", tail) is not None
            or re.match(r"GreyboxBase/ladder\d+_plane$", tail) is not None)


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
        # EVERY CUT IN EVERY SLAB, as the builder recorded it: a floor or roof slot's `fit.voids` are
        # the holes in that slab (stair wells, ladder hatches, floor holes), in the slot's own centred
        # coords, so world (spec frame) = the slot's translation + the rect. An edge at that slab's
        # level within SLAB_MARGIN of a void is the cut's own lip: declared by the builder, whatever
        # a guard does or does not do there. (`deli_counter/build/<id>.slots.json`)
        cuts = []
        sp = os.path.join(DC, "build", f"{b['id']}.slots.json")
        if os.path.exists(sp):
            for sl in json.load(open(sp, encoding="utf-8")).get("slots", []):
                if sl.get("role") not in ("floor", "roof"):
                    continue
                tx, ty = sl["transform"]["translation"][:2]
                lvl = oy + (float(sl["transform"]["translation"][2]) if sl.get("role") == "roof"
                            else float(sl.get("story") or 0) * h)
                for v in (sl.get("fit") or {}).get("voids") or []:
                    x0, y0, x1, y1 = (float(v["x0"]) + tx, float(v["y0"]) + ty,
                                      float(v["x1"]) + tx, float(v["y1"]) + ty)
                    # spec (x, y) -> world (ox + x, oz - y): the y axis flips, so the rect's z order does
                    cuts.append((ox + x0, oz - y1, ox + x1, oz - y0, lvl))
        frames.append({"id": b["id"], "node": b["node"], "rect": rect, "stairs": stairs,
                       "hatches": hatches, "holes": holes, "cuts": cuts, "levels": levels,
                       "roof": oy + n * h if n else None})

    classes = {k: [] for k in ("site_edge", "wall_line", "declared_link", "stair", "hatch", "floor_hole",
                               "slab_cut", "roof_rim", "storey_rim", "prop_top", "perimeter_top", "parapet_top",
                               "ground", "other")}
    owners = rep.get("owners") or []
    # THE DECLARED SET, FROM THE PACKAGE ITSELF (Deli Counter 0.226.0 / Lot 0.125.0 / Dispatch 0.5.3): every
    # off-mesh link in `navigation_hints.json` with `required_capability` "drop" is a floor_hole / hatch the
    # spec declared, carrying the cut's rect as `hole` (two corners, site XY, Blender frame: Godot x = x,
    # z = -y) and its start on the storey whose floor it opens (already in Godot's frame). An edge at that
    # level within SLAB_MARGIN of the rect is declared by the package, not by this repo's build records --
    # the gate's list and the AI's list are the same list. A package without such links (every one before
    # cold run 9319) claims nothing here, which is the control.
    declared = []
    hints_path = os.path.join(pkg, "navigation_hints.json")
    if os.path.exists(hints_path):
        hints = json.load(open(hints_path, encoding="utf-8"))
        for link in hints.get("links") or []:
            if link.get("required_capability") != "drop" or not link.get("hole"):
                continue
            (hx0, hy0), (hx1, hy1) = link["hole"]
            level = float(link["start_position"][1])
            declared.append((min(hx0, hx1), -max(hy0, hy1), max(hx0, hx1), -min(hy0, hy1), level, link.get("id")))
    by_cap = {}
    if os.path.exists(hints_path):
        for link in hints.get("links") or []:
            cap = link.get("required_capability", "?")
            by_cap[cap] = by_cap.get(cap, 0) + 1
    print(f"package links by capability: {by_cap}; declared drops with a hole rect: {len(declared)}")
    for e in rows:
        x, y, z, drop = float(e["x"]), float(e["y"]), float(e["z"]), float(e.get("drop_m", 0))
        cls = None
        # WHAT THE CELL STANDS ON, FIRST. From the instrument's sixth run the row names the collider's
        # owner, and a surface that is not a floor, a roof, a tread or Lot's ground is a thing's top --
        # a car, a cubicle bank, a desk, a parapet, the perimeter fence -- whatever its height. The
        # earlier runs' rows carry no owner and fall through to the height bands below.
        on = _tail(owners, e.get("on")) if owners else ""
        if owners:
            if on.startswith("Site/perim_"):
                cls = "perimeter_top"
            elif on.startswith("GreyboxBase/parapet_") or re.match(r"parapet_[A-Z]_t\d+_\d+/", on):
                cls = "parapet_top"
            elif not _floor_like(on):
                cls = "prop_top"
        fallback = "ground" if owners else ("prop_top" if y > KERB else "ground")
        if cls is not None:
            pass
        elif any(abs(y - lvl) <= LEVEL_TOL and _dist_to_rect_edge(x, z, (dx0, dz0, dx1, dz1)) >= -SLAB_MARGIN
                 for dx0, dz0, dx1, dz1, lvl, _lid in declared):
            cls = "declared_link"
        # The instrument writes a bottomless drop as 1e9 and snaps it; it arrives as 999.0.
        elif drop >= 999.0 and not any(abs(_dist_to_rect_edge(x, z, f["rect"])) <= WALL_LINE for f in frames):
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
                if any(abs(y - lvl) <= LEVEL_TOL and _dist_to_rect_edge(x, z, (cx0, cz0, cx1, cz1)) >= -SLAB_MARGIN
                       for cx0, cz0, cx1, cz1, lvl in f["cuts"]):
                    cls = "slab_cut"
                    break
                if d >= -RIM:
                    if f["roof"] is not None and abs(y - f["roof"]) <= LEVEL_TOL and d <= RIM:
                        cls = "roof_rim"
                        break
                    if d >= 0 and any(abs(y - lv) <= LEVEL_TOL for lv in f["levels"]):
                        cls = "storey_rim"
                        break
                    if d >= 0:
                        cls = fallback
                        break
            if cls is None:
                cls = fallback
        e["class"] = cls
        classes[cls].append(e)

    print(f"edges {len(rows)}  (report: standable {rep.get('standable_cells')}, drop edges "
          f"{rep.get('drop_edges')}, unguarded {rep.get('unguarded')}, unguarded indoors "
          f"{rep.get('unguarded_indoors')}; rows capped at the instrument's MAX_ROWS)")
    for k, v in classes.items():
        ind = sum(1 for e in v if e.get("indoors"))
        print(f"  {k:12s} {len(v):5d}   indoors {ind:5d}   drop max {max((float(e['drop_m']) for e in v if float(e['drop_m']) < 1e8), default=0):.2f}")
    # WHAT EACH CLASS STANDS ON, by the collider's owner (the instrument's `owners[]` table, from its
    # sixth run on): the last two components of the node path, so `GreyboxBase/slab_col_1` is a floor
    # slab and `cartons_r2f2d413e_4/CartonStack` a thing. A gate excludes furniture by this, not by height.
    if owners:
        print("-- what each class stands ON (owner tail: rows), the top entries:")
        for k, v in classes.items():
            if not v:
                continue
            tally = {}
            for e in v:
                t = re.sub(r"_r[0-9a-f]{8}_\d+", "_r*", _tail(owners, e.get("on")))
                t = re.sub(r"_\d+(/|$)", r"_N\1", t)
                tally[t] = tally.get(t, 0) + 1
            top = sorted(tally.items(), key=lambda kv: -kv[1])[:8]
            print(f"   {k:12s} " + "; ".join(f"{t} {n}" for t, n in top))
    # WHAT THE FLOOD REACHED (the instrument's eighth run on: `standable_by_owner` / `reachable_by_owner`,
    # keyed by owner index). Floors and ground first: a storey the flood did not reach has no edges asked
    # of it, and that absence is the first thing to read before trusting a zero.
    if rep.get("reachable_by_owner") is not None:
        std = rep.get("standable_by_owner") or {}
        rch = rep.get("reachable_by_owner") or {}
        trip = [(_tail(owners, int(i)), int(rch.get(i, 0)), int(n)) for i, n in std.items()]
        print(f"-- reached from the seed {rep.get('seed')}: {rep.get('reachable_cells')} of "
              f"{rep.get('standable_cells')} standable cells; floors and ground (reached / standable):")
        for t, r, n in sorted((v for v in trip if _floor_like(v[0])), key=lambda v: -v[2])[:36]:
            print(f"   {r:6d} / {n:6d}  {t}")
        print("   tops reached that are not floors (reached / standable):")
        for t, r, n in sorted((v for v in trip if not _floor_like(v[0]) and v[1]), key=lambda v: -v[1])[:16]:
            print(f"   {r:6d} / {n:6d}  {t}")
    # THE RESIDUE, by building and level: what a reader attributes next.
    by = {}
    for e in classes["storey_rim"]:
        x, y, z = float(e["x"]), float(e["y"]), float(e["z"])
        owner = "elsewhere"
        for f in frames:
            if _dist_to_rect_edge(x, z, f["rect"]) >= -RIM:
                owner = f["id"]
                break
        key = (owner, round(y, 1), "indoors" if e.get("indoors") else "sky",
               "full storey" if float(e["drop_m"]) >= 2.9 else ("under 1.5" if float(e["drop_m"]) < 1.5 else "mid"))
        by[key] = by.get(key, 0) + 1
    print("-- storey_rim by (building, level, where, depth):")
    for key, n in sorted(by.items(), key=lambda kv: -kv[1])[:24]:
        print(f"   {n:5d}  {key}")
    for k in ("storey_rim", "other", "hatch"):
        print(f"-- {k}: the first rows")
        for e in classes[k][:12]:
            print(f"   ({e['x']:7.2f}, {e['y']:6.2f}, {e['z']:7.2f})  drop {float(e['drop_m']):6.2f}  indoors {e.get('indoors')}")
    # Every row with its class, for a probe to read its points from (`--dump <file>`).
    if "--dump" in argv:
        dump = argv[argv.index("--dump") + 1]
        with open(dump, "w", encoding="utf-8") as fh:
            json.dump([{"class": e["class"], "x": float(e["x"]), "y": float(e["y"]), "z": float(e["z"]),
                        "drop_m": float(e["drop_m"]), "indoors": bool(e.get("indoors"))} for e in rows], fh)
        print(f"-- dumped {len(rows)} rows with their class to {dump}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
