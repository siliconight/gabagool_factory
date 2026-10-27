"""Edit a Deli Counter clone for 0.279.0: a supermarket's fluorescent rows carry `bake_reach`, their lamp spacing, so
Lux (>= 0.80.0) bakes them to the floor under the next lamp along while their live range stays the short one. Run from
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
('''                         storefronts=None, residence=False, landings=None):
    """Derive default light anchors: one fluorescent ceiling row per interior''',
'''                         storefronts=None, residence=False, landings=None,
                         bake_reach_rooms=None):
    """Derive default light anchors: one fluorescent ceiling row per interior'''),
('''            if not moody:
                reach = _storefront_reach(bounds, story, pos, rot, n, sp,
                                          storefronts, wall_thick)
                if reach > 0.0:
                    anchors[-1]["reach"] = reach
                    rep["storefront_rows"] += 1
                    room_reach = max(room_reach, reach)
''',
'''            if not moody:
                reach = _storefront_reach(bounds, story, pos, rot, n, sp,
                                          storefronts, wall_thick)
                if reach > 0.0:
                    anchors[-1]["reach"] = reach
                    rep["storefront_rows"] += 1
                    room_reach = max(room_reach, reach)
            # A ROW THAT BAKES TO THE NEXT LAMP (0.279.0): a room in
            # `bake_reach_rooms` -- a supermarket's selling floor -- stamps its
            # row's spacing as `bake_reach`, and Lux (>= 0.80.0) bakes the
            # lamp to the floor under the next one along while its live
            # range, the per-mesh claim, stays the drop rule. Measured on the
            # walker's level: the store's frame 38.5 -> 61.5 mean at x 1.6
            # range (the factory's docs/findings/black_gondola_ends/).
            if (not moody and not home and sp > 0.0
                    and r.get("id") in (bake_reach_rooms or ())):
                anchors[-1]["bake_reach"] = round(float(sp), 3)
'''),
('''                                   residence=is_residence(business),
                                   landings=landings)''',
'''                                   residence=is_residence(business),
                                   landings=landings,
                                   bake_reach_rooms=_bake_reach_rooms(rooms, business))'''),
('''def build_light_manifest(building_id, rooms, openings, story_height,''',
'''def _bake_reach_rooms(rooms, business):
    """The rooms whose fluorescent rows bake to the next lamp (0.279.0): a
    supermarket's selling floor (`level_design.is_supermarket_floor`), the
    walker's "far too dark in the super market"."""
    if not business:
        return set()
    import level_design
    return {r.get("id") for r in rooms or () if level_design.is_supermarket_floor(r, business)}


def build_light_manifest(building_id, rooms, openings, story_height,'''),
])
