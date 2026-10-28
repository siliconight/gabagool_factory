"""Level Factory: a bank's band is dealt the name Zoo's teller line, time-and-temperature sign and canopy already give it.
Run in a Level Factory clone's root. Every anchor is asserted to occur exactly once; nothing is written on a miss.
"""
import pathlib

HERE = pathlib.Path(__file__).parent
R = pathlib.Path.cwd()


def edit(rel, pairs):
    p = R / rel
    t = p.read_bytes().decode("utf-8")
    crlf = "\r\n" in t
    t = t.replace("\r\n", "\n")
    for a, b in pairs:
        assert t.count(a) == 1, (rel, t.count(a), a[:80])
        t = t.replace(a, b)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print(p, "edited")


edit("apps/cli/commands/__init__.py", [
('''def deal_signs(ws, buildings, theme: str) -> dict[str, str]:''',
 '''#: A BANK'S NAME IS ZOO'S (0.262.0). Zoo 1.138.0 names a bank on four more
#: faces than its band -- the teller line's nameboard, the time-and-temperature
#: sign, the drive-up canopy's fascia, the door -- every one by
#: `storefront_names`' rule: these four names, the crc32 of the business, which
#: for a library shell is its archetype (Deli Counter's `bank_teller_variant`,
#: Lot's `bank_sign_variant`, Zoo's `teller_line_forms.variant_for`). The deal
#: keyed its own hash, so on the bank level (bank_block_001, seed 9082) the band
#: said MATTRESS MONEY TRUST over a line, a sign and a canopy saying YOUSE
#: CREDIT CO-OP. A bank's deal now starts at Zoo's name; the street's one-name
#: rule still moves a second bank on to the next. Pixelcoat's delco profile
#: lists the same four. `tests/unit/test_bank_deal.py` holds the list to Zoo.
ZOO_BANK_NAMES = ("FIRST DELCO SAVINGS", "PIKE SAVINGS & LOAN", "MATTRESS MONEY TRUST", "YOUSE CREDIT CO-OP")


def zoo_bank_name(key: str) -> str:
    """The name Zoo's `storefront_names.sign_for` gives a bank whose business is ``key``."""
    import zlib
    return ZOO_BANK_NAMES[(zlib.crc32(str(key or "").encode("utf-8")) & 0xFFFFFFFF) % len(ZOO_BANK_NAMES)]


def deal_signs(ws, buildings, theme: str) -> dict[str, str]:'''),
('''        start = h % len(pool)
        pick = None''',
 '''        start = h % len(pool)
        # a bank starts at the name Zoo's other faces give it
        if family == "bank":
            want = zoo_bank_name(key)
            start = next((i for i, s in enumerate(pool) if s.get("text") == want), start)
        pick = None'''),
])

dst = R / "tests" / "unit" / "test_bank_deal.py"
assert not dst.exists(), dst
dst.write_bytes((HERE / "test_bank_deal.py").read_bytes())
print(dst, "written")
