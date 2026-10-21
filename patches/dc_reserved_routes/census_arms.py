"""The route census on the corner-store specs of one Deli Counter checkout (argv[1]), with that checkout's modules
loaded first so `route_cost.py` measures it; prints the census's summary over those specs and, per corner-store
floor, its floor share and its generated gondolas. Writes nothing."""
import json
import os
import sys

dc = sys.argv[1]
sys.path.insert(0, dc)
import level_design  # noqa: E402,F401  -- the checkout's, before route_cost asks for it
import migrate_furnish_recipes  # noqa: E402,F401
import partition_bounds  # noqa: E402,F401
import stairwell  # noqa: E402,F401
import spec_types  # noqa: E402,F401
sys.path.insert(0, r"C:\Projects\gabagool_studios\gabagool_factory\docs\findings\furnish_route_cost")
import route_cost as R  # noqa: E402

L = R.L
assert os.path.samefile(L.__file__, os.path.join(dc, "level_design.py")), L.__file__
rows, floors = [], []
for fn in sorted(os.listdir(os.path.join(dc, "specs"))):
    if not fn.endswith(".json") or fn.startswith("lf_"):
        continue
    d = json.load(open(os.path.join(dc, "specs", fn), encoding="utf-8"))
    b = L.club_building_id(d)
    corner = [r for r in d.get("rooms") or [] if L.is_corner_store_floor(r, b)]
    if not corner:
        continue
    rows.extend(R.measure_spec(d, fn[:-5]))
    for r in corner:
        tag = L._room_tag(r)
        g = sum(1 for v in d["volumes"] if v["name"].startswith("gondola_aisle_" + tag))
        floors.append("%-22s %-14s share %.3f  generated gondolas %d" % (fn[:-5], r["id"], L.room_floor_share(d, r), g))
print("\n".join(R.summarise(rows)))
print()
print("\n".join(floors))
