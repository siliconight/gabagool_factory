"""Deli Counter 0.251.0's refurnish in the dc_routes_obj clone, attributed room by room against the factory's checkout
(0.250.0): per spec that moved, each room whose furnish-written pieces differ -- whether it holds an objective or loot
marker, its kind and area, pieces before -> after, floor share before -> after (`room_floor_share`). Then the totals:
rooms moved with and without a marker, and where the moved rooms' shares sit against the walker's 12-25 % band.
Read-only; the clone's modules are loaded for the clone's specs and the factory's for the factory's, each in its own
process (argv: which checkout to dump), so neither module set measures the other's specs.

    python routes_obj_rooms.py dump <checkout> <out.json>
    python routes_obj_rooms.py compare <before.json> <after.json>
"""
import collections
import json
import os
import re
import sys

if sys.argv[1] == "dump":
    dc, out = sys.argv[2], sys.argv[3]
    sys.path.insert(0, dc)
    import level_design as L  # noqa: E402
    import migrate_furnish_recipes as M  # noqa: E402
    assert os.path.samefile(L.__file__, os.path.join(dc, "level_design.py")), L.__file__
    res = {}
    for fn in sorted(os.listdir(os.path.join(dc, "specs"))):
        if not fn.endswith(".json") or fn.startswith("lf_"):
            continue
        d = json.load(open(os.path.join(dc, "specs", fn), encoding="utf-8"))
        if not d.get("rooms"):
            continue
        b = L.club_building_id(d)
        tags = {L._room_tag(r) for r in d["rooms"]}
        rooms = {}
        for r in d["rooms"]:
            tag = L._room_tag(r)
            mine = sorted("%s@%.2f,%.2f" % (v["name"], v["x"], v["y"]) for v in d.get("volumes") or []
                          if M.furnished_by_this_pass(v, tags) and re.search("_" + tag + "_", v["name"]))
            x0, y0, x1, y1 = r["bounds"]
            marker = (L.holds_route_marker(d, r) if hasattr(L, "holds_route_marker") else None)
            rooms[r["id"]] = {"tag": tag, "kind": L._room_kind(r, b), "area": round((x1 - x0) * (y1 - y0), 1),
                              "share": round(L.room_floor_share(d, r), 4), "pieces": mine, "marker": marker,
                              "story": r.get("story", 0)}
        rooms["__all__"] = {"tag": "", "kind": "", "area": 0, "share": 0, "story": 0, "marker": None,
                            "pieces": sorted(v["name"] for v in d.get("volumes") or [] if M.furnished_by_this_pass(v, tags))}
        res[fn[:-5]] = rooms
    json.dump(res, open(out, "w", encoding="utf-8"), indent=0)
    print("dumped", len(res), "specs from", dc)
    sys.exit(0)

before = json.load(open(sys.argv[2], encoding="utf-8"))
after = json.load(open(sys.argv[3], encoding="utf-8"))
assert sorted(before) == sorted(after)
moved, band = [], collections.Counter()
tot_b = sum(len(before[s]["__all__"]["pieces"]) for s in before)
tot_a = sum(len(after[s]["__all__"]["pieces"]) for s in after)
in_rooms = lambda side: sum(len(r["pieces"]) for s in side for k, r in side[s].items() if k != "__all__")
print("furnish's pieces, whole library: %d -> %d (%+d); assigned to a room by tag: %d -> %d"
      % (tot_b, tot_a, tot_a - tot_b, in_rooms(before), in_rooms(after)))
for spec in sorted(after):
    for rid, a in after[spec].items():
        if rid == "__all__":
            continue
        b = before[spec][rid]
        if a["pieces"] == b["pieces"]:
            continue
        moved.append((spec, rid, a, b))
print("rooms moved: %d in %d specs" % (len(moved), len({m[0] for m in moved})))
print("  holding a marker: %d; not: %d" % (sum(1 for m in moved if m[2]["marker"]),
                                           sum(1 for m in moved if not m[2]["marker"])))
for spec, rid, a, b in moved:
    if not a["marker"]:
        print("  NO MARKER: %s / %s (%s, %.0f m2) pieces %d -> %d" % (spec, rid, a["kind"], a["area"],
                                                                      len(b["pieces"]), len(a["pieces"])))


def where(s):
    return "under 12 %" if s < 0.12 else ("12-25 %" if s <= 0.25 else "over 25 %")


for spec, rid, a, b in moved:
    band[(where(b["share"]), where(a["share"]))] += 1
print("moved rooms by band, before -> after:", sorted(band.items()))
d_pieces = [len(a["pieces"]) - len(b["pieces"]) for _s, _r, a, b in moved]
d_share = [a["share"] - b["share"] for _s, _r, a, b in moved]
print("pieces per moved room: total %+d, fewest %+d, most %+d" % (sum(d_pieces), min(d_pieces), max(d_pieces)))
print("share per moved room: fewest %+.1f pts, most %+.1f pts" % (100 * min(d_share), 100 * max(d_share)))
print("by kind (rooms moved, pieces before -> after, mean share before -> after):")
by = collections.defaultdict(list)
for spec, rid, a, b in moved:
    by[a["kind"]].append((a, b))
for k, v in sorted(by.items(), key=lambda kv: -len(kv[1])):
    print("  %-18s %3d  %4d -> %4d  %.1f -> %.1f %%" % (k, len(v), sum(len(b["pieces"]) for a, b in v),
                                                        sum(len(a["pieces"]) for a, b in v),
                                                        100 * sum(b["share"] for a, b in v) / len(v),
                                                        100 * sum(a["share"] for a, b in v) / len(v)))
print("the 12 rooms that lost the most share:")
for spec, rid, a, b in sorted(moved, key=lambda m: m[2]["share"] - m[3]["share"])[:12]:
    print("  %-30s %-22s %-12s %6.0f m2  pieces %3d -> %3d  share %.1f -> %.1f %%"
          % (spec, rid, a["kind"], a["area"], len(b["pieces"]), len(a["pieces"]), 100 * b["share"], 100 * a["share"]))
