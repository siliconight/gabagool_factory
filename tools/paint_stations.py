"""The paint stations of a level, for look_shots: down each street and close on its paint.

    python tools/paint_stations.py <site.site.drawn.json> [<site.markings.json>] [--eye 1.7]

Prints `--station name:ex,ey,ez,tx,ty,tz` arguments in look_shots' Godot frame (x, up, -y):
`paint_r<i>_along`, the eye 12 m in from each street's first end on its centre line looking 30 m
down the road at the surface, so the frame holds the centre line, the edge lines and the first
crosswalk; `paint_r<i>_xwalk`, 7 m short of that street's first crosswalk (its `crosswalk_bar`
markings clustered by position) looking down at its centre; and `paint_bays`, 6 m off the first
field's first bay tick looking at it. Service lanes (`kind: service_lane`) carry no paint and get
no station. The manifest defaults to `site.markings.json` beside the drawn spec. It prints what
it derived to stderr and stops.

Written for cold run 9234 (Lot 0.114.0, roadmap 231): the same stations shot in 9233's package
and 9234's put the per-marking materials beside the one mesh a colour, bar for bar.
"""
import json
import math
import os
import sys


def _road_frame(r):
    (ax, ay), (bx, by) = r["a"], r["b"]
    length = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / length, (by - ay) / length
    return ax, ay, ux, uy, length


def _clusters(points, within=4.0):
    """Points grouped by plan distance: a crosswalk's bars lie within `within` m."""
    groups = []
    for p in points:
        for g in groups:
            if any(math.hypot(p[0] - q[0], p[1] - q[1]) <= within for q in g):
                g.append(p)
                break
        else:
            groups.append([p])
    return [(sum(p[0] for p in g) / len(g), sum(p[1] for p in g) / len(g), len(g)) for g in groups]


def stations(drawn, marks, eye=1.7):
    notes, args = [], []

    def put(name, ex, ey, tx, ty, th):
        args.append("--station %s:%g,%g,%g,%g,%g,%g" % (name, ex, eye, -ey, tx, th, -ty))

    roads = drawn.get("roads") or []
    for i, r in enumerate(roads):
        if str(r.get("kind", "")) == "service_lane":
            continue
        ax, ay, ux, uy, length = _road_frame(r)
        if length < 50.0:
            continue
        ex, ey = ax + ux * 12.0, ay + uy * 12.0
        tx, ty = ax + ux * 42.0, ay + uy * 42.0
        put("paint_r%d_along" % i, ex, ey, tx, ty, 0.3)
        notes.append("paint_r%d_along: eye at plan (%.1f, %.1f) looking down the road at (%.1f, %.1f)"
                     % (i, ex, ey, tx, ty))
        bars = [tuple(m["at"]) for m in marks if m.get("road") == i and m.get("kind") == "crosswalk_bar"]
        if bars:
            cx, cy, n = sorted(_clusters(bars), key=lambda c: (c[0] - ax) * ux + (c[1] - ay) * uy)[0]
            # along-road distance of the crosswalk from a; the eye stands 7 m short of it
            s = (cx - ax) * ux + (cy - ay) * uy
            ex, ey = ax + ux * (s - 7.0), ay + uy * (s - 7.0)
            put("paint_r%d_xwalk" % i, ex, ey, cx, cy, 0.0)
            notes.append("paint_r%d_xwalk: %d bars at (%.1f, %.1f), eye 7 m short at (%.1f, %.1f)"
                         % (i, n, cx, cy, ex, ey))
    ticks = [tuple(m["at"]) for m in marks if m.get("kind") == "bay_tick"]
    if ticks:
        cx, cy, n = _clusters(ticks, within=6.0)[0]
        # the eye 6 m off the ticks on the side away from the nearest road
        away = (0.0, 1.0)
        if roads:
            ax, ay, ux, uy, _ = _road_frame(roads[0])
            d = (cx - ax) * (-uy) + (cy - ay) * ux        # signed offset from road 0's line
            away = (-uy, ux) if d >= 0 else (uy, -ux)
        ex, ey = cx + away[0] * 6.0, cy + away[1] * 6.0
        put("paint_bays", ex, ey, cx, cy, 0.0)
        notes.append("paint_bays: %d ticks about (%.1f, %.1f), eye 6 m off at (%.1f, %.1f)"
                     % (n, cx, cy, ex, ey))
    return notes, args


def main(argv):
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__, file=sys.stderr)
        return 2
    eye = 1.7
    if "--eye" in argv:
        eye = float(argv[argv.index("--eye") + 1])
    drawn_path = paths[0]
    marks_path = paths[1] if len(paths) > 1 else os.path.join(os.path.dirname(drawn_path), "site.markings.json")
    with open(drawn_path, encoding="utf-8") as f:
        drawn = json.load(f)
    with open(marks_path, encoding="utf-8") as f:
        manifest = json.load(f)
    marks = manifest["markings"] if isinstance(manifest, dict) else manifest
    notes, args = stations(drawn, marks, eye)
    if not args:
        print("# no street with paint in %s" % drawn_path, file=sys.stderr)
        return 2
    for n in notes:
        print("# " + n, file=sys.stderr)
    print(" ".join(args))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
