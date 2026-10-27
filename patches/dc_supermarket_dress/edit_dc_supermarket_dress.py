"""Edit a Deli Counter clone for 0.275.0: the supermarket is furnished as one (its own kind, rows in every one) and
stands a cooler wall. Run from the clone's root. Asserts every anchor once; refuses on a miss."""
from pathlib import Path

p = Path("level_design.py")
t = p.read_bytes().decode("utf-8")
assert "\r\n" not in t
n_lines = t.count("\n")


def sub(old, new):
    global t
    assert t.count(old) == 1, (old[:70], t.count(old))
    t = t.replace(old, new)


# 1. the recipe
sub('''    "garage": {"anchors": ("workbench",),
               "wall": ("shelf_run", "cabinet_tool"),''',
'''    # THE SUPERMARKET (0.275.0). The walker, 2026-10-26, in seed 9205's
    # supermarket: "far too dark in teh super market", and the comps after it
    # -- "shiny floor, bright lights, isles, glowing freezer section, stacked
    # high" (the factory's docs/reference/GROCERY_STORE_COMPS.md). Its sales
    # floor was the shop floor's recipe, which is a corner store without its
    # rows: supermarket_a01's stood a service counter, two filing cabinets,
    # two vending machines, two video poker machines with their stools and
    # eleven cartons and bins round five authored aisles, and supermarket_a02
    # no aisle at all. A supermarket is shelving: rows of aisle gondolas laid
    # to the floor's share (`_shop_rows`), shelving stacked along its walls,
    # one cluster of cartons -- a delivery being worked -- and an ATM. Its
    # cooler wall is placed before it is furnished
    # (`migrations/migrate_supermarket_cooler.py`). NO AISLE SIGNS YET: a
    # fixture hangs where a hung slot is free, and the first build of this
    # recipe hung one over the checkout; a supermarket's sign hangs over its
    # aisle, which is a rule of its own.
    "supermarket": {"anchors": (),
                    "wall": ("shelf_run",),
                    "floor": (),
                    "rows": (), "rows_share": 0.25,
                    "clusters": ((("cartons",), 1, 2),),
                    "one_cluster": True,
                    "fixtures": ("atm_store",)},
    "garage": {"anchors": ("workbench",),
               "wall": ("shelf_run", "cabinet_tool"),''')

# 2. the rule and the rows
sub('''def _shop_rows(room, building):
    """The shop floor's ROWS for one room, as `_card_shop_floor` is the card
    shop's floor run: aisle gondolas on a corner store's selling floor,
    nothing on any other."""
    return ("gondola_aisle",) if is_corner_store_floor(room, building) else ()''',
'''#: THE SUPERMARKET'S SELLING FLOOR (0.275.0), read on the corner store's
#: terms: a building whose id says it is a supermarket, and a room whose id
#: says it sells. Its stockroom, mezzanine, offices and cash room keep their
#: kinds -- supermarket_a02's `mezz_floor` says `floor` and is not a shop.
_SUPERMARKET_IDS = frozenset(("supermarket", "grocery", "grocer"))
_SUPERMARKET_FLOOR_TOKENS = frozenset(("sales", "floor", "market", "aisle",
                                       "aisles", "retail", "shop"))
_SUPERMARKET_NOT_FLOOR = frozenset(("stock", "stockroom", "storage", "office",
                                    "back", "receiving", "mezz", "manager",
                                    "cash", "count"))


def is_supermarket_floor(room, building):
    """Is `room` the selling floor of a supermarket? The one rule, as
    `is_corner_store_floor` is the corner store's."""
    import re
    ids = set(re.split(r"[^a-z0-9]+", str(building or "").lower()))
    if not ids & _SUPERMARKET_IDS:
        return False
    tokens = set(str(room.get("id", "")).lower().replace("-", "_").split("_"))
    if tokens & _SUPERMARKET_NOT_FLOOR:
        return False
    return bool(tokens & _SUPERMARKET_FLOOR_TOKENS)


def _shop_rows(room, building):
    """The shop floor's ROWS for one room, as `_card_shop_floor` is the card
    shop's floor run: aisle gondolas on a corner store's or a supermarket's
    selling floor (0.275.0), nothing on any other."""
    if is_corner_store_floor(room, building):
        return ("gondola_aisle",)
    if is_supermarket_floor(room, building):
        return ("gondola_run",)
    return ()


def authored_aisles(spec, room):
    """The gondolas standing on `room`'s floor that furnish did not lay -- a
    spec's own aisles (0.275.0). A supermarket floor that has them takes no
    rows: its aisles are the rows, and the first build of the supermarket's
    recipe laid 3.6 m islands down the 5.6 m lanes between supermarket_a01's
    five 14 m aisles, 2.1 m from each."""
    x0, y0, x1, y1 = room["bounds"]
    sh = _story_height(spec)
    floor = int(room.get("story", 0) or 0) * sh
    return [v for v in unfurnished(spec).get("volumes") or []
            if str(v.get("name", "")).startswith("gondola_")
            and x0 <= v.get("x", 1e9) <= x1 and y0 <= v.get("y", 1e9) <= y1
            and _on_storey(float(v.get("z", 0.0)), float(v.get("size_z", 0.0)), floor, sh)]''')

