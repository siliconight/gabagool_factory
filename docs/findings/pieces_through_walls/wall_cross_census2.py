"""Authored volumes that pass THROUGH a wall, measured on the walls the
builder actually cuts. Second instrument; the first (`wall_cross_census.py`)
measured authored runs with no setback, no stairwell split and no turned piece.

    python wall_cross_census2.py [--list]

Frame and units: the spec's frame, metres, footprint centred on 0, z up from
the storey-0 floor.

THE WALLS, as `deli_counter.Builder` builds them:
  * a partition is `partition_bounds.partition_spans` of its authored run --
    clamped to `setbacks.storey_extent` on its storey, split round
    `stairwell.wall_voids` -- with `min_span` the wall thickness, as
    `_partitions` calls it; its band is `pos +- wall_thick / 2`;
  * an exterior wall runs between its storey's extent corners on the extent's
    edge (`storey_extent` is the centreline), band `+- wall_thick / 2`;
  * a wall stands from its storey's floor to the next (z story*sh .. +sh).
Openings are NOT cut: the first census measured that no crossing in the
library sits at one, and a leaf, a breach panel, a rollgate or glass fills
every opening anyway.

THE PIECE: its authored box (the greybox and its collider are drawn
axis-aligned whatever `rot_z` says -- `Builder._volumes`), and, when `rot_z`
is set, the art's footprint turned by it about the centre (counter-clockwise
from above, Blender's z). A wall is crossed when either footprint, clipped to
the wall's run, reaches past BOTH faces of its band: matter on both sides.

Prints what it measured. No cause.
"""
import glob
import json
import math
import os
import sys

#: Deli Counter beside the factory root this folder sits under
DC = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "..", "..", "..", "deli_counter"))
sys.path.insert(0, DC)

import partition_bounds  # noqa: E402
import setbacks as setbacks_mod  # noqa: E402
import spec_loader  # noqa: E402
import stairwell  # noqa: E402

EPS = 1e-6


def footprints(v):
    x, y = float(v["x"]), float(v["y"])
    hx, hy = float(v["size_x"]) / 2.0, float(v["size_y"]) / 2.0
    box = [(x - hx, y - hy), (x + hx, y - hy), (x + hx, y + hy), (x - hx, y + hy)]
    out = [("box", box)]
    rz = float(v.get("rot_z", 0.0) or 0.0) % 360.0
    if rz > EPS:
        c, s = math.cos(math.radians(rz)), math.sin(math.radians(rz))
        out.append(("art", [(x + c * (px - x) - s * (py - y), y + s * (px - x) + c * (py - y))
                            for px, py in box]))
    return out


def clip(poly, a, lo, hi):
    """Clip a convex polygon to lo <= coord[a] <= hi (Sutherland-Hodgman)."""
    def half(pts, keep, edge):
        out = []
        n = len(pts)
        for i in range(n):
            p, q = pts[i], pts[(i + 1) % n]
            kp, kq = keep(p), keep(q)
            if kp:
                out.append(p)
            if kp != kq:
                t = (edge - p[a]) / (q[a] - p[a])
                out.append(tuple(p[k] + t * (q[k] - p[k]) for k in (0, 1)))
        return out
    pts = half(poly, lambda p: p[a] >= lo, lo)
    if pts:
        pts = half(pts, lambda p: p[a] <= hi, hi)
    return pts


def walls(d, LS):
    """``[(label, story, n, plane, half, [(s0, s1)])]``; ``n`` is the axis the
    wall's faces look along (0: a wall running along y)."""
    wt = float(d.get("wall_thick") or LS.wall_thick or 0.3)
    fx, fy = float(LS.footprint_x), float(LS.footprint_y)
    voids = stairwell.wall_voids(LS)
    out = []
    for i, p in enumerate(LS.partitions):
        spans = partition_bounds.partition_spans(
            p.start, p.end, p.axis, p.pos, fx, fy, voids.get(p.story, ()),
            min_span=wt, extent=setbacks_mod.storey_extent(LS, p.story))
        n = 0 if p.axis == "Y" else 1
        out.append(("int_%d_%d" % (p.story, i), p.story, n, float(p.pos), wt / 2.0, spans))
    # `Builder._exterior`: every storey in `_story_range`, all four sides
    # when `auto_exterior` (the default), else only those `ext_walls` lists
    explicit = {(w.wall, w.story) for w in LS.ext_walls}
    for s in range(-1 if LS.has_basement else 0, LS.n_stories):
        x0, y0, x1, y1 = setbacks_mod.storey_extent(LS, s)
        for side in ("N", "S", "E", "W"):
            if (side, s) not in explicit and not LS.auto_exterior:
                continue
            if side in ("S", "N"):
                out.append(("ext_%d_%s" % (s, side), s, 1, y0 if side == "S" else y1, wt / 2.0, [(x0, x1)]))
            else:
                out.append(("ext_%d_%s" % (s, side), s, 0, x0 if side == "W" else x1, wt / 2.0, [(y0, y1)]))
    return out


def crossings(d):
    LS = spec_loader.spec_from_dict(d)
    sh = float(LS.story_height)
    ws = walls(d, LS)
    rows = []
    for v in d.get("volumes") or []:
        z = float(v.get("z", 0.0))
        z0v, z1v = z - float(v["size_z"]) / 2.0, z + float(v["size_z"]) / 2.0
        fps = footprints(v)
        for label, story, n, plane, half, spans in ws:
            if z1v <= story * sh + EPS or z0v >= (story + 1) * sh - EPS:
                continue
            a = 1 - n
            f0, f1 = plane - half, plane + half
            hit = []
            for kind, poly in fps:
                reach = None
                for s0, s1 in spans:
                    pts = clip(poly, a, s0, s1)
                    if len(pts) < 3:
                        continue
                    lo = min(p[n] for p in pts)
                    hi = max(p[n] for p in pts)
                    if lo < f0 - EPS and hi > f1 + EPS:
                        c = sum(p[n] for p in poly) / len(poly)
                        r = (hi - f1) if c < plane else (f0 - lo)
                        reach = r if reach is None else max(reach, r)
                if reach is not None:
                    hit.append((kind, round(reach, 3)))
            if hit:
                rows.append((v.get("name"), label, hit))
    return rows


def main(argv):
    root = os.path.join(DC, "specs")
    if "--specs" in argv:
        root = argv[argv.index("--specs") + 1]
    n_specs, pairs, specs_with = 0, 0, 0
    for p in sorted(glob.glob(os.path.join(root, "*.json"))):
        name = os.path.basename(p)[:-5]
        if name.startswith("lf_"):
            continue
        n_specs += 1
        d = json.load(open(p, encoding="utf-8"))
        rows = crossings(d)
        pairs += len(rows)
        specs_with += bool(rows)
        if "--list" in argv:
            for vn, label, hit in rows:
                print("%-30s %-36s %-10s %s" % (name, vn, label, hit))
    print("specs read (no lf_*): %d; piece x wall crossings: %d in %d specs" % (n_specs, pairs, specs_with))


if __name__ == "__main__":
    main(sys.argv[1:])
