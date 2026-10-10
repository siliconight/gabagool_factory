"""Census of the ground BEHIND the row in every drawn site: where a rear service lane could run.

    python docs/findings/rear_lane/rear_census.py [<site.site.drawn.json> ...]
    python docs/findings/rear_lane/rear_census.py --cold        # every cold workspace's themed spec

Roadmap 230 step 3 and roadmap 199: the adjacency guide's `service_lane` / `rear_passage` behind
the row, with an owner and users, is the return loop every level lacks (every drawn site is a
T with two approaches and no cycle, `docs/findings/walkable_city/`). Before a tool lays one,
this measures what the ground behind the row is today, from the themed drawn spec alone:

- the ROW: the lot buildings, each one's rect from `at`, `_footprint` and `rot` (90/270 swap the
  sides), its FRONT the rect side nearest the nearest road's centreline (no rotation sign to
  guess), its REAR the opposite side; the row's axis is the main road's;
- the REAR BAND: from the row's farthest rear face (the yards with a dumpster, which stand on
  the rear wall, counted with their pads) to the plate edge on that side, over the row's length;
  its depth, and what stands in it: Empties (`blockers`), parking fields, cover, the side roads
  that reach into it (a lane could meet them) and how far they reach;
- the far side: whether the Empties' terrace stands across the main road (the other frontage) or
  behind the row.

It prints a row a site and stops. Whether a lane fits, where it meets the street and who uses
it is step 3's design, in the README beside this.
"""
import glob
import json
import math
import os
import sys

FACTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(FACTORY, "lot"))
try:
    import site_extent as _site_extent        # Lot's own rotated footprint, the frame the yards use
except Exception:                             # noqa: BLE001
    _site_extent = None


def _rect(at, w, d, rot):
    x, y = float(at[0]), float(at[1])
    if int(round(float(rot or 0))) % 180 == 90:
        w, d = d, w
    return (x - w / 2.0, y - d / 2.0, x + w / 2.0, y + d / 2.0)


def _building_rect(b):
    if _site_extent is not None:
        try:
            r = _site_extent.rotated_footprint(b)
            if r is not None:
                return tuple(float(v) for v in r)
        except Exception:                     # noqa: BLE001
            pass
    return _rect(b["at"], b["_footprint"][0], b["_footprint"][1], b.get("rot", 0))


def _dist_pt_seg(px, py, a, b):
    (ax, ay), (bx, by) = a, b
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _front_side(rect, roads):
    """The rect side nearest any road centreline: 'S', 'N', 'W' or 'E'."""
    x0, y0, x1, y1 = rect
    mids = {"S": ((x0 + x1) / 2.0, y0), "N": ((x0 + x1) / 2.0, y1),
            "W": (x0, (y0 + y1) / 2.0), "E": (x1, (y0 + y1) / 2.0)}
    best = None
    for side, (mx, my) in mids.items():
        d = min((_dist_pt_seg(mx, my, r["a"], r["b"]) for r in roads), default=1e9)
        if best is None or d < best[0]:
            best = (d, side)
    return best[1] if best else "S"


OPPOSITE = {"S": "N", "N": "S", "W": "E", "E": "W"}


