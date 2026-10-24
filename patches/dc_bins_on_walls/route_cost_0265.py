#!/usr/bin/env python3
"""What furnishing costs a route through a room: a census over Deli Counter's library.

The walker, 2026-10-21: rooms neither crowded nor barren, and "free navigation and fun gun fights" first. The guide
filed the same day (`docs/reference/Lived_In_Levels_Clear_Navigation_4P_PVE_1999_PA.md`) asks for widths measured
after furnishing (section 5) and a dressing traversal cost (section 14: flag a route that grows more than 10 %). Until
this, nothing in the factory compared a route with and without what furnish stands in a room: the nav gate asks
whether a marker is reachable, and a density change shipped with no number for what it did to movement.

THREE ARMS, ONE SPEC. AUTHORED is the spec less every volume furnish or the shelter pass wrote
(`migrate_furnish_recipes.furnished_by_this_pass`, `level_design._seeded_cover`): its walls, stairs, authored pieces,
queues and enclosures. FURNISHED is the spec as it ships. FUNCTIONAL (added the same day) is the spec less only
furnish's DRESSING (`dressing`: a cluster pool's stem the room's recipe places nowhere else) -- the guide's "B", its
functional build, where AUTHORED is nearer its blockout "A". FURNISHED / FUNCTIONAL is the guide's own section-14
measure, the dressing's traversal cost; FURNISHED / AUTHORED charges a store's rows and a room's desks too, which in
the guide's terms are the building's function, not its dressing.

ENDPOINTS of a room: each walkable opening bordering it (door, garage, a vault's leaf; partition and exterior, placed
by `partition_bounds.host_openings`, the builder's own arithmetic), each edge it is open to with no partition on it
(`open_to`), and each objective and loot marker standing in it. A door's endpoint is a body's centre 0.5 m inside the
wall's face.

PER PAIR OF ENDPOINTS, PER ARM, on a grid of the bake's cell (`nav_bake.cell_size_m`, 0.10 m), shifted 3.1 / 2.3 mm
off round coordinates so no cell centre sits on a seam:
  * LENGTH -- the shortest 8-connected path whose every cell centre keeps the body's radius
    (`characters.player.radius_m`, 0.35 m) from every obstacle;
  * BOTTLENECK -- the widest-path bottleneck: the largest clearance c such that the two are joined through cells of
    clearance >= c. A body of radius r passes when c >= r; the bake passes when 2c >= its door floor, derived here
    from the contract as the contract derives it (2 * ceil(agent_radius / cell) * cell + 2 * cell, 1.00 m). A door's
    own approach -- a 1.0 m disc round its endpoint -- counts as open, because the aperture is the door-width checks'
    question and a wall either side of a door would otherwise cap every bottleneck at the endpoint's own 0.5 m.
CLEARANCE is the Euclidean distance from a cell centre to the nearest obstacle, capped at 2.0 m: the wall boxes
`level_design._corridor_obstacles` stands (each `wall_thick` thick, centred on its line), each stair's body
(`stairwell.footprint_rect`) on the storeys it climbs through, authored slab holes on their storey, and every
standing collision volume on the storey (`_on_storey`, not `_hung`, `collision` not "none") by its axis-aligned
footprint -- `_seed_clear`'s own reading, so a chair turned a few degrees counts unturned. Both arms share every
obstacle but furnish's and the shelter pass's, so what differs between them is what those passes stood.

NOT MEASURED: a route that leaves the room (through a neighbour) -- a path is confined to its room's bounds; stair
guards and the hole a flight cuts in the storey above (only authored holes are obstacles); door leaves; anything a
navmesh does that geometry does not. Frame: spec plan coordinates, metres. Prints measurements; names no cause.

    python route_cost.py                    # the census: route_cost.out.txt and route_cost.json beside this file
    python route_cost.py --spec deli_a03    # one spec, printed
    python route_cost.py --controls         # the instrument's own controls; exit 1 on any failure
"""
import argparse
import heapq
import json
import math
import os
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
FACTORY = HERE.parents[1]
DC = FACTORY / "deli_counter"
sys.path.insert(0, str(DC))

import level_design as L  # noqa: E402
import migrate_furnish_recipes as MF  # noqa: E402
import partition_bounds as PB  # noqa: E402
import stairwell  # noqa: E402
from spec_types import Stairwell  # noqa: E402

