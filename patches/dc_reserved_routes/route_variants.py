"""Variants of the reserved routes, measured in memory: argv[1] the dc_cross clone (its code), argv[2] the real
deli_counter (0.249.0's specs, the starting library). For each variant -- the corridor's width and the spanner's
stretch -- every corner-store spec is stripped and refurnished by the clone's code with the variant's numbers
(`migrate_furnish_recipes.migrate`), then measured by `route_cost.py` and `room_floor_share`. Writes nothing."""
import copy
import json
import os
import sys

import numpy as np

clone, real = sys.argv[1], sys.argv[2]
sys.path.insert(0, clone)
import level_design as L  # noqa: E402
import migrate_furnish_recipes as M  # noqa: E402
import partition_bounds  # noqa: E402,F401
import stairwell  # noqa: E402,F401
import spec_types  # noqa: E402,F401
sys.path.insert(0, r"C:\Projects\gabagool_studios\gabagool_factory\docs\findings\furnish_route_cost")
import route_cost as R  # noqa: E402

specs = {}
for fn in sorted(os.listdir(os.path.join(real, "specs"))):
    if not fn.endswith(".json") or fn.startswith("lf_"):
        continue
    d = json.load(open(os.path.join(real, "specs", fn), encoding="utf-8"))
    if any(L.is_corner_store_floor(r, L.club_building_id(d)) for r in d.get("rooms") or []):
        specs[fn[:-5]] = d
base_two = L.two_abreast_width
VARIANTS = [("none (0.249.0)", None, None), ("two abreast, 1.10", 1.90, 1.10), ("aisle, 1.10", 1.25, 1.10),
            ("two abreast, 1.25", 1.90, 1.25), ("aisle, 1.25", 1.25, 1.25), ("two abreast, tree", 1.90, 1e9)]
for label, width, stretch in VARIANTS:
    rows, shares, gond = [], [], []
    for name, d0 in specs.items():
        d = copy.deepcopy(d0)
        if width is not None:
            L.two_abreast_width = (lambda w=width: w)
            L._ROUTE_STRETCH = stretch
            M.migrate(d)
        b = L.club_building_id(d)
        rows.extend(R.measure_spec(d, name))
        for r in d["rooms"]:
            if L.is_corner_store_floor(r, b):
                shares.append(L.room_floor_share(d, r))
                gond.append(sum(1 for v in d["volumes"] if v["name"].startswith("gondola_aisle_" + L._room_tag(r))))
    L.two_abreast_width = base_two
    ratios, narrowed = [], 0
    for r in rows:
        n = len(r["endpoints"])
        for p in range(n):
            for q in range(p + 1, n):
                k = "%d-%d" % (p, q)
                la, lf = r["arms"]["authored"]["length"].get(k), r["arms"]["furnished"]["length"].get(k)
                if la and lf:
                    ratios.append(lf / la)
                ba, bf = r["arms"]["authored"]["bottleneck"].get(k, 0), r["arms"]["furnished"]["bottleneck"].get(k, 0)
                narrowed += ba >= R.TWO_ABREAST > bf
    v, s = np.array(ratios), np.array(shares)
    print("%-20s pairs>10%% %3d  p90 %.3f  max %.3f  narrowed %3d | corner floors' share min %.3f median %.3f max "
          "%.3f, under 12 %%: %d of %d | gondolas %d" % (label, int((v > 1.10).sum()), np.percentile(v, 90), v.max(),
                                                       narrowed, s.min(), np.median(s), s.max(), int((s < 0.12).sum()),
                                                       len(s), sum(gond)))
