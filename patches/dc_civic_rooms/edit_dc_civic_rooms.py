"""Deli Counter 0.270.0 on a clone: a chapel, a courtroom, an assembly hall and a gallery furnished as what they are
(the factory's roadmap 308). Anchored; refuses on a miss.

    python edit_dc_civic_rooms.py <clone>

Edits level_design.py (the room kinds, the pew piece, the front and facing rows, the four recipes, the plan) and
prop_species.py (the pew row); tests/test_furnish.py's two `hall` assertions. Writes tests/test_civic_rooms.py.
VERSION and CHANGELOG are the generator's.
"""
import pathlib
import sys

C = pathlib.Path(sys.argv[1])


def edit(rel, edits):
    p = C / rel
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in edits:
        assert t.count(old) == 1, (rel, t.count(old), old[:90])
        t = t.replace(old, new)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print("edited", rel, len(edits))


KINDS_OLD = '''    ("hall", ("gallery", "galleries", "exhibit", "chapel",
              "assembly", "courtroom", "courtrooms", "viewing", "artifact")),
'''
KINDS_NEW = '''    # A CIVIC ROOM IS FURNISHED AS WHAT IT IS (0.270.0, the factory's roadmap
    # 308). These words were one `hall` row, and its recipe was a dining
    # hall's -- a service counter, waiting chairs, vending, dining tables --
    # so a chapel, a funeral home's viewing rooms, two courtrooms and two
    # assembly halls each stood a cafeteria. Three face a front now
    # (`facing_slots`): pews in rows towards an altar, a judge's bench, a
    # lectern. A gallery keeps its floor open, its cases on its walls.
    ("chapel", ("chapel", "viewing")),
    ("courtroom", ("courtroom", "courtrooms")),
    ("assembly", ("assembly",)),
    ("gallery", ("gallery", "galleries", "exhibit", "artifact")),
'''

RECIPE_OLD = '''    "hall": {"anchors": ("counter_service",),
             "wall": ("chair_waiting", "shelf_run", "chair_waiting",
                      "cabinet_file", "vending"),
             "floor": ("table_dining",),
             "clusters": ((("litter_bin",), 1, 1),),
             "fixtures": ("cigarettes",)},
'''
RECIPE_NEW = '''    # THE CIVIC ROOMS (0.270.0, the factory's roadmap 308; `_ROOM_KINDS`).
    # `facing` is a layer of its own (`facing_slots`): a piece at the room's
    # FRONT -- the long-axis end away from its doors -- facing back into it,
    # any `well` pieces in a row before it, then rows of `seat` across the
    # room facing the front, a centre aisle and two side aisles, from `gap`
    # metres off the front wall back to a door's clearance from the back
    # one, until the room's floor share reaches `share`. It is laid first,
    # so nothing else takes the floor the rows need. A chapel and a funeral
    # home's viewing room are the altar and the pews; a courtroom is the
    # judge's bench, two counsel tables in the well and the public's pews
    # behind; an assembly hall a lectern and pews. `rows` caps the rows:
    # every pew is its own mesh, so a draw, and these rooms run to 42 m --
    # courthouse_a02's first trial stood 60 pews, the piece's cap, where the
    # cafeteria had stood 21 pieces. A courtroom's public benches are six
    # rows; the back of a long chapel is its narthex, left to walk. A
    # courtroom's `cap` keeps its clerk's cabinets to six: uncapped, the
    # 42 m room's wall run stood twelve.
    "chapel": {"anchors": (), "wall": (), "floor": (), "clusters": (),
               "facing": {"seat": "pew", "front": "table_work", "well": (),
                          "gap": 3.0, "share": 0.30, "rows": 12}},
    "courtroom": {"anchors": (), "wall": ("cabinet_file",), "floor": (),
                  "clusters": (), "cap": 6,
                  "facing": {"seat": "pew", "front": "counter_service",
                             "well": ("table_work", "table_work"),
                             "gap": 6.0, "share": 0.30, "rows": 6}},
    "assembly": {"anchors": (), "wall": (), "floor": (), "clusters": (),
                 "facing": {"seat": "pew", "front": "table_work", "well": (),
                            "gap": 3.0, "share": 0.30, "rows": 12}},
    # a gallery is looked at, not sat in: its cases on its walls, a pew or
    # two to look from, the floor left open to walk (one piece in 40 m2, ten
    # at most: museum_a02's 44 x 24 m galleries first stood twelve pews)
    "gallery": {"anchors": (), "wall": ("display_case", "display_case",
                                        "shelf_run"),
                "floor": ("pew",), "clusters": (), "per_area": 40.0,
                "cap": 10},
'''

