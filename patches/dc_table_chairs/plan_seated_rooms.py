"""Plan views of rooms 0.252.0 moved, before (a Deli Counter checkout at 0.251.0) and after (one at 0.252.0): every
standing volume on the room's storey as a box -- furnish's dressing orange, its working furniture blue, a host's chairs
teal, the shelter pass's piece red, authored geometry grey -- the storey's partitions and door openings, the room's
objective and loot markers as crosses, and under them in yellow the routes the room reserves, if it reserves any
(`protected_routes` on the 0.252.0 checkout's unfurnished floor, half `two_abreast_width()` wide). The share printed
is `room_floor_share`. Writes plan_<spec>_<room>.png beside this file. Copied from
`patches/dc_marker_routes/plan_marker_rooms.py`, its versions changed and the chairs given a colour of their own.

    python patches/dc_table_chairs/plan_seated_rooms.py <0.251.0 checkout> <0.252.0 checkout> <spec>/<room> ...
"""
import json
import os
import pathlib
import sys

from PIL import Image, ImageDraw

HERE = pathlib.Path(__file__).resolve().parent
before_dc, after_dc = sys.argv[1], sys.argv[2]
sys.path.insert(0, after_dc)
import level_design as L  # noqa: E402  -- the 0.252.0 checkout's, which draws the routes
import migrate_furnish_recipes as M  # noqa: E402

assert os.path.samefile(L.__file__, os.path.join(after_dc, "level_design.py"))
S = 24  # px a metre
PAD = 1.5
# a table's, desk's and counter's chair is `chair_set_<tag>_<host>_<j>` (`_seats`); stools and club chairs are pieces
SEATS = set(L._SEAT_PIECES.values()) | {"chair_set"}


def dressing_stems(room, building):
    kind = L._room_kind(room, building)
    recipe = L._RECIPES[kind]
    pools = list(recipe.get("clusters") or ())
    if room.get("story", 0) < 0 and kind not in ("basement", "vault", "corridor", "wine_cellar"):
        pools.append(L._BASEMENT_CLUSTER)
    clustered = {s for pool, _lo, _hi in pools for s in pool}
    functional = set()
    for key in ("anchors", "wall", "floor", "fixtures"):
        functional |= set(recipe.get(key) or ())
    return clustered - functional


def panel(d, rid, routes, title):
    room = next(r for r in d["rooms"] if r["id"] == rid)
    b = L.club_building_id(d)
    x0, y0, x1, y1 = room["bounds"]
    W, H = int((x1 - x0 + 2 * PAD) * S), int((y1 - y0 + 2 * PAD) * S) + 30
    im = Image.new("RGB", (W, H), "white")
    g = ImageDraw.Draw(im)

    def P(x, y):
        return ((x - x0 + PAD) * S, (y1 + PAD - y) * S + 30)

    def box(cx, cy, sx, sy, fill, outline=None):
        a, c = P(cx - sx / 2, cy + sy / 2), P(cx + sx / 2, cy - sy / 2)
        g.rectangle([a, c], fill=fill, outline=outline)

    for pts, half in routes:
        w = int(2 * half * S)
        for p, q in zip(pts, pts[1:]):
            g.line([P(*p), P(*q)], fill=(255, 236, 140), width=w)
        for p in pts:
            cx, cy = P(*p)
            g.ellipse([cx - w / 2, cy - w / 2, cx + w / 2, cy + w / 2], fill=(255, 236, 140))
    st = room.get("story", 0)
    sh = L._story_height(d)
    t = float(d.get("wall_thick", 0.3))
    for p in d.get("partitions", []):
        if p.get("story", 0) != st:
            continue
        s, e = p["start"], p["end"]
        if str(p["axis"]).upper() == "Y":
            box(p["pos"], (s + e) / 2, t, e - s, (70, 70, 70))
        else:
            box((s + e) / 2, p["pos"], e - s, t, (70, 70, 70))
    for kind, label, ex, ey in L.room_route_endpoints(d, room):
        if kind in ("door", "open"):
            box(ex, ey, 0.4, 0.4, (40, 200, 40))
    floor = st * sh
    stems, tag = dressing_stems(room, b), L._room_tag(room)
    for v in d["volumes"]:
        if v.get("visual") is False or v.get("collision") == "none":
            continue
        if not L.stands_on_storey(float(v.get("z", 0)), float(v.get("size_z", 0)), floor, sh):
            continue
        vx, vy, sx, sy = v["x"], v["y"], v["size_x"], v["size_y"]
        if not (x0 - PAD < vx < x1 + PAD and y0 - PAD < vy < y1 + PAD) or sx * sy > 60:
            continue
        m = M._GENERATED.match(v["name"])
        if v["name"].endswith("_shelter"):
            col = (215, 40, 40)
        elif m and m.group("tag") == tag and m.group("stem") in SEATS:
            col = (40, 170, 160)
        elif m and m.group("tag") == tag and m.group("stem") in stems:
            col = (245, 150, 30)
        elif m and m.group("tag") == tag:
            col = (60, 110, 200)
        else:
            col = (160, 160, 160)
        box(vx, vy, sx, sy, col, (0, 0, 0))
    for mk in d.get("markers") or []:
        if mk.get("type") in ("objective", "loot") and x0 <= mk["x"] <= x1 and y0 <= mk["y"] <= y1 \
                and L.marker_on_storey(mk, floor, sh):
            cx, cy = P(mk["x"], mk["y"])
            g.line([cx - 7, cy - 7, cx + 7, cy + 7], fill=(0, 0, 0), width=3)
            g.line([cx - 7, cy + 7, cx + 7, cy - 7], fill=(0, 0, 0), width=3)
    a, c = P(x0, y1), P(x1, y0)
    g.rectangle([a, c], outline=(0, 0, 0), width=2)
    g.text((6, 6), "%s  share %.1f%%" % (title, 100 * L.room_floor_share(d, room)), fill=(0, 0, 0))
    return im


for arg in sys.argv[3:]:
    name, rid = arg.split("/")
    d0 = json.load(open(os.path.join(before_dc, "specs", name + ".json"), encoding="utf-8"))
    d1 = json.load(open(os.path.join(after_dc, "specs", name + ".json"), encoding="utf-8"))
    room1 = next(r for r in d1["rooms"] if r["id"] == rid)
    reserves = L.reserves_routes(d1, room1, L.club_building_id(d1))
    routes = L.protected_routes(L.unfurnished(d1), room1) if reserves else []
    a = panel(d0, rid, routes, "%s/%s at 0.251.0" % (name, rid))
    b = panel(d1, rid, routes, "at 0.252.0 (reserves %r)" % reserves)
    im = Image.new("RGB", (a.width + b.width + 20, max(a.height, b.height) + 24), "white")
    im.paste(a, (0, 0))
    im.paste(b, (a.width + 20, 0))
    ImageDraw.Draw(im).text((6, im.height - 18), "yellow: the routes the room reserves  orange: dressing  blue: working "
                            "furniture  teal: chairs  red: shelter  grey: authored  green: doors  X: objective/loot",
                            fill=(0, 0, 0))
    out = HERE / ("plan_%s_%s.png" % (name, rid))
    im.save(out)
    print("wrote", out.name, im.size)
