"""Deli Counter 0.264.0, applied to a CLONE (<repo>): a room's seeded pieces stand in one line. The walker, walking cold
run 9383, of deli_a03's stair landing: "layout of these tables doesn't seem to have a rhyme or reason". Anchored;
refuses on a miss; keeps line endings."""
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
    ("""_SEED_MIN_AREA = 30.0     # below this a bare room still reads fine
_SEED_MAX_PIECES = 4      # thesis: don't over-cover
""",
     """_SEED_MIN_AREA = 30.0     # below this a bare room still reads fine
_SEED_MAX_PIECES = 4      # thesis: don't over-cover
#: SEEDED PIECES STAND IN ONE LINE (0.264.0, `_line_up`). The walker, walking
#: cold run 9383, of deli_a03's stair landing: "layout of these tables doesn't
#: seem to have a rhyme or reason" -- its four pieces stood where a shuffled,
#: jittered grid's first fits fell, turned by coin flip. A line is tried
#: every `_SEED_LINE_CROSS` across the room, both ways, sampled every
#: `_SEED_LINE_STEP` along it; the spread between pieces is `_seed_clear`'s.
_SEED_LINE_CROSS = 0.5
_SEED_LINE_STEP = 0.2
_SEED_SPREAD = 2.2
"""),
    ("""    for (qx, qy) in placed:
        if math.hypot(qx - px, qy - py) < 2.2:
            return False
    return True
""",
     """    for (qx, qy) in placed:
        if math.hypot(qx - px, qy - py) < _SEED_SPREAD:
            return False
    return True


def _line_up(spec, room, pieces, routes=()):
    \"\"\"Stand a room's seeded `pieces` (its volume dicts, in the seeder's order)
    evenly along ONE straight line, long sides along it, in place; True when
    a line holds them all, else False and nothing moved (0.264.0).

    The lines through the room parallel to a wall, every `_SEED_LINE_CROSS`
    across it, tried in order -- the room's long axis first, then its middle
    outward -- and on the first whose longest clear stretch holds them all,
    the first piece at the stretch's one end and the last at its other. Clear is
    `_seed_clear`'s, asked as the seeder asks it with the pieces themselves
    set aside, and off the room's reserved `routes`.

    The same pieces, the same kinds and heights: only where they stand and
    which way they lie. A room no line fits keeps them where they were --
    cover that stood somewhere beats cover in a line that cannot.\"\"\"
    n = len(pieces)
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
"""),
    ("""        if needs_shelter:
            # THE ROOM'S OWN SHELTER PIECE FIRST, THEN THE SMALLEST (0.249.0,""",
     """        start = len(spec.get("volumes") or [])   # this room's pieces are appended after
        if needs_shelter:
            # THE ROOM'S OWN SHELTER PIECE FIRST, THEN THE SMALLEST (0.249.0,"""),
    ("""            placed.append((px, py))
            added += 1
    return added


#: FURNITURE: what a room gets, as a RECIPE per room KIND (0.131.0).""",
     """            placed.append((px, py))
            added += 1
        # THEN THE SAME PIECES IN ONE LINE (0.264.0, `_line_up`): the
        # shelter piece first and the archetype's after, as they were drawn.
        mine = [v for v in (spec.get("volumes") or [])[start:] if _seeded_cover(v, room)]
        _line_up(spec, room, mine, routes)
    return added


#: FURNITURE: what a room gets, as a RECIPE per room KIND (0.131.0)."""),
])
edit("test_club_fixtures.py", [
    ("""    # gallery recipe furnished, and the hallway recipe stands none
    assert counts == {"dartboard": 11, "cigarettes": 86}, counts""",
     """    # gallery recipe furnished, and the hallway recipe stands none. 86 -> 85
    # (0.264.0): twin_a01's 38 m2 front_left_0, its kiosk and planter stood in
    # a line, left the refurnish no wall for its machine
    assert counts == {"dartboard": 11, "cigarettes": 85}, counts"""),
])
print("edited", R)
