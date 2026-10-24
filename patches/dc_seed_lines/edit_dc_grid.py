"""Deli Counter 0.264.0, second edit, applied to a CLONE (<repo>) after edit_dc_lines.py: a room's seeded pieces stand on a lattice -- one line
where one holds them, else parallel rows -- each cleared by its own footprint. The walker, walking cold run 9383, of
deli_a03's stair landing: "layout of these tables doesn't seem to have a rhyme or reason", and of the fix: "nuance and
flavor, but not look like random assortment". Anchored; refuses on a miss; keeps line endings."""
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


OLD_LINE_UP = '''    n = len(pieces)
    if n < 2:
        return False
    ids = {id(v) for v in pieces}
    probe = dict(spec, volumes=[v for v in spec.get("volumes") or [] if id(v) not in ids])
    x0, y0, x1, y1 = room["bounds"]
    long_x = (x1 - x0) >= (y1 - y0)
    dims = [(max(float(v["size_x"]), float(v["size_y"])),
             min(float(v["size_x"]), float(v["size_y"]))) for v in pieces]
    half = max(d[0] for d in dims) / 2.0

    def clear(px, py, placed, h, standing=()):
        # the line's pieces already stood are volumes to this one, so a body
        # passes between two of them as it passes any piece (`corridor`)
        within = dict(probe, volumes=probe["volumes"] + list(standing)) if standing else probe
        if not _seed_clear(within, room, px, py, placed, half=h, corridor=True):
            return False
        return not (routes and on_protected_route(routes, px, py, 2 * h, 2 * h))

    # lines in order of preference -- the room's long axis, then its middle outward -- and the first whose longest
    # clear stretch holds every piece wins: a preset furnishes hundreds of rooms, so the search stops early
    lines = []
    for along_x in (long_x, not long_x):
        a0, a1, c0, c1 = (x0, x1, y0, y1) if along_x else (y0, y1, x0, x1)
        mid = (c0 + c1) / 2.0
        k = 0
        while c0 + 0.5 + k * _SEED_LINE_CROSS <= c1 - 0.5 + 1e-9:
            c = c0 + 0.5 + k * _SEED_LINE_CROSS
            k += 1
            lines.append((along_x != long_x, abs(c - mid), c, along_x, a0, a1))
    for _short, _off, c, along_x, a0, a1 in sorted(lines):
        steps = int(round((a1 - a0) / _SEED_LINE_STEP))
        runs, run = [], None
        for i in range(steps + 1):
            a = a0 + i * _SEED_LINE_STEP
            ok = clear(*((a, c) if along_x else (c, a)), [], half)
            if ok:
                run = [a, a] if run is None else [run[0], a]
            if run is not None and (not ok or i == steps):
                runs.append(tuple(run))
                run = None
        for r0, r1 in sorted(runs, key=lambda r: r[0] - r[1]):
            if (r1 - r0) / (n - 1) < _SEED_SPREAD:
                break
            placed, at, standing = [], [], []
            for j, (lo, hi) in enumerate(dims):
                a = r0 + j * (r1 - r0) / (n - 1)
                px, py = (a, c) if along_x else (c, a)
                if not clear(px, py, placed, lo / 2.0, standing):
                    break
                sx, sy = (lo, hi) if along_x else (hi, lo)
                placed.append((px, py))
                at.append((px, py, (sx, sy)))
                standing.append(dict(pieces[j], x=px, y=py, size_x=sx, size_y=sy))
            if len(at) == n:
                for v, (px, py, (sx, sy)) in zip(pieces, at):
                    v.update({"x": round(px, 2), "y": round(py, 2), "size_x": sx, "size_y": sy})
                return True
    return False
'''

