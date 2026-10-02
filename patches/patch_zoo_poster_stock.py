"""Zoo 1.41.0: most posters are on plain paper, and one or two a cluster are loud.

The walker, 2026-09-30, on cold run 9119's pole flyers and the poster work so
far: "if anything its just too much color". Their palette guide
(docs/reference/) says the same: "a few bright flyers ... stand out more if
neighboring posters use cream or newsprint". Until now every bar bill,
handbill and sale poster drew its paper from a table that was three-quarters
or more coloured stock, so a wrapped pole was a column of equally loud
sheets.

  * `poster_art`: a painter takes ``stock`` -- "loud" (the coloured papers it
    always had), "plain" (white, cream, newsprint) or None (either, as
    before: the door every caller but a run comes through). The club is
    untouched: the walker liked its colour and its blacklight.
  * `poster_wall_forms.loud_sheets`: which sheets of a run are loud -- one,
    two from six sheets, three from sixteen, spread along the run.
  * `pole_flyers_forms`: ONE bill a pole is loud, the one its newest front
    sheet carries; the rest is plain paper.
  * `card_art`: hands the tile's ``stock`` to the painter.

Every edit asserts its anchor once and refuses to write on a miss.
"""
from __future__ import annotations

import pathlib

ZOO = pathlib.Path(__file__).resolve().parents[1] / "zoo"


