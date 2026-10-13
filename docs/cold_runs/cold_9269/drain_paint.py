"""Where cold run 9269's drains (Lot 0.120.0) lie against the street's paint, read off the package.

Two artefacts, both written by the themed site's Lot run (the job `themed_site_assemble`, the one the
package ships):
  * the drains: every `site_drains_*.obj` in the package, its faces joined into connected parts, and
    parts whose plan boxes come within `MERGE` (0.1 m) of each other merged into one piece -- a
    cover's lid and studs are separate parts over its frame, an inlet's bars over its well; an inlet
    and the lid behind it are 0.5 m apart. Each piece's footprint is the plan hull of its vertices:
    what is drawn, not a re-run plan. A piece with any `void` vertex is an inlet; of the rest, a hull
    over 0.4 m^2 is a manhole cover's frame and smaller a sidewalk lid. The count is checked against
    the one Lot printed.
    RETRACTED, KEPT: the first version clustered VERTICES nearer than 0.3 m and read 36 pieces where
    Lot printed 16 (4 covers, 8 inlets, 4 lids) -- a lid's corners are 0.46 m apart with no vertex
    between them and an inlet's two long edges 0.61 m, so every lid read as four pieces of no area
    and every inlet as two. Its overlaps were real paint under real halves; its counts were not.
  * the paint: the job's `<site>.markings.json` (`site_streets.manifest`), each marking a rectangle
    of `size` [along, across] at `at`, turned by `yaw` degrees -- the street's paint, the parking
    fields' lines not among them.
Frames: an OBJ is Godot's (x, height, z), plan (x, -z); the manifest is plan. Metres.

For every piece: each marking it overlaps and the area in common, and the clearance to the nearest
marking it does not overlap. It prints measurements and stops.

    python docs/cold_runs/cold_9269/drain_paint.py <package dir> <job out dir> [<site name>]
"""
import glob
import json
import math
import os
import re
import sys

MERGE = 0.1


def _hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]                       # counter-clockwise


def _area(poly):
    return abs(sum(poly[i][0] * poly[i - 1][1] - poly[i - 1][0] * poly[i][1]
                   for i in range(len(poly)))) / 2.0


def _clip(subject, clip):
    """Sutherland-Hodgman: ``subject`` clipped to the convex, counter-clockwise ``clip``."""
    out = list(subject)
    for i in range(len(clip)):
        a, b = clip[i - 1], clip[i]
        inp, out = out, []
        if not inp:
            break

        def inside(p):
            return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= 0.0

        def meet(p, q):
            x1, y1, x2, y2 = p[0], p[1], q[0], q[1]
            x3, y3, x4, y4 = a[0], a[1], b[0], b[1]
            den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
            return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

        for j in range(len(inp)):
            p, q = inp[j - 1], inp[j]
            if inside(q):
                if not inside(p):
                    out.append(meet(p, q))
                out.append(q)
            elif inside(p):
                out.append(meet(p, q))
    return out


def _seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def _gap(a, b):
    """The distance between two convex polygons that do not overlap: a true point-to-edge distance,
    not a per-axis margin."""
    return min(min(_seg_dist(p, q[i - 1], q[i]) for p in r for i in range(len(q)))
               for r, q in ((a, b), (b, a)))


def _rect(m):
    (cx, cy), (along, across) = m["at"], m["size"]
    ca, sa = math.cos(math.radians(m["yaw"])), math.sin(math.radians(m["yaw"]))
    corners = [(-along / 2, -across / 2), (along / 2, -across / 2), (along / 2, across / 2),
               (-along / 2, across / 2)]
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in corners]


