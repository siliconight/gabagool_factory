"""Edit a Zoo clone for 1.137.0: `poster_wall`'s `bank` family -- a bank lobby's printed offers and its rate board.
Run from the clone's root. Asserts every anchor once; refuses on a miss."""
import json
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


edit("zoo_keeper/core/poster_copy.py", [
('''Family keys are the locations the walker named: `club`, `bar`, `alley`,
`store`.''',
'''Family keys are the locations the walker named: `club`, `bar`, `alley`,
`store` -- and (1.137.0) `bank`, the walker's bank comps
(the factory's docs/reference/BANK_INTERIOR_COMPS.md): a lobby's printed
offers in frames, and the rate board.'''),
('''FAMILIES = ("club", "bar", "alley", "store")''',
'''FAMILIES = ("club", "bar", "alley", "store", "bank")'''),
('''COPY = {"club": CLUB, "bar": BAR, "alley": ALLEY, "store": STORE}''',
'''#: The bank's printed offers (1.137.0): the lobby's framed posters the comps
#: show beside the rate board -- the offer, its one big figure, and the fine
#: print that lets the air out of it. A Christmas Club is the Depression-era
#: holiday savings account banks still opened in the 1990s; a free toaster for
#: a new account is the decade's joke about banks that is also true. Every
#: headline word sets at scale 2 across the sheet (CHRISTMAS did not).
BANK = (
    ("XMAS CLUB", "SAVE ALL YEAR. SPEND IT IN A WEEK."),
    ("FREE CHECKING", "FREE-ISH. SEE A TELLER."),
    ("CD RATES", "LOCK IT UP. LIKE YOUR COUSIN."),
    ("HOME EQUITY", "YOUR ROWHOME. OUR PROBLEM."),
    ("AUTO LOANS", "FOR THE CAR IN THE YARD"),
    ("SAT HOURS", "9 TO NOON. NOT A MINUTE AFTER."),
    ("NEW ACCOUNT", "FREE TOASTER. WHILE THEY LAST."),
    ("ATM CARDS", "THE MACHINE IS NICER THAN US"),
    ("RATES TODAY", "ANNUAL PERCENTAGE YIELD. ASK US WHY."),
    ("PASSBOOK", "STILL GOT YOURS IN A DRAWER?"),
    ("LOW RATES", "LOW-ISH. ASK US."),
    ("NIGHT DROP", "AROUND BACK. WATCH YOUR STEP."),
)
#: The one big figure each offer shows; the rate board shows `RATE_BOARD`.
#: Rates of the autumn of 1997.
BANK_FIGURES = {"XMAS CLUB": "JOIN", "FREE CHECKING": "$0", "CD RATES": "5.65%", "HOME EQUITY": "7.9%",
                "AUTO LOANS": "8.5%", "SAT HOURS": "9-12", "NEW ACCOUNT": "FREE", "ATM CARDS": "24 HR",
                "PASSBOOK": "2.5%", "LOW RATES": "6.9%", "NIGHT DROP": "3 PM"}
#: The rate board's rows, product and APY, the lobby's changeable letters.
RATE_BOARD = (("PASSBOOK", "2.50%"), ("CD 6 MO", "5.15%"), ("CD 1 YR", "5.65%"), ("CD 5 YR", "6.25%"),
              ("IRA", "6.00%"))

COPY = {"club": CLUB, "bar": BAR, "alley": ALLEY, "store": STORE, "bank": BANK}'''),
('''    "CHEERLEADERS", "PENTHOUSE", "PLAYBOY", "HOOTERS", "BON JOVI",
    "SPRINGSTEEN", "HALL & OATES", "PHISH", "PEARL JAM", "NIRVANA",
)''',
'''    "CHEERLEADERS", "PENTHOUSE", "PLAYBOY", "HOOTERS", "BON JOVI",
    "SPRINGSTEEN", "HALL & OATES", "PHISH", "PEARL JAM", "NIRVANA",
    # the region's 1990s banks and ATM network (1.137.0; the bank reference's
    # "researched" section)
    "CORESTATES", "MERIDIAN", "PSFS", "MELLON", "PNC", "FIRST UNION",
    "COMMERCE BANK", "FIDELITY", "MAC MACHINE", "FDIC",
)'''),
('''    out = []
    for fam in FAMILIES:
        for head, small in COPY[fam]:
            out += [head, small]
    return out + list(PHONES) + list(DATES)''',
'''    out = []
    for fam in FAMILIES:
        for head, small in COPY[fam]:
            out += [head, small]
    out += list(BANK_FIGURES.values()) + [s for row in RATE_BOARD for s in row]
    return out + list(PHONES) + list(DATES)'''),
])

