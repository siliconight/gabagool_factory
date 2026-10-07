"""Rooms L12 calls reachable that a body cannot WALK to: every way in is a
breach, a window, or a drop. Over every spec in deli_counter/specs/.
Measures; names no cause.

    python walk_reach_census.py

L12 (layout_lint.reachability_findings) searches from EXT over every edge
`graph()` makes -- doors, garages, breaches, vaultable windows -- plus its
stair/ladder/ramp chains and floor-hole/hatch drops. This repeats that search
twice: once as L12 does, once over a copy of the spec whose openings are cut
down to doors, garages and vault doors, without the drops. A room in the
first set and not the second is reachable only by breaching, vaulting a
window or dropping through a hole.

The vault-door kind is kept apart from windows HERE because `graph()` labels
both "vault"; the filter acts on the raw opening kind before graph() sees it.
"""
import copy
import glob
import json
import os
import sys

DC = r"C:\Projects\gabagool_studios\gabagool_factory\deli_counter"
sys.path.insert(0, DC)
import layout_lint as LL  # noqa: E402

WALK_KINDS = ("door", "garage", "vault")


def reach(spec, walk_only):
    s = copy.deepcopy(spec)
    if walk_only:
        for w in s.get("partitions", []) + s.get("ext_walls", []):
            w["openings"] = [o for o in w.get("openings", []) if o.get("kind", "door") in WALK_KINDS]
    edges, _ = LL.graph(s)
    by = LL._rooms_by_story(s)

    def link(a, b):
        edges.setdefault(a, set()).add((b, "vert"))
        edges.setdefault(b, set()).add((a, "vert"))

    hx, hy = s["footprint_x"] / 2, s["footprint_y"] / 2
    for r in s.get("rooms", []):
        x0, y0, x1, y1 = r["bounds"]
        if x0 < -hx - 0.5 or x1 > hx + 0.5 or y0 < -hy - 0.5 or y1 > hy + 0.5:
            link(r["id"], "EXT")
    for st in list(s.get("stairs", [])) + list(s.get("ladders", [])):
        a, b = st.get("from_story"), st.get("to_story")
        if a is None or b is None:
            continue
        chain = [r["id"] for fl in range(min(a, b), max(a, b) + 1)
                 for r in [LL._room_at(by.get(fl, []), st.get("x", 0), st.get("y", 0))] if r]
        for i in range(len(chain) - 1):
            link(chain[i], chain[i + 1])
    for rp in s.get("ramps", []):
        a = LL._room_at(by.get(rp.get("from_story", 0), []), rp.get("x", 0), rp.get("y", 0))
        b = LL._room_at(by.get(rp.get("to_story", 0), []), rp.get("x", 0), rp.get("y", 0))
        if a and b:
            link(a["id"], b["id"])
    if not walk_only:
        for vl in s.get("vertical_links", []):
            if vl.get("kind") in ("floor_hole", "hatch") and vl.get("x") is not None:
                st_ = vl.get("story", 0)
                a = LL._room_at(by.get(st_, []), vl["x"], vl["y"])
                b = LL._room_at(by.get(st_ - 1, []), vl["x"], vl["y"])
                if a and b:
                    link(a["id"], b["id"])
    seen, stk = {"EXT"}, ["EXT"]
    while stk:
        u = stk.pop()
        for v, _k in edges.get(u, ()):
            if v not in seen:
                seen.add(v)
                stk.append(v)
    return seen


def main():
    paths = sorted(glob.glob(os.path.join(DC, "specs", "*.json")))
    n_specs = n_rooms = 0
    hits = []
    for p in paths:
        spec = json.load(open(p, encoding="utf-8"))
        if not spec.get("rooms") or "footprint_x" not in spec:
            continue
        n_specs += 1
        n_rooms += len(spec["rooms"])
        full = reach(spec, False)
        walk = reach(spec, True)
        for r in spec["rooms"]:
            if r["id"] in full and r["id"] not in walk:
                hits.append((os.path.basename(p), r["id"], r.get("story"), r.get("role")))
    print("%d specs with rooms, %d rooms; %d reachable by L12 but not on foot, in %d specs"
          % (n_specs, n_rooms, len(hits), len({h[0] for h in hits})))
    for h in hits:
        print("   %-34s %-26s story %-3s role %s" % h)


if __name__ == "__main__":
    main()
