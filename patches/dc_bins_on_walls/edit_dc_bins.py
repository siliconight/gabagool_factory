"""Deli Counter 0.266.0 on a CLONE (<repo>): an indoor litter bin stands against a wall (the walker's walk of cold run
9386, finding 8: "garbage cans are usually up against walls inside buildings"). Anchored; refuses on a miss.

The second design. The first (`draft1/`) made the bin a wall piece and moved it into five recipes' wall runs; a longer
wall run re-shuffles every room that has one, and 241 rooms were redrawn for 288 bins -- a queued lobby lost its
payphone, ATM and sofa, deli_a03 its ATM, a stair core took a chair and foundry_heist_vertical's stair stopped
traversing. This one leaves every recipe and every draw as it was and moves only the bins, last.

    python edit_dc_bins.py <repo>
"""
import pathlib
import sys

R = pathlib.Path(sys.argv[1])


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


edit("level_design.py", [
    ('''def _glazed_walls(spec, story):''',
     '''#: A LITTER BIN STANDS AGAINST A WALL (0.266.0). The walker, of deli_a03's bin
#: alone at an aisle's end, walking cold run 9386: "garbage cans are usually up
#: against walls inside buildings". Recipes draw a bin as a cluster piece, or in
#: a corridor's wall run where its own `where` still sends it to the floor grid;
#: 288 of the library's furnished bins stood off every wall, 260 of them with no
#: reason the arrangement census could name. `stand_bins_on_walls` moves each to
#: the nearest spot flush against a held wall, LAST, so no other piece in any room
#: is drawn differently. Spots are tried every this many metres along each edge.
_BIN_STEP = 0.2
_BIN_RE = None


def _bin_wall_spots(spec, room, sx, sy):
    """Every spot a bin ``sx`` by ``sy`` stands flush against a built wall of
    `room`: ``(x, y, backed_on)``, every `_BIN_STEP` along each edge a wall holds
    the bin's whole run on, at `_wall_slots`' own offset from the wall's face,
    clear of exterior openings by `_clear_of_openings`. ``backed_on`` is the edge
    for `_seed_clear`. A storey with a setback offers no exterior edge, as in
    `_wall_slots`."""
    x0, y0, x1, y1 = room["bounds"]
    story = int(room.get("story", 0) or 0)
    hx = float(spec.get("footprint_x", 0.0)) / 2.0
    hy = float(spec.get("footprint_y", 0.0)) / 2.0
    openings = _ext_openings(spec, story)
    back = float(spec.get("wall_thick") or 0.3) / 2.0 + _WALL_PIECE_AIR
    out = []

    def ext_of(value, half, lo_name, hi_name):
        if not half or abs(abs(value) - half) >= _FURNISH_EXT_KEEPOUT:
            return None
        return lo_name if value < 0 else hi_name

    for wy, inset in ((y0, +1), (y1, -1)):
        ext = ext_of(wy, hy, "S", "N")
        if ext and openings is None:
            continue
        backing = _edge_backing(spec, story, 1, wy)
        py = wy + inset * (sy / 2.0 + back)
        k = 0
        while True:
            px = x0 + 0.3 + sx / 2.0 + k * _BIN_STEP
            k += 1
            if px + sx / 2.0 > x1 - 0.3 + 1e-9:
                break
            if ext and not _clear_of_openings(openings, ext, px, sx / 2.0):
                continue
            if _held(backing, px - sx / 2.0, px + sx / 2.0):
                out.append((px, py, ("X", wy)))
    for wx, inset in ((x0, +1), (x1, -1)):
        ext = ext_of(wx, hx, "W", "E")
        if ext and openings is None:
            continue
        backing = _edge_backing(spec, story, 0, wx)
        px = wx + inset * (sx / 2.0 + back)
        k = 0
        while True:
            py = y0 + 0.3 + sy / 2.0 + k * _BIN_STEP
            k += 1
            if py + sy / 2.0 > y1 - 0.3 + 1e-9:
                break
            if ext and not _clear_of_openings(openings, ext, py, sy / 2.0):
                continue
            if _held(backing, py - sy / 2.0, py + sy / 2.0):
                out.append((px, py, ("Y", wx)))
    return out


def stand_bins_on_walls(spec, routes_of=None):
    """Stand every litter bin `furnish` placed against a wall of its room, in
    place: ``(moved, removed)``.

    A bin already standing on one of `_bin_wall_spots` (to the centimetre it is
    stored to) where `_seed_clear` lets it stand stays. Any other goes to the
    nearest of them that
    `_seed_clear` lets it stand on, asked with the bin itself set aside and
    backed on its wall's edge, and off any route its room reserves
    (`reserves_routes`) -- ties by position, so a re-run makes the same
    move; with no such spot it goes, because a bin in the middle of the floor
    is the defect and a room without one is not. Its size, height, storey and
    turn are kept. Bins in name order, each asked against the others where they
    then stand. Idempotent; reads only the spec, so a room furnished by an
    earlier release gets the same answer (`migrations/migrate_bins_on_walls.py`
    is this function over the library). `routes_of`, ``{room id: routes}``,
    are routes already asked of rooms (`furnish` passes those it reserved),
    so a room's are not searched twice."""
    import re
    global _BIN_RE
    if _BIN_RE is None:
        _BIN_RE = re.compile(r"^litter_bin_(r[0-9a-f]{8})_\\d+$")
    rooms = {_room_tag(r): r for r in spec.get("rooms") or [] if r.get("bounds")}
    bins = sorted((v for v in spec.get("volumes") or []
                   if _BIN_RE.match(str(v.get("name", "")))
                   and _BIN_RE.match(v["name"]).group(1) in rooms),
                  key=lambda v: v["name"])
    moved = removed = 0
    # A ROOM'S RESERVED ROUTES, as furnish reserves them (0.250.0, 0.251.0):
    # a bin was dressing, which keeps off them wherever a room reserves any,
    # and a bin on its wall still does. Asked once a room, of the floor
    # `furnish` asks it of.
    building = club_building_id(spec)
    routes_of = dict(routes_of or {})
    for v in bins:
        room = rooms[_BIN_RE.match(v["name"]).group(1)]
        if room["id"] not in routes_of:
            routes_of[room["id"]] = (protected_routes(unfurnished(spec), room)
                                     if reserves_routes(spec, room, building) else [])
        routes = routes_of[room["id"]]
        sx, sy = float(v["size_x"]), float(v["size_y"])
        half = max(sx, sy) / 2.0
        probe = dict(spec, volumes=[o for o in spec["volumes"] if o is not v])
        x, y = float(v["x"]), float(v["y"])
        spots = _bin_wall_spots(spec, room, sx, sy)
        # nearest first, as stored (to the centimetre): a bin already on a
        # spot is nearest to itself. In a corner two edges offer the same
        # spot, each backed on its own wall, and either one clearing it is
        # the bin standing there -- so a bin that stays is not counted moved.
        spots.sort(key=lambda s: (math.hypot(round(s[0], 2) - x, round(s[1], 2) - y), s[0], s[1]))
        for px, py, b in spots:
            if routes and on_protected_route(routes, px, py, sx, sy):
                continue
            if _seed_clear(probe, room, px, py, [], half=half, size=(sx, sy), backed_on=b):
                nx, ny = round(px, 2), round(py, 2)
                if (nx, ny) != (x, y):
                    v["x"], v["y"] = nx, ny
                    moved += 1
                break
        else:
            spec["volumes"] = [o for o in spec["volumes"] if o is not v]
            removed += 1
    return moved, removed


def _glazed_walls(spec, story):'''),
    ('''    # FIXTURES LAST, over every room, from the spec alone (0.136.0): a room
    # furnished in this call and a room furnished by an earlier release get
    # the same pass, so `migrate_club_fixtures.py` is this line.
    return added + place_fixtures(spec)''',
     '''    # FIXTURES LAST, over every room, from the spec alone (0.136.0): a room
    # furnished in this call and a room furnished by an earlier release get
    # the same pass, so `migrate_club_fixtures.py` is this line.
    added += place_fixtures(spec)
    # ...AND THE BINS AFTER THEM (0.266.0): every bin this pass or an earlier
    # one stood goes against a wall, and nothing else moves.
    return added - stand_bins_on_walls(spec, routes_of=room_routes)[1]'''),
    ('''    stems = set(_PIECES) | set(_LEGACY_STEMS) | set(_COLLIDER_STEMS) | {"chair_set"}
    added = 0
    building = club_building_id(spec)
    dress_club_rooms(spec)''',
     '''    stems = set(_PIECES) | set(_LEGACY_STEMS) | set(_COLLIDER_STEMS) | {"chair_set"}
    added = 0
    # each room's reserved routes as this call asks them, for the bins (0.266.0)
    room_routes = {}
    building = club_building_id(spec)
    dress_club_rooms(spec)'''),
    ('''        routes = (protected_routes(unfurnished(spec), room)
                  if recipe.get("protect_routes") else [])
''',
     '''        routes = (protected_routes(unfurnished(spec), room)
                  if recipe.get("protect_routes") else [])
        room_routes[room["id"]] = routes
'''),
])
print("level_design: stand_bins_on_walls, last in furnish")
