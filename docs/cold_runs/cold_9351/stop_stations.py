"""look_shots stations at each street payphone, from the road side of the sidewalk where a caller walks up.

    python docs/cold_runs/cold_9351/stop_stations.py <workspace> <mission> [--back 4.0]

Reads the mission's drawn site (`<mission>.themed_site_assemble/1/out/site.site.drawn.json`) for its roads and its
stop-corner pieces, and Lot's own road geometry (`lot/site_streets.roads`): for each payphone, the eye stands `--back`
metres from the phone toward the point on its road's centre line at the phone's station, at a person's 1.7 m, looking
at the phone 1.2 m up -- whichever way the phone faces, so a before and an after are shot from one place. Plan frame
(x, y) is Godot (x, -z). Prints `--station NAME:ex,ey,ez,tx,ty,tz`, look_shots' own; prints what it derived and stops.
"""
import json
import math
import os
import sys

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "lot"))
import site_streets  # noqa: E402

ws, mission = sys.argv[1], sys.argv[2]
back = float(sys.argv[sys.argv.index("--back") + 1]) if "--back" in sys.argv else 4.0
drawn = os.path.join(ws, ".level_factory", "jobs", f"{mission}.themed_site_assemble", "1", "out", "site.site.drawn.json")
spec = json.load(open(drawn, encoding="utf-8"))
roads = site_streets.roads(spec)
pieces = []


def walk(o):
    if isinstance(o, dict):
        if o.get("species") == "payphone" and o.get("source") == "site_furniture":
            pieces.append(o)
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(spec)
seen, out = set(), []
for p in pieces:
    if p["name"] in seen:
        continue
    seen.add(p["name"])
    road = roads[int(p["road"])]
    cx, cy = road.point(float(p["t"]), 0.0)
    px, py = p["at"]
    dx, dy = cx - px, cy - py
    n = math.hypot(dx, dy)
    ex, ey = px + dx / n * back, py + dy / n * back
    print("# %s: at (%.2f, %.2f) yaw %s, kerb %s of road %s, variant %s; eye at (%.2f, %.2f)"
          % (p["name"], px, py, p.get("yaw"), p.get("kerb"), p.get("road"), p.get("variant"), ex, ey), file=sys.stderr)
    out.append("--station %s:%.3f,1.7,%.3f,%.3f,1.2,%.3f" % (p["name"], ex, -ey, px, -py))
print(" ".join(out))