def _edit(rel, pairs):
    p = ZOO / rel
    raw = p.read_bytes()
    assert b"\r\n" not in raw, f"{rel}: CRLF in an LF file"
    s = raw.decode("utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, f"{rel}: anchor found {n} times: {old[:60]!r}"
        s = s.replace(old, new)
    p.write_bytes(s.encode("utf-8"))
    print("patched", rel)


ART = [
    ('''COPY_PAPER = ((236, 232, 220), (250, 214, 226), (252, 246, 176), (206, 228, 246))


def bar(w, h, row, key):
    roll = Roll(f"bar|{row}|{key}")
    paper = COPY_PAPER[roll.below(len(COPY_PAPER))]
''', '''COPY_PAPER = ((236, 232, 220), (250, 214, 226), (252, 246, 176), (206, 228, 246))

#: THE STOCK (1.41.0). The walker, 2026-09-30: "if anything its just too
#: much color"; the palette guide: "a few bright flyers ... stand out more if
#: neighboring posters use cream or newsprint". A painter asked for "plain"
#: prints on white, cream or newsprint; asked for "loud", on the coloured
#: papers it always had; asked for neither (None), on any, as before. Which
#: sheets of a cluster are loud is the cluster's to say
#: (`poster_wall_forms.loud_sheets`, `pole_flyers_forms.plan`).
STOCKS = ("loud", "plain")
PLAIN_PAPER = ((244, 244, 236), (232, 224, 200), (214, 205, 180))


def _pool(stock, both, loud, plain):
    if stock is None:
        return both
    if stock not in STOCKS:
        raise ValueError(f"no poster stock {stock!r}; the stocks are {', '.join(STOCKS)}")
    return loud if stock == "loud" else plain


def bar(w, h, row, key, stock=None):
    roll = Roll(f"bar|{row}|{key}")
    pool = _pool(stock, COPY_PAPER, COPY_PAPER[1:], PLAIN_PAPER)
    paper = pool[roll.below(len(pool))]
'''),
    ('''def alley(w, h, row, key):
    roll = Roll(f"alley|{row}|{key}")
    paper = DAYGLO[roll.below(len(DAYGLO))]
''', '''def alley(w, h, row, key, stock=None):
    roll = Roll(f"alley|{row}|{key}")
    pool = _pool(stock, DAYGLO, DAYGLO[:4], PLAIN_PAPER)
    paper = pool[roll.below(len(pool))]
'''),
    ('''SHOUT = ("SALE", "NOW", "HOT", "WOW")


def store(w, h, row, key):
    roll = Roll(f"store|{row}|{key}")
    paper, head_ink = STORE_PAPER[roll.below(len(STORE_PAPER))]
''', '''#: A plain sale poster: the deal in red on white, or in navy on cream.
STORE_PLAIN = (((250, 250, 244), (214, 22, 30)), ((238, 232, 210), (20, 24, 110)))
SHOUT = ("SALE", "NOW", "HOT", "WOW")


def store(w, h, row, key, stock=None):
    roll = Roll(f"store|{row}|{key}")
    pool = _pool(stock, STORE_PAPER, STORE_PAPER[:3], STORE_PLAIN)
    paper, head_ink = pool[roll.below(len(pool))]
'''),
    ('''def paint(family, w_px, h_px, row, key=""):
    if family not in PAINTERS:
        raise ValueError(f"no poster family {family!r}; the families are {', '.join(PC.FAMILIES)}")
    return PAINTERS[family](int(w_px), int(h_px), int(row), str(key))''',
     '''def paint(family, w_px, h_px, row, key="", stock=None):
    """``stock`` (1.41.0) is "loud", "plain" or None; the club has one stock
    and takes none."""
    if family not in PAINTERS:
        raise ValueError(f"no poster family {family!r}; the families are {', '.join(PC.FAMILIES)}")
    if family == "club" or stock is None:
        if stock is not None and stock not in STOCKS:
            raise ValueError(f"no poster stock {stock!r}; the stocks are {', '.join(STOCKS)}")
        return PAINTERS[family](int(w_px), int(h_px), int(row), str(key))
    return PAINTERS[family](int(w_px), int(h_px), int(row), str(key), stock)'''),
]

WALL = [
    ('''def band_height(family, rows=1):''', '''def loud_sheets(n, key, variant):
    """Which of a run's ``n`` sheets are on loud paper (1.41.0): one; two
    from six sheets; three from sixteen -- spread evenly along the run from
    a start the run's own name picks. The rest are plain."""
    count = 1 if n < 6 else (2 if n < 16 else 3)
    start = _h(key, variant, "loud") % max(1, n)
    return {(start + k * n // count) % n for k in range(count)} if n else set()


def band_height(family, rows=1):'''),
    ('''    rows = _order(family, key, variant, len(places))
    prims, tiles = [], {}
''', '''    rows = _order(family, key, variant, len(places))
    loud = loud_sheets(len(places), key, variant)
    prims, tiles = [], {}
'''),
    ('''                       "w_m": round(sw, 4), "h_m": round(sh, 4), "key": f"{key}|{variant}|{j}"}
''', '''                       "w_m": round(sw, 4), "h_m": round(sh, 4), "key": f"{key}|{variant}|{j}"}
        # the club's sheets are one stock: its colour and blacklight stay
        if family != "club":
            tiles[tile]["stock"] = "loud" if j in loud else "plain"
'''),
    ('''                      "sheet_m": (round(sw, 4), round(sh, 4)), "rows": rows, "tilts": tilts,
''', '''                      "sheet_m": (round(sw, 4), round(sh, 4)), "rows": rows, "tilts": tilts,
                      "loud": sorted(loud) if family != "club" else [],
'''),
]

POLE = [
    ('''                       "key": f"{key}|{variant}|{row}", "fade": FADE[layer]}
''', '''                       "key": f"{key}|{variant}|{row}", "fade": FADE[layer],
                       # ONE BILL A POLE IS LOUD (1.41.0): the one its newest
                       # front sheet carries (`rows[0]`); every other is plain
                       "stock": "loud" if row == rows[0] else "plain"}
'''),
]

CARD = [
    ('''        c = PA.paint(spec["family"], w, hgt, spec["row"], key)[0]
''', '''        c = PA.paint(spec["family"], w, hgt, spec["row"], key, spec.get("stock"))[0]
'''),
]

T_WALL = [
    ('''def test_a_club_title_sets_at_display_size():''', '''STOCKED = tuple(f for f in PC.FAMILIES if f != "club")


@pytest.mark.parametrize("family", STOCKED)
@pytest.mark.parametrize("stock", PA.STOCKS)
def test_every_stock_sets_both_lines_and_passes_the_three_tests(family, stock):
    """1.41.0: a sheet on plain paper is held to what a loud one is."""
    w, h = _size(family)
    for row in range(len(PC.COPY[family])):
        for key in KEYS:
            c, info = PA.paint(family, w, h, row, key, stock)
            tag = (family, stock, row, key, info["headline"])
            assert info["title"] is not None and info["small_at"] is not None, tag
            m = K.measure(c, info, CA.TEXEL)
            assert m["title_ratio"] is not None and m["title_ratio"] >= K.TITLE_RATIO, (tag, m)
            assert m["focal_step"] is not None and m["focal_step"] >= K.FOCAL_STEP, (tag, m)
            assert m["mass_spread"] >= K.MASS_SPREAD, (tag, m)


def _chroma(rgb):
    return max(rgb) - min(rgb)


@pytest.mark.parametrize("family", STOCKED)
def test_plain_paper_is_plain_and_loud_paper_is_not(family):
    """The walker: "if anything its just too much color". Plain is white,
    cream or newsprint -- its channels within 35 of each other; loud is a
    coloured stock. Asked for neither, a painter draws from both, as it did."""
    w, h = _size(family)
    seen = {None: set(), "loud": set(), "plain": set()}
    for stock in seen:
        for row in range(len(PC.COPY[family])):
            for key in KEYS:
                seen[stock].add(tuple(PA.paint(family, w, h, row, key, stock)[1]["ground"]))
    assert all(_chroma(p) <= 35 for p in seen["plain"]), seen["plain"]
    assert all(_chroma(p) > 35 for p in seen["loud"]), seen["loud"]
    assert seen["loud"] <= seen[None]
    with pytest.raises(ValueError):
        PA.paint(family, w, h, 0, "k", "neon")


@pytest.mark.parametrize("family", STOCKED)
@pytest.mark.parametrize("w", (1.0, 1.6, 2.4, 4.0, 8.0))
def test_a_run_is_mostly_plain_with_one_to_three_loud_sheets(family, w):
    for variant in range(4):
        g = F.plan(w, 0.01, F.band_height(family, 2), family, variant, "run")
        stocks = [g["tiles"][f"p{j}"]["stock"] for j in range(g["facts"]["sheets"])]
        n, loud = len(stocks), stocks.count("loud")
        assert loud == (1 if n < 6 else 2 if n < 16 else 3), (family, w, variant, n, loud)
        assert g["facts"]["loud"] == [j for j, s in enumerate(stocks) if s == "loud"]
        if n >= 3:
            assert loud * 2 < n, (family, w, n, loud)


def test_a_club_run_names_no_stock():
    g = F.plan(2.4, 0.01, F.band_height("club"), "club", 1, "run")
    assert all("stock" not in t for t in g["tiles"].values())
    assert g["facts"]["loud"] == []
    # and the club paints what it painted, whatever it is asked
    w, h = _size("club")
    a = PA.paint("club", w, h, 2, "k")[0]
    b = PA.paint("club", w, h, 2, "k", "plain")[0]
    assert bytes(a.buf) == bytes(b.buf)


def test_a_club_title_sets_at_display_size():'''),
]

T_POLE = [
    ('''def test_fading_takes_bright_ink_before_dark():''', '''@pytest.mark.parametrize("form", F.FORMS)
def test_one_bill_a_pole_is_loud(form):
    """1.41.0, the walker: "if anything its just too much color". Every
    sheet names its stock; the loud ones all carry ONE bill; and the newest
    layer shows it."""
    for variant in range(4):
        g = F.plan(0.3, 0.3, 1.6, form, variant, "pole")
        tiles = list(g["tiles"].values())
        assert all(t["stock"] in ("loud", "plain") for t in tiles)
        loud_rows = {t["row"] for t in tiles if t["stock"] == "loud"}
        assert len(loud_rows) == 1, (form, variant, loud_rows)
        assert any(t["stock"] == "loud" and not t["fade"] for t in tiles), (form, variant)
        assert sum(t["stock"] == "plain" for t in tiles) >= 2, (form, variant)


def test_fading_takes_bright_ink_before_dark():'''),
]


def main():
    s = (ZOO / "zoo_keeper/core/poster_art.py").read_text(encoding="utf-8")
    assert "STOCKS" not in s, "already applied"
    _edit("zoo_keeper/core/poster_art.py", ART)
    _edit("zoo_keeper/core/poster_wall_forms.py", WALL)
    _edit("zoo_keeper/core/pole_flyers_forms.py", POLE)
    _edit("zoo_keeper/core/card_art.py", CARD)
    _edit("tests/test_poster_wall.py", T_WALL)
    _edit("tests/test_pole_flyers.py", T_POLE)


if __name__ == "__main__":
    main()
