"""route_cost.json read by room kind: per kind (a corner store's selling floor apart), the pairs joined in both arms,
those that grow over 10 % and those furnishing narrows from two abreast to single file -- against the AUTHORED arm
(all furnishing) and, where the census has it, against the FUNCTIONAL arm (dressing alone, the guide's own B -> C);
then the same for every pair with an objective or loot marker at one end. A pair whose two endpoints share a cell (two
markers on one spot) has no length to compare and is left out, counted. Prints measurements only.

    python by_kind.py [route_cost.json]
"""
import collections
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import route_cost as R  # noqa: E402

src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "route_cost.json"
rows = json.loads(src.read_text(encoding="utf-8"))
specs = {}
by_kind = collections.defaultdict(collections.Counter)
obj, obj_r, same_cell = collections.Counter(), [], 0
three = all("functional" in r["arms"] for r in rows)
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
            c = by_kind[tag]
            c["pairs"] += 1
            c["grew"] += lf / la > 1.10
            c["narrowed"] += ba >= R.TWO_ABREAST > bf
            if three:
                b = r["arms"]["functional"]
                lb, bb = b["length"].get(k), b["bottleneck"].get(k, 0.0)
                c["dressing grew"] += bool(lb) and lf / lb > 1.10
                c["dressing narrowed"] += bb >= R.TWO_ABREAST > bf
            if {r["endpoints"][p][0], r["endpoints"][q][0]} & set(R.MARK_KINDS):
                obj["pairs"] += 1
                obj["grew"] += lf / la > 1.10
                obj["narrowed"] += ba >= R.TWO_ABREAST > bf
                obj_r.append(lf / la)
                if three:
                    lb = r["arms"]["functional"]["length"].get(k)
                    obj["dressing grew"] += bool(lb) and lf / lb > 1.10
cols = ["pairs", "grew", "narrowed"] + (["dressing grew", "dressing narrowed"] if three else [])
print("%-20s" % "room kind" + "".join("%19s" % c for c in cols))
for k, c in sorted(by_kind.items(), key=lambda kv: (-(kv[1]["grew"] + kv[1]["narrowed"]), kv[0])):
    print("%-20s" % k + "".join("%19d" % c[col] for col in cols))
v = np.array(obj_r)
print("pairs with an objective or loot marker at one end: %d; grew over 10 %%: %d; two abreast -> one: %d%s; "
      "FURNISHED / AUTHORED median %.3f, p90 %.3f, max %.3f"
      % (obj["pairs"], obj["grew"], obj["narrowed"],
         ("; dressing grew over 10 %%: %d" % obj["dressing grew"]) if three else "",
         np.median(v), np.percentile(v, 90), v.max()))
print("pairs left out, both endpoints on one cell: %d" % same_cell)