def census(d):
    g = d.get("ground") or {}
    sx, sy = float(g.get("size_x", 0)), float(g.get("size_y", 0))
    roads = d.get("roads") or []
    bs = [b for b in d.get("buildings", []) if b.get("at") and b.get("_footprint")]
    if not bs or not roads or not sx:
        return {"name": d.get("name") or d.get("site_id"), "skipped": "no buildings, roads or plate"}
    rects = {b["id"]: _building_rect(b) for b in bs}
    fronts = {bid: _front_side(r, roads) for bid, r in rects.items()}
    # the row's rear side: the side most buildings turn their back to
    rear = max(set(OPPOSITE[f] for f in fronts.values()), key=lambda s: sum(1 for f in fronts.values() if OPPOSITE[f] == s))
    axis_x = rear in ("N", "S")           # the row runs along x, the rear normal is y
    sign = 1.0 if rear in ("N", "E") else -1.0
    edge = (sy / 2.0 if axis_x else sx / 2.0) * sign

    def along(r):
        return (r[0], r[2]) if axis_x else (r[1], r[3])

    def rear_face(r):
        if axis_x:
            return r[3] if sign > 0 else r[1]
        return r[2] if sign > 0 else r[0]

    faces = {bid: rear_face(r) for bid, r in rects.items()}
    row_lo = min(along(r)[0] for r in rects.values())
    row_hi = max(along(r)[1] for r in rects.values())
    # the yards with a dumpster stand on a wall; count the ones on the rear
    yard_out = []
    for y in d.get("yards", []) or []:
        at = y.get("at")
        if not at:
            continue
        s = (float(y.get("size_y", 0)) if axis_x else float(y.get("size_x", 0))) / 2.0
        c = float(at[1]) if axis_x else float(at[0])
        if (c - faces.get(y.get("building"), c)) * sign > -1e-6:
            yard_out.append(c + sign * s)
    rear_line = max((f * sign for f in faces.values())) * sign
    rear_with_yards = max([rear_line * sign] + [v * sign for v in yard_out]) * sign
    depth = (edge - rear_with_yards) * sign
    # what stands in the band behind the row
    def in_band(r):
        a, b = along(r)
        n0, n1 = ((r[1], r[3]) if axis_x else (r[0], r[2]))
        beyond = (max(n0, n1) if sign > 0 else min(n0, n1))
        return b > row_lo and a < row_hi and (beyond - rear_line) * sign > 0.5
    empties = d.get("blockers") or []
    e_rects = [_rect(e["at"], float(e.get("size_x", 6)), float(e.get("size_y", 12)), e.get("rot", 0)) for e in empties if e.get("at")]
    empties_behind = sum(1 for r in e_rects if in_band(r))
    empties_across = len(e_rects) - empties_behind
    fields_behind = []
    for f in d.get("fields", []) or []:
        r = f.get("rect")
        if r and in_band(tuple(r)):
            fields_behind.append((f.get("name"), round(f.get("depth", 0.0), 1), f.get("bays")))
    cover_behind = 0
    for c in d.get("cover", []) or []:
        at, s = c.get("at"), c.get("size", [1, 1, 1])
        if at and in_band((at[0] - s[0] / 2, at[1] - s[2] / 2, at[0] + s[0] / 2, at[1] + s[2] / 2)):
            cover_behind += 1
    # side roads reaching behind the row: a road end past the rear line, within the row's span
    reach = []
    for r in roads:
        for end in (r["a"], r["b"]):
            n = float(end[1]) if axis_x else float(end[0])
            a = float(end[0]) if axis_x else float(end[1])
            if (n - rear_line) * sign > 0.5 and row_lo - 5.0 <= a <= row_hi + 5.0:
                reach.append((round(a, 1), round((n - rear_line) * sign, 1)))
    main = max(roads, key=lambda r: math.hypot(r["b"][0] - r["a"][0], r["b"][1] - r["a"][1]))
    return {
        "name": d.get("name") or d.get("site_id"),
        "plate": (sx, sy),
        "shape": (d.get("site_shape_resolved") or {}).get("got", d.get("site_shape")),
        "buildings": len(bs),
        "fronts": "".join(fronts[b["id"]] for b in bs),
        "rear": rear,
        "row_m": round(row_hi - row_lo, 1),
        "rear_faces": [round(faces[b["id"]], 1) for b in bs],
        "rear_line": round(rear_line, 1),
        "yards_on_rear": len(yard_out),
        "rear_with_yards": round(rear_with_yards, 1),
        "edge": round(edge, 1),
        "band_depth_m": round(depth, 1),
        "empties_behind": empties_behind,
        "empties_across": empties_across,
        "fields_behind": fields_behind,
        "cover_behind": cover_behind,
        "roads": len(roads),
        "main_road_m": round(math.hypot(main["b"][0] - main["a"][0], main["b"][1] - main["a"][1]), 1),
        "side_roads_reaching_behind": reach,
        "fenced_runs": (d.get("perimeter") or {}).get("fenced_runs"),
    }


def main(argv):
    paths = argv
    if argv == ["--cold"]:
        paths = sorted(glob.glob(os.path.join(FACTORY, "workspaces", "cold-*-ws", ".level_factory", "jobs",
                                              "*.themed_site_assemble", "1", "out", "site.site.drawn.json")))
    for p in paths:
        d = json.load(open(p, encoding="utf-8"))
        row = census(d)
        ws = p.split(os.sep + "workspaces" + os.sep)[-1].split(os.sep)[0] if "workspaces" in p else os.path.basename(p)
        print(ws, json.dumps(row, separators=(", ", ": ")))


if __name__ == "__main__":
    main(sys.argv[1:])
