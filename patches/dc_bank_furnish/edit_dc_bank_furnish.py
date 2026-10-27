"""Edit a Deli Counter clone for 0.281.0: a bank's lobby is furnished as the walker's comps -- a check desk mid-floor,
waiting chairs, an ATM, a queue; no vending, cigarettes or payphone -- and a vault keeps a cash cart. Run from the
clone's root. Asserts every anchor once; refuses on a miss."""
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


edit("level_design.py", [
# --- the pieces ------------------------------------------------------------------------------------
('''    _piece("produce_table", ((2.4, 1.2, 0.95), (3.0, 1.2, 0.95),
                             (1.8, 1.0, 0.9)), "island", front=True,
           variants=True, most=3),''',
'''    _piece("produce_table", ((2.4, 1.2, 0.95), (3.0, 1.2, 0.95),
                             (1.8, 1.0, 0.9)), "island", front=True,
           variants=True, most=3),
    # A BANK'S CHECK DESK (0.281.0, Zoo 1.135.0's `check_desk`; the factory's
    # roadmap 321): the comps' "check desk island ... mid-floor in front of
    # [the teller line]: a standing-height table with slots for slips", its
    # date block on its middle. An island a customer stands at from either
    # side, 1.1 m high -- below cover height, so a body sees over it; two in a
    # big hall at most.
    _piece("check_desk", ((1.6, 0.9, 1.1), (2.4, 1.0, 1.1)), "island", front=True, most=2),
    # A VAULT'S CASH CART (0.281.0, Zoo 1.135.0's `cash_cart`): the money
    # room's steel cage cart and its load, the comps' "carts and tubs". On the
    # floor, its load the variant, two a room at most.
    _piece("cash_cart", ((1.2, 0.7, 1.1), (0.9, 0.6, 1.0)), "floor", variants=True, most=2),'''),
# --- a bank's vault keeps a cart --------------------------------------------------------------------
('''    "vault": {"anchors": ("safe_floor",),''',
'''    # A BANK'S VAULT (0.281.0, `_room_kind`'s `bank_vault`): a vault's
    # furniture and the comps' cash cart beside the count table. A BANK'S
    # only: the first build put a cart in every `vault`-kind room and moved
    # 44 specs -- a deli's back safe, a stadium's, a funeral home's.
    "bank_vault": {"anchors": ("safe_floor",),
                   "wall": ("shelf_run", "cabinet_locker", "safe_floor"),
                   "floor": ("table_count", "cash_cart"),
                   "clusters": ((("cartons",), 2, 3),)},
    "vault": {"anchors": ("safe_floor",),'''),
('''        if story < 0 and kind not in ("basement", "vault", "corridor",
                                      "hallway", "wine_cellar"):''',
'''        if story < 0 and kind not in ("basement", "vault", "bank_vault", "corridor",
                                      "hallway", "wine_cellar"):'''),
# --- the bank's lobby -------------------------------------------------------------------------------
('''    "lobby": {"anchors": ("counter_service",),''',
'''    # A BANK'S LOBBY (0.281.0, the factory's roadmap 321; `is_bank_lobby`): the
    # walker's bank comps (docs/reference/BANK_INTERIOR_COMPS.md) -- the teller
    # line is the room, a check desk mid-floor before it, a queue of
    # stanchions, waiting chairs, an ATM. Not the general lobby's vending
    # machine, cigarettes, payphone or sofa: measured on bank_branch_a02
    # (docs/findings/bank_interior/), its 390 m2 lobby stood a bench, two
    # bins and a queue. The service counter stays its anchor where a spec
    # has one; the check desk is the room's second.
    "bank_lobby": {"anchors": ("check_desk",),
                   "wall": ("chair_waiting", "chair_waiting", "atm"),
                   "floor": (),
                   "clusters": ((("stanchion",), 3, 4), (("litter_bin",), 1, 1))},
    "lobby": {"anchors": ("counter_service",),'''),
('''    if is_supermarket_floor(room, building):             # 0.275.0
        return "supermarket"''',
'''    if is_supermarket_floor(room, building):             # 0.275.0
        return "supermarket"
    if is_bank_lobby(room, building):                    # 0.281.0
        return "bank_lobby"'''),
('''def _room_kind(room, building=None):''',
'''def is_bank_lobby(room, building):
    """Is `room` a bank's public room (`lights.bank_public`: its
    `public_entry`, a lobby or banking hall)? The one rule for its furniture
    (0.281.0), its light and its floor (0.280.0)."""
    import lights
    return lights.bank_public(room, building)


def _room_kind(room, building=None):
    """`_room_kind_of`, and a bank's `vault` is a `bank_vault` (0.281.0): the
    same furniture and the comps' cash cart, in a bank's vault only."""
    kind = _room_kind_of(room, building)
    if kind == "vault":
        import lights
        if lights.is_bank(building):
            return "bank_vault"
    return kind


def _room_kind_of(room, building=None):'''),
])