PIECE_OLD = '''    _piece("table_work", ((1.6, 0.8, 0.9), (1.2, 0.7, 0.9)), "floor"),
'''
PIECE_NEW = '''    _piece("table_work", ((1.6, 0.8, 0.9), (1.2, 0.7, 0.9)), "floor"),
    # A PEW (0.270.0, the factory's roadmap 308; Zoo's `pew`, >= 1.130.0):
    # the seat a chapel's, a courtroom's and an assembly hall's rows are
    # made of (`facing_slots`), and a gallery's bench to look from. Its
    # front is where a person sitting faces.
    _piece("pew", ((3.6, 0.62, 0.95), (3.0, 0.62, 0.95), (2.4, 0.62, 0.95),
                   (4.2, 0.62, 0.95)), "floor", front=True, most=60),
'''

FUNCS_ANCHOR = '''def _island(key, make, spec, px, py, w, d, h, front, twin=False):
'''
FUNCS_NEW = '''#: A facing row's pews stand this far apart, back of one to front of the next:
#: a pew's pitch in a church is 0.85 to 0.95 m, and a 0.62 m pew leaves knees
#: and a hymnal rack 0.3 m. Not an aisle -- nobody walks the length of it.
FACING_ROW_GAP = 0.3
#: The back row stops this far from the back wall's face: `_seed_clear_doors`'
#: door approach, so a door in the back wall opens onto floor, not a pew.
FACING_BACK_CLEAR = 1.5
#: A front piece stands this far off the front wall's face.
FACING_FRONT_OFF = 0.3


def room_openings(spec, room):
    """The doorways on `room`'s bounds: ``[(x, y, width), ...]``, every opening
    of an exterior wall or a partition on its storey within half a metre of
    one of its edges and inside its span. Read the way `_seed_clear_doors`
    reads them, so the two agree on where a door is."""
    story = room.get("story", 0)
    x0, y0, x1, y1 = room["bounds"]
    hx = spec.get("footprint_x", 20) / 2
    hy = spec.get("footprint_y", 20) / 2
    found = []
    for w in spec.get("ext_walls", []):
        if w.get("story", 0) != story:
            continue
        run = spec.get("footprint_x", 20) if w["wall"] in ("N", "S") else spec.get("footprint_y", 20)
        for op in w.get("openings", []):
            u = op.get("pos", 0.0) * run
            ox, oy = {"N": (u, hy), "S": (u, -hy), "E": (hx, u), "W": (-hx, u)}[w["wall"]]
            found.append((ox, oy, float(op.get("width", 1.0))))
    for p in spec.get("partitions", []):
        if p.get("story", 0) != story:
            continue
        run = abs(p["end"] - p["start"])
        for op in p.get("openings", []):
            u = p["start"] + (op.get("pos", 0.0) + 0.5) * run
            ox, oy = (p["pos"], u) if p["axis"] == "Y" else (u, p["pos"])
            found.append((ox, oy, float(op.get("width", 1.0))))
    out = []
    for ox, oy, ow in found:
        inside = x0 - 0.5 <= ox <= x1 + 0.5 and y0 - 0.5 <= oy <= y1 + 0.5
        edge = min(abs(ox - x0), abs(ox - x1), abs(oy - y0), abs(oy - y1))
        if inside and edge <= 0.5:
            out.append((ox, oy, ow))
    return out


#: An authored volume whose name carries one of these tokens is a row of seats
#: its author laid (`room_front`): funeral_home_a01's chapel `pew_row_a`/`_b`,
#: landmark_hall_a02's `bench_row`.
FACING_AUTHORED_ROWS = ("pew", "bench")


def room_front(spec, room):
    """``(along_x, sign)``: the room's FRONT is an end of its long axis
    (``along_x`` True when that is x), at the high end when ``sign`` is +1:
    the end whose own wall has less doorway in it, and between two walls
    with as much, the end away from the doors' mean -- where a person walking
    in looks. Doors are weighed by width, so a pair of main doors outweighs a
    side door; a room with no door on its bounds faces its high end.
    MEASURED: landmark_hall_a02's assembly hall has three doors in each long
    wall, and the mean alone put the front on a wall of doors, its lectern
    refused by the middle one's approach.

    AN AUTHORED ROW DECIDES THE AXIS: a seat row the spec's author stood in
    the room (`FACING_AUTHORED_ROWS`, long one way) faces across its own
    length, and the rows furnish lays continue it rather than crossing it.
    MEASURED: funeral_home_a01's chapel is 32 x 14 m with two authored 8 m
    pews long in x; the long-axis rule faced the room along x, and its first
    plan stood pews at right angles to the author's."""
    x0, y0, x1, y1 = room["bounds"]
    along_x = (x1 - x0) >= (y1 - y0)
    floor = room.get("story", 0) * _story_height(spec)
    tag = "_%s_" % _room_tag(room)
    for v in spec.get("volumes", []):
        name = str(v.get("name", ""))
        toks = set(name.lower().split("_"))
        if tag in name or not toks.intersection(FACING_AUTHORED_ROWS):
            continue
        vx, vy = float(v.get("x", 0.0)), float(v.get("y", 0.0))
        if not (x0 <= vx <= x1 and y0 <= vy <= y1):
            continue
        if abs(float(v.get("z", 0.0)) - float(v.get("size_z", 0.0)) / 2.0 - floor) > 0.3:
            continue
        along_x = float(v.get("size_y", 0.0)) > float(v.get("size_x", 0.0))
        break
    lo, hi = (x0, x1) if along_x else (y0, y1)
    mid = (lo + hi) / 2.0
    doors = room_openings(spec, room)
    total = sum(w for _x, _y, w in doors)
    if not total:
        return along_x, 1
    on_lo = sum(w for x, y, w in doors if abs((x if along_x else y) - lo) <= 0.5)
    on_hi = sum(w for x, y, w in doors if abs((x if along_x else y) - hi) <= 0.5)
    if abs(on_lo - on_hi) > 1e-6:
        return along_x, (1 if on_hi < on_lo else -1)
    mean = sum((x if along_x else y) * w for x, y, w in doors) / total
    return along_x, (-1 if mean > mid + 1e-6 else 1)


def facing_slots(spec, room, sizes, gap, hosts, routes=None):
    """Where rows of seats stand facing `room`'s front (`room_front`):
    ``(bearing, [[(x, y, sx, sy, (w, d, h)), ...], ...])``, the bearing the
    seats face and the rows from the front back, each row its blocks left
    and right of a centre aisle.

    ACROSS THE ROOM: the band inside the walls' faces less an aisle each side
    and one down the middle (`island_aisle_width`), halved into two blocks,
    each taking the longest of `sizes` that fits it, as many as fit with an
    aisle between them -- a wide room is sections, not one pew stretched; a
    band too narrow for two blocks of the shortest takes one, centred. ALONG
    IT: from `gap`
    metres off the front wall's face, a pew's depth and `FACING_ROW_GAP`
    apart, to `FACING_BACK_CLEAR` off the back wall's face.

    EVERY SLOT IS ASKED OF THE ROOM AS IT STANDS BEFORE ANY ROW IS WRITTEN
    (`_row_clear`): a row keeps an aisle from every wall, partition, stair
    and standing piece, and from a door's approach, but not from the rows
    beside it, which stand a knee's width apart by design. A slot that fails
    is left out of its row; the rest of the row stands."""
    face = float(spec.get("wall_thick", 0.3)) / 2.0
    x0, y0, x1, y1 = room["bounds"]
    cx0, cy0, cx1, cy1 = x0 + face, y0 + face, x1 - face, y1 - face
    along_x, sign = room_front(spec, room)
    l0, l1, s0, s1 = (cx0, cx1, cy0, cy1) if along_x else (cy0, cy1, cx0, cx1)
    bearing = (90.0 if sign > 0 else 270.0) if along_x else (0.0 if sign > 0 else 180.0)
    aisle = island_aisle_width()
    sizes = sorted(sizes, key=lambda s: -s[0])
    shortest = min(s[0] for s in sizes)
    band = (s1 - s0) - 2.0 * aisle
    block = (band - aisle) / 2.0
    if block >= shortest - 1e-9:
        mid = (s0 + s1) / 2.0
        centres = [(mid - aisle / 2.0 - block / 2.0, block), (mid + aisle / 2.0 + block / 2.0, block)]
    elif band >= shortest - 1e-9:
        centres = [((s0 + s1) / 2.0, band)]
    else:
        return bearing, []
    pick = []
    for c, room_for in centres:
        fits = [s for s in sizes if s[0] <= room_for + 1e-9]
        if not fits:
            continue
        size = fits[0]
        n = max(1, int((room_for + aisle) / (size[0] + aisle) + 1e-9))
        run = n * size[0] + (n - 1) * aisle
        for i in range(n):
            pick.append((c - run / 2.0 + size[0] / 2.0 + i * (size[0] + aisle), size))
    if not pick:
        return bearing, []
    depth = max(size[1] for _c, size in pick)
    front_face = l1 if sign > 0 else l0
    length = l1 - l0
    obstacles = _corridor_obstacles(spec, room.get("story", 0),
                                    room.get("story", 0) * _story_height(spec), _story_height(spec))
    rows = []
    t = gap + depth / 2.0
    while t <= length - FACING_BACK_CLEAR - depth / 2.0 + 1e-9:
        lc = round(front_face - sign * t, 2)
        row = []
        for c, (w, d, h) in pick:
            sc = round(c, 2)
            px, py = (lc, sc) if along_x else (sc, lc)
            sx, sy = (d, w) if along_x else (w, d)
            if _row_clear(spec, room, px, py, sx, sy, hosts, obstacles, routes):
                row.append((px, py, sx, sy, (w, d, h)))
        if row:
            rows.append(row)
        t += depth + FACING_ROW_GAP
    return bearing, rows


'''

