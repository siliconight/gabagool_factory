"""twin_a01's front_right_1 in a checkout (argv[1]), as the 0.251.0 test will ask it: strip the room's furnish pieces
and its shelter piece so it needs shelter whatever version furnished it; run the shelter pass asked no route, to find
where it stands the crate; plant a thin reserved route (half 0.30 m) through that spot and run it again. Does the
second crate stand off the planted route? Read-only (works on copies)."""
import copy
import json
import os
import sys

dc = sys.argv[1]
sys.path.insert(0, dc)
import level_design as L  # noqa: E402
import migrate_furnish_recipes as M  # noqa: E402

d0 = json.load(open(os.path.join(dc, "specs", "twin_a01.json"), encoding="utf-8"))
room = next(r for r in d0["rooms"] if r["id"] == "front_right_1")
tag = L._room_tag(room)
d0["volumes"] = [v for v in d0["volumes"]
                 if not str(v.get("name", "")).endswith("_front_right_1_shelter")
                 and not (M._GENERATED.match(str(v.get("name", ""))) and "_" + tag + "_" in v["name"])]
real = L.protected_routes


def shelter(routes):
    L.protected_routes = lambda spec, rm: (routes if rm["id"] == "front_right_1" else [])
    try:
        d = copy.deepcopy(d0)
        L.seed_cover(d)
    finally:
        L.protected_routes = real
    return [v for v in d["volumes"] if str(v.get("name", "")).endswith("_front_right_1_shelter")]


free = shelter([])
print("asked no route:", [(v["x"], v["y"]) for v in free])
if free:
    px, py = free[0]["x"], free[0]["y"]
    x0, y0, x1, y1 = room["bounds"]
    planted = [([(x0, py), (x1, py)], 0.30)]
    second = shelter(planted)
    for v in second:
        print("route planted through it: %s at (%.2f, %.2f) -- on the planted route: %s"
              % (v["name"], v["x"], v["y"], L.on_protected_route(planted, v["x"], v["y"], v["size_x"] - 0.01,
                                                                 v["size_y"] - 0.01)))
    if not second:
        print("route planted through it: no shelter piece placed")
