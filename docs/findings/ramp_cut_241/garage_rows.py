"""The drop-edge rows round one building, in the building's own frame: what each edge stands on, what it drops to,
how far, and whether the gate counts it indoors.

    python docs/findings/ramp_cut_241/garage_rows.py <drop_edges.json> <building x> <building y> [x0 x1 y0 y1]

Reads Level Factory's `drop_edges.json` (`lf.walkable_edge.v1`): `edges[]` in Godot metres (x, y up, z), `owners[]`
naming each collider. The building's plan position is Lot's `at` (plan x, plan y), and plan y is Godot -z; the window
is in the building's frame (default: 0..25 by -20..20). Refuses a report of another shape. Prints what it read.
"""
import json
import sys

path, ax, ay = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
x0, x1, y0, y1 = (float(v) for v in sys.argv[4:8]) if len(sys.argv) > 7 else (0.0, 25.0, -20.0, 20.0)
rep = json.load(open(path, encoding="utf-8"))
if rep.get("schema") != "lf.walkable_edge.v1" or not isinstance(rep.get("edges"), list):
    raise SystemExit("UNRECOGNISED: %s is %r, not lf.walkable_edge.v1 with edges[]" % (path, rep.get("schema")))
own = rep["owners"]


def tail(i):
    return "none" if i is None or int(i) < 0 else "/".join(str(own[int(i)]).split("/")[-2:])


rows = []
for r in rep["edges"]:
    lx, ly = r["x"] - ax, -r["z"] - ay
    if x0 < lx < x1 and y0 < ly < y1:
        rows.append((round(lx, 2), round(ly, 2), r["y"], r["drop_m"], tail(r["on"]), tail(r["to"]), r["indoors"]))
print("%d edges in the report, %d in the window; local x, local y, height, drop, on -> to, indoors"
      % (len(rep["edges"]), len(rows)))
for row in sorted(rows):
    print("%6.2f %6.2f %5.2f %5.2f  %-26s -> %-26s %s" % row)
