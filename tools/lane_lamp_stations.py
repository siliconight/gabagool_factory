"""Stations at a level's lane lamps, for look_shots: one a lamp, on the lane looking past the pole.

    python tools/lane_lamp_stations.py <site.site.drawn.json> [--back 12] [--eye 1.7]

Prints `--station name:ex,ey,ez,tx,ty,tz` arguments in look_shots' Godot frame (x, up, -y), one
per `streetlight` cover piece the drawn spec marks `lane: true` (Lot 0.116.0's lane lamps): the
eye on the lane's centre line `--back` metres short of the pole, looking at the ground 12 m past
it, so the frame holds the pool and the dark either side of it. The lane is the road the lamp's
record names (`road`). A spec with no lane lamp prints nothing and says so on stderr. It prints
what it derived and stops.
"""
import json
import math
import sys


def stations(drawn, back=12.0, eye=1.7):
    out, args = [], []
    roads = drawn.get("roads") or []
    for cv in drawn.get("cover") or []:
        if cv.get("species") != "streetlight" or not cv.get("lane"):
            continue
        r = roads[int(cv["road"])]
        (ax, ay), (bx, by) = r["a"], r["b"]
        length = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / length, (by - ay) / length
        t = (cv["at"][0] - ax) * ux + (cv["at"][1] - ay) * uy
        ex, ey = ax + ux * (t - back), ay + uy * (t - back)
        tx, ty = ax + ux * (t + 12.0), ay + uy * (t + 12.0)
        name = "lanelamp_%s" % str(cv.get("name", len(args))).lower()
        args.append("--station %s:%g,%g,%g,%g,%g,%g" % (name, ex, eye, -ey, tx, 0.0, -ty))
        out.append("%s: pole at plan (%.1f, %.1f), eye %g m short on the lane at (%.1f, %.1f)"
                   % (name, cv["at"][0], cv["at"][1], back, ex, ey))
    return out, args


def main(argv):
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__, file=sys.stderr)
        return 2
    back = float(argv[argv.index("--back") + 1]) if "--back" in argv else 12.0
    eye = float(argv[argv.index("--eye") + 1]) if "--eye" in argv else 1.7
    with open(paths[0], encoding="utf-8") as f:
        drawn = json.load(f)
    notes, args = stations(drawn, back, eye)
    if not args:
        print("# no lane lamp in %s" % paths[0], file=sys.stderr)
        return 0
    for n in notes:
        print("# " + n, file=sys.stderr)
    print(" ".join(args))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
