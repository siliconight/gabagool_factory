"""Edit a Deli Counter clone for 0.280.0: a bank's rooms lit and floored as the walker's bank comps -- its public rooms a
selling room's lamp density, the bake-only reach and a hard floor; its money rooms bare tubes, not moody bulbs. Run from
the clone's root. Asserts every anchor once; refuses on a miss."""
from pathlib import Path


def edit(path, pairs):
    p = Path(path)
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in pairs:
        assert t.count(old) == 1, (path, old[:70], t.count(old))
        t = t.replace(old, new)
    if crlf:
        t = t.replace("\n", "\r\n")
    p.write_bytes(t.encode("utf-8"))
    print(path, "edited", len(pairs), "anchors", "CRLF" if crlf else "LF")


edit("lights.py", [
# --- the bank rule, one place --------------------------------------------------------------------
('''def is_residence(business):''',
'''#: A BANK READS AS THE WALKER'S COMPS (0.280.0, the factory's roadmap 321;
#: docs/reference/BANK_INTERIOR_COMPS.md): "bright, even ceilings" in every
#: public room, the money "in hard rooms ... all lit by bare tubes". Measured
#: on bank_branch_a02 before (docs/findings/bank_interior/): its lobby one lamp
#: a 39 m2, a mean of 37 under the level's light; its vault floor under bare
#: bulbs, one a 55 m2, 30-40. A bank's public room (`public_entry`) takes a
#: selling room's lamp density (`room_caps`) and the bake-only reach
#: (`bake_reach`); its rooms below grade and over the take take ceiling rows
#: of tubes instead of the moody bulbs every other building's do.
_BANK_WORDS = ("bank",)


def is_bank(business):
    """Does ``business`` (`level_design.club_building_id`) name a bank? A
    whole word of it: `bank_branch_a02`, `bank_job`, `bank_tower_a01`."""
    import re
    words = set(re.split(r"[^a-z0-9]+", str(business or "").lower()))
    return bool(words & set(_BANK_WORDS))


def bank_public(r, business):
    """A bank's public room: its `public_entry` (lobby, banking hall)."""
    return is_bank(business) and (r or {}).get("role") == "public_entry"


def is_residence(business):'''),
# --- room_caps: a named selling room as well as a selling id ------------------------------------
('''def room_caps(r, bounds):
    """``(max_rows, max_fixtures, max_lamps)`` for a room's ceiling rows: the
    library's `_MAX_ROWS`, `_MAX_FIXTURES` and `_MAX_LAMPS_ROOM`, except in a
    room whose id sells, whose lamps are one a `_SELLING_M2_PER_LAMP` of its
    floor and never fewer than `_MAX_LAMPS_ROOM`, bounding its rows and its
    lamps along alike (0.274.0)."""
    import floors
    if floors.floor_by_use((r or {}).get("id")) != "tile":
        return _MAX_ROWS, _MAX_FIXTURES, _MAX_LAMPS_ROOM''',
'''def room_caps(r, bounds, selling=False):
    """``(max_rows, max_fixtures, max_lamps)`` for a room's ceiling rows: the
    library's `_MAX_ROWS`, `_MAX_FIXTURES` and `_MAX_LAMPS_ROOM`, except in a
    room whose id sells -- or that the caller says is lit as one, ``selling``
    (a bank's public room, 0.280.0) -- whose lamps are one a
    `_SELLING_M2_PER_LAMP` of its floor and never fewer than `_MAX_LAMPS_ROOM`,
    bounding its rows and its lamps along alike (0.274.0)."""
    import floors
    if not selling and floors.floor_by_use((r or {}).get("id")) != "tile":
        return _MAX_ROWS, _MAX_FIXTURES, _MAX_LAMPS_ROOM'''),
# --- derive_light_anchors: the bank's rooms ------------------------------------------------------
('''                         storefronts=None, residence=False, landings=None,
                         bake_reach_rooms=None):''',
'''                         storefronts=None, residence=False, landings=None,
                         bake_reach_rooms=None, selling_rooms=None, tube_rooms=None):'''),
('''        moody = story < 0 or (bool(r.get("objective")) and r.get("role") not in _LIT_ROLES)
        if moody:
            home = False          # a bare bulb below grade or over the take''',
'''        moody = story < 0 or (bool(r.get("objective")) and r.get("role") not in _LIT_ROLES)
        # A BANK'S MONEY ROOMS ARE LIT BY TUBES (0.280.0, `tube_rooms`): the
        # comps' counting room and cage, not a moody cellar
        if moody and r.get("id") in (tube_rooms or ()):
            moody = False
        if moody:
            home = False          # a bare bulb below grade or over the take'''),
('''            rows = _rows_for_room(bounds, ceiling_z, c[2],
                                  _work_plane(r, home), home, lanes=lanes,
                                  caps=None if home else room_caps(r, bounds))''',
'''            rows = _rows_for_room(bounds, ceiling_z, c[2],
                                  _work_plane(r, home), home, lanes=lanes,
                                  caps=None if home else room_caps(
                                      r, bounds, selling=r.get("id") in (selling_rooms or ())))'''),
('''            for i, (pos, n, sp) in enumerate(got):
                runs.append((pos, n, sp, rot,
                             row_id if len(got) == 1 else "%s_%d" % (row_id, i)))
        room_reach = 0.0
        for pos, n, sp, rot, rid in runs:''',
'''            for i, (pos, n, sp) in enumerate(got):
                runs.append((pos, n, sp, rot,
                             row_id if len(got) == 1 else "%s_%d" % (row_id, i), spacing))
        room_reach = 0.0
        for pos, n, sp, rot, rid, row_sp in runs:'''),
('''            if (not moody and not home and sp > 0.0
                    and r.get("id") in (bake_reach_rooms or ())):
                anchors[-1]["bake_reach"] = round(float(sp), 3)''',
'''            # THE ROW'S spacing, not the run's (0.280.0): a row split round a
            # teller line's staff room leaves one-lamp runs whose own spacing
            # is 0, and they hang over the line
            if (not moody and not home and row_sp > 0.0
                    and r.get("id") in (bake_reach_rooms or ())):
                anchors[-1]["bake_reach"] = round(float(row_sp), 3)'''),
('''                                   landings=landings,
                                   bake_reach_rooms=_bake_reach_rooms(rooms, business))''',
'''                                   landings=landings,
                                   bake_reach_rooms=_bake_reach_rooms(rooms, business),
                                   selling_rooms=_selling_rooms(rooms, business),
                                   tube_rooms=_tube_rooms(rooms, business))'''),
('''    if not business:
        return set()
    import level_design
    return {r.get("id") for r in rooms or () if level_design.is_supermarket_floor(r, business)}
''',
'''    if not business:
        return set()
    import level_design
    return ({r.get("id") for r in rooms or () if level_design.is_supermarket_floor(r, business)}
            | _selling_rooms(rooms, business))


def _selling_rooms(rooms, business):
    """The rooms lit at a selling room's density whatever their id says
    (0.280.0): a bank's public rooms (`bank_public`)."""
    return {r.get("id") for r in rooms or () if bank_public(r, business)}


def _tube_rooms(rooms, business):
    """The rooms below grade or over the take that are lit by tubes, not
    moody bulbs (0.280.0): every such room of a bank."""
    if not is_bank(business):
        return set()
    return {r.get("id") for r in rooms or ()}
'''),
])