FURNISH_OLD = '''        def _cluster(pool, n):
            """Place 2-4 small pieces as one group. Returns pieces placed."""
'''
FURNISH_NEW = '''        def _facing(conf):
            """The room's front piece, its well and its facing rows
            (`facing_slots`; the recipe's `facing`). Returns pieces placed.

            THE FRONT AND THE WELL FIRST, so the rows keep an aisle from
            them: the front piece centred on the front wall, facing back
            into the room; the well's pieces in one row, spread across the
            middle, half way from the front piece to where the rows begin.
            Then every row the room keeps clear, front to back, until the
            room's floor share reaches `share` or `rows` rows stand. Draws
            nothing from `rng`."""
            nonlocal added
            n = 0
            along_x, sign = room_front(spec, room)
            face = float(spec.get("wall_thick", 0.3)) / 2.0
            l0, l1 = (x0 + face, x1 - face) if along_x else (y0 + face, y1 - face)
            s0, s1 = (y0 + face, y1 - face) if along_x else (x0 + face, x1 - face)
            front_face = l1 if sign > 0 else l0
            seat_bearing = ((90.0 if sign > 0 else 270.0) if along_x
                            else (0.0 if sign > 0 else 180.0))
            back = (seat_bearing + 180.0) % 360.0

            def _stand(key, t, s, bearing, slide=False):
                """One piece `t` off the front wall's face at `s` across; a
                piece that may `slide` takes the nearest spot along the wall,
                a metre at a time, that a door's approach leaves it."""
                w, d, h = _palette(spec, key)[0]
                if h is None:
                    h = to_ceiling_height(spec, _PIECES[key], clear_h)
                lc = front_face - sign * (t + d / 2.0)
                sx, sy = (d, w) if along_x else (w, d)
                tries = [s]
                if slide:
                    k = 1
                    while k <= (s1 - s0) / 2.0 - w / 2.0:
                        tries += [s - k, s + k]
                        k += 1
                for s_try in tries:
                    px, py = (lc, s_try) if along_x else (s_try, lc)
                    if _seed_clear_doors(spec, room, px, py, max(sx, sy) / 2.0):
                        break
                else:
                    return 0
                vol = _volume(key, px, py, sx, sy, h, _front_turn(key, sx, sy, bearing))
                spec.setdefault("volumes", []).append(vol)
                placed.append((px, py))
                per_name[key] += 1
                return 1

            mid = (s0 + s1) / 2.0
            depth = 0.0
            if conf.get("front"):
                got = _stand(conf["front"], FACING_FRONT_OFF, mid, back, slide=True)
                n += got
                if got:
                    depth = _palette(spec, conf["front"])[0][1]
            well = list(conf.get("well") or ())
            if well:
                t = (FACING_FRONT_OFF + depth + float(conf["gap"])) / 2.0 - 0.5
                span = (s1 - s0) / (len(well) + 1)
                for i, key in enumerate(well):
                    n += _stand(key, t, s0 + span * (i + 1), seat_bearing)
            goal = float(conf.get("share") or 1.0)
            seat = conf["seat"]
            bearing, rows = facing_slots(spec, room, _palette(spec, seat),
                                         float(conf["gap"]), list(placed),
                                         routes if keep_all else None)
            for row in rows[:int(conf.get("rows") or len(rows))]:
                if room_floor_share(spec, room) >= goal:
                    break
                if len(row) > _PIECES[seat]["most"] - per_name[seat]:
                    break
                for qx, qy, _sx, _sy, (w, d, h) in row:
                    n += _island(seat, _volume, spec, qx, qy, w, d, h, bearing)
                    placed.append((qx, qy))
                    per_name[seat] += 1
            added += n
            return n

        def _cluster(pool, n):
            """Place 2-4 small pieces as one group. Returns pieces placed."""
'''