_C = json.loads((DC / "agent_contract.json").read_text(encoding="utf-8"))
R_BODY = float(_C["characters"]["player"]["radius_m"])
_AGENT = float(_C["nav_bake"]["agent_radius_m"])
CELL = float(_C["nav_bake"]["cell_size_m"])
BAKE_DOOR_FLOOR = 2 * math.ceil(round(_AGENT / CELL, 9)) * CELL + 2 * CELL
C_BAKE = BAKE_DOOR_FLOOR / 2.0
OFFSET = (0.0031, 0.0023)
CAP = 2.0
DOOR_IN = 0.5
DOOR_ZONE = 1.0
SNAP = {"door": 0.6, "open": 0.6, "objective": 1.0, "loot": 1.0}
WALK_KINDS = ("door", "garage", "vault")
MARK_KINDS = ("objective", "loot")
MIN_AREA = 9.0
#: The guide's clear width for n bodies side by side (section 5), with its own margins on the contract's body:
#: n * 2r + 2 * 0.15 + (n - 1) * 0.20. Two abreast need 1.90 m, so a bottleneck clearance of 0.95.
TWO_ABREAST = (2 * 2 * R_BODY + 2 * 0.15 + 0.20) / 2.0
NEAR = 0.05


def _tags(d):
    return {L._room_tag(r) for r in d.get("rooms") or []}


def generated(d, v, tags=None):
    """Did furnish or the shelter pass write this volume?"""
    tags = _tags(d) if tags is None else tags
    if MF.furnished_by_this_pass(v, tags):
        return True
    return any(L._seeded_cover(v, r) for r in d.get("rooms") or [])


def dressing(d, v, rooms_by_tag, building):
    """Is this volume furnish's DRESSING -- the guide's "C" over its functional build "B"? A volume furnish wrote whose
    stem is in its room kind's cluster pools (with the basement's, as furnish adds it below ground) and in none of
    the kind's functional lists: anchors, wall run, floor sets, rows, fixtures. A table and its chairs, a desk, a shelf
    run, a gondola and a shelter piece are the room's working furniture; cartons, pallets, bins and dust sheets are
    what the guide calls story clusters and small accents."""
    m = MF._GENERATED.match(str(v.get("name") or ""))
    if not m or m.group("tag") not in rooms_by_tag:
        return False
    room = rooms_by_tag[m.group("tag")]
    kind = L._room_kind(room, building)
    recipe = L._RECIPES[kind]
    pools = list(recipe.get("clusters") or ())
    if room.get("story", 0) < 0 and kind not in ("basement", "vault", "corridor", "wine_cellar"):
        pools.append(L._BASEMENT_CLUSTER)
    clustered = {s for pool, _lo, _hi in pools for s in pool}
    functional = set()
    for key in ("anchors", "wall", "floor", "fixtures"):
        functional |= set(recipe.get(key) or ())
    if kind == "shop_floor":
        functional |= set(L._shop_rows(room, building) or ())
    stem = m.group("stem")
    return stem in clustered and stem not in functional


def obstacles(d, story, arm):
    """[(x0, y0, x1, y1)] on `story`, for `arm` "authored", "functional" or "furnished"."""
    sh = L._story_height(d)
    floor = story * sh
    out = list(L._corridor_obstacles(dict(d, volumes=[], stairs=[]), story, floor, sh))
    for s in d.get("stairs") or []:
        try:
            st = Stairwell(**{k: s[k] for k in L._STAIR_FIELDS if k in s})
        except TypeError:
            continue
        lo, hi = min(st.from_story, st.to_story), max(st.from_story, st.to_story)
        if lo <= story < hi:
            out.append(tuple(stairwell.footprint_rect(st)))
    for h in d.get("slab_holes") or []:
        if int(h.get("story", 0) or 0) == story:
            out.append((h["x"] - h["size_x"] / 2.0, h["y"] - h["size_y"] / 2.0,
                        h["x"] + h["size_x"] / 2.0, h["y"] + h["size_y"] / 2.0))
    tags = _tags(d)
    rooms_by_tag = {L._room_tag(r): r for r in d.get("rooms") or []}
    building = L.club_building_id(d)
    for v in d.get("volumes") or []:
        if v.get("collision") == "none":
            continue
        vz, vh = float(v.get("z", 0.0)), float(v.get("size_z", 0.0))
        if not L._on_storey(vz, vh, floor, sh) or L._hung(v, floor):
            continue
        if arm == "authored" and generated(d, v, tags):
            continue
        if arm == "functional" and dressing(d, v, rooms_by_tag, building):
            continue
        ax, ay = float(v.get("size_x", 1)) / 2.0, float(v.get("size_y", 1)) / 2.0
        out.append((v["x"] - ax, v["y"] - ay, v["x"] + ax, v["y"] + ay))
    return out


