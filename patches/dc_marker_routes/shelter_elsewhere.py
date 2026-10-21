"""Find marker rooms of the dc_routes_obj clone's library where the shelter pass has an elsewhere: stripped of furnish's
pieces and the shelter pass's, it stands its piece at P asked no route; given a thin route (half 0.30 m, along x)
through P, it stands it off that route. Prints the first few, smallest first. Read-only."""
import copy
import glob
import json
import os
import sys

dc = sys.argv[1]
sys.path.insert(0, dc)
import level_design as L  # noqa: E402
import migrate_furnish_recipes as M  # noqa: E402

found = []
real = L.protected_routes
for p in sorted(glob.glob(os.path.join(dc, "specs", "*.json"))):
    if os.path.basename(p).startswith("lf_"):
        continue
    d = json.load(open(p, encoding="utf-8"))
    if not d.get("rooms"):
        continue
    b = L.club_building_id(d)
    for room in d["rooms"]:
        if L.reserves_routes(d, room, b) != "dressing":
            continue
        tag = L._room_tag(room)
        rid = room["id"]
        d0 = copy.deepcopy(d)
        d0["volumes"] = [v for v in d0["volumes"] if not v["name"].endswith("_" + rid + "_shelter")
                         and not (M._GENERATED.match(v["name"]) and "_" + tag + "_" in v["name"])]

        def shelter(routes):
            L.protected_routes = lambda spec, rm: routes if rm["id"] == rid else []
            try:
                dd = copy.deepcopy(d0)
                L.seed_cover(dd)
            finally:
                L.protected_routes = real
            return [v for v in dd["volumes"] if v["name"].endswith("_" + rid + "_shelter")]

        free = shelter([])
        if len(free) != 1:
            continue
        x0, y0, x1, y1 = room["bounds"]
        planted = [([(x0, free[0]["y"]), (x1, free[0]["y"])], 0.30)]
        second = shelter(planted)
        if len(second) == 1 and not L.on_protected_route(planted, second[0]["x"], second[0]["y"],
                                                         second[0]["size_x"] - 0.01, second[0]["size_y"] - 0.01):
            found.append(((x1 - x0) * (y1 - y0), os.path.basename(p)[:-5], rid, (free[0]["x"], free[0]["y"]),
                          (second[0]["x"], second[0]["y"])))
    if len(found) >= 6:
        break
for f in sorted(found):
    print("%6.1f m2  %s / %s  asked no route %s, planted route -> %s" % f)
