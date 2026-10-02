"""Deli Counter 0.171.0: a 1997 video rental store.

The walker's queue, 2026-09-29: "a new building type: a VHS movie rental
store". Their calls, 2026-10-02: MACDADE MOVIES; the curtained back room,
"suggestive only"; no references -- build from the era. Zoo 1.43.0 draws the
tape racks (`video_rack`: wall, island, adult) and names the door.

  * `presets.video_store`: a strip-mall unit, 18 x 14 m, one storey. A glass
    storefront; the sales floor wall to wall; behind it a stockroom on the
    rear door and the BACK ROOM behind a curtain. THE RACKS ARE AUTHORED,
    the gas station's gondolas' way: racks down both side walls and along
    the back wall, four rows of low islands, the checkout counter by the
    door, the back room's two walls.
  * `level_design`: the kinds `video_store` (a selling room of a building
    whose id says `video_store`) and `video_back` (its back room) and their
    recipes -- what the furnisher may ADD round the authored racks.
  * `prop_species`: `tape_wall` and `tape_island` route to Zoo's
    `video_rack`, above the counter row (whose `island` would claim every
    `tape_island_*`).

WHY THE RACKS ARE NOT THE FURNISHER'S, MEASURED. The first draft gave the
recipe `tape_wall` pieces. `_seed_clear` clears a piece as a square of its
longest side, the sales floor's cover is seeded first, and an 18 x 10 m floor
stood ONE 4 m rack, then two 2 m ones with the racks as anchors -- a video
store with two shelves. A rental store's walls are lined end to end, and
that is a floor plan, which is what a preset is.

Every edit asserts its anchor once and refuses to write on a miss.
"""
from __future__ import annotations

import pathlib

DC = pathlib.Path(__file__).resolve().parents[1] / "deli_counter"