def _walkable(host):
    """A copy of a wall holding only its walkable openings, a vault's leaf named a door, for `host_openings`."""
    ops = [dict(op, kind="door") for op in host.get("openings") or []
           if op.get("kind", "door") in WALK_KINDS]
    return dict(host, openings=ops)


def endpoints(d, room):
    """[(kind, label, x, y)] for one room."""
    x0, y0, x1, y1 = room["bounds"]
    story = room.get("story", 0)
    sh = L._story_height(d)
    t = float(d.get("wall_thick", 0.3))
    hx, hy = d["footprint_x"] / 2.0, d["footprint_y"] / 2.0
    out = []
    for p in d.get("partitions") or []:
        if p.get("story", 0) != story:
            continue
        for along, _w, label in PB.host_openings(d, _walkable(p), False):
            if str(p.get("axis", "X")).upper() == "Y":
                if not (y0 - NEAR <= along <= y1 + NEAR):
                    continue
                if abs(p["pos"] - x0) < NEAR:
                    out.append(("door", label, x0 + t / 2 + DOOR_IN, along))
                elif abs(p["pos"] - x1) < NEAR:
                    out.append(("door", label, x1 - t / 2 - DOOR_IN, along))
            else:
                if not (x0 - NEAR <= along <= x1 + NEAR):
                    continue
                if abs(p["pos"] - y0) < NEAR:
                    out.append(("door", label, along, y0 + t / 2 + DOOR_IN))
                elif abs(p["pos"] - y1) < NEAR:
                    out.append(("door", label, along, y1 - t / 2 - DOOR_IN))
    for w in d.get("ext_walls") or []:
        if w.get("story", 0) != story:
            continue
        face = w.get("wall")
        for along, _w, label in PB.host_openings(d, _walkable(w), True):
            if face == "N" and abs(y1 - hy) < NEAR and x0 - NEAR <= along <= x1 + NEAR:
                out.append(("door", label, along, hy - t / 2 - DOOR_IN))
            elif face == "S" and abs(y0 + hy) < NEAR and x0 - NEAR <= along <= x1 + NEAR:
                out.append(("door", label, along, -hy + t / 2 + DOOR_IN))
            elif face == "E" and abs(x1 - hx) < NEAR and y0 - NEAR <= along <= y1 + NEAR:
                out.append(("door", label, hx - t / 2 - DOOR_IN, along))
            elif face == "W" and abs(x0 + hx) < NEAR and y0 - NEAR <= along <= y1 + NEAR:
                out.append(("door", label, -hx + t / 2 + DOOR_IN, along))
    rooms = {r["id"]: r for r in d.get("rooms") or []}
    joined = set(room.get("open_to") or [])
    joined |= {r["id"] for r in rooms.values() if room["id"] in (r.get("open_to") or [])}
    for rid in sorted(joined):
        n = rooms.get(rid)
        if n is None or n.get("story", 0) != story:
            continue
        a0, b0, a1, b1 = n["bounds"]
        for line, lo, hi, axis, inward in ((x1, max(y0, b0), min(y1, b1), "Y", -1), (x0, max(y0, b0), min(y1, b1), "Y", 1),
                                           (y1, max(x0, a0), min(x1, a1), "X", -1), (y0, max(x0, a0), min(x1, a1), "X", 1)):
            touching = (axis == "Y" and ((line == x1 and abs(a0 - x1) < NEAR) or (line == x0 and abs(a1 - x0) < NEAR))) or \
                       (axis == "X" and ((line == y1 and abs(b0 - y1) < NEAR) or (line == y0 and abs(b1 - y0) < NEAR)))
            if not touching or hi - lo < 1.0:
                continue
            walled = any(p.get("story", 0) == story and str(p.get("axis", "X")).upper() == axis
                         and abs(p["pos"] - line) < NEAR for p in d.get("partitions") or [])
            if walled:
                continue
            mid = (lo + hi) / 2.0
            if axis == "Y":
                out.append(("open", rid, line + inward * DOOR_IN, mid))
            else:
                out.append(("open", rid, mid, line + inward * DOOR_IN))
    for m in d.get("markers") or []:
        if m.get("type") in MARK_KINDS and x0 <= m.get("x", 1e9) <= x1 and y0 <= m.get("y", 1e9) <= y1 \
                and L.marker_on_storey(m, story * sh, sh):
            out.append((m["type"], m.get("id") or m["type"], float(m["x"]), float(m["y"])))
    return out


