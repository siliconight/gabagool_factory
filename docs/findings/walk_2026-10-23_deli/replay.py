"""Replay seed_cover + furnish on deli_a03 with the furnished/seeded pieces
stripped, in memory, and compare to the shipped spec. Prints what it measured."""
import copy, json, re, sys
sys.path.insert(0, r"C:\Projects\gabagool_studios\gabagool_factory\deli_counter")
import level_design as ld

SPEC = r"C:\Projects\gabagool_studios\gabagool_factory\deli_counter\specs\deli_a03.json"
d = json.load(open(SPEC, encoding="utf-8"))
ROOMS = ("upper_hall", "manager_office")
rooms = {r["id"]: r for r in d["rooms"]}
sh = d["story_height"]

def in_room(v, r):
    x0, y0, x1, y1 = r["bounds"]
    return (x0 <= v["x"] <= x1 and y0 <= v["y"] <= y1 and
            ld.stands_on_storey(float(v["z"]), float(v["size_z"]), r["story"] * sh, sh))

shipped = {rid: [v for v in d["volumes"] if in_room(v, rooms[rid])] for rid in ROOMS}

base = ld.unfurnished(d)
seedpat = re.compile(r"_(%s)_(\d+|shelter)$" % "|".join(r["id"] for r in d["rooms"]))
base = dict(base, volumes=[v for v in base["volumes"] if not seedpat.search(v["name"])])
base = copy.deepcopy(base)
print("stripped", len(d["volumes"]) - len(base["volumes"]), "volumes")
for rid in ROOMS:
    r = rooms[rid]
    print(rid, "kind", ld._room_kind(r, ld.club_building_id(d)),
          "area", (r["bounds"][2]-r["bounds"][0])*(r["bounds"][3]-r["bounds"][1]),
          "bare_before_seed", not ld._room_has_cover(base, r),
          "needs_shelter", not ld._room_has_shelter(base, r),
          "reserves_routes", repr(ld.reserves_routes(base, r, ld.club_building_id(d))))

orig_plan = ld._furnish_plan
def plan(recipe, clusters, want, rng):
    items = orig_plan(recipe, clusters, want, rng)
    print("  plan want=%d:" % want, items)
    return items
ld._furnish_plan = plan
orig_move = None
n_seed = ld.seed_cover(base)
print("seed_cover added", n_seed)
for rid in ROOMS:
    print(rid, "have after seed", ld._room_volume_count(base, rooms[rid]),
          "target", ld._furnish_target((rooms[rid]["bounds"][2]-rooms[rid]["bounds"][0])*(rooms[rid]["bounds"][3]-rooms[rid]["bounds"][1])))
n_f = ld.furnish(base)
print("furnish added", n_f)
for rid in ROOMS:
    got = [v for v in base["volumes"] if in_room(v, rooms[rid])]
    key = lambda v: (v["name"], round(v["x"], 2), round(v["y"], 2), v["size_x"], v["size_y"], v.get("rot_z", 0))
    a, b = sorted(map(key, shipped[rid])), sorted(map(key, got))
    print(rid, "shipped", len(a), "replayed", len(b), "identical", a == b)
    for v in shipped[rid]:
        print("   %-34s kind=%-14s x=%7.2f y=%7.2f  %4.2fx%4.2fx%4.2f rot=%s" % (
            v["name"], v["name"].split("_")[0], v["x"], v["y"], v["size_x"], v["size_y"], v["size_z"], v.get("rot_z", 0)))
print("---- diffs")
for rid in ROOMS:
    got = [v for v in base["volumes"] if in_room(v, rooms[rid])]
    key = lambda v: (v["name"], round(v["x"], 2), round(v["y"], 2), v["size_x"], v["size_y"], v.get("rot_z", 0))
    A, B = set(map(key, shipped[rid])), set(map(key, got))
    for k in sorted(A - B): print(rid, "ONLY SHIPPED", k)
    for k in sorted(B - A): print(rid, "ONLY REPLAY ", k)