# 3. the kind
sub('''    if is_office_floor(room, building):                  # 0.248.0
        return "office"
    tokens = set(str(room.get("id", "")).lower().replace("-", "_").split("_"))
    for kind, words in _ROOM_KINDS:''',
'''    if is_office_floor(room, building):                  # 0.248.0
        return "office"
    if is_supermarket_floor(room, building):             # 0.275.0
        return "supermarket"
    tokens = set(str(room.get("id", "")).lower().replace("-", "_").split("_"))
    for kind, words in _ROOM_KINDS:''')

# 4. routes reserved where rows stand
sub('''    if _room_kind(room, building) == "shop_floor" and _shop_rows(room, building):
        return "all"''',
'''    if _room_kind(room, building) in ("shop_floor", "supermarket") and _shop_rows(room, building):
        return "all"''')

# 5. the recipe takes its rows
sub('''        elif kind == "shop_floor":
            recipe = dict(recipe, rows=_shop_rows(room, building))''',
'''        elif kind == "shop_floor":
            recipe = dict(recipe, rows=_shop_rows(room, building))
        elif kind == "supermarket":
            recipe = dict(recipe, rows=() if authored_aisles(spec, room)
                          else _shop_rows(room, building))''')

# 6. a one-cluster recipe lays its rows too
sub('''        items += [("host", wall[i % len(wall)]) for i in range(rest)] if wall else []
        return items''',
'''        items += [("host", wall[i % len(wall)]) for i in range(rest)] if wall else []
        # its rows after its wall run, as below (0.275.0: the supermarket is
        # the first one-cluster recipe with rows; the others have none)
        items += [("rows", key) for key in recipe.get("rows") or ()]
        return items''')

# 7. the supermarket's gondola run
sub('''    _piece("gondola_aisle", ((3.6, 0.9, 1.4), (4.8, 1.0, 1.45),
                             (2.4, 0.9, 1.4)), "island", front=True,
           variants=True, most=16),''',
'''    _piece("gondola_aisle", ((3.6, 0.9, 1.4), (4.8, 1.0, 1.45),
                             (2.4, 0.9, 1.4)), "island", front=True,
           variants=True, most=16),
    # THE SUPERMARKET'S GONDOLA RUN (0.275.0): the same species, laid in the
    # same rows (`_shop_rows`), in the lengths a supermarket's aisles are --
    # the library's authored ones are 12 and 14 m. The corner store's 2.4 to
    # 4.8 m islands across a 44 x 25 m floor are a maze of crossings, not
    # aisles. Its height is `gondola_aisle`'s, below shelter, for that
    # piece's reasons; `most` is a guard on rows that are never more than a
    # dozen long runs.
    _piece("gondola_run", ((9.6, 1.4, 1.45), (12.0, 1.4, 1.45),
                           (7.2, 1.4, 1.45)), "island", front=True,
           variants=True, most=12),''')
sub('''    (("gondola_aisle",), "metal_painted"),
)''', '''    (("gondola_aisle",), "metal_painted"),
    (("gondola_run",), "metal_painted"),
)''')

p.write_bytes(t.encode("utf-8"))
print("level_design.py: %d -> %d lines" % (n_lines, t.count("\n")))

q = Path("prop_species.py")
s = q.read_bytes().decode("utf-8")
assert "\r\n" not in s
old = """    (("gondola_aisle",), "snack_gondola"),
"""
assert s.count(old) == 1
s = s.replace(old, old + """    # the supermarket's long runs (Deli Counter 0.275.0, `level_design`'s
    # `gondola_run`): the same species, which builds 1.2 to 14.0 m
    (("gondola_run",), "snack_gondola"),
""")
q.write_bytes(s.encode("utf-8"))
print("prop_species.py: gondola_run routed")