def grid(room):
    x0, y0, x1, y1 = room["bounds"]
    xs = np.arange(x0 + OFFSET[0] + CELL / 2.0, x1, CELL)
    ys = np.arange(y0 + OFFSET[1] + CELL / 2.0, y1, CELL)
    return xs, ys


def clearance(xs, ys, boxes):
    """Distance from each cell centre (ys x xs) to the nearest box, capped at CAP."""
    X, Y = np.meshgrid(xs, ys)
    c = np.full(X.shape, CAP)
    lo_x, hi_x, lo_y, hi_y = xs[0] - CAP, xs[-1] + CAP, ys[0] - CAP, ys[-1] + CAP
    for (bx0, by0, bx1, by1) in boxes:
        if bx1 < lo_x or bx0 > hi_x or by1 < lo_y or by0 > hi_y:
            continue
        dx = np.maximum(np.maximum(bx0 - X, 0.0), X - bx1)
        dy = np.maximum(np.maximum(by0 - Y, 0.0), Y - by1)
        np.minimum(c, np.hypot(dx, dy), out=c)
    return c


_STEPS = [(-1, -1, math.sqrt(2)), (-1, 0, 1.0), (-1, 1, math.sqrt(2)), (0, -1, 1.0),
          (0, 1, 1.0), (1, -1, math.sqrt(2)), (1, 0, 1.0), (1, 1, math.sqrt(2))]


def snap(c, xs, ys, x, y, radius, need):
    """The nearest cell to (x, y) within `radius` m whose clearance >= `need`, or None."""
    j = int(round((x - xs[0]) / CELL))
    i = int(round((y - ys[0]) / CELL))
    k = int(math.ceil(radius / CELL))
    best = None
    for di in range(-k, k + 1):
        for dj in range(-k, k + 1):
            a, b = i + di, j + dj
            if 0 <= a < c.shape[0] and 0 <= b < c.shape[1] and c[a, b] >= need:
                dd = math.hypot(xs[b] - x, ys[a] - y)
                if dd <= radius and (best is None or dd < best[0]):
                    best = (dd, a, b)
    return None if best is None else (best[1], best[2])


def lengths(c, starts, need):
    """{(p, q): metres} -- 8-connected shortest paths through cells of clearance >= need, between snapped endpoints."""
    H, W = c.shape
    free = c >= need
    out = {}
    cells = {k: v for k, v in starts.items() if v is not None}
    for p, (si, sj) in cells.items():
        want = {q: v for q, v in cells.items() if q != p and (min(p, q), max(p, q)) not in out}
        if not want:
            continue
        targets = {v: q for q, v in want.items()}
        dist = {(si, sj): 0.0}
        heap = [(0.0, si, sj)]
        found = 0
        while heap and found < len(targets):
            dd, i, j = heapq.heappop(heap)
            if dd > dist.get((i, j), 1e18):
                continue
            if (i, j) in targets:
                q = targets[(i, j)]
                out[(min(p, q), max(p, q))] = dd * CELL
                found += 1
            for di, dj, w in _STEPS:
                a, b = i + di, j + dj
                if 0 <= a < H and 0 <= b < W and free[a, b]:
                    nd = dd + w
                    if nd < dist.get((a, b), 1e18):
                        dist[(a, b)] = nd
                        heapq.heappush(heap, (nd, a, b))
    return out


