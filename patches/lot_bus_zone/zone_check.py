"""Lot 0.131.0's proof on a real site: in each arm's assembled outputs, the parked cars, meters and bay paint inside a
bus stop's zone. The zones are the clone's (`site.site.drawn.json`'s `bus_zones`); the base arm, 0.130.0, has none and
is read against the clone's to count what stood there before.

    python zone_check.py <base out dir> <clone out dir>

A car or meter is in a zone when its plan point projects inside the zone's span along its road and lies on the zone's
side; a bay tick when its centre does. Prints the counts per arm; exit 1 if the clone has any. Measurements only.
"""
import json
import math
import pathlib
import sys

base, clone = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
drawn = json.loads((clone / "site.site.drawn.json").read_text(encoding="utf-8"))
zones = drawn.get("bus_zones")
assert zones, "the clone records no bus_zones: not the clone this reads"
roads = drawn["roads"]


def frame(r):
    a, b = r["a"], r["b"]
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    return a, (ux, uy), (-uy, ux)


def in_zone(pt):
    for z in zones:
        a, (ux, uy), (px, py) = frame(roads[z["road"]])
        t = (pt[0] - a[0]) * ux + (pt[1] - a[1]) * uy
        s = (pt[0] - a[0]) * px + (pt[1] - a[1]) * py
        width = float(roads[z["road"]].get("width", 9.0))
        if z["t0"] <= t <= z["t1"] and (s > 0) == (z["side"] == "L") and abs(s) <= width / 2.0 + 0.5:
            return True
    return False


def in_zone_band(pt):
    """A meter stands on the sidewalk band beside the lane: the zone's span, its side, out to the band's edge."""
    for z in zones:
        r = roads[z["road"]]
        a, (ux, uy), (px, py) = frame(r)
        t = (pt[0] - a[0]) * ux + (pt[1] - a[1]) * uy
        s = (pt[0] - a[0]) * px + (pt[1] - a[1]) * py
        edge = float(r.get("width", 9.0)) / 2.0 + float(r.get("sidewalk", 0.0))
        if z["t0"] <= t <= z["t1"] and (s > 0) == (z["side"] == "L") and abs(s) <= edge + 0.5:
            return True
    return False


bad = 0
for name, d in (("base", base), ("clone", clone)):
    gp = json.loads((d / "site.site.gameplay.json").read_text(encoding="utf-8"))
    cars = (gp.get("parking_plan") or {}).get("placed") or []
    dr = json.loads((d / "site.site.drawn.json").read_text(encoding="utf-8"))
    meters = [c for c in dr.get("cover", []) if c.get("species") == "parking_meter"]
    marks = json.loads((d / "site.markings.json").read_text(encoding="utf-8"))
    marks = marks.get("markings", marks) if isinstance(marks, dict) else marks
    ticks = [m for m in marks if m.get("kind") == "bay_tick"]
    c_in = sum(in_zone(c["at"]) for c in cars)
    m_in = sum(in_zone_band(m["at"]) for m in meters)
    t_in = sum(in_zone(m["at"]) for m in ticks)
    print("%-5s cars %d (in a zone %d), meters %d (%d), bay ticks %d (%d)" % (
        name, len(cars), c_in, len(meters), m_in, len(ticks), t_in))
    if name == "clone":
        bad = c_in + m_in + t_in
sys.exit(1 if bad else 0)