edit("zoo_keeper/core/poster_art.py", [
('''PAINTERS = {"club": club, "bar": bar, "alley": alley, "store": store}''',
'''#: A bank's printed colours (1.137.0): ``(accent, paper)``, one a wall -- the
#: bank's own, as every sheet of one lobby is printed by one bank.
BANK_PALETTES = (((22, 40, 108), (248, 246, 238)), ((122, 24, 38), (246, 240, 226)),
                 ((24, 84, 56), (246, 244, 232)), ((30, 70, 150), (250, 250, 246)))
#: The rate board: white changeable letters on a black felt board.
BOARD = (26, 26, 30)
BOARD_INK = (240, 240, 232)


def bank(w, h, row, key, stock=None):
    """A bank lobby's printed offer (1.137.0): the bank's band across the
    top, the offer, its one big figure on a panel, the fine print at the foot
    -- or, on the `RATES TODAY` row, the rate board: white letters on black
    felt, a product and its yield a line. The palette is the WALL's (``key``
    alone), so one lobby's sheets are one bank's. A LOUD sheet is printed on
    the bank's colour; a plain one on its paper. THE FLAW: the lower corner
    has curled off its tape, a fold of the paper's back showing."""
    roll = Roll(f"bank|{row}|{key}")
    accent, paper = BANK_PALETTES[Roll(f"bank|{key}").below(len(BANK_PALETTES))]
    head, small = PC.BANK[row % len(PC.BANK)]
    # the stock by `_pool`, as the bar's, the alley's and the store's: one sheet in four loud when the run does not say
    pool = _pool(stock, (True, False, False, False), (True,), (False,))
    loud = pool[roll.below(len(pool))]
    ground = accent if loud else paper
    if head == "RATES TODAY":
        # the board on the sheet's ground, the bank's band and title above it: black felt with white letters on
        # paper, a white letterboard with black ones on the bank's colour -- both were changeable-letter boards, and
        # a dark board on a dark colour stepped 18 of the 42.5 `poster_checks` asks (so did a sheet that WAS the felt)
        felt, letters = ((244, 244, 238), INK) if loud else (BOARD, BOARD_INK)
        c = Canvas(w, h, ground)
        c.rect(0, 0, w, int(h * 0.10), _mix(accent, (0, 0, 0), 0.45) if loud else accent)
        title = fit_text(c, head, (3, int(h * 0.12), w - 3, int(h * 0.34)), (252, 252, 246) if loud else accent)
        rows = PC.RATE_BOARD
        y0, y1 = int(h * 0.37), int(h * 0.79)
        c.rect(4, y0, w - 4, y1, felt)
        rh = (y1 - y0 - 4) / float(len(rows))
        # where each line set, product and rate: `fit_text` returns None for a line too wide for its column at its
        # smallest size and draws nothing, so a board can lose a rate silently (a MONEY MKT line, and then every
        # rate at the shipped 118 px, did)
        board = []
        for k, (prod, rate) in enumerate(rows):
            ya, yb = int(y0 + 2 + k * rh), int(y0 + 2 + (k + 1) * rh) - 1
            set_at = [fit_text(c, prod, (6, ya, int(w * 0.58), yb), letters, face=SMALL_FACE, cap=1)]
            set_at.append(fit_text(c, rate, (int(w * 0.60), ya, w - 6, yb), letters, face=SMALL_FACE, cap=1))
            board.append(set_at)
        focal = (4, y0, w - 4, y1)
        c.rect(2, int(h * 0.82), w - 2, h - 2, (252, 252, 246))
        small_at = fit_text(c, small, (4, int(h * 0.82) + 1, w - 4, h - 3), INK, face=SMALL_FACE, cap=1)
        return c, {"family": "bank", "headline": head, "small": small, "small_at": small_at,
                   "title": title, "focal": focal, "ground": ground, "board": board}
    ink = (252, 252, 246) if loud else accent
    c = Canvas(w, h, ground)
    # the bank's band: its colour on plain paper, a dark rule on its colour
    c.rect(0, 0, w, int(h * 0.10), _mix(accent, (0, 0, 0), 0.45) if loud else accent)
    title = fit_text(c, head, (3, int(h * 0.12), w - 3, int(h * 0.38)), ink,
                     outline=_mix(ink, (0, 0, 0), 0.5) if loud else None)
    # the figure on a panel against the ground, the sheet's focal mass: white on the bank's colour on plain paper,
    # dark on white on loud. A light panel on light paper stepped 37 of the 42.5 `poster_checks` asks.
    fy0, fy1 = int(h * 0.42), int(h * 0.74)
    panel, fig = ((252, 252, 246), INK) if loud else (_mix(accent, (0, 0, 0), 0.2), (252, 252, 246))
    c.rect(5, fy0, w - 5, fy1, panel)
    fit_text(c, PC.BANK_FIGURES[head], (8, fy0 + 3, w - 8, fy1 - 2), fig)
    focal = (5, fy0, w - 5, fy1)
    # the fine print on a white strip, both ends of the value range on every sheet
    c.rect(2, int(h * 0.80), w - 2, h - 2, (252, 252, 246))
    small_at = fit_text(c, small, (4, int(h * 0.80) + 1, w - 4, h - 3), INK, face=SMALL_FACE, cap=1)
    # THE FLAW: the lower right corner curled off its tape
    k = max(4, w // 9)
    for i in range(k):
        for j in range(k - i):
            c.px(w - 1 - j, h - 1 - i, _mix(ground, (255, 255, 255), 0.55) if j < k - i - 1 else (90, 90, 90))
    return c, {"family": "bank", "headline": head, "small": small, "small_at": small_at,
               "title": title, "focal": focal, "ground": ground}


PAINTERS = {"club": club, "bar": bar, "alley": alley, "store": store, "bank": bank}'''),
('''SIZES_M = {"club": (0.46, 0.64), "bar": (0.30, 0.44), "alley": (0.30, 0.42), "store": (0.46, 0.60)}''',
'''SIZES_M = {"club": (0.46, 0.64), "bar": (0.30, 0.44), "alley": (0.30, 0.42), "store": (0.46, 0.60),
           "bank": (0.46, 0.62)}'''),
])

