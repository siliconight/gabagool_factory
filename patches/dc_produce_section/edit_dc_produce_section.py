"""Edit a Deli Counter clone for 0.277.0: a supermarket stands a produce section (Zoo 1.132.0's `produce_table`). Run
from the clone's root. Asserts every anchor once; refuses on a miss."""
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
('''    _piece("gondola_run", ((9.6, 1.4, 1.45), (12.0, 1.4, 1.45),
                           (7.2, 1.4, 1.45)), "island", front=True,
           variants=True, most=12),''',
'''    _piece("gondola_run", ((9.6, 1.4, 1.45), (12.0, 1.4, 1.45),
                           (7.2, 1.4, 1.45)), "island", front=True,
           variants=True, most=12),
    # THE PRODUCE SECTION (0.277.0): Zoo 1.132.0's `produce_table`, a
    # green-skirted cabinet with a raked bed of produce heaps, a kind a bay --
    # the walker's comps' "retro produce section ... neatly arranged fruit and
    # vegetables" (the factory's docs/reference/GROCERY_STORE_COMPS.md). An
    # island a shopper walks round, front to the aisle; below cover height, so
    # it stands mid-floor under furnish's rule. Its variant is its stock (Zoo's
    # `PRODUCE`, the heap a table's first bay starts from), and FOUR, not
    # Zoo's eight: a piece past four draws its variant from the BUILDING's id
    # (`_make_volume`, the neon sign's rule), and the first build gave both
    # tables in every store the same heaps. At four it is the name's, and a
    # table's four bays still walk the kinds from where it starts.
    _piece("produce_table", ((2.4, 1.2, 0.95), (3.0, 1.2, 0.95),
                             (1.8, 1.0, 0.9)), "island", front=True,
           variants=True, most=3),'''),
('''    "supermarket": {"anchors": (),''', '''    "supermarket": {"anchors": ("produce_table", "produce_table"),
                    "all_anchors": True,'''),
('''    # one cluster of cartons -- a delivery being worked -- and an ATM. Its''',
'''    # one cluster of cartons -- a delivery being worked -- and an ATM; and
    # two produce tables first, its produce section, standing where furnish's
    # island rule finds them clear floor (0.277.0). Its'''),
('''    # (`migrations/migrate_supermarket_cooler.py`). NO AISLE SIGNS YET: a
    # fixture hangs where a hung slot is free, and the first build of this
    # recipe hung one over the checkout; a supermarket's sign hangs over its
    # aisle, which is a rule of its own.''',
'''    # (`migrations/migrate_supermarket_cooler.py`). ITS AISLE SIGNS ARE NOT A
    # FIXTURE: a fixture hangs where a hung slot is free, and the first build
    # of this recipe hung one over the checkout; a supermarket's sign hangs
    # over its aisle, `aisle_markers`'s rule (0.276.0).'''),
('''    (("gondola_run",), "metal_painted"),''', '''    (("gondola_run",), "metal_painted"),
    (("produce_table",), "wood"),'''),
])

edit("prop_species.py", [
('''    (("gondola_run",), "snack_gondola"),''', '''    (("gondola_run",), "snack_gondola"),
    # a supermarket's produce section (Deli Counter 0.277.0; Zoo 1.132.0)
    (("produce_table",), "produce_table"),'''),
])
