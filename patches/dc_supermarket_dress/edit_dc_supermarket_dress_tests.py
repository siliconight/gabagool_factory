"""Edit a Deli Counter clone's tests for 0.275.0 (after edit_dc_supermarket_dress.py): two tests that named a
supermarket's sales floor a shop floor. Run from the clone's root. Asserts every anchor once; refuses on a miss."""
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


edit("tests/test_card_shop.py", [
('''    """`sales_floor` is a shop floor everywhere else, and must stay one --
    the club's `main_floor` defect (0.131.0) one building along."""
    room = {"id": "sales_floor", "story": 0}
    assert level_design._room_kind(room, "supermarket_a01") == "shop_floor"
    assert level_design._room_kind(room, "lf_card_shop_001_7") == "card_shop"''',
'''    """`sales_floor` is a shop floor everywhere else, and must stay one --
    the club's `main_floor` defect (0.131.0) one building along. A
    supermarket's is its own kind since 0.275.0, and never the card shop's."""
    room = {"id": "sales_floor", "story": 0}
    assert level_design._room_kind(room, "pawn_shop_a01") == "shop_floor"
    assert level_design._room_kind(room, "supermarket_a01") == "supermarket"
    assert level_design._room_kind(room, "lf_card_shop_001_7") == "card_shop"'''),
])

edit("tests/test_store_atms.py", [
('''        sells = any(level_design._room_kind(r, building) == "shop_floor" and _tokens(r) & SELLING''',
'''        # a supermarket's selling floor is its own kind since 0.275.0, and sells
        sells = any(level_design._room_kind(r, building) in ("shop_floor", "supermarket")
                    and _tokens(r) & SELLING'''),
])
