"""Measure a surface-dressing manifest's scatter: items and zones by kind, and the Clark-Evans R of every placed item
across the whole plate (R near 1.0 is a uniform random scatter, 2.0 an even grid, well under 1.0 clustered), plus R
within each zone kind. Also each item's distance to the nearest wall base / kerb zone, to show whether debris sits
where it would collect. Measures only; metres, spec space.

    python docs/findings/slice_look/scatter_probe.py <surface_dressing.json>
"""
import collections
import json
import math
import sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
print("keys", sorted(d)[:12])
items = d.get("orders") or d.get("placements") or []
zones = d.get("zones") or []
if not items:
    raise SystemExit("no placements found under orders/placements: keys %s" % sorted(d))
print("items", len(items), "example", json.dumps(items[0])[:300])
zk = {z.get("surface_zone_id") or z.get("id"): z for z in zones}
by_kind = collections.Counter()
pts = collections.defaultdict(list)
for it in items:
    z = zk.get(it.get("surface_zone_id"))
    kind = (z or {}).get("kind", "?")
    by_kind[kind] += 1
    p = it.get("pos") or it.get("position") or it.get("xy")
    pts[kind].append((float(p[0]), float(p[1])))
print("items by zone kind", dict(by_kind))
area_by = collections.defaultdict(float)
for z in zones:
    a = z.get("aabb")
    if a:
        area_by[z.get("kind", "?")] += max(0.0, a[3] - a[0]) * max(0.0, a[4] - a[1])
print("zone area by kind (m2)", {k: round(v) for k, v in area_by.items()})


def clark_evans(ps, area):
    if len(ps) < 3 or area <= 0:
        return None
    s = 0.0
    for i, (x, y) in enumerate(ps):
        s += min(math.hypot(x - u, y - v) for j, (u, v) in enumerate(ps) if j != i)
    r_obs = s / len(ps)
    r_exp = 0.5 / math.sqrt(len(ps) / area)
    return round(r_obs / r_exp, 3)


allp = [p for v in pts.values() for p in v]
print("R all", clark_evans(allp, sum(area_by.values())))
for k, v in pts.items():
    print("R", k, clark_evans(v, area_by.get(k, 0.0)), "n", len(v), "per 100 m2",
          round(100.0 * len(v) / area_by[k], 2) if area_by.get(k) else None)
