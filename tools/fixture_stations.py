"""Stations at a level's light fixtures of one type, for look_shots: inside the room, looking at the lamp.

    python tools/fixture_stations.py <site.site.lights.json> --type dome [--back 3.0] [--eye 1.6] [--max 6]

Prints `--station name:ex,ey,ez,tx,ty,tz` arguments in look_shots' Godot frame (x, up, -y), one
per anchor of `--type` in a site's merged lights manifest (Lot's `site.site.lights.json`, plan
Z-up metres, `pos` the emitter): the eye `--eye` metres over the anchor's own floor (`pos.z -
drop`) and `--back` metres from the anchor along its row's normal, looking at the anchor, so the
frame holds the fixture against its ceiling and the pool it throws. One station an anchor (its
row's first lamp), up to `--max`, in manifest order. Written for Deli Counter 0.208.0 (a home's
room writes `dome` where it wrote `fluorescent`, at the same ids and positions), so the same
stations shoot a package from before and after it. A manifest with no such anchor prints nothing
and says so on stderr. It prints what it derived and stops.
"""
import json
import math
import sys


def stations(manifest, kind, back=3.0, eye=1.6, limit=6):
    notes, args = [], []
    for a in manifest.get("anchors") or []:
        if str(a.get("type")) != kind:
            continue
        x, y, z = (float(v) for v in a["pos"])
        drop = float(a.get("drop") or 0.0)
        floor = z - drop if drop > 0.0 else z - 2.9
        row = a.get("row") or {}
        n = int(row.get("count", 1) or 1)
        sp = float(row.get("spacing", 0.0) or 0.0)
        r = math.radians(float(a.get("rot_y") or 0.0))
        # the row's first lamp, as a row is laid centred on pos along rot_y
        fx = x - math.cos(r) * sp * (n - 1) / 2.0
        fy = y - math.sin(r) * sp * (n - 1) / 2.0
        # the eye stands off the row, square to it
        ex, ey = fx - math.sin(r) * back, fy + math.cos(r) * back
        name = "fix_%s" % str(a.get("id", len(args))).replace("/", "_").lower()
        args.append("--station %s:%g,%g,%g,%g,%g,%g" % (name, ex, floor + eye, -ey, fx, z - 0.1, -fy))
        notes.append("%s: lamp at plan (%.1f, %.1f) %.1f m up, eye %.1f m off at (%.1f, %.1f)"
                     % (name, fx, fy, z - floor, back, ex, ey))
        if len(args) >= limit:
            break
    return notes, args


def main(argv):
    paths = [a for a in argv if not a.startswith("--")]

    def opt(flag, default):
        return argv[argv.index(flag) + 1] if flag in argv else default
    if not paths or "--type" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    kind = opt("--type", "")
    paths = [p for p in paths if p not in (kind, opt("--back", ""), opt("--eye", ""), opt("--max", ""))]
    with open(paths[0], encoding="utf-8") as f:
        manifest = json.load(f)
    notes, args = stations(manifest, kind, float(opt("--back", 3.0)), float(opt("--eye", 1.6)),
                           int(opt("--max", 6)))
    if not args:
        print("# no %s anchor in %s" % (kind, paths[0]), file=sys.stderr)
        return 0
    for n in notes:
        print("# " + n, file=sys.stderr)
    print(" ".join(args))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