def bottlenecks(c, xs, ys, eps, zones):
    """{(p, q): clearance} -- the widest-path bottleneck between endpoints, a union-find over cells taken in falling
    clearance. `zones[p]` is the disc radius round endpoint p counted as open (0 = its snapped cell alone)."""
    H, W = c.shape
    cc = c.copy()
    member = {}
    X, Y = np.meshgrid(xs, ys)
    for p, cell in eps.items():
        if cell is None:
            continue
        if zones[p] > 0:
            ex, ey = xs[cell[1]], ys[cell[0]]
            disc = np.hypot(X - ex, Y - ey) <= zones[p]
            idx = np.flatnonzero(disc & (c > 0))
        else:
            idx = np.array([cell[0] * W + cell[1]])
        cc.flat[idx] = np.inf
        for k in idx.tolist():
            member.setdefault(k, set()).add(p)
    flat = cc.ravel()
    order = np.argsort(-flat, kind="stable")
    parent = list(range(H * W))
    sets = {}
    active = bytearray(H * W)
    out = {}
    names = [p for p, cell in eps.items() if cell is not None]
    want = len(names) * (len(names) - 1) // 2

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for k in order.tolist():
        level = flat[k]
        if level <= 0 or len(out) >= want:
            break
        active[k] = 1
        sets[k] = set(member.get(k, ()))
        i, j = divmod(k, W)
        for di, dj, _w in _STEPS:
            a, b = i + di, j + dj
            if not (0 <= a < H and 0 <= b < W):
                continue
            n = a * W + b
            if not active[n]:
                continue
            ra, rb = find(k), find(n)
            if ra == rb:
                continue
            sa, sb = sets[ra], sets[rb]
            for p in sa:
                for q in sb:
                    if p != q:
                        key = (min(p, q), max(p, q))
                        if key not in out:
                            out[key] = min(float(level), CAP)
            if len(sa) < len(sb):
                ra, rb, sa, sb = rb, ra, sb, sa
            parent[rb] = ra
            sa |= sb
            sets[ra] = sa
            del sets[rb]
    return out


def measure_room(d, room, cache):
    x0, y0, x1, y1 = room["bounds"]
    area = max(0.0, x1 - x0) * max(0.0, y1 - y0)
    eps = endpoints(d, room)
    if area < MIN_AREA or len(eps) < 2:
        return None
    xs, ys = grid(room)
    story = room.get("story", 0)
    res = {"room": room["id"], "story": story, "area": round(area, 1),
           "kind": L._room_kind(room, L.club_building_id(d)),
           "endpoints": [(k, str(lab), round(x, 2), round(y, 2)) for k, lab, x, y in eps],
           "floor_share": round(L.room_floor_share(d, room), 4), "arms": {}}
    tags = _tags(d)
    res["generated_in_room"] = sum(1 for v in d.get("volumes") or []
                                   if generated(d, v, tags) and x0 <= v["x"] <= x1 and y0 <= v["y"] <= y1
                                   and L.stands_on_storey(float(v.get("z", 0)), float(v.get("size_z", 0)),
                                                          story * L._story_height(d), L._story_height(d)))
    for arm in ("authored", "functional", "furnished"):
        key = (story, arm)
        if key not in cache:
            cache[key] = obstacles(d, story, arm)
        c = clearance(xs, ys, cache[key])
        snapped = {p: snap(c, xs, ys, x, y, SNAP[k], R_BODY) for p, (k, _l, x, y) in enumerate(eps)}
        zones = {p: (DOOR_ZONE if eps[p][0] in ("door", "open") else 0.0) for p in snapped}
        ln = lengths(c, snapped, R_BODY)
        bn = bottlenecks(c, xs, ys, snapped, zones)
        res["arms"][arm] = {"unsnapped": [p for p, v in snapped.items() if v is None],
                            "length": {"%d-%d" % k: round(v, 3) for k, v in ln.items()},
                            "bottleneck": {"%d-%d" % k: round(v, 3) for k, v in bn.items()}}
    return res


def measure_spec(d, name):
    out = []
    cache = {}
    for room in d.get("rooms") or []:
        r = measure_room(d, room, cache)
        if r is not None:
            r["spec"] = name
            out.append(r)
    return out


def _pairs(r):
    n = len(r["endpoints"])
    return ["%d-%d" % (p, q) for p in range(n) for q in range(p + 1, n)]


