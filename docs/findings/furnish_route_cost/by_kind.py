"""route_cost.json read by room kind: per kind (a corner store's selling floor apart, Deli Counter 0.247.0's rows),
the pairs joined in both arms, those that grow over 10 % and those furnishing narrows from two abreast to single
file; then the same for every pair with an objective or loot marker at one end. A pair whose two endpoints share a
cell (two markers on one spot) has no length to compare and is left out, counted. Prints measurements only."""
import collections
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import route_cost as R  # noqa: E402

rows = json.loads((HERE / "route_cost.json").read_text(encoding="utf-8"))
specs = {}
by_kind = collections.defaultdict(collections.Counter)
obj, obj_r, same_cell = collections.Counter(), [], 0
for r in rows:
    d = specs.setdefault(r["spec"], json.loads((R.DC / "specs" / (r["spec"] + ".json")).read_text(encoding="utf-8")))
    room = next(x for x in d["rooms"] if x["id"] == r["room"])
    tag = "corner_store_floor" if R.L.is_corner_store_floor(room, R.L.club_building_id(d)) else r["kind"]
    n = len(r["endpoints"])
    for p in range(n):
        for q in range(p + 1, n):
            k = "%d-%d" % (p, q)
            a, f = r["arms"]["authored"], r["arms"]["furnished"]
            la, lf = a["length"].get(k), f["length"].get(k)
            if la is None or lf is None:
                continue
            if la <= 0:
                same_cell += 1
                continue
            ba, bf = a["bottleneck"].get(k, 0.0), f["bottleneck"].get(k, 0.0)
            grew, narrowed = lf / la > 1.10, ba >= R.TWO_ABREAST > bf
            c = by_kind[tag]
            c["pairs"] += 1
            c["grew"] += grew
            c["narrowed"] += narrowed
            if {r["endpoints"][p][0], r["endpoints"][q][0]} & set(R.MARK_KINDS):
                obj["pairs"] += 1
                obj["grew"] += grew
                obj["narrowed"] += narrowed
                obj_r.append(lf / la)
print("%-20s %6s %16s %24s" % ("room kind", "pairs", "grew over 10 %", "two abreast -> one"))
for k, c in sorted(by_kind.items(), key=lambda kv: (-(kv[1]["grew"] + kv[1]["narrowed"]), kv[0])):
    print("%-20s %6d %16d %24d" % (k, c["pairs"], c["grew"], c["narrowed"]))
v = np.array(obj_r)
print("pairs with an objective or loot marker at one end: %d; grew over 10 %%: %d; two abreast -> one: %d; "
      "FURNISHED / AUTHORED median %.3f, p90 %.3f, max %.3f" % (obj["pairs"], obj["grew"], obj["narrowed"],
                                                               np.median(v), np.percentile(v, 90), v.max()))
print("pairs left out, both endpoints on one cell: %d" % same_cell)
