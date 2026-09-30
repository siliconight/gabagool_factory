"""Deli Counter 0.163.0: poster walls hung as fixtures in club, bar and shop rooms.

Every anchor asserted to match exactly once; nothing is written on a miss.
"""
import pathlib
import sys

DC = pathlib.Path(__file__).resolve().parent.parent / "deli_counter"

DISTINCT = '        vol = _make_volume(spec, key, f"{key}_{rtag}_{seq}", qx, qy, sx, sy, h, rot,\n                           story, sh, building)\n        if p["distinct"] and not _distinct_variant(spec, key, rtag, vol, variant_count(p)):\n            continue\n        spec.setdefault("volumes", []).append(vol)\n        return vol\n    return None\n\n\ndef _distinct_variant(spec, key, rtag, vol, mod):\n    """A `distinct` piece\'s variant, moved off any the same-size piece in its\n    room already shows; False when every variant is taken at this size.\n\n    WHY (0.163.0): a poster run\'s art is keyed on its Zoo module stem, which\n    is its size, form and variant, so two runs in one room with the same\n    width and variant are the SAME sheets in the same order -- measured on\n    the library at placement, 5 rooms of 48 had such a pair (the poster\n    baseline\'s "identical pairs side by side"). The name\'s crc32 still\n    chooses first, so a room with no clash is exactly what it was."""\n    size = (vol["size_x"], vol["size_y"], vol["size_z"])\n    taken = {int(v.get("variant", 0) or 0) for v in spec.get("volumes") or []\n             if str(v.get("name", "")).startswith(f"{key}_{rtag}_")\n             and (v["size_x"], v["size_y"], v["size_z"]) == size}\n    n = int(vol.get("variant", 0) or 0)\n    free = [(n + i) % mod for i in range(mod) if (n + i) % mod not in taken]\n    if not free:\n        return False\n    if free[0]:\n        vol["variant"] = free[0]\n    else:\n        vol.pop("variant", None)\n    return True'

