"""The edge stations of a level, for look_shots: down each road to the plate's edge it leaves by.

    python tools/edge_stations.py <site.site.drawn.json> [--inside 45] [--eye 1.7]

Prints `--station name:ex,ey,ez,tx,ty,tz` arguments in look_shots' Godot frame (x, up, -y),
one per road end that reaches the plate's edge: the eye `--inside` metres in from that end on the
road's centre line, looking along the road to the edge, pitched 0.5 m up over the distance as
the edge menu's stations were. A road end that stops short of the edge by more than its width is
not an edge and is skipped, and the plate's rect is the drawn spec's `ground` size, centred, which
is what Lot built. It prints what it derived and stops.
"""
import json
import math
import sys


def stations(drawn, inside=45.0, eye=1.7):
    g = drawn.get("ground") or {}
    sx, sy = float(g.get("size_x", 0)), float(g.get("size_y", 0))
    x0, y0, x1, y1 = -sx / 2.0, -sy / 2.0, sx / 2.0, sy / 2.0
    out = []
    for i, r in enumerate(drawn.get("roads") or []):
        a, b = r.get("a"), r.get("b")
        if not a or not b:
            continue
        w = float(r.get("width") or 8.0)
        for end_name, end, other in (("a", a, b), ("b", b, a)):
            ex, ey = float(end[0]), float(end[1])
            ox, oy = float(other[0]), float(other[1])
            # which edge, if any, this end reaches
            edge = None
            if abs(ex - x0) <= w: edge = "W"
            elif abs(ex - x1) <= w: edge = "E"
            elif abs(ey - y0) <= w: edge = "S"
            elif abs(ey - y1) <= w: edge = "N"
            if edge is None:
                continue
            L = math.hypot(ex - ox, ey - oy)
            if L < 1e-6:
                continue
            ux, uy = (ex - ox) / L, (ey - oy) / L
            d = min(inside, L * 0.8)
            px, py = ex - ux * d, ey - uy * d
            tx, ty = ex, ey
            out.append((f"road{i}_{end_name}_{edge}", px, py, tx, ty, d))
    args = []
    for name, px, py, tx, ty, d in out:
        args.append("--station %s:%g,%g,%g,%g,%g,%g" % (name, px, eye, -py, tx, eye + 0.5, -ty))
    return out, args


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    inside = float(argv[argv.index("--inside") + 1]) if "--inside" in argv else 45.0
    eye = float(argv[argv.index("--eye") + 1]) if "--eye" in argv else 1.7
    drawn = json.load(open(argv[0], encoding="utf-8"))
    out, args = stations(drawn, inside, eye)
    for name, px, py, tx, ty, d in out:
        print("# %s: eye at plan (%.1f, %.1f), %g m inside the edge, looking at (%.1f, %.1f)"
              % (name, px, py, d, tx, ty), file=sys.stderr)
    print(" ".join(args))


if __name__ == "__main__":
    main(sys.argv[1:])