def _pieces(pkg):
    verts = []                                       # (plan x, plan y, is_void, file)
    parent = []

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def join(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    for path in sorted(glob.glob(os.path.join(pkg, "site_drains_*.obj"))):
        void = "_void_" in os.path.basename(path)
        base = len(verts)                            # an OBJ's indices are 1-based within its file
        for line in open(path, encoding="utf-8"):
            if line.startswith("v "):
                _, x, _h, z = line.split()[:4]
                verts.append((float(x), -float(z), void, os.path.basename(path)))
                parent.append(len(parent))
            elif line.startswith("f "):
                idx = [base + int(c.split("/")[0]) - 1 for c in line.split()[1:]]
                for k in idx[1:]:
                    join(idx[0], k)
    parts = {}
    for i in range(len(verts)):
        parts.setdefault(find(i), []).append(i)
    # parts whose plan boxes come within MERGE of each other are one piece
    boxes = []
    for members in parts.values():
        xs = [verts[i][0] for i in members]
        ys = [verts[i][1] for i in members]
        boxes.append([min(xs), min(ys), max(xs), max(ys), members])
    merged = True
    while merged:
        merged = False
        for a in range(len(boxes)):
            for b in range(a + 1, len(boxes)):
                A, B = boxes[a], boxes[b]
                if (A[0] - MERGE <= B[2] and B[0] - MERGE <= A[2]
                        and A[1] - MERGE <= B[3] and B[1] - MERGE <= A[3]):
                    boxes[a] = [min(A[0], B[0]), min(A[1], B[1]), max(A[2], B[2]), max(A[3], B[3]),
                                A[4] + B[4]]
                    del boxes[b]
                    merged = True
                    break
            if merged:
                break
    out = []
    for box in boxes:
        vs = [verts[i] for i in box[4]]
        hull = _hull([(round(v[0], 4), round(v[1], 4)) for v in vs])
        area = _area(hull)
        kind = "inlet" if any(v[2] for v in vs) else ("manhole" if area > 0.4 else "walk_cover")
        cx = sum(p[0] for p in hull) / len(hull)
        cy = sum(p[1] for p in hull) / len(hull)
        out.append({"kind": kind, "hull": hull, "area": area, "at": (cx, cy), "n": len(vs),
                    "files": sorted({v[3] for v in vs})})
    return sorted(out, key=lambda p: (p["kind"], round(p["at"][0], 2), round(p["at"][1], 2)))


def main():
    pkg, out_dir = sys.argv[1], sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else "site"
    manifest = json.load(open(os.path.join(out_dir, "%s.markings.json" % name), encoding="utf-8"))
    marks = manifest["markings"]
    pieces = _pieces(pkg)
    kinds = {}
    for p in pieces:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    # the count Lot printed when it stood them (the job's log, beside its out dir)
    log = open(os.path.join(os.path.dirname(os.path.abspath(out_dir)), "job.log"), encoding="utf-8",
               errors="replace").read()
    said = re.findall(r"\[lot\] drains: (\d+) manhole cover\(s\), (\d+) inlet\(s\), (\d+) sidewalk lid\(s\)",
                      log)
    if len(said) != 1:
        sys.exit("the job's log carries %d drains line(s), not one: nothing to check the count against"
                 % len(said))
    want = dict(zip(("manhole", "inlet", "walk_cover"), (int(n) for n in said[0])))
    got = {k: kinds.get(k, 0) for k in want}
    if got != want or sum(kinds.values()) != sum(want.values()):
        sys.exit("COUNT MISMATCH: the OBJs read as %s, Lot printed %s -- the clustering is wrong, "
                 "nothing below would be about the pieces" % (kinds, want))
    print("package: %s" % pkg)
    print("Lot printed %s; the OBJs read the same" % want)
    print("drains: %d piece(s) %s from %d OBJ(s); paint: %d marking(s) %s" % (
        len(pieces), kinds, len(glob.glob(os.path.join(pkg, "site_drains_*.obj"))), len(marks),
        dict(sorted((k, sum(1 for m in marks if m["kind"] == k)) for k in {m["kind"] for m in marks}))))
    print("frame: plan metres (Godot x, -z); a piece's footprint is the hull of its vertices")
    print()
    total = {}
    for p in pieces:
        rects = [(m, _rect(m)) for m in marks
                 if math.hypot(m["at"][0] - p["at"][0], m["at"][1] - p["at"][1])
                 < 2.0 + max(m["size"]) / 2.0]
        over, clear = [], []
        for m, r in rects:
            common = _clip(p["hull"], r)
            a = _area(common) if len(common) >= 3 else 0.0
            if a > 1e-6:
                over.append((m["kind"], a, m))
            else:
                clear.append((_gap(p["hull"], r), m["kind"]))
        line = "%-10s at (%8.3f, %8.3f)  hull %.3f m^2" % (p["kind"], p["at"][0], p["at"][1], p["area"])
        if over:
            share = sum(a for _k, a, _m in over) / p["area"]
            line += "  OVERLAPS %d marking(s), %.3f m^2 = %.1f %% of the piece: %s" % (
                len(over), sum(a for _k, a, _m in over), 100.0 * share,
                ", ".join("%s road %s at (%.3f, %.3f) %.3f m^2" % (k, m.get("road"), m["at"][0], m["at"][1], a)
                          for k, a, m in over))
            total[p["kind"]] = total.get(p["kind"], 0) + 1
        else:
            near = min(clear) if clear else None
            line += "  clear; nearest %s" % ("%s at %.3f m" % (near[1], near[0]) if near else "none within 2 m")
        print(line)
    print()
    print("pieces overlapping paint: %s of %d" % (total or "none", len(pieces)))


if __name__ == "__main__":
    main()
