"""The rooms whose door-to-marker routes the dressing lengthens most (route_cost.json at Deli Counter 0.250.0): per room,
its kind, size, floor share, endpoints, and for each pair with a marker at one end the three arms' lengths and
bottlenecks; then the dressing pieces furnish stood in it. Read-only."""
import json
import pathlib
import sys

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
sys.path.insert(0, str(F / "docs" / "findings" / "furnish_route_cost"))
import route_cost as R  # noqa: E402

rows = json.loads((F / "docs/findings/furnish_route_cost/route_cost.json").read_text(encoding="utf-8"))
MARK = set(R.MARK_KINDS)
flagged = []
for r in rows:
    n = len(r["endpoints"])
    for p in range(n):
        for q in range(p + 1, n):
            k = "%d-%d" % (p, q)
            b, f = r["arms"]["functional"], r["arms"]["furnished"]
            lb, lf = b["length"].get(k), f["length"].get(k)
            if lb and lf and lf / lb > 1.10:
                flagged.append((r, p, q, k))
specs = {}
for r, p, q, k in flagged:
    d = specs.setdefault(r["spec"], json.loads((R.DC / "specs" / (r["spec"] + ".json")).read_text(encoding="utf-8")))
    room = next(x for x in d["rooms"] if x["id"] == r["room"])
    building = R.L.club_building_id(d)
    kind = R.L._room_kind(room, building)
    x0, y0, x1, y1 = room["bounds"]
    area = (x1 - x0) * (y1 - y0)
    tag = R.L._room_tag(room)
    story = room.get("story", 0)
    sh = R.L._story_height(d)
    mine = [v for v in d.get("volumes") or [] if x0 <= v["x"] <= x1 and y0 <= v["y"] <= y1
            and R.L.stands_on_storey(float(v.get("z", 0)), float(v.get("size_z", 0)), story * sh, sh)
            and v.get("collision") != "none"]
    rooms_by_tag = {R.L._room_tag(x): x for x in d["rooms"]}
    dress = [v for v in mine if R.dressing(d, v, rooms_by_tag, building)]
    gen = [v for v in mine if R.generated(d, v, R._tags(d)) and v not in dress]
    share = sum(v["size_x"] * v["size_y"] for v in mine) / area
    e = r["endpoints"]
    print("%s / %s  kind %s  %.1f x %.1f m (%.1f m2)  floor share %.1f %%  endpoints %s"
          % (r["spec"], r["room"], kind, x1 - x0, y1 - y0, area, 100 * share, [x[:2] for x in e]))
    for arm in ("authored", "functional", "furnished"):
        a = r["arms"][arm]
        print("    %-10s %s -> %s  length %s  bottleneck %s" % (arm, e[p][1], e[q][1], a["length"].get(k),
                                                                a["bottleneck"].get(k)))
    print("    dressing:", sorted("%s %.2fx%.2f" % (v["name"], v["size_x"], v["size_y"]) for v in dress))
    print("    function (furnish's):", sorted("%s %.2fx%.2f" % (v["name"], v["size_x"], v["size_y"]) for v in gen))