NEW_LINE_UP = '''    n = len(pieces)
    if n < 1:
        return False
    # ONE KIND A ROW: like with like -- desks in a row and the cabinets behind them, not alternating -- each kind in
    # the order the seeder first drew it, its pieces in theirs. A row ending mid-kind carries it on into the next.
    first = {}
    for v in pieces:
        first.setdefault(_seed_kind(v, room), len(first))
    order = sorted(range(n), key=lambda i: (first[_seed_kind(pieces[i], room)], i))
    pieces = [pieces[i] for i in order]
    ids = {id(v) for v in pieces}
    probe = dict(spec, volumes=[v for v in spec.get("volumes") or [] if id(v) not in ids])
    x0, y0, x1, y1 = room["bounds"]
    long_x = (x1 - x0) >= (y1 - y0)
    dims = [(max(float(v["size_x"]), float(v["size_y"])),
             min(float(v["size_x"]), float(v["size_y"]))) for v in pieces]
    along_len = max(d[0] for d in dims)      # the longest piece, along its row
    across = max(d[1] for d in dims)         # the deepest, across it
    import agent_contract
    cw = agent_contract.min_corridor_width()

    def clear(px, py, placed, size, standing=()):
        # by the piece's own footprint (`_seed_clear`'s `size`); the pieces
        # already stood are volumes to this one, so a body passes between two
        # of them as it passes any piece (`corridor`)
        within = dict(probe, volumes=probe["volumes"] + list(standing)) if standing else probe
        if not _seed_clear(within, room, px, py, placed, half=max(size) / 2.0, corridor=True, size=size):
            return False
        return not (routes and on_protected_route(routes, px, py, size[0], size[1]))

    for rows in range(1, min(n, _SEED_LINE_ROWS) + 1):
        cols = -(-n // rows)
        if rows > 1 and (rows - 1) * cols >= n:          # a row left empty is not a lattice
            continue
        # row to row: the deepest piece and a body's corridor, and never under the seeder's spread
        pitch = max(across + cw, _SEED_SPREAD) if rows > 1 else 0.0
        cands = []
        for along_x in (long_x, not long_x):
            a0, a1, c0, c1 = (x0, x1, y0, y1) if along_x else (y0, y1, x0, x1)
            mid = (c0 + c1) / 2.0
            k = 0
            while c0 + 0.5 + k * _SEED_LINE_CROSS + (rows - 1) * pitch <= c1 - 0.5 + 1e-9:
                c = c0 + 0.5 + k * _SEED_LINE_CROSS
                k += 1
                cands.append((along_x != long_x, abs(c + (rows - 1) * pitch / 2.0 - mid), c, along_x, a0, a1))
        for _short, _off, c, along_x, a0, a1 in sorted(cands):
            probe_size = (along_len, across) if along_x else (across, along_len)
            steps = int(round((a1 - a0) / _SEED_LINE_STEP))
            ok = [True] * (steps + 1)
            for r in range(rows):                         # a stretch clear on every row: the lattice is square
                cr = c + r * pitch
                for i in range(steps + 1):
                    if ok[i]:
                        a = a0 + i * _SEED_LINE_STEP
                        ok[i] = clear(*((a, cr) if along_x else (cr, a)), [], probe_size)
            runs, run = [], None
            for i in range(steps + 1):
                a = a0 + i * _SEED_LINE_STEP
                if ok[i]:
                    run = [a, a] if run is None else [run[0], a]
                if run is not None and (not ok[i] or i == steps):
                    runs.append(tuple(run))
                    run = None
            for r0, r1 in sorted(runs, key=lambda r: r[0] - r[1]):
                if cols > 1 and (r1 - r0) / (cols - 1) < _SEED_SPREAD:
                    break
                step = (r1 - r0) / (cols - 1) if cols > 1 else 0.0
                placed, at, standing = [], [], []
                for j, (lo, hi) in enumerate(dims):
                    r, col = divmod(j, cols)
                    in_row = min(cols, n - r * cols)
                    # a short last row stands centred under the full ones
                    a = (r0 + r1) / 2.0 if cols == 1 else r0 + (col + (cols - in_row) / 2.0) * step
                    cr = c + r * pitch
                    px, py = (a, cr) if along_x else (cr, a)
                    size = (lo, hi) if along_x else (hi, lo)
                    if not clear(px, py, placed, size, standing):
                        break
                    placed.append((px, py))
                    at.append((px, py, size))
                    standing.append(dict(pieces[j], x=px, y=py, size_x=size[0], size_y=size[1]))
                if len(at) == n:
                    for v, (px, py, (sx, sy)) in zip(pieces, at):
                        v.update({"x": round(px, 2), "y": round(py, 2), "size_x": sx, "size_y": sy})
                    return True
    return False
'''

