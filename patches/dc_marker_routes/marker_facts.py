"""Facts the 0.251.0 tests will assert, read off the dc_routes_obj clone's library with its own modules: (1) every
shelter-pass piece (`*_shelter`, and a bare room's `seed_cover` cover) standing in a room that reserves routes, and
whether it stands on them; (2) every cluster (dressing) piece in a marker room on its routes; (3) the rooms of
`office` and `deli_a03` that hold a marker, in furnish's order. Read-only."""
import json
import os
import sys

dc = sys.argv[1]
sys.path.insert(0, dc)
import level_design as L  # noqa: E402
import migrate_furnish_recipes as M  # noqa: E402

assert os.path.samefile(L.__file__, os.path.join(dc, "level_design.py"))
on_shelter, off_shelter, on_dress, dress_n, rooms_n = [], 0, [], 0, 0
for fn in sorted(os.listdir(os.path.join(dc, "specs"))):
    if not fn.endswith(".json") or fn.startswith("lf_"):
        continue
    d = json.load(open(os.path.join(dc, "specs", fn), encoding="utf-8"))
    if not d.get("rooms"):
        continue
    b = L.club_building_id(d)
    for room in d["rooms"]:
        mode = L.reserves_routes(d, room, b)
        if not mode:
            continue
        rooms_n += 1
        routes = L.protected_routes(L.unfurnished(d), room)
        tag = L._room_tag(room)
        x0, y0, x1, y1 = room["bounds"]
        sh = L._story_height(d)
        floor = room.get("story", 0) * sh
        for v in d.get("volumes") or []:
            if not (x0 <= v["x"] <= x1 and y0 <= v["y"] <= y1):
                continue
            if not L.stands_on_storey(float(v.get("z", 0)), float(v.get("size_z", 0)), floor, sh):
                continue
            name = str(v.get("name") or "")
            if name.endswith("_" + room["id"] + "_shelter"):
                if L.on_protected_route(routes, v["x"], v["y"], v["size_x"] - 0.01, v["size_y"] - 0.01):
                    on_shelter.append((fn, room["id"], name))
                else:
                    off_shelter += 1
            m = M._GENERATED.match(name)
            if mode == "dressing" and m and m.group("tag") == tag:
                kind = L._room_kind(room, b)
                recipe = L._RECIPES[kind]
                pools = list(recipe.get("clusters") or ())
                if room.get("story", 0) < 0 and kind not in ("basement", "vault", "corridor", "wine_cellar"):
                    pools.append(L._BASEMENT_CLUSTER)
                clustered = {s for pool, _lo, _hi in pools for s in pool}
                functional = set()
                for key in ("anchors", "wall", "floor", "fixtures"):
                    functional |= set(recipe.get(key) or ())
                stem = m.group("stem")
                if stem in clustered and stem not in functional:
                    dress_n += 1
                    if L.on_protected_route(routes, v["x"], v["y"], v["size_x"] - 0.01, v["size_y"] - 0.01):
                        on_dress.append((fn, room["id"], name))
print("rooms that reserve routes:", rooms_n)
print("shelter pieces in them: %d off their routes, %d on: %s" % (off_shelter, len(on_shelter), on_shelter[:10]))
print("dressing pieces in marker rooms: %d, on their routes: %d %s" % (dress_n, len(on_dress), on_dress[:10]))
for name in ("office", "deli_a03"):
    d = json.load(open(os.path.join(dc, "specs", name + ".json"), encoding="utf-8"))
    b = L.club_building_id(d)
    print(name, [(r["id"], L.reserves_routes(d, r, b)) for r in d["rooms"] if L.reserves_routes(d, r, b)])