def _edit(rel, pairs):
    p = DC / rel
    raw = p.read_bytes()
    assert b"\r\n" not in raw, f"{rel}: CRLF in an LF file"
    s = raw.decode("utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, f"{rel}: anchor found {n} times: {old[:60]!r}"
        s = s.replace(old, new)
    p.write_bytes(s.encode("utf-8"))
    print("patched", rel)


PRESET = '''def video_store(name: str = "video_store_preset", mode: str = "heist",
                floors: int = 1, basement: bool = False,
                scale_ref: bool = False) -> dict:
    """A 1997 Delco video rental store: a strip-mall unit with a GLASS
    STOREFRONT, a sales floor of tape racks, a stockroom on the rear door,
    and THE BACK ROOM behind a curtain.

    The walker, 2026-09-29: "a new building type: a VHS movie rental store";
    2026-10-02: it is MACDADE MOVIES, it has the curtained back room
    ("suggestive only"), and there are no references -- build from the era.
    The era's store is walls of boxes faced out under a genre board, low
    islands of more down the floor, a checkout counter, and a doorway at
    the back with a sign over it.

    The selling rooms are furnished as a video store by 0.171.0's recipes:
    the kind is read off the building's id (`level_design.
    is_video_store_room`), and this spec carries `preset: "video_store"` so
    that holds when Level Factory names the level `lf_<mission>_<seed>`. The
    stockroom keeps `storage`.

    THE RACKS ARE AUTHORED HERE, not furnished: both side walls and the
    back wall lined, four rows of low islands, the checkout by the door,
    the back room's two walls -- the gas station's gondolas' way. The side
    walls are blank brick so the racks have a wall to stand against.

    ONE STOREY. `floors` and `basement` are accepted so the CLI stays
    uniform and are not read: a strip-mall unit has no flat over it and its
    back of house is behind the shop."""
    del floors, basement
    sh = 3.4
    fx, fy = 18.0, 14.0
    hx, hy = fx / 2, fy / 2
    band = 3.0                      # shop front | back of house
    mid_x = 3.0                     # stockroom | back room
    spec = {
        "$schema": "../schema/level.schema.json",
        "name": name, "mode": mode, "preset": "video_store",
        "seed": 1997, "grid": 0.5,
        "footprint_x": fx, "footprint_y": fy, "story_height": sh,
        "n_stories": 1, "has_basement": False,
        "wall_thick": 0.25, "floor_thick": 0.25,
        "collision": "convex", "auto_exterior": True,
        "scale_ref": bool(scale_ref),
        "default_material": "brick_ext",
        "materials": [
            {"id": "brick_ext", "acoustic": "Concrete", "absorption": 0.6, "damping": 0.5},
            {"id": "storefront_glass", "acoustic": "Glass", "absorption": 0.1, "damping": 0.05},
            {"id": "glass", "acoustic": "Glass", "absorption": 0.1, "damping": 0.05},
            {"id": "drywall", "acoustic": "Drywall", "absorption": 0.42, "damping": 0.38},
            {"id": "concrete", "acoustic": "Concrete", "absorption": 0.7, "damping": 0.6},
            {"id": "metal", "acoustic": "Metal", "absorption": 0.2, "damping": 0.15},
            {"id": "wood", "acoustic": "Wood", "absorption": 0.35, "damping": 0.3},
        ],
    }

    def _along(x, lo, hi):
        """An opening's `pos` for a wall running lo..hi, placed at x."""
        return round((x - (lo + hi) / 2.0) / (hi - lo), 4)

    spec["ext_walls"] = [
        {"wall": "S", "story": 0, "material": "storefront_glass", "openings": [
            {"kind": "door", "pos": _along(-4.0, -hx, hx), "width": 1.6,
             "tag": "front_door"},
            {"kind": "window", "pos": _along(3.0, -hx, hx), "width": 8.0,
             "sill": 0.6, "vaultable": True, "material": "glass"}]},
        {"wall": "N", "story": 0, "material": "brick_ext", "openings": [
            {"kind": "door", "pos": _along(-6.0, -hx, hx), "width": 1.25,
             "tag": "rear_door"},
            {"kind": "breach", "pos": _along(0.5, -hx, hx), "width": 1.2,
             "breach_class": "soft_wall", "material": "drywall",
             "tag": "stock_breach"}]},
        {"wall": "W", "story": 0, "material": "brick_ext", "openings": []},
        {"wall": "E", "story": 0, "material": "brick_ext", "openings": []},
    ]
    # --- plan. SOUTH BAND (y -7..3, 10 m deep): the sales floor, wall to
    # wall. NORTH BAND (y 3..7, 4 m deep): the stockroom on the rear door,
    # west; the back room behind its curtain, east. Every partition ends
    # clear of every doorway it meets (layout_lint L18) and every door joins
    # two rooms (L10). The back room's second way in is the stockroom's
    # door through the wall they share, so it is not a dead end.
    spec["partitions"] = [
        {"story": 0, "axis": "X", "pos": band, "start": -hx, "end": hx,
         "material": "drywall", "openings": [
             {"kind": "door", "pos": _along(-6.0, -hx, hx), "width": 1.25,
              "reinforceable": True, "tag": "stock_door"},
             {"kind": "door", "pos": _along(6.0, -hx, hx), "width": 1.25,
              "tag": "back_room_curtain"}]},
        {"story": 0, "axis": "Y", "pos": mid_x, "start": band, "end": hy,
         "material": "drywall", "openings": [
             {"kind": "door", "pos": _along(5.0, band, hy), "width": 1.25,
              "tag": "back_room_staff_door"}]},
    ]
    spec["stairs"] = []
    spec["ladders"] = []
    spec["vertical_links"] = []
    # THE RACKS ARE AUTHORED (see this function's note in the changelog):
    # Zoo's `video_rack`, 2.4 m runs set 2 cm apart, in the frame every
    # authored prop uses -- a volume long in x faces -y, one long in y faces
    # -x, and `rot_z` 180 turns either round.
    wt = spec["wall_thick"]
    run, gap, deep, tall = 2.4, 0.02, 0.45, 2.0
    off = wt / 2.0 + 0.01 + deep / 2.0         # a rack's centre off a wall's line

    def _rack(name, x, y, along, form, variant, turned=False, d=deep, h=tall):
        v = {"name": name, "x": round(x, 3), "y": round(y, 3), "z": h / 2.0,
             "size_x": run if along == "x" else d,
             "size_y": d if along == "x" else run, "size_z": h,
             "collision": "convex", "material": "metal_painted",
             "form": form, "variant": variant}
        if turned:
            v["rot_z"] = 180.0
        return v

    step = run + gap
    racks = []
    # the WEST wall, north of the checkout: two runs, facing the room (+x)
    for k, y in enumerate((-1.75, -1.75 + step)):
        racks.append(_rack(f"tape_wall_w{k + 1}", -hx + off, y, "y", "wall", k, turned=True))
    # the EAST wall, door to back: three runs, facing the room (-x)
    for k, y in enumerate((-4.2, -4.2 + step, -4.2 + 2 * step)):
        racks.append(_rack(f"tape_wall_e{k + 1}", hx - off, y, "y", "wall", 2 + k))
    # the BACK wall, between the two doors: three runs, facing the door (-y)
    for k, x in enumerate((-step, 0.0, step)):
        racks.append(_rack(f"tape_wall_n{k + 1}", x, band - off, "x", "wall", (5 + k) % 6))
    # FOUR ROWS OF ISLANDS, two runs a row, low enough to see the back wall
    # over. The aisles between rows are 1.7 to 2.6 m and the one along the
    # back wall is 1.4: every one is over `min_corridor_width` 1.1.
    for c, x in enumerate((-3.5, 0.0, 3.0, 6.0)):
        for k, y in enumerate((-2.82, -2.82 + step)):
            racks.append(_rack(f"tape_island_{c + 1}{'ab'[k]}", x, y, "y", "island",
                               (c * 2 + k) % 6, d=0.9, h=1.4))
    # THE BACK ROOM: its north and east walls, MEETING AT THE CORNER -- the
    # north run ends on the east rack's front and the east rack ends 2 cm
    # under the north run's. The first draft left a 0.2 x 0.6 m pocket
    # between them, which is neither a wall nor an aisle.
    east_front = hx - off - deep / 2.0
    north_front = hy - off - deep / 2.0
    for k in range(2):
        racks.append(_rack(f"tape_wall_adult_n{k + 1}", east_front - run / 2.0 - (1 - k) * step,
                           hy - off, "x", "adult", k))
    racks.append(_rack("tape_wall_adult_e1", hx - off, north_front - gap - run / 2.0,
                       "y", "adult", 2))
    # THE CHECKOUT, by the front door: the counter stands a staff aisle off
    # the west wall, the clerk behind it
    # (y -5.2: at -4.8 its corner stood 1.04 m off the first west rack's,
    # under `min_corridor_width`, across the way out of the staff aisle)
    counter = {"name": "counter_checkout", "x": -7.2, "y": -5.2, "z": 0.525,
               "size_x": 0.8, "size_y": 2.4, "size_z": 1.05,
               "collision": "convex", "material": "wood"}
    # ...and the store's floor safe, the objective.
    safe = (-8.2, 6.2, 0.2)
    spec["materials"].append(
        {"id": "metal_painted", "acoustic": "Metal", "absorption": 0.25, "damping": 0.2})
    spec["volumes"] = [
        {"name": "safe_stockroom", "x": safe[0], "y": safe[1], "z": 0.5,
         "size_x": 0.9, "size_y": 0.9, "size_z": 1.0, "collision": "convex",
         "material": "metal"},
        counter,
    ] + racks
    spec["rooms"] = [
        {"id": "sales_floor", "story": 0, "bounds": [-hx, -hy, hx, band],
         "role": "public_entry", "combat_range": "long"},
        {"id": "stockroom", "story": 0, "bounds": [-hx, band, mid_x, hy],
         "role": "objective_room", "objective": True, "fortifiable": True,
         "combat_range": "medium"},
        {"id": "back_room", "story": 0, "bounds": [mid_x, band, hx, hy],
         "role": "connector", "combat_range": "close"},
    ]
    door_in = (-4.0, -5.5)          # just inside the front door
    markers = [
        {"type": "camera_socket", "id": "01", "x": -8.0, "y": -6.0, "z": 2.9,
         "room": "sales_floor", "rot_z": 45},
        {"type": "camera_socket", "id": "02", "x": -8.2, "y": 3.8, "z": 2.9,
         "room": "stockroom", "rot_z": 135},
    ]
    if mode == "heist":
        spec["objectives"] = [
            {"id": "crack_safe", "kind": "drill", "x": safe[0], "y": safe[1],
             "z": safe[2], "room": "stockroom", "required": True,
             "duration": 25.0},
            {"id": "grab_late_fees", "kind": "grab", "x": 6.0, "y": 5.0,
             "z": 0.9, "room": "back_room", "required": False,
             "duration": 6.0},
        ]
        spec["loot"] = [
            {"id": "store_safe", "kind": "cash", "x": safe[0], "y": safe[1],
             "z": safe[2], "value": 7000, "bags": 2, "room": "stockroom"},
            {"id": "late_fees", "kind": "cash", "x": 6.0, "y": 5.0,
             "z": 0.9, "value": 1500, "bags": 1, "room": "back_room"},
        ]
        spec["zones"] = [
            {"id": "front_extract", "kind": "extraction", "story": 0,
             "bounds": [-hx, -hy, hx, -4.5]},
            {"id": "stock_secure", "kind": "secure", "story": 0,
             "bounds": [-hx, band, mid_x, hy]},
        ]
        markers += [
            {"type": "crew_spawn", "id": "A", "x": door_in[0], "y": door_in[1],
             "z": 0.0, "rot_z": 0, "room": "sales_floor",
             "meta": {"phase": "stealth"}},
            {"type": "objective", "id": "SAFE", "x": safe[0], "y": safe[1],
             "z": safe[2], "room": "stockroom"},
            {"type": "extraction", "id": "FRONT", "x": door_in[0] - 2.0,
             "y": door_in[1], "z": 0.0, "room": "sales_floor"},
        ]
    else:
        markers += [
            {"type": "attacker_spawn", "id": "A", "x": door_in[0],
             "y": door_in[1], "z": 0.0, "rot_z": 0, "room": "sales_floor"},
            {"type": "attacker_spawn", "id": "B", "x": 6.0, "y": 5.0,
             "z": 0.0, "rot_z": 180, "room": "back_room"},
            {"type": "defender_spawn", "id": "D", "x": -4.0, "y": 5.0,
             "z": 0.0, "rot_z": 180, "room": "stockroom"},
            {"type": "objective", "id": "SAFE", "x": safe[0], "y": safe[1],
             "z": safe[2], "room": "stockroom",
             "meta": {"kind": "secure"}},
        ]
    spec["markers"] = markers
    spec["parapets"] = [{"story": 1, "height": 0.9, "thick": 0.3}]
    return spec


'''

PRESETS = [
    ('''# ---------------------------------------------------------------------------
# FACADE shells -- non-enterable filler buildings: exterior + roof + collision
''', PRESET + '''# ---------------------------------------------------------------------------
# FACADE shells -- non-enterable filler buildings: exterior + roof + collision
'''),
    ('''    "card_shop": card_shop,
''', '''    "card_shop": card_shop,
    "video_store": video_store,
'''),
]

LEVEL = [
    # --- the room rule ---------------------------------------------------------
    ('''def is_card_play_room(room, building):''', '''#: THE VIDEO RENTAL STORE (0.171.0), on the card shop's terms: only inside a
#: building whose id says `video_store`. Its SELLING rooms are a video
#: store; its BACK ROOM -- the one behind the curtain -- is its own kind,
#: because what stands in it is its own. The stockroom keeps `storage`.
_VIDEO_STORE_ID = "video_store"
_VIDEO_STORE_TOKENS = frozenset(("sales", "showroom", "rental", "rentals", "video"))
_VIDEO_BACK_TOKENS = frozenset(("back", "adult", "adults", "curtain"))


def _video_store_building(building):
    return _VIDEO_STORE_ID in str(building or "").lower()


def video_store_room_kind(room, building):
    """``"video_store"`` for a video store's selling room, ``"video_back"``
    for its back room, None for any other room or any other building."""
    if not _video_store_building(building):
        return None
    tokens = set(str(room.get("id", "")).lower().replace("-", "_").split("_"))
    # `stock` first: a `back_stockroom` is a stockroom
    if tokens & {"stock", "stockroom", "storage", "office"}:
        return None
    if tokens & _VIDEO_BACK_TOKENS:
        return "video_back"
    if tokens & _VIDEO_STORE_TOKENS or {"main", "floor"} <= tokens:
        return "video_store"
    return None


def is_card_play_room(room, building):'''),
    ('''    if is_card_shop_room(room, building):
        return "card_shop"
    tokens = set(str(room.get("id", "")).lower().replace("-", "_").split("_"))
    for kind, words in _ROOM_KINDS:''', '''    if is_card_shop_room(room, building):
        return "card_shop"
    video = video_store_room_kind(room, building)       # 0.171.0
    if video:
        return video
    tokens = set(str(room.get("id", "")).lower().replace("-", "_").split("_"))
    for kind, words in _ROOM_KINDS:'''),
    # --- the recipes -----------------------------------------------------------
    ('''    "office": {"anchors": ("desk",),
               "wall": ("cabinet_file", "shelf_run", "cabinet_file"),''',
     '''    # THE VIDEO STORE (0.171.0). The walker: "a VHS movie rental store",
    # MACDADE MOVIES. Its racks, islands and checkout are AUTHORED by the
    # preset (`presets.video_store`); this is what the furnisher may add
    # round them: a vending machine if a wall is left, a carton or two, and
    # a run of sale posters where the racks are not. NO `wall_tv`: the
    # first draft listed it and the pass hung three by the checkout, one of
    # them on the shop glass. A store's one TV is the preset's to author.
    "video_store": {"anchors": (),
                    "wall": ("vending",),
                    "floor": (),
                    "clusters": ((("cartons",), 1, 2),),
                    "one_cluster": True,
                    "fixtures": ("poster_wall_store",)},
    # ITS BACK ROOM: the authored racks and nothing else. Suggestive only,
    # and that is Zoo's to hold (`video_rack_forms`, the `adult` form).
    "video_back": {"anchors": (), "wall": (), "floor": (), "clusters": ()},
    "office": {"anchors": ("desk",),
               "wall": ("cabinet_file", "shelf_run", "cabinet_file"),'''),
]

SPECIES = [
    ('''    # THE VIDEO-POKER CABINET (Zoo 1.39.0; placed 0.168.0). Above the
    # counter row, whose `bar_` would claim every `video_poker_bar_*`.''',
     '''    # THE VIDEO STORE'S TAPE RACKS (Zoo 1.43.0; placed 0.171.0). Above the
    # counter row, whose `island` would claim every `tape_island_*`.
    (("tape_wall", "tape_island"), "video_rack"),
    # THE VIDEO-POKER CABINET (Zoo 1.39.0; placed 0.168.0). Above the
    # counter row, whose `bar_` would claim every `video_poker_bar_*`.'''),
]

def main():
    s = (DC / "presets.py").read_text(encoding="utf-8")
    assert "def video_store(" not in s, "already applied"
    _edit("presets.py", PRESETS)
    _edit("level_design.py", LEVEL)
    _edit("prop_species.py", SPECIES)


if __name__ == "__main__":
    main()