edit("zoo_keeper/core/poster_wall_forms.py", [
('''LAYOUT = {"club": (0.22, 0.0), "store": (0.08, 0.0), "bar": (0.05, 3.0), "alley": (-0.06, 5.0)}''',
'''LAYOUT = {"club": (0.22, 0.0), "store": (0.08, 0.0), "bar": (0.05, 3.0), "alley": (-0.06, 5.0),
          # a bank's framed offers hang square and apart (1.137.0)
          "bank": (0.30, 0.0)}'''),
('''WANDER = {"club": 0.0, "store": 0.0, "bar": 0.06, "alley": 0.10}''',
'''WANDER = {"club": 0.0, "store": 0.0, "bar": 0.06, "alley": 0.10, "bank": 0.0}'''),
])

g = Path("zoo_keeper/genome/species/poster_wall.json")
d = json.loads(g.read_bytes())
assert d["params"]["form"] == ["club", "bar", "alley", "store"], d["params"]["form"]
d["params"]["form"] = ["club", "bar", "alley", "store", "bank"]
d["license"]["notes"] += (" 1.137.0: form 'bank' -- a bank lobby's printed offers (the walker's bank comps): the bank's "
                          "band, the offer, one big figure on a panel, the fine print; the RATES TODAY row a rate "
                          "board, black felt on plain paper and a white letterboard on loud; one palette a wall, "
                          "a bank's.")
# the genome is Zoo's indent of 2; at 1 every line of it moved
g.write_bytes((json.dumps(d, indent=2) + "\n").encode("utf-8"))
print(g, "edited")

edit("tests/test_poster_wall.py", [
('''HEAD_FACE = {"club": PA.CLUB_FACE, "bar": "m5x7", "alley": "bold", "store": "m5x7"}
SMALL_FACE = {"club": "small", "bar": "m5x7", "alley": "m5x7", "store": "small"}''',
'''HEAD_FACE = {"club": PA.CLUB_FACE, "bar": "m5x7", "alley": "bold", "store": "m5x7", "bank": "m5x7"}
SMALL_FACE = {"club": "small", "bar": "m5x7", "alley": "m5x7", "store": "small", "bank": "small"}'''),
('''    else:
        assert not (m.get("emissiveFactor") and max(m["emissiveFactor"]) > 0), m
''',
'''    else:
        assert not (m.get("emissiveFactor") and max(m["emissiveFactor"]) > 0), m


@pytest.mark.parametrize("stock", (None, "loud", "plain"))
def test_the_rate_board_sets_every_product_and_rate(stock):
    """1.137.0: the bank's rate board at the size it ships. `fit_text` sets
    nothing for a line too wide for its column, and the three tests above
    passed a board that had lost every rate."""
    w, h = _size("bank")
    row = [head for head, _ in PC.BANK].index("RATES TODAY")
    for key in KEYS:
        board = PA.paint("bank", w, h, row, key, stock)[1]["board"]
        assert len(board) == len(PC.RATE_BOARD), (key, board)
        assert all(at is not None for line in board for at in line), (key, stock, board)
'''),
])