edit("level_design.py", [
    ("""_SEED_LINE_CROSS = 0.5
_SEED_LINE_STEP = 0.2
_SEED_SPREAD = 2.2
""",
     """_SEED_LINE_CROSS = 0.5
_SEED_LINE_STEP = 0.2
_SEED_SPREAD = 2.2
#: AND WHERE ONE LINE CANNOT, PARALLEL ROWS (0.264.0): up to this many, the
#: same spacing on each, a body's corridor between them. deli_a03's landing
#: holds no line of its four pieces -- they want 10.5 m with the corridor
#: between each, and the clear strip beside its stairwell is shorter -- and
#: holds two rows of two.
_SEED_LINE_ROWS = 3
"""),
    ("""def _seed_clear(spec, room, px, py, placed, half=0.0, above=None,
                below=None, over_openings=False, corridor=False, backed_on=None):""",
     """def _seed_clear(spec, room, px, py, placed, half=0.0, above=None,
                below=None, over_openings=False, corridor=False, backed_on=None,
                size=None):"""),
    ("""    rule and every other rule still apply. Only a piece with
    ``backs_on_partitions`` passes it (`_place_fixture`).\"\"\"
    story = room.get("story", 0)""",
     """    rule and every other rule still apply. Only a piece with
    ``backs_on_partitions`` passes it (`_place_fixture`).

    `size` (0.264.0), when given, is the piece's own footprint, ``(size_x,
    size_y)``, for a piece that will stand the way it is asked -- a lined-up
    seeded piece (`_line_up`), a stored one (`migrate_seed_corridor`). Every
    BOX rule -- off another volume, a stair's reserve, a hole, a vault leaf,
    the body's corridor -- then asks the footprint rather than the square of
    its longest side; the RADIUS rules -- a stair's centre, a ladder, a door's
    approach -- still ask `half`. A counter 0.8 m deep was cleared as if it
    were 2.2 m deep, and no line of four fitted where two rows of two do.\"\"\"
    hx, hy = (float(size[0]) / 2.0, float(size[1]) / 2.0) if size else (half, half)
    story = room.get("story", 0)"""),
    ("""        if abs(v["x"] - px) < v.get("size_x", 1) / 2 + 0.9 + half and \\
                abs(v["y"] - py) < v.get("size_y", 1) / 2 + 0.9 + half:
            return False""",
     """        if abs(v["x"] - px) < v.get("size_x", 1) / 2 + 0.9 + hx and \\
                abs(v["y"] - py) < v.get("size_y", 1) / 2 + 0.9 + hy:
            return False"""),
    ("""    for rect in _stair_reserved_rects(spec):
        if px + half > rect[0] - 0.3 and px - half < rect[2] + 0.3 and \\
                py + half > rect[1] - 0.3 and py - half < rect[3] + 0.3:
            return False""",
     """    for rect in _stair_reserved_rects(spec):
        if px + hx > rect[0] - 0.3 and px - hx < rect[2] + 0.3 and \\
                py + hy > rect[1] - 0.3 and py - hy < rect[3] + 0.3:
            return False"""),
    ("""            if px + half > hx0 - 0.3 and px - half < hx1 + 0.3 and \\
                    py + half > hy0 - 0.3 and py - half < hy1 + 0.3:
                return False""",
     """            if px + hx > hx0 - 0.3 and px - hx < hx1 + 0.3 and \\
                    py + hy > hy0 - 0.3 and py - hy < hy1 + 0.3:
                return False"""),
    ("""        if (px + half > x0 - 0.3 and px - half < x1 + 0.3
                and py + half > y0 - 0.3 and py - half < y1 + 0.3):
            return False""",
     """        if (px + hx > x0 - 0.3 and px - hx < x1 + 0.3
                and py + hy > y0 - 0.3 and py - hy < y1 + 0.3):
            return False"""),
    ("""    # the docstring). The box is the piece's worst-case square, as above.
    if corridor and above is None:
        import agent_contract
        cw = agent_contract.min_corridor_width()
        box = (px - half, py - half, px + half, py + half)""",
     """    # the docstring). The box is the piece's worst-case square, as above --
    # or its footprint, given `size`.
    if corridor and above is None:
        import agent_contract
        cw = agent_contract.min_corridor_width()
        box = (px - hx, py - hy, px + hx, py + hy)"""),
    ("""    \"\"\"Stand a room's seeded `pieces` (its volume dicts, in the seeder's order)
    evenly along ONE straight line, long sides along it, in place; True when
    a line holds them all, else False and nothing moved (0.264.0).

    The lines through the room parallel to a wall, every `_SEED_LINE_CROSS`
    across it, tried in order -- the room's long axis first, then its middle
    outward -- and on the first whose longest clear stretch holds them all,
    the first piece at the stretch's one end and the last at its other. Clear is
    `_seed_clear`'s, asked as the seeder asks it with the pieces themselves
    set aside, and off the room's reserved `routes`.""",
     """    \"\"\"Stand a room's seeded `pieces` (its volume dicts, in the seeder's order)
    on a LATTICE, long sides along its rows, in place; True when one holds
    them all, else False and nothing moved (0.264.0).

    One row first, then two, up to `_SEED_LINE_ROWS`: rows parallel to a
    wall, a body's corridor between them, every row's pieces at the same
    stations along it (a short last row centred), so the lattice is square.
    For each count, the rows' first position across the room every
    `_SEED_LINE_CROSS`, tried in order -- the room's long axis first, then the
    lattice's middle nearest the room's -- and on the first whose stretch
    clear on every row holds a row, the first piece at its one end and the
    last at its other. Clear is `_seed_clear`'s by each piece's own footprint,
    asked as the seeder asks it with the pieces themselves set aside, the
    pieces already stood among what it clears, and off the room's reserved
    `routes`."""),
    ("""def _line_up(spec, room, pieces, routes=()):""",
     """def _seed_kind(v, room):
    \"\"\"A seeded piece's kind: its name before ``_<room>_<k>`` or ``_<room>_shelter``.\"\"\"
    name = str(v.get("name", ""))
    head = name.rsplit("_" + str(room.get("id", "")) + "_", 1)[0]
    return head or name


def _line_up(spec, room, pieces, routes=()):"""),
    (OLD_LINE_UP, NEW_LINE_UP),
])