def summarise(rows):
    """The census's measurements, as lines."""
    L_ = []
    pairs = [(r, k) for r in rows for k in _pairs(r)]
    L_.append("rooms measured (>= %.0f m2, >= 2 endpoints): %d in %d specs; endpoint pairs: %d"
              % (MIN_AREA, len(rows), len({r["spec"] for r in rows}), len(pairs)))
    L_.append("body radius %.2f m; the bake's door floor %.2f m (clearance %.2f); two abreast by the guide's formula "
              "%.2f m (clearance %.3f); grid %.2f m" % (R_BODY, BAKE_DOOR_FLOOR, C_BAKE, 2 * TWO_ABREAST, TWO_ABREAST,
                                                         CELL))
    ratios, lost_body, lost_bake, lost_two, both_none = [], [], [], [], 0
    for r, k in pairs:
        a, f = r["arms"]["authored"], r["arms"]["furnished"]
        la, lf = a["length"].get(k), f["length"].get(k)
        ba, bf = a["bottleneck"].get(k, 0.0), f["bottleneck"].get(k, 0.0)
        if la is not None and lf is not None and la > 0:
            ratios.append((lf / la, r, k, la, lf))
        if la is None and lf is None:
            both_none += 1
        if ba >= R_BODY and bf < R_BODY:
            lost_body.append((r, k, ba, bf))
        if ba >= C_BAKE and bf < C_BAKE:
            lost_bake.append((r, k, ba, bf))
        if ba >= TWO_ABREAST and bf < TWO_ABREAST:
            lost_two.append((r, k, ba, bf))
    if ratios:
        v = np.array([x[0] for x in ratios])
        L_.append("path length FURNISHED / AUTHORED, over the %d pairs joined in both: median %.3f, p90 %.3f, p99 %.3f, "
                  "max %.3f; > 1.10 (the guide's warning): %d pairs in %d rooms"
                  % (len(v), np.median(v), np.percentile(v, 90), np.percentile(v, 99), v.max(),
                     int((v > 1.10).sum()), len({(x[1]["spec"], x[1]["room"]) for x in ratios if x[0] > 1.10})))
    # THE GUIDE'S OWN MEASURE: dressing over the functional build (its section 14, B -> C)
    bc, bc_two, bc_body = [], 0, 0
    for r, k in pairs:
        if "functional" not in r["arms"]:
            continue
        b_, f = r["arms"]["functional"], r["arms"]["furnished"]
        lb, lf = b_["length"].get(k), f["length"].get(k)
        bb, bf = b_["bottleneck"].get(k, 0.0), f["bottleneck"].get(k, 0.0)
        if lb is not None and lf is not None and lb > 0:
            bc.append((lf / lb, r, k, lb, lf))
        bc_two += bb >= TWO_ABREAST > bf
        bc_body += bb >= R_BODY > bf
    if bc:
        v = np.array([x[0] for x in bc])
        L_.append("path length FURNISHED / FUNCTIONAL -- dressing over the functional build, the guide's own B -> C -- "
                  "over the %d pairs joined in both: median %.3f, p90 %.3f, p99 %.3f, max %.3f; > 1.10: %d pairs in %d "
                  "rooms; dressing narrows %d pairs from two abreast to single file and closes %d to a body"
                  % (len(v), np.median(v), np.percentile(v, 90), np.percentile(v, 99), v.max(), int((v > 1.10).sum()),
                     len({(x[1]["spec"], x[1]["room"]) for x in bc if x[0] > 1.10}), bc_two, bc_body))
    L_.append("pairs no body path joins in either arm (a door that cannot be reached for walls or stairs alone): %d"
              % both_none)
    L_.append("pairs furnishing closes to the body (bottleneck >= %.2f authored, < %.2f furnished): %d"
              % (R_BODY, R_BODY, len(lost_body)))
    L_.append("pairs furnishing closes to the bake (>= %.2f authored, < %.2f furnished): %d" % (C_BAKE, C_BAKE,
                                                                                             len(lost_bake)))
    L_.append("pairs furnishing narrows from two abreast to single file (>= %.3f authored, < %.3f furnished): %d"
              % (TWO_ABREAST, TWO_ABREAST, len(lost_two)))
    widths = np.array([2 * r["arms"]["furnished"]["bottleneck"].get(k, 0.0) for r, k in pairs])
    widths_a = np.array([2 * r["arms"]["authored"]["bottleneck"].get(k, 0.0) for r, k in pairs])
    for lab, w in (("AUTHORED", widths_a), ("FURNISHED", widths)):
        L_.append("bottleneck width, %s: < %.2f (no body) %d; < %.2f (under the bake's floor) %d; < %.2f (single file) "
                  "%d; >= %.2f %d" % (lab, 2 * R_BODY, int((w < 2 * R_BODY).sum()), BAKE_DOOR_FLOOR,
                                      int((w < BAKE_DOOR_FLOOR).sum()), 2 * TWO_ABREAST,
                                      int((w < 2 * TWO_ABREAST).sum()), 2 * TWO_ABREAST,
                                      int((w >= 2 * TWO_ABREAST).sum())))
    L_.append("")
    L_.append("the 20 longest detours (FURNISHED / AUTHORED):")
    for ratio, r, k, la, lf in sorted(ratios, key=lambda x: -x[0])[:20]:
        p, q = (int(s) for s in k.split("-"))
        L_.append("  %.3f  %-38s %-24s %s -> %s  %.1f -> %.1f m" % (ratio, r["spec"], r["room"], r["endpoints"][p][1],
                                                                    r["endpoints"][q][1], la, lf))
    L_.append("")
    L_.append("the 10 longest dressing detours (FURNISHED / FUNCTIONAL):")
    for ratio, r, k, lb, lf in sorted(bc, key=lambda x: -x[0])[:10]:
        p, q = (int(s) for s in k.split("-"))
        L_.append("  %.3f  %-38s %-24s %s -> %s  %.1f -> %.1f m" % (ratio, r["spec"], r["room"], r["endpoints"][p][1],
                                                                    r["endpoints"][q][1], lb, lf))
    for title, rowsx, thr in (("closed to the body", lost_body, R_BODY), ("closed to the bake", lost_bake, C_BAKE),
                              ("two abreast -> single file", lost_two, TWO_ABREAST)):
        L_.append("")
        L_.append("%s: %d (first 25, by the furnished bottleneck)" % (title, len(rowsx)))
        for r, k, ba, bf in sorted(rowsx, key=lambda x: x[3])[:25]:
            p, q = (int(s) for s in k.split("-"))
            L_.append("  %-38s %-24s %s -> %s  width %.2f -> %.2f m" % (r["spec"], r["room"], r["endpoints"][p][1],
                                                                        r["endpoints"][q][1], 2 * ba, 2 * bf))
    return L_