DISPATCH_OLD = '''            elif item[0] == "rows":
                _rows(item[1])
'''
DISPATCH_NEW = '''            elif item[0] == "rows":
                _rows(item[1])
            elif item[0] == "facing":
                _facing(item[1])
'''

PLAN_OLD = '''    items = []
    anchors = list(recipe["anchors"])
'''
PLAN_NEW = '''    # A ROOM THAT FACES A FRONT LAYS IT FIRST (0.270.0, `facing_slots`): its
    # rows are the room, and a wall run laid before them would take the
    # aisles they need. Outside the count, as rows are.
    items = [("facing", recipe["facing"])] if recipe.get("facing") else []
    anchors = list(recipe["anchors"])
'''

edit("level_design.py", [(KINDS_OLD, KINDS_NEW), (RECIPE_OLD, RECIPE_NEW), (PIECE_OLD, PIECE_NEW),
                         (FUNCS_ANCHOR, FUNCS_NEW + FUNCS_ANCHOR), (FURNISH_OLD, FURNISH_NEW),
                         (DISPATCH_OLD, DISPATCH_NEW), (PLAN_OLD, PLAN_NEW)])
edit("level_design.py", [('''    and twin_a01's front_right_1 both of its own and the shelter they gave."""
    if _room_kind(room, building) == "shop_floor" and _shop_rows(room, building):
        return "all"
''', '''    and twin_a01's front_right_1 both of its own and the shelter they gave.

    ``"all"`` in a room that FACES A FRONT (0.270.0, its recipe's `facing`):
    rows of pews are a store's rows by another name, and the census said so --
    unreserved, landmark_hall_a01's assembly hall stood a block of pews across
    its door to `entry_e`, 16.3 -> 20.8 m."""
    if _room_kind(room, building) == "shop_floor" and _shop_rows(room, building):
        return "all"
    if _RECIPES.get(_room_kind(room, building), {}).get("facing"):
        return "all"
''')])
edit("prop_species.py", [('''    (("chair", "seat", "bench", "waiting"), "chair"),
    (("pool", "billiard"), "pool_table"),''', '''    # a pew before a seat (0.270.0; Zoo's `pew`, >= 1.130.0): furnish's
    # `pew` and the funeral home's authored `pew_row` boxes
    (("pew",), "pew"),
    (("chair", "seat", "bench", "waiting"), "chair"),
    (("pool", "billiard"), "pool_table"),''')])