edit("prop_species.py", [
('''    (("milk_crate",), "milk_crate_stack"),
    (("crate", "col_", "pillar", "column", "stack", "pump_island",''',
'''    (("milk_crate",), "milk_crate_stack"),
    # A BANK'S CHECK DESK AND A VAULT'S CASH CART (0.281.0, Zoo 1.135.0). Ahead
    # of the box row, whose `cart` would build the cart as a grey box, and of
    # the `desk` rows below
    (("check_desk",), "check_desk"),
    (("cash_cart",), "cash_cart"),
    (("crate", "col_", "pillar", "column", "stack", "pump_island",'''),
])

edit("tests/test_furnish.py", [
('''    assert naming == {"card_shop", "supermarket"}, naming''',
'''    # 0.281.0: a bank's lobby, its check desk -- an island below cover height
    assert naming == {"card_shop", "supermarket", "bank_lobby"}, naming'''),
('''    "produce_table": ((1.2, 4.8), (0.8, 1.6), (0.8, 1.1)),''',
'''    "produce_table": ((1.2, 4.8), (0.8, 1.6), (0.8, 1.1)),
    "check_desk": ((1.0, 3.2), (0.6, 1.2), (1.0, 1.2)),
    "cash_cart": ((0.8, 1.6), (0.5, 0.9), (0.9, 1.4)),'''),
])


# --- the tests that pinned the old bank lobby: its cigarettes, its payphone, its sofa ---------------------------
edit("tests/test_club_fixtures.py", [
('''             ("bank_x", "lobby"): 1, ("museum_x", "exhibit_hall"): 0,''',
'''             # 0.281.0: a bank's lobby is the comps' (`bank_lobby`), and no bank
             # sells cigarettes; a hotel's lobby is the lobby that keeps one
             ("bank_x", "lobby"): 0, ("hotel_x", "lobby"): 1, ("museum_x", "exhibit_hall"): 0,'''),
('''    # which a dining hall's recipe furnished, and whose own recipes stand none
    assert counts == {"dartboard": 11, "cigarettes": 71}, counts''',
'''    # which a dining hall's recipe furnished, and whose own recipes stand none.
    # 71 -> 64 (0.281.0): the seven banks' lobbies, now `bank_lobby`'s, whose
    # recipe stands none
    assert counts == {"dartboard": 11, "cigarettes": 64}, counts'''),
])

edit("tests/test_payphone_wall_form.py", [
('''#: Where the piece stands payphones today: 39 in 38 specs (0.204.0).
PAYPHONES = 39''',
'''#: Where the piece stands payphones today: 39 in 38 specs (0.204.0); 32 since
#: 0.281.0, the seven banks' lobbies furnished as `bank_lobby`, which stands none.
PAYPHONES = 32'''),
])

edit("tests/test_ticket_queue.py", [
('''@pytest.mark.parametrize("name, kinds", [("bank_job", ("payphone", "atm", "sofa")),''',
'''# 0.281.0: bank_job's lobby is `bank_lobby`'s -- its ATM and its check desk, no
# payphone or sofa (the walker's bank comps)
@pytest.mark.parametrize("name, kinds", [("bank_job", ("atm", "check_desk")),'''),
])
