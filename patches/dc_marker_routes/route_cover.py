"""For named rooms of a Deli Counter checkout (argv[1]): their route endpoints, their reserved routes
(`protected_routes` on the unfurnished floor), and the share of the room's floor -- and of the part a cluster may stand
on, a body's width (1.0 m) in from the bounds as `_cluster` asks -- within a route's half width. Sampled on a 0.05 m
grid. Read-only."""
import json
import os
import sys

dc = sys.argv[1]
sys.path.insert(0, dc)
import level_design as L  # noqa: E402

assert os.path.samefile(L.__file__, os.path.join(dc, "level_design.py"))
ROOMS = [("twin_a01", "front_right_1"), ("auto_shop_a01", "parts_back"), ("video_store_a01", "stockroom"),
         ("clinic_a01", "dispensary"), ("funeral_home_a02", "records_office"), ("courthouse_a02", "records_room")]
for spec_name, rid in ROOMS:
    d = json.load(open(os.path.join(dc, "specs", spec_name + ".json"), encoding="utf-8"))
    room = next(r for r in d["rooms"] if r["id"] == rid)
    x0, y0, x1, y1 = room["bounds"]
    ends = L.room_route_endpoints(d, room)
    routes = L.protected_routes(L.unfurnished(d), room)
    step = 0.05
    n = m = in_r = in_m = 0
    y = y0 + step / 2
    while y < y1:
        x = x0 + step / 2
        while x < x1:
            hit = L.on_protected_route(routes, x, y, 0.0, 0.0)
            n += 1
            in_r += hit
            if x0 + 1.0 <= x <= x1 - 1.0 and y0 + 1.0 <= y <= y1 - 1.0:
                m += 1
                in_m += hit
            x += step
        y += step
    print("%s / %s: %.1f x %.1f m, kind %s; endpoints %s" % (spec_name, rid, x1 - x0, y1 - y0,
                                                             L._room_kind(room, L.club_building_id(d)),
                                                             [(e[0], e[1]) for e in ends]))
    print("    %d routes, %s; floor within a route %.0f %%, of a cluster's floor %.0f %%"
          % (len(routes), [len(p) for p, _h in routes], 100.0 * in_r / n, 100.0 * in_m / max(1, m)))