def controls():
    """The instrument's own checks. Each states what a correct instrument must read, and fails loudly."""
    fails = []

    def room_spec(vols, extra_doors=()):
        d = {"name": "ctl", "footprint_x": 10.0, "footprint_y": 6.0, "wall_thick": 0.3, "story_height": 3.0,
             "rooms": [{"id": "ctl_room", "story": 0, "bounds": [-5.0, -3.0, 5.0, 3.0], "combat_range": "medium"}],
             "partitions": [], "stairs": [], "markers": [],
             "ext_walls": [{"wall": "W", "story": 0, "openings": [{"kind": "door", "pos": 0.0, "width": 1.25}]},
                           {"wall": "E", "story": 0, "openings": [{"kind": "door", "pos": 0.0, "width": 1.25}]}]}
        d["volumes"] = vols
        return d

    tag = L._room_tag({"id": "ctl_room"})

    def wall_piece(n, y0, y1):
        return {"name": "shelf_run_%s_%d" % (tag, n), "x": 0.0, "y": (y0 + y1) / 2.0, "z": 0.9, "size_x": 0.6,
                "size_y": y1 - y0, "size_z": 1.8, "collision": "convex"}

    # 1. an empty room: the arms agree, the straight route is the distance between the two endpoints
    r = measure_spec(room_spec([]), "ctl")[0]
    la, lf = r["arms"]["authored"]["length"].get("0-1"), r["arms"]["furnished"]["length"].get("0-1")
    straight = 10.0 - 2 * (0.15 + DOOR_IN)
    if la is None or lf is None or abs(la - lf) > 1e-9 or abs(la - straight) > 2 * CELL:
        fails.append("empty room: lengths %s / %s, want %.2f in both" % (la, lf, straight))
    # 2. a 0.90 m slot (furnish's own margin) across the room: open to the body, closed to the bake
    gap = 0.90
    vols = [wall_piece(1, -2.85, -gap / 2), wall_piece(2, gap / 2, 2.85)]
    r = measure_spec(room_spec(vols), "ctl")[0]
    bf = r["arms"]["furnished"]["bottleneck"].get("0-1", 0.0)
    ba = r["arms"]["authored"]["bottleneck"].get("0-1", 0.0)
    if not (R_BODY <= bf < C_BAKE) or abs(bf - gap / 2) > CELL / 2 + 1e-9:
        fails.append("0.90 m slot: bottleneck %.3f, want %.3f +- %.2f, >= %.2f (body) and < %.2f (bake)"
                     % (bf, gap / 2, CELL / 2, R_BODY, C_BAKE))
    if ba < 1.0:
        fails.append("0.90 m slot: the AUTHORED arm saw the generated pieces (bottleneck %.3f)" % ba)
    if r["arms"]["furnished"]["length"].get("0-1") is None:
        fails.append("0.90 m slot: no body path through a slot wider than a body")
    # 3. a 0.60 m slot: closed to the body, so no furnished path at all
    gap = 0.60
    vols = [wall_piece(1, -2.85, -gap / 2), wall_piece(2, gap / 2, 2.85)]
    r = measure_spec(room_spec(vols), "ctl")[0]
    if r["arms"]["furnished"]["length"].get("0-1") is not None:
        fails.append("0.60 m slot: a body path through a slot narrower than a body")
    if r["arms"]["furnished"]["bottleneck"].get("0-1", 0.0) >= R_BODY:
        fails.append("0.60 m slot: bottleneck reads a body through")
    # 4. a detour: a barrier with its slot at one end lengthens the route, and the authored arm does not see it
    vols = [wall_piece(1, -2.85, 1.6)]
    r = measure_spec(room_spec(vols), "ctl")[0]
    la, lf = r["arms"]["authored"]["length"].get("0-1"), r["arms"]["furnished"]["length"].get("0-1")
    if la is None or lf is None or not lf > la * 1.05:
        fails.append("detour: lengths %s -> %s, want the furnished one over 5 %% longer" % (la, lf))
    # 5. dressing against function: a 0.60 m slot across the room in cartons (the fallback recipe's cluster stem, placed
    # nowhere else) is dressing -- the FUNCTIONAL arm walks straight through, FURNISHED cannot; the same slot in shelf
    # runs (its wall run) is the room's function, and the FUNCTIONAL arm is closed by it too
    gap = 0.60

    def carton(n, y0, y1):
        return dict(wall_piece(n, y0, y1), name="cartons_%s_%d" % (tag, n))

    r = measure_spec(room_spec([carton(1, -2.85, -gap / 2), carton(2, gap / 2, 2.85)]), "ctl")[0]
    if r["arms"]["functional"]["length"].get("0-1") is None or r["arms"]["furnished"]["length"].get("0-1") is not None:
        fails.append("dressing: a slot of cartons read %s functional, %s furnished; want a path, then none"
                     % (r["arms"]["functional"]["length"].get("0-1"), r["arms"]["furnished"]["length"].get("0-1")))
    r = measure_spec(room_spec([wall_piece(1, -2.85, -gap / 2), wall_piece(2, gap / 2, 2.85)]), "ctl")[0]
    if r["arms"]["functional"]["length"].get("0-1") is not None:
        fails.append("function: a slot of shelf runs read open to the FUNCTIONAL arm")
    for f in fails:
        print("CONTROL FAILED:", f)
    print("controls: %d failed" % len(fails))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec")
    ap.add_argument("--controls", action="store_true")
    a = ap.parse_args(argv)
    if a.controls:
        return controls()
    specs = sorted(p for p in (DC / "specs").glob("*.json") if not p.name.startswith("lf_"))
    if a.spec:
        specs = [DC / "specs" / (a.spec + ".json")]
    rows, t0 = [], time.time()
    for p in specs:
        d = json.loads(p.read_text(encoding="utf-8"))
        if not d.get("rooms") or d.get("facade"):
            continue
        rows.extend(measure_spec(d, p.stem))
    lines = ["# route_cost.py over Deli Counter %s's library (%s), %.0f s"
             % ((DC / "VERSION").read_text(encoding="utf-8").split()[-1], ", ".join(x.stem for x in specs)
                if a.spec else "%d specs" % len(specs), time.time() - t0)] + summarise(rows)
    text = "\n".join(lines) + "\n"
    print(text)
    if not a.spec:
        (HERE / "route_cost.out.txt").write_text(text, encoding="utf-8", newline="\n")
        (HERE / "route_cost.json").write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
