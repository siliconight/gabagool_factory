"""Authored volumes that pass THROUGH a wall, across Deli Counter's specs.

    python wall_cross_census.py [--specs DIR] [--list]

Frame and units: the spec's own frame, metres, footprint centred on 0, z up
from the storey-0 floor. A volume is its axis-aligned box (rot_z of 90/270
swaps x and y; any other turn is reported, not measured). A partition is the
band `pos +- wall_thick/2` across its axis, from `start` to `end`, on its
storey (z from story*sh to (story+1)*sh), minus each opening's span along it.
An exterior wall is the footprint's edge, the same band.

A volume CROSSES a wall when its box reaches past BOTH faces of the band
somewhere along a solid (non-opening) stretch of it: matter on both sides.
A volume that only reaches INTO the band (ends inside it) is counted
separately as EMBEDDED, and one that touches a face as neither.

Prints what it measured. No cause.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
#: Deli Counter beside the factory root this folder sits under
DC = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "..", "..", "..", "deli_counter"))


def _story_h(s):
    return float(s.get("story_height") or 3.6)


def _wt(s):
    return float(s.get("wall_thick") or 0.3)


def vol_box(v):
    sx, sy, sz = float(v["size_x"]), float(v["size_y"]), float(v["size_z"])
    rz = float(v.get("rot_z", 0.0) or 0.0) % 360.0
    if abs(rz - 90.0) < 1e-6 or abs(rz - 270.0) < 1e-6:
        sx, sy = sy, sx
    elif abs(rz) > 1e-6 and abs(rz - 180.0) > 1e-6:
        return None
    x, y, z = float(v["x"]), float(v["y"]), float(v.get("z", 0.0))
    return (x - sx / 2, y - sy / 2, z - sz / 2), (x + sx / 2, y + sy / 2, z + sz / 2)


def solid_spans(start, end, openings, length, grid=0.5):
    """The wall's solid stretches along its run, openings cut out. An
    opening is cut at `snap(pos * run)` from the piece's centre, as
    `deli_counter.Builder` cuts it (`_opening_to_hole`, `_record_openings`)."""
    centre = (start + end) / 2.0
    cuts = []
    for o in openings or []:
        u = centre + round(float(o.get("pos", 0.0)) * length / grid) * grid
        w = float(o.get("width") or {"door": 1.2, "window": 1.6, "garage": 3.5,
                                     "breach": 1.5, "vault": 1.3}.get(o.get("kind"), 1.2))
        # a window is solid below its sill: a volume may stand under it
        if o.get("kind") == "window":
            continue
        cuts.append((u - w / 2.0, u + w / 2.0))
    spans = [(min(start, end), max(start, end))]
    for a, b in cuts:
        nxt = []
        for lo, hi in spans:
            if b <= lo or a >= hi:
                nxt.append((lo, hi))
                continue
            if a > lo:
                nxt.append((lo, a))
            if b < hi:
                nxt.append((b, hi))
        spans = nxt
    return spans


def walls(s):
    """``[(label, story, axis_of_normal, plane, band_half, along_spans)]``.
    axis_of_normal 0: the wall's faces look along x (a wall running along y)."""
    out = []
    wt = _wt(s)
    grid = float(s.get("grid") or 0.5)
    fx, fy = float(s["footprint_x"]), float(s["footprint_y"])
    for i, p in enumerate(s.get("partitions") or []):
        ax = p.get("axis")
        start, end = float(p.get("start", 0.0)), float(p.get("end", 0.0))
        length = abs(end - start)
        spans = solid_spans(start, end, p.get("openings"), length, grid)
        # axis "Y": the wall runs along y at x = pos, its faces look along x
        n = 0 if ax == "Y" else 1
        out.append(("int_%d_%d" % (int(p.get("story", 0)), i), int(p.get("story", 0)), n,
                    float(p["pos"]), wt / 2.0, spans))
    for w in s.get("ext_walls") or []:
        side = w["wall"]
        if side in ("S", "N"):
            plane = -fy / 2.0 if side == "S" else fy / 2.0
            spans = solid_spans(-fx / 2.0, fx / 2.0, w.get("openings"), fx, grid)
            out.append(("ext_%d_%s" % (int(w.get("story", 0)), side), int(w.get("story", 0)), 1, plane, wt / 2.0, spans))
        else:
            plane = -fx / 2.0 if side == "W" else fx / 2.0
            spans = solid_spans(-fy / 2.0, fy / 2.0, w.get("openings"), fy, grid)
            out.append(("ext_%d_%s" % (int(w.get("story", 0)), side), int(w.get("story", 0)), 0, plane, wt / 2.0, spans))
    return out


def census(s, eps=1e-6):
    sh = _story_h(s)
    rows = []
    for v in s.get("volumes") or []:
        b = vol_box(v)
        if b is None:
            rows.append((v.get("name"), "TURNED", None, None))
            continue
        lo, hi = b
        for label, story, n, plane, half, spans in walls(s):
            z0, z1 = story * sh, (story + 1) * sh
            if hi[2] <= z0 + eps or lo[2] >= z1 - eps:
                continue
            a = 1 - n                             # the axis the wall runs along
            along = [(max(lo[a], s0), min(hi[a], s1)) for s0, s1 in spans]
            along = [(p, q) for p, q in along if q - p > eps]
            if not along:
                continue
            f0, f1 = plane - half, plane + half
            if hi[n] <= f0 + eps or lo[n] >= f1 - eps:
                continue
            through = lo[n] < f0 - eps and hi[n] > f1 + eps
            past = max(min(hi[n] - f1, f1 - lo[n]), min(f0 - lo[n], hi[n] - f0)) if through else None
            # how far the box reaches past the FAR face, from the side its centre is on
            c = (lo[n] + hi[n]) / 2.0
            reach = (hi[n] - f1) if c < plane else (f0 - lo[n])
            rows.append((v.get("name"), "CROSSES" if through else "EMBEDDED", label,
                         round(reach if through else max(min(hi[n], f1) - max(lo[n], f0), 0.0), 3)))
    return rows


def main(argv):
    root = os.path.join(DC, "specs")
    if "--specs" in argv:
        root = argv[argv.index("--specs") + 1]
    listing = "--list" in argv
    tot = {"CROSSES": 0, "EMBEDDED": 0, "TURNED": 0}
    specs_with = 0
    for p in sorted(glob.glob(os.path.join(root, "*.json"))):
        name = os.path.basename(p)[:-5]
        if name.startswith("lf_"):
            continue
        s = json.load(open(p, encoding="utf-8"))
        rows = census(s)
        cross = [r for r in rows if r[1] == "CROSSES"]
        for r in rows:
            tot[r[1]] += 1
        if cross:
            specs_with += 1
        if listing and cross:
            for r in cross:
                print("%-28s %-34s %-9s %-10s past the far face by %.3f m" % (name, r[0], r[1], r[2], r[3]))
    # Refuted, kept: this line first printed every JSON in specs/ (427) as
    # "no lf_*"; the measurement above it always skipped them.
    every = glob.glob(os.path.join(root, "*.json"))
    print("specs read: %d of %d (lf_* skipped)"
          % (len([p for p in every if not os.path.basename(p).startswith("lf_")]), len(every)))
    print("volume x wall pairs: CROSSES %d, EMBEDDED %d; volumes turned off-axis %d" %
          (tot["CROSSES"], tot["EMBEDDED"], tot["TURNED"]))
    print("specs with a crossing: %d" % specs_with)


if __name__ == "__main__":
    main(sys.argv[1:])
