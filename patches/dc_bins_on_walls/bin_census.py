"""Where furnish's litter bins stand, and what the five recipes' rooms hold, over every preset at N seeds built in
memory: the recipes as the repo has them, and (--wall) with litter_bin a wall piece out of every cluster and into the
five recipes' wall runs, patched in memory only. Measurements, by arrangement.py's reasons.

    python bin_census.py <deli_counter> <seeds> [--wall]
"""
import collections
import os
import sys

DC = os.path.abspath(sys.argv[1])
sys.path.insert(0, DC)
import level_design as L  # noqa: E402
import arrangement as A  # noqa: E402
import presets  # noqa: E402

KINDS = ("mechanical", "kitchen", "lobby", "hall", "shop_floor", "corridor", "hallway")
if "--wall" in sys.argv:
    L._PIECES["litter_bin"] = dict(L._PIECES["litter_bin"], where="wall")
    for k in ("mechanical", "kitchen", "lobby", "hall", "shop_floor"):
        r = L._RECIPES[k]
        cl = tuple((tuple(x for x in pool if x != "litter_bin"), lo, hi) for pool, lo, hi in r["clusters"])
        L._RECIPES[k] = dict(r, wall=tuple(r["wall"]) + ("litter_bin",), clusters=tuple(c for c in cl if c[0]))

bins = collections.Counter()
stems = collections.defaultdict(collections.Counter)
rooms_n = collections.Counter()
for key in sorted(presets.REGISTRY):
    for seed in range(int(sys.argv[2])):
        s = presets.make(key, name="%s_bc_%d" % (key, seed), seed=seed)
        s = s if isinstance(s, dict) else s.to_dict()
        building = L.club_building_id(s)
        rooms = {r["id"]: r for r in s.get("rooms") or [] if r.get("bounds")}
        for rid, ps in A.standing(s).items():
            if rid not in rooms:
                continue
            kind = L._room_kind(rooms[rid], building)
            got = A.reasons(rooms[rid], ps)
            if kind in KINDS:
                rooms_n[kind] += 1
            for v, why in got:
                if A.producer(v, rooms[rid]) != "furnish":
                    continue
                st = A.stem(v["name"], rid)
                if st == "litter_bin":
                    bins[why] += 1
                if kind in KINDS:
                    stems[kind][st] += 1
print("furnish's litter bins by reason:", dict(bins), "total", sum(bins.values()))
for k in KINDS:
    print("  %-11s rooms %3d  %s" % (k, rooms_n[k], ", ".join("%s %d" % kv for kv in sorted(stems[k].items()))))