edit("tests/test_furnish.py", [('''    assert k({"id": "assembly_hall", "role": "public_entry"}) == "hall"
    assert k({"id": "chapel", "role": "public_entry"}) == "hall"
''', '''    assert k({"id": "assembly_hall", "role": "public_entry"}) == "assembly"
    assert k({"id": "chapel", "role": "public_entry"}) == "chapel"
'''), ('''    "chair": ((0.38, 12.0), (0.38, 2.0), (0.5, 1.1)),
''', '''    "chair": ((0.38, 12.0), (0.38, 2.0), (0.5, 1.1)),
    "pew": ((1.2, 8.0), (0.5, 1.0), (0.85, 1.1)),
''')])
edit("tests/test_seed_lines.py", [('''LINED = 35
''', '''# 35 -> 38 (0.270.0): funeral_home_a01's chapel and viewing_wing and funeral_home_a02's viewing_rooms. A dining
# hall's vending and shelves gave them shelter-height cover; pews are 0.95 m, so the shelter pass seeds a piece in
# each, laid in line.
LINED = 38
''')])
edit("tests/test_club_fixtures.py", [('''             ("bank_x", "lobby"): 1, ("museum_x", "exhibit_hall"): 1,
''', '''             # 0.270.0: an exhibit hall is a gallery, and a gallery is looked
             # at, not smoked in
             ("bank_x", "lobby"): 1, ("museum_x", "exhibit_hall"): 0,
'''), ('''    # a line, left the refurnish no wall for its machine
    assert counts == {"dartboard": 11, "cigarettes": 85}, counts
''', '''    # a line, left the refurnish no wall for its machine. 85 -> 71 (0.270.0):
    # the 14 that stood in chapels, courtrooms, assembly halls and galleries,
    # which a dining hall's recipe furnished, and whose own recipes stand none
    assert counts == {"dartboard": 11, "cigarettes": 71}, counts
''')])
edit("level_design.py", [('''    _piece("pew", ((3.6, 0.62, 0.95), (3.0, 0.62, 0.95), (2.4, 0.62, 0.95),
                   (4.2, 0.62, 0.95)), "floor", front=True, most=60),
''', '''    _piece("pew", ((3.6, 0.62, 0.95), (3.0, 0.62, 0.95), (2.4, 0.62, 0.95),
                   (4.2, 0.62, 0.95)), "floor", front=True, most=60),
    # A gallery's pew is a short one: a floor piece's spot stands a metre off
    # the room's bounds, which holds a piece to about 2.4 m, and the first
    # trial turned a 4.2 m pew 0.45 m through the generated compound's south
    # wall (`tests/test_wall_crossing.py`). The same species, by name.
    _piece("pew_short", ((2.4, 0.62, 0.95), (1.8, 0.62, 0.95)), "floor",
           front=True, most=6),
'''), ('''                "floor": ("pew",), "clusters": (), "per_area": 40.0,''',
       '''                "floor": ("pew_short",), "clusters": (), "per_area": 40.0,''')])
