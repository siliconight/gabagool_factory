"""For each corner-store selling floor in a Deli Counter checkout (argv[1]): the rows' axis as `_row_slots` decides it
(the room's own island, else the long axis), the span along it inside the faces, the room's own islands' extents along
it, and each endpoint `route_cost.endpoints` finds -- which wall it is on relative to the rows (an END wall, across
the rows' ends, or a SIDE wall, parallel to them) and its coordinate along the rows' axis. Prints measurements."""
import json
import math
import os
import sys

dc = sys.argv[1]
sys.path.insert(0, dc)
sys.path.insert(0, r"C:\Projects\gabagool_studios\gabagool_factory\docs\findings\furnish_route_cost")
import level_design as L  # noqa: E402
import route_cost as R  # noqa: E402

for fn in sorted(os.listdir(os.path.join(dc, "specs"))):
    if not fn.endswith(".json") or fn.startswith("lf_"):
        continue
    d = json.load(open(os.path.join(dc, "specs", fn), encoding="utf-8"))
    b = L.club_building_id(d)
    for room in d.get("rooms") or []:
        if not L.is_corner_store_floor(room, b):
            continue
        face = float(d.get("wall_thick", 0.3)) / 2.0
        x0, y0, x1, y1 = room["bounds"]
        cx0, cy0, cx1, cy1 = x0 + face, y0 + face, x1 - face, y1 - face
        floor = room.get("story", 0) * L._story_height(d)
        own = []
        for v in d.get("volumes") or []:
            if v.get("collision") == "none" or R.generated(d, v):
                continue
            vz, vh = float(v.get("z", 0)), float(v.get("size_z", 0))
            if abs(vz - vh / 2 - floor) > 0.05 or vh < L._ROW_OWN_MIN_H:
                continue
            sx, sy = float(v.get("size_x", 0)), float(v.get("size_y", 0))
            lng, dep = max(sx, sy), min(sx, sy)
            if not (L._ROW_OWN_DEPTH[0] <= dep <= L._ROW_OWN_DEPTH[1] and lng > dep):
                continue
            if min(v["x"] - sx / 2 - cx0, cx1 - v["x"] - sx / 2, v["y"] - sy / 2 - cy0, cy1 - v["y"] - sy / 2) \
                    < L._ROW_OWN_OFF_WALL:
                continue
            own.append(v)
        if own:
            o = min(own, key=lambda v: abs(v["x"] - (cx0 + cx1) / 2) + abs(v["y"] - (cy0 + cy1) / 2))
            along_x = o["size_x"] >= o["size_y"]
        else:
            along_x = (x1 - x0) >= (y1 - y0)
        a0, a1 = (cx0, cx1) if along_x else (cy0, cy1)
        print("%s / %s: rows along %s, span %.2f..%.2f; own islands along: %s" % (
            fn[:-5], room["id"], "x" if along_x else "y", a0, a1,
            [(round((v["x"] if along_x else v["y"]) - (v["size_x"] if along_x else v["size_y"]) / 2, 2),
              round((v["x"] if along_x else v["y"]) + (v["size_x"] if along_x else v["size_y"]) / 2, 2)) for v in own]))
        for k, lab, x, y in R.endpoints(d, room):
            if k not in ("door", "open"):
                continue
            # an END wall is across the rows' ends: for rows along x, the walls at x0 and x1
            on_end = (abs(x - (x0 + face + R.DOOR_IN)) < 0.1 or abs(x - (x1 - face - R.DOOR_IN)) < 0.1) if along_x \
                else (abs(y - (y0 + face + R.DOOR_IN)) < 0.1 or abs(y - (y1 - face - R.DOOR_IN)) < 0.1)
            print("    %-5s %-26s %s along %.2f" % (k, lab, "END " if on_end else "SIDE", x if along_x else y))
