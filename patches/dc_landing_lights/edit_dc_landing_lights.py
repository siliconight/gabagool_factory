"""Deli Counter 0.261.0, applied to a CLONE (<repo>): every opening's landing is lit to read from above, even in a
moody room. The walker, walking cold run 9383: "this shouldn't look pitch black" of a stair opening onto deli_a03's
basement, and the rule they gave: "you should be able to see into holes to know you can go forward into them"
(`docs/findings/walk_2026-10-23_deli/`). Anchored; refuses on a miss; keeps line endings."""
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


edit("lights.py", [
    # the rule, beside the moody rule it overrides at one point
    ("""_PENDANT_AREA = 25.0    # m^2 of room per bare bulb""",
     """_PENDANT_AREA = 25.0    # m^2 of room per bare bulb
#: AN OPENING SHOWS WHERE IT GOES (0.261.0). The walker, 2026-10-23, of a stair opening onto deli_a03's basement read
#: pitch black from above: "you should be able to see into holes to know you can go forward into them". A moody room
#: keeps its bare bulbs and its dark corners, but the LANDING of every opening into it -- a stair's foot, the floor
#: under a hole, a ladder's base (`opening_landings`) -- gets a fluorescent over it, the light an ordinary room is
#: lit by, so the place a way leads to reads from the way in. Measured before: the stairs land in cold storage at
#: luma p50 10, the vault p50 3, against the stairwell above at 74 (`tools/light_check.py`).
_LANDING_OFF_HOLE = 0.6   # metres past a hole's edge a landing lamp hangs, so it is mounted to ceiling, not air"""),
    ("""def derive_light_anchors(rooms, openings, story_height, *, cap_thick,
                         wall_thick, ceiling_voids=None, partitions=None,
                         report=None, volumes=None, club_rooms=None,
                         storefronts=None, residence=False):""",
     """def opening_landings(spec):
    \"\"\"Where every opening into a storey lands, in spec metres: [{story, x, y, kind}] -- a stair's lower end
    (`stairwell.stair_endpoints`), the floor under each hole in a slab that is not a stair's own
    (`axonometric._slab_holes`: authored holes, floor holes, hatches), a ladder's base. One entry a place: a hole
    named twice (as authored and as its link) is one landing.\"\"\"
    import axonometric
    import stairwell
    out, seen = [], set()

    def add(story, x, y, kind):
        key = (int(story), round(float(x), 2), round(float(y), 2))
        if key not in seen:
            seen.add(key)
            out.append({"story": int(story), "x": round(float(x), 3), "y": round(float(y), 3), "kind": kind})
    for st in getattr(spec, "stairs", []) or []:
        for e in stairwell.stair_endpoints(st):
            if e["end"] == "lower":
                add(min(st.from_story, st.to_story), e["point"][0], e["point"][1], "stair")
    for s, rects in sorted(axonometric._slab_holes(spec).items()):
        for r, kind in rects:
            if kind != "stair":
                add(s - 1, (r[0] + r[2]) / 2.0, (r[1] + r[3]) / 2.0, "hole")
    for ld in getattr(spec, "ladders", []) or []:
        add(min(ld.from_story, ld.to_story), ld.x, ld.y, "ladder")
    return out


def _landing_point(x, y, bounds, voids):
    \"\"\"A landing lamp's point: over the landing, or -- where a hole is over it, as over a hole's own landing --
    just past the hole's edge on the side nearest the room's middle, so it hangs from ceiling. None when no side
    stands inside the room.\"\"\"
    hit = [v for v in (voids or ()) if v[0] <= x <= v[2] and v[1] <= y <= v[3]]
    if not hit:
        return (x, y)
    x0, y0, x1, y1 = hit[0]
    cx, cy = (bounds[0] + bounds[2]) / 2.0, (bounds[1] + bounds[3]) / 2.0
    d = _LANDING_OFF_HOLE
    cands = [(x0 - d, (y0 + y1) / 2.0), (x1 + d, (y0 + y1) / 2.0), ((x0 + x1) / 2.0, y0 - d),
             ((x0 + x1) / 2.0, y1 + d)]
    cands = [p for p in cands if bounds[0] < p[0] < bounds[2] and bounds[1] < p[1] < bounds[3]
             and not any(v[0] <= p[0] <= v[2] and v[1] <= p[1] <= v[3] for v in voids)]
    if not cands:
        return None
    return min(cands, key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2)


def derive_light_anchors(rooms, openings, story_height, *, cap_thick,
                         wall_thick, ceiling_voids=None, partitions=None,
                         report=None, volumes=None, club_rooms=None,
                         storefronts=None, residence=False, landings=None):"""),
    ("""    `storefronts` (0.155.0) are the storefront slots as ``{story, facing, x,
    y}``; a fluorescent row whose room they wall carries `reach`, the metres
    to that glass (`_storefront_reach`). Without them no anchor carries it.
    \"\"\"""",
     """    `storefronts` (0.155.0) are the storefront slots as ``{story, facing, x,
    y}``; a fluorescent row whose room they wall carries `reach`, the metres
    to that glass (`_storefront_reach`). Without them no anchor carries it.

    `landings` (0.261.0) are `opening_landings`: a moody room gets a
    fluorescent over each one inside it (see `_LANDING_OFF_HOLE`), appended
    last with the spills, so every anchor before it keeps its place.
    \"\"\""""),
    ("""    rep.setdefault("rows_over_aisles", 0)""",
     """    rep.setdefault("rows_over_aisles", 0)
    rep.setdefault("landing_lights", 0)"""),
    ("""                rep["counter_accents"] += 1
""",
     """                rep["counter_accents"] += 1
        # THE LANDINGS (0.261.0): in a moody room, a fluorescent over every place an opening comes down into it
        if moody:
            mine = [g for g in (landings or ()) if int(g["story"]) == story
                    and bounds[0] <= g["x"] <= bounds[2] and bounds[1] <= g["y"] <= bounds[3]]
            for k, g in enumerate(mine):
                at = _landing_point(g["x"], g["y"], bounds, rects)
                if at is None:
                    continue
                for pos, _n, _sp in _row_runs([at[0], at[1], ceiling_z], 0.0, 1, 0.0, rects,
                                              walls=walls, clear=clear, report=rep):
                    spills.append({
                        "id": "%s_landing%s" % (r.get("id", "room"), "_%d" % k if k else ""),
                        "type": "fluorescent",
                        "source": "derived",
                        "pos": pos,
                        "rot_y": 0.0,
                        "room": r.get("id"),
                        "row": {"count": 1, "spacing": 0.0},
                        "drop": round(ceiling_z - c[2], 3),
                        "landing": g["kind"],
                        "reacts_to_alarm": True,
                    })
                    rep["landing_lights"] += 1
"""),
    ("""def build_light_manifest(building_id, rooms, openings, story_height,
                         *, cap_thick, wall_thick, authored=None, theme=None,
                         ceiling_voids=None, partitions=None, report=None,
                         volumes=None, club_rooms=None, storefronts=None,
                         business=None):""",
     """def build_light_manifest(building_id, rooms, openings, story_height,
                         *, cap_thick, wall_thick, authored=None, theme=None,
                         ceiling_voids=None, partitions=None, report=None,
                         volumes=None, club_rooms=None, storefronts=None,
                         business=None, landings=None):"""),
    ("""                                   storefronts=storefronts,
                                   residence=is_residence(business))""",
     """                                   storefronts=storefronts,
                                   residence=is_residence(business),
                                   landings=landings)"""),
])

edit("deli_counter.py", [
    ("""        # WHO IS INSIDE (0.165.0): the identity a club's neon is keyed on,
        # which the sign over the door names (Zoo 1.37.0)
        business=_ld.club_building_id(builder.s),
    )""",
     """        # WHO IS INSIDE (0.165.0): the identity a club's neon is keyed on,
        # which the sign over the door names (Zoo 1.37.0)
        business=_ld.club_building_id(builder.s),
        # WHERE EVERY OPENING LANDS (0.261.0): lit in a moody room, so it reads from above
        landings=_lights.opening_landings(builder.s),
    )"""),
])
edit("test_lights_partitions.py", [
    ('''                   "storefront_spills": 0, "counter_accents": 0, "rows_laid": 1,
                   "rows_over_aisles": 0}''',
     '''                   "storefront_spills": 0, "counter_accents": 0, "rows_laid": 1,
                   "rows_over_aisles": 0, "landing_lights": 0}'''),
])
print("edited", R)