TEST = '''"""A chapel, a courtroom, an assembly hall and a gallery are furnished as what they are (0.270.0, the factory's
roadmap 308). These words were one `hall` kind with a dining hall's recipe, and a chapel stood a service counter,
vending and dining tables. FAILS ON 0.269.0: no such kinds, no front, no facing rows, no pew."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import level_design   # noqa: E402
import prop_species   # noqa: E402


def _spec(rid, w=24.0, d=12.0, door_x=None, volumes=()):
    """One room the shell, a door in its west (low-x) wall unless `door_x` says where in the south one."""
    s = {"name": "civic_probe", "seed": 1997, "story_height": 4.0,
         "footprint_x": w, "footprint_y": d, "n_stories": 1,
         "rooms": [{"id": rid, "story": 0, "role": "public_entry",
                    "bounds": [-w / 2, -d / 2, w / 2, d / 2], "combat_range": "medium"}],
         "ext_walls": [{"wall": "W", "story": 0, "openings": [{"kind": "door", "pos": 0.0, "width": 1.8}]}]
         if door_x is None else
         [{"wall": "S", "story": 0, "openings": [{"kind": "door", "pos": door_x / w, "width": 1.8}]}],
         "volumes": list(volumes), "partitions": [], "stairs": []}
    return s


def test_the_civic_words_have_their_own_kinds():
    k = level_design._room_kind
    assert k({"id": "chapel"}) == "chapel"
    assert k({"id": "viewing_wing"}) == "chapel"
    assert k({"id": "main_courtroom"}) == "courtroom"
    assert k({"id": "courtrooms"}) == "courtroom"
    assert k({"id": "assembly_hall"}) == "assembly"
    assert k({"id": "north_galleries"}) == "gallery"
    assert k({"id": "artifact_wing"}) == "gallery"
    assert "hall" not in level_design._RECIPES
    assert prop_species.species_for_name("pew_row_a") == "pew"


def test_the_front_is_the_end_away_from_the_door():
    s = _spec("chapel")
    assert level_design.room_front(s, s["rooms"][0]) == (True, 1)


def test_an_authored_row_turns_the_axis():
    row = {"name": "pew_row_a", "x": 0.0, "y": 0.0, "z": 0.45, "size_x": 8.0, "size_y": 0.9, "size_z": 0.9,
           "collision": "convex", "material": "wood"}
    s = _spec("chapel", door_x=0.0, volumes=[row])
    along_x, _sign = level_design.room_front(s, s["rooms"][0])
    assert along_x is False


def test_a_chapel_is_an_altar_and_pews_all_facing_it():
    s = _spec("chapel")
    level_design.furnish(s)
    names = [v["name"] for v in s["volumes"]]
    pews = [v for v in s["volumes"] if v["name"].startswith("pew_")]
    assert len(pews) >= 4, names
    assert sum(n.startswith("table_work_") for n in names) == 1
    assert not any(n.startswith(("counter_service_", "vending_", "table_dining_", "chair_waiting_")) for n in names)
    assert len({v.get("rot_z") for v in pews}) == 1, "every pew faces one way"
    altar = next(v for v in s["volumes"] if v["name"].startswith("table_work_"))
    assert altar["x"] > max(v["x"] for v in pews), "the altar stands at the front, beyond the rows"
    # a centre aisle: no pew crosses the room's middle line across the rows
    assert not any(abs(v["y"]) < v["size_y"] / 2.0 for v in pews)


def test_a_courtroom_has_its_bench_and_a_well_before_the_public():
    s = _spec("courtroom", w=30.0, d=14.0)
    level_design.furnish(s)
    by = lambda stem: [v for v in s["volumes"] if v["name"].startswith(stem + "_")]
    bench, tables, pews = by("counter_service"), by("table_work"), by("pew")
    assert len(bench) == 1 and len(tables) == 2 and pews
    assert bench[0]["x"] > max(t["x"] for t in tables) > max(p["x"] for p in pews)


def test_a_gallery_keeps_its_floor_open():
    s = _spec("galleries", w=30.0, d=14.0)
    level_design.furnish(s)
    r = s["rooms"][0]
    assert level_design.room_floor_share(s, r) < 0.12
    assert not any(v["name"].startswith(("counter_service_", "vending_", "table_dining_")) for v in s["volumes"])
'''
test = C / "tests" / "test_civic_rooms.py"
assert not test.exists()
test.write_bytes(TEST.encode("utf-8"))
print("wrote", test.name)
mig = C / "migrations" / "migrate_civic_rooms.py"
assert not mig.exists()
mig.write_bytes((pathlib.Path(__file__).resolve().parent / "migrate_civic_rooms.py").read_bytes())
print("wrote", mig.name)
print("done")