edit("migrate_seed_corridor.py", [
    ("""        if not level_design._seed_clear(without, room, float(v["x"]), float(v["y"]),
                                        placed, half=half, corridor=True):""",
     """        # by its own footprint (0.264.0): a stored piece stands the way it is
        if not level_design._seed_clear(without, room, float(v["x"]), float(v["y"]),
                                        placed, half=half, corridor=True,
                                        size=(float(v["size_x"]), float(v["size_y"]))):"""),
])
edit("test_seed_corridor.py", [
    ("""        half = max(float(v["size_x"]), float(v["size_y"])) / 2.0
        if not level_design._seed_clear(without, room, float(v["x"]), float(v["y"]),
                                        placed, half=half, corridor=True):""",
     """        half = max(float(v["size_x"]), float(v["size_y"])) / 2.0
        # by its own footprint (0.264.0), as `migrate_seed_corridor.failing` asks
        if not level_design._seed_clear(without, room, float(v["x"]), float(v["y"]),
                                        placed, half=half, corridor=True,
                                        size=(float(v["size_x"]), float(v["size_y"]))):"""),
])
edit("migrate_seed_lines.py", [
    ("""        routes = (level_design.protected_routes(level_design.unfurnished(view), room)
                  if level_design.reserves_routes(view, room, building) else [])""",
     """        # THE ROUTES THE ROOM HAS WITHOUT THESE PIECES (0.264.0), as `seed_cover`
        # asks them before it stands any: asked with them standing, the routes
        # bent round where they stood, and this migration's first draft lined
        # pawn_shop_a01's two crates onto the safe room's true route
        ids = {id(v) for v in pieces}
        bare = dict(view, volumes=[v for v in view["volumes"] if id(v) not in ids])
        routes = (level_design.protected_routes(level_design.unfurnished(bare), room)
                  if level_design.reserves_routes(view, room, building) else [])"""),
    ("""    \"\"\"``[(room, [pieces in the seeder's order])]`` for every room storing two or more seeded pieces.\"\"\"""",
     """    \"\"\"``[(room, [pieces in the seeder's order])]`` for every room storing a seeded piece: a lone one
    stands on the room's line too (0.264.0).\"\"\""""),
    ("""    return [(room, sorted(vs, key=_order)) for room, vs in by_room.values() if len(vs) >= 2]""",
     """    return [(room, sorted(vs, key=_order)) for room, vs in by_room.values()]"""),
])
edit("test_marker_room_routes.py", [
    ("""def test_a_room_with_no_spot_off_its_routes_keeps_its_shelter(monkeypatch):
    \"\"\"twin_a01's front_right_1 has one clear spot for a crate stack. With a route through it, the pass stands the
    crate there rather than leave a room both sides see over everything in: kept strictly off its routes, the
    pawn_shop preset's safe_room lost its shelter and `test_cover_breaks_sightlines` failed on it.\"\"\"
    d0, room = _stripped_room("twin_a01", "front_right_1")
    free = _sheltered(d0, "front_right_1", [], monkeypatch)
    assert len(free) == 1, "asked no route the room is sheltered"
    kept = _sheltered(d0, "front_right_1", _through(room, free[0]), monkeypatch)
    assert [(v["x"], v["y"]) for v in kept] == [(free[0]["x"], free[0]["y"])], kept""",
     """def test_a_room_with_no_spot_off_its_routes_keeps_its_shelter(monkeypatch):
    \"\"\"twin_a01's front_right_1, its every clear spot on a route: the pass stands a crate anyway rather than leave
    a room both sides see over everything in -- kept strictly off its routes, the pawn_shop preset's safe_room lost
    its shelter and `test_cover_breaks_sightlines` failed on it. 0.264.0: the route covers the room's whole depth.
    Through the one spot the square of the crate's longest side once left, it no longer holds the test's premise: by
    the crate's own footprint the room has a second spot off that route (`_seed_clear`'s `size`).\"\"\"
    d0, room = _stripped_room("twin_a01", "front_right_1")
    free = _sheltered(d0, "front_right_1", [], monkeypatch)
    assert len(free) == 1, "asked no route the room is sheltered"
    x0, y0, x1, y1 = room["bounds"]
    everywhere = [([(x0, (y0 + y1) / 2.0), (x1, (y0 + y1) / 2.0)], (y1 - y0) / 2.0 + 1.0)]
    kept = _sheltered(d0, "front_right_1", everywhere, monkeypatch)
    assert len(kept) == 1, kept"""),
])
print("edited", R)