EDITS = {
    "agent_contract.py": [
        ('''def chest_height():
    """Where a shot is aimed on a body, in metres above its feet.
''',
         '''def eye_height():
    """Where the gameplay camera sees from, in metres above the floor
    (`review.gameplay_camera_eye_m`): what a player's eye is level with, so
    the height a thing meant to be LOOKED AT hangs at. First caller:
    `level_design`'s poster walls (0.163.0), centred on it."""
    return float(contract()["review"]["gameplay_camera_eye_m"])


def chest_height():
    """Where a shot is aimed on a body, in metres above its feet.
'''),
    ],
    "prop_species.py": [
        ('''    (("poster", "wall_poster", "set_poster", "art_print", "framed_print",
      "picture_frame"), "poster"),''',
         '''    # THE POSTER WALLS (Zoo 1.30.0; placed 0.163.0): a run of posters, one
    # draw. Above the `poster` row, whose `poster` keyword is a substring of
    # every `poster_wall_*` name and would build each run as one card-shop
    # print.
    (("poster_wall",), "poster_wall"),
    (("poster", "wall_poster", "set_poster", "art_print", "framed_print",
      "picture_frame"), "poster"),'''),
    ],
    "level_design.py": [
        # the contract's eye, imported where it is asked (this file's habit)
        ('''    return _clear_height(spec) - float(p["under"]) - h / 2.0


_PIECES = {p["name"]: p for p in (''',
         '''    return _clear_height(spec) - float(p["under"]) - h / 2.0


def _eye_height():
    """`agent_contract.eye_height`, imported where it is asked as this file
    imports the contract everywhere else."""
    import agent_contract
    return agent_contract.eye_height()


_PIECES = {p["name"]: p for p in ('''),
        # the piece's room gate
        ('''           ceiling=None, under_hung=False, twin=False, wall_band=False):
    return {"name": name, "sizes": tuple(sizes), "where": where,''',
         '''           ceiling=None, under_hung=False, twin=False, wall_band=False,
           rooms=None):
    return {"name": name, "sizes": tuple(sizes), "where": where,'''),
        ('''            "ceiling": ceiling, "under_hung": under_hung, "twin": twin,
            "wall_band": wall_band}''',
         '''            "ceiling": ceiling, "under_hung": under_hung, "twin": twin,
            "wall_band": wall_band,
            "rooms": frozenset(rooms) if rooms else None}'''),
        # the three pieces, after the banner
        ('''    _piece("hanging_banner", ((1.8, 0.05, 0.7), (2.4, 0.06, 0.9),
                              (1.2, 0.04, 0.6)), "wall", front=True,
           variants=True, most=2, under=_UNDER_PENNANTS, collision="none"),''',
         '''    _piece("hanging_banner", ((1.8, 0.05, 0.7), (2.4, 0.06, 0.9),
                              (1.2, 0.04, 0.6)), "wall", front=True,
           variants=True, most=2, under=_UNDER_PENNANTS, collision="none"),
    # --- THE POSTER WALLS (Zoo 1.30.0-1.32.0; placed 0.163.0). The walker,
    # 2026-09-29, choosing where posters go: strip club interiors, bar
    # interiors, exterior alley walls and poles, store windows and walls.
    # This is the three INTERIOR kinds; the alleys and poles are Lot's.
    #
    # A RUN, NOT A POSTER: Zoo's `poster_wall` lays sheets along the slot
    # and builds the run as ONE object with ONE material, so a wall of five
    # club posters is one draw (CLAUDE.md: draw calls are the budget). The
    # slot's HEIGHT is Zoo's `poster_wall_forms.band_height(family)` -- the
    # sheet plus the family's wander: club 0.64, bar 0.44 + 0.06, store 0.60
    # -- and its depth the genome's default 0.01. Widths are runs of three
    # to six sheets.
    #
    # HUNG AT THE EYE (`agent_contract.eye_height`, 1.6): a poster is there
    # to be looked at, and the band's centre on the camera's eye is where it
    # faces a player square. Hung, so `_seed_clear` keeps a unit standing
    # under it lower than its bottom -- a shelf run to 2.70 takes the wall
    # and the posters go to one that is free, the card shop's arbitration.
    #
    # FOUR VARIANTS, NOT ZOO'S EIGHT, and the reason is `_make_volume`: past
    # four it keys the variant on the BUILDING (neon_sign's one name over
    # every door), so every same-width run in a building would draw the same
    # sheets in the same order -- the baseline's "identical pairs side by
    # side". At four it is the volume name's, and two runs in one room differ.
    #
    # `rooms` GATES THE BAR'S AND THE STORE'S. The `club` kind is a tavern's
    # bar and also a country club's lounge, a stadium's skybox and a trophy
    # room, and a photocopied gig bill belongs in the first only. The
    # `shop_floor` kind claims any room whose id says `floor` or `aisle`, and
    # MEASURED before this gate the library would have hung sale posters on
    # 158 walls including warehouse, foundry, arena, office and self-storage
    # floors; a sale poster belongs where something is sold. And OFF THE
    # GLASS: a run hung inside a storefront faces the shop, so the street
    # sees its back; a store's window posters face out, and that is a rule
    # of its own (the window sign's), not this one.
    _piece("poster_wall_club", ((2.4, 0.01, 0.64), (1.6, 0.01, 0.64),
                                (3.2, 0.01, 0.64)), "wall", front=True,
           variants=4, form="club", most=3, most_big=(150.0, 5),
           lift=_eye_height(), collision="none", distinct=True),
    _piece("poster_wall_bar", ((1.8, 0.01, 0.5), (1.2, 0.01, 0.5),
                               (2.4, 0.01, 0.5)), "wall", front=True,
           variants=4, form="bar", most=2, most_big=(80.0, 3),
           lift=_eye_height(), collision="none", distinct=True,
           rooms=("bar", "taproom", "tavern", "pub", "social")),
    _piece("poster_wall_store", ((1.6, 0.01, 0.6), (1.0, 0.01, 0.6),
                                 (2.2, 0.01, 0.6)), "wall", front=True,
           variants=4, form="store", most=2, most_big=(150.0, 3),
           lift=_eye_height(), collision="none", distinct=True, off_glass=True,
           rooms=("sales", "retail", "shop", "customer", "market", "showroom",
                  "stall")),'''),
        # recipes
        ('''             "floor": ("table_dining",),
             "clusters": (), "fixtures": ("cigarettes",)},''',
         '''             "floor": ("table_dining",),
             "clusters": (), "fixtures": ("cigarettes", "poster_wall_bar")},'''),
        ('''                   # placed after the room is furnished (`place_fixtures`)
                   "fixtures": ("dartboard", "cigarettes")},''',
         '''                   # placed after the room is furnished (`place_fixtures`)
                   "fixtures": ("dartboard", "cigarettes", "poster_wall_club")},'''),
        ('''                   "floor": (),
                   "clusters": ((("cartons",), 2, 3), (("litter_bin",), 1, 1))},''',
         '''                   "floor": (),
                   "clusters": ((("cartons",), 2, 3), (("litter_bin",), 1, 1)),
                   "fixtures": ("poster_wall_store",)},'''),
        # material: before the card-shop poster's row
        ('''    (("poster",), "metal_bare"),
    (("hanging_banner",), "cloth"),''',
         '''    # `poster_wall` is paper, its genome's own kind; above `poster`, whose
    # keyword every `poster_wall_*` key contains
    (("poster_wall",), "paper"),
    (("poster",), "metal_bare"),
    (("hanging_banner",), "cloth"),'''),
        # the gate, in place_fixtures
        ('''        fixtures = _RECIPES[_room_kind(room, building)].get("fixtures") or ()
        rtag = _room_tag(room)
        for key in fixtures:
            for k in range(fixture_limit(key, area)):''',
         '''        fixtures = _RECIPES[_room_kind(room, building)].get("fixtures") or ()
        rtag = _room_tag(room)
        tokens = set(str(room.get("id", "")).lower().replace("-", "_").split("_"))
        for key in fixtures:
            only = _PIECES[key]["rooms"]
            if only and not tokens & only:
                continue
            for k in range(fixture_limit(key, area)):'''),
        # a distinct piece's variant (applied after the edits above)
        ('''           rooms=None):''',
         '''           rooms=None, distinct=False):'''),
        ('''            "rooms": frozenset(rooms) if rooms else None}''',
         '''            "rooms": frozenset(rooms) if rooms else None,
            "distinct": distinct}'''),
        ('''        vol = _make_volume(spec, key, f"{key}_{rtag}_{seq}", qx, qy, sx, sy, h, rot,
                           story, sh, building)
        spec.setdefault("volumes", []).append(vol)
        return vol
    return None''',
         DISTINCT),
    ],
}


def main():
    staged = {}
    for name, edits in EDITS.items():
        p = DC / name
        raw = p.read_bytes()
        assert b"\r\n" not in raw, f"{name}: CRLF, expected LF"
        s = raw.decode("utf-8")
        for a, b in edits:
            n = s.count(a)
            if n != 1:
                sys.exit(f"REFUSED: {name}: anchor matched {n} times:\n{a[:120]}")
            s = s.replace(a, b, 1)
        staged[p] = s
    for p, s in staged.items():
        p.write_bytes(s.encode("utf-8"))
        print(f"patched {p.name}")


if __name__ == "__main__":
    main()
