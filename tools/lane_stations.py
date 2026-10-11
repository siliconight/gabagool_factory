"""The lane stations of a level, for look_shots: along each service lane from either end.

    python tools/lane_stations.py <site.site.drawn.json> [--inside 6] [--eye 1.7]

Prints `--station name:ex,ey,ez,tx,ty,tz` arguments in look_shots' Godot frame (x, up, -y), two
per road the spec marks `kind: service_lane` (Level Factory 0.177.0's `block` grammar): the eye
`--inside` metres in from each end on the lane's centre line, looking at the far end, so the
frame shows the lane between the yards and the plate's far band, the rear walls and their
dumpsters on one side. A spec with no lane prints nothing and says so on stderr. It prints what
it derived and stops.
"""
import json
import math
import sys


def stations(drawn, inside=6.0, eye=1.7):
    out, args = [], []
    for i, r in enumerate(drawn.get("roads") or []):
        if str(r.get("kind", "")) != "service_lane":
            continue
        (ax, ay), (bx, by) = r["a"], r["b"]
        length = math.hypot(bx - ax, by - ay)
        if length < 2.0 * inside:
            continue
        ux, uy = (bx - ax) / length, (by - ay) / length
        for tag, (sx, sy), (tx, ty), (dx, dy) in (("a", (ax, ay), (bx, by), (ux, uy)),
                                                   ("b", (bx, by), (ax, ay), (-ux, -uy))):
            px, py = sx + dx * inside, sy + dy * inside
            name = "lane%d_%s" % (i, tag)
            out.append((name, px, py, tx, ty))
            args.append("--station %s:%g,%g,%g,%g,%g,%g" % (name, px, eye, -py, tx, eye + 0.5, -ty))
    return out, args


def main(argv):
    path = argv[0]
    inside = float(argv[argv.index("--inside") + 1]) if "--inside" in argv else 6.0
    eye = float(argv[argv.index("--eye") + 1]) if "--eye" in argv else 1.7
    drawn = json.load(open(path, encoding="utf-8"))
    out, args = stations(drawn, inside, eye)
    if not out:
        print("# no road carries kind: service_lane in %s" % path, file=sys.stderr)
    for name, px, py, tx, ty in out:
        print("# %s: eye at plan (%.1f, %.1f), %g m in from the end, looking at (%.1f, %.1f)"
              % (name, px, py, inside, tx, ty), file=sys.stderr)
    print(" ".join(args))


if __name__ == "__main__":
    main(sys.argv[1:])