edit("floors.py", [
('''def _material(room, surface, mapping, default):
    """A room's own per-surface material wins (``floor_material`` /
    ``ceiling_material``); then its ``material`` for both; then the role
    map -- except that a floor the map would carpet is asked its use first
    (`floor_by_use`, 0.271.0); then the spec default."""
    own = (getattr(room, "%s_material" % surface, None)
           or getattr(room, "material", None))
    if own:
        return own
    got = mapping.get(getattr(room, "role", None), default)
    if surface == "floor" and got == "carpet":
        return floor_by_use(getattr(room, "id", None)) or got
    return got''',
'''#: A BANK'S PUBLIC FLOOR IS HARD (0.280.0, the factory's roadmap 321). The
#: note above kept carpet "right for a lobby, a banking hall"; the walker's
#: bank comps (docs/reference/BANK_INTERIOR_COMPS.md) put terrazzo or pale
#: tile in the public room in five of twelve, carpet only behind the line. A
#: bank's `public_entry` takes `tile`; what the tile is, the theme's.
BANK_PUBLIC_FLOOR = "tile"


def _material(room, surface, mapping, default, business=None):
    """A room's own per-surface material wins (``floor_material`` /
    ``ceiling_material``); then its ``material`` for both; then the role
    map -- except that a floor the map would carpet is asked its use first
    (`floor_by_use`, 0.271.0), and a bank's public floor is
    `BANK_PUBLIC_FLOOR` (0.280.0, ``business`` the building's
    `level_design.club_building_id`); then the spec default."""
    own = (getattr(room, "%s_material" % surface, None)
           or getattr(room, "material", None))
    if own:
        return own
    got = mapping.get(getattr(room, "role", None), default)
    if surface == "floor" and got == "carpet":
        import lights
        if lights.bank_public({"role": getattr(room, "role", None)}, business):
            return BANK_PUBLIC_FLOOR
        return floor_by_use(getattr(room, "id", None)) or got
    return got'''),
('''    import skin_style
    default = getattr(spec, "default_material", None)
    mapping = skin_style.material_styles(palette_ids(spec))
    out = []''',
'''    import skin_style
    import level_design
    default = getattr(spec, "default_material", None)
    mapping = skin_style.material_styles(palette_ids(spec))
    business = level_design.club_building_id(spec)
    out = []'''),
('''        fmat = _material(r, "floor", FLOOR_BY_ROLE, default)''',
'''        fmat = _material(r, "floor", FLOOR_BY_ROLE, default, business)'''),
])

edit("hole_causes.py", [
('''def _surface(spec, room, surface):
    mapping = floors.FLOOR_BY_ROLE if surface == "floor" else floors.CEILING_BY_ROLE
    return floors._material(types.SimpleNamespace(**room), surface, mapping,
                            spec.get("default_material"))''',
'''def _surface(spec, room, surface):
    # the building asked as `floors.slab_slots` asks it (0.280.0): a bank's
    # public floor is the slab's answer here too
    import level_design
    mapping = floors.FLOOR_BY_ROLE if surface == "floor" else floors.CEILING_BY_ROLE
    return floors._material(types.SimpleNamespace(**room), surface, mapping,
                            spec.get("default_material"), level_design.club_building_id(spec))'''),
])
