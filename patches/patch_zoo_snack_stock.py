"""Zoo 1.40.0: the snack gondola sells more than chips.

The walker's 90s snack references (2026-09-29, the store-dressing queue):
"fruit snacks, lunch kits, snack cakes on shelves, candy". And the walker's
own first named brand, docs/proposals/GAS_STATION_SHOP.md: "yummyjawns --
tastycake rip off", whose shelf is "flat rectangular cartons standing on
edge, four to six of each flavour side by side, each flavour a saturated
colour band ... From two metres it reads as stripes of colour".

  * `core/snack_brands.py`: `BOXED`, ten invented products of three kinds --
    five YUMMYJAWNS snack-cake cartons, three fruit snacks, two lunch kits --
    and the real makers of each on the denylists.
  * `core/snack_gondola_forms.py`: one long face stays the chip aisle,
    untouched; the other is SECTIONS, a bay each, cycling snack cakes, fruit
    snacks, lunch kits and bagged candy (`candy_brands`, the counter rack's
    own names). A carton is a box with its front on its tile. Every product
    is on the ONE image the bags were on, so the gondola is still two
    submissions.
  * `tests/test_snack_gondola.py`: a stock item names its own front faces
    (`front`), the sections, the boxed brands, and that every word sets.

Every edit asserts its anchor once and refuses to write on a miss.
"""
from __future__ import annotations

import pathlib

ZOO = pathlib.Path(__file__).resolve().parents[1] / "zoo"


def _load(rel):
    p = ZOO / rel
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    if crlf:
        assert raw.count(b"\r\n") == raw.count(b"\n"), f"{rel}: mixed line endings"
    return p, raw.replace(b"\r\n", b"\n").decode("utf-8"), crlf


def _save(p, s, crlf):
    b = s.encode("utf-8")
    p.write_bytes(b.replace(b"\n", b"\r\n") if crlf else b)
    print("patched", p.relative_to(ZOO))


def _once(rel, s, old, new):
    n = s.count(old)
    assert n == 1, f"{rel}: anchor found {n} times: {old[:60]!r}"
    return s.replace(old, new)


def _between(rel, s, start, end, new):
    """Replace from ``start`` up to (not including) ``end``."""
    assert s.count(start) == 1, f"{rel}: start anchor: {start[:60]!r}"
    a = s.index(start)
    assert s.count(end) == 1, f"{rel}: end anchor: {end[:60]!r}"
    b = s.index(end)
    assert a < b, rel
    return s[:a] + new + s[b:]


# --------------------------------------------------------------------------- #
# core/snack_brands.py
# --------------------------------------------------------------------------- #

BRANDS_OLD = '''BY_ID = {b["id"]: b for b in BRANDS}
IDS = tuple(b["id"] for b in BRANDS)
'''
BRANDS_NEW = '''#: THE BOXED STOCK (1.40.0): what a gondola sells that is not a chip bag. The
#: walker's 90s snack references, 2026-09-29: "fruit snacks, lunch kits,
#: snack cakes on shelves, candy" -- the candy is `candy_brands`, the counter
#: rack's own names in a bag.
#:   cake   YUMMYJAWNS, the walker's first named brand ("yummyjawns --
#:          tastycake rip off", docs/proposals/GAS_STATION_SHOP.md): one
#:          wordmark, five flavours, each a saturated colour band -- "from
#:          two metres it reads as stripes of colour". The carton says YUMMY.
#:   fruit  fruit snacks, an upright box.
#:   kit    lunch kits, the cracker-meat-cheese tray.
#: The same keys as a bag, so `words` and the denylists read them alike.
CAKE_MARK = "YUMMY"
BOXED = (
    {"id": "yummy_butter", "kind": "cake", "logo": ("YUMMYJAWNS", "BUTTER JAWNS"),
     "flavour": "Butterscotch. Sticks to the Wrapper.",
     "short": "BUTTER", "body": "#2a5cc8", "second": "#9ab8f0", "ink": "#ffffff"},
    {"id": "yummy_logs", "kind": "cake", "logo": ("YUMMYJAWNS", "CHOCOLATE LOGS"),
     "flavour": "Rolled Tight. Don't Ask.",
     "short": "LOGS", "body": "#6a3aa8", "second": "#c0a0e8", "ink": "#ffffff"},
    {"id": "yummy_pies", "kind": "cake", "logo": ("YUMMYJAWNS", "CHERRY PIES"),
     "flavour": "Fruit Filling. Lava Hot.",
     "short": "PIES", "body": "#e85a9a", "second": "#ffd0e4", "ink": "#ffffff"},
    {"id": "yummy_pucks", "kind": "cake", "logo": ("YUMMYJAWNS", "PEANUT BUTTER PUCKS"),
     "flavour": "Three to a Pack. Fight for the Third.",
     "short": "PUCKS", "body": "#1a9a98", "second": "#a0e8e0", "ink": "#ffffff"},
    {"id": "yummy_lemon", "kind": "cake", "logo": ("YUMMYJAWNS", "LEMON SQUARES"),
     "flavour": "Tart. Like Your Aunt.",
     "short": "LEMON", "body": "#f0c820", "second": "#fff4a0", "ink": "#4a3000"},
    {"id": "gummy_geese", "kind": "fruit", "logo": ("GUMMY", "GEESE"),
     "flavour": "Fruit Flavoured. Goose Shaped.",
     "short": "GEESE", "body": "#5a2aa0", "second": "#f0e040", "ink": "#ffffff"},
    {"id": "fruit_tape", "kind": "fruit", "logo": ("FRUIT", "TAPE"),
     "flavour": "Three Feet of Something Red.",
     "short": "TAPE", "body": "#d82a3a", "second": "#f8e060", "ink": "#ffffff"},
    {"id": "juice_bombs", "kind": "fruit", "logo": ("JUICE", "BOMBS"),
     "flavour": "Explodes. Stains.",
     "short": "BOMBS", "body": "#1aa0d0", "second": "#f04a90", "ink": "#ffffff"},
    {"id": "hoagie_kit", "kind": "kit", "logo": ("HOAGIE", "KIT"),
     "flavour": "Some Assembly Required.",
     "short": "KIT", "body": "#f0c818", "second": "#c8202a", "ink": "#ffffff"},
    {"id": "pizza_kit", "kind": "kit", "logo": ("PIZZA", "KIT"),
     "flavour": "Cold. On Purpose.",
     "short": "PIZZA", "body": "#e8a018", "second": "#1e8a4a", "ink": "#ffffff"},
)
BOXED_KINDS = ("cake", "fruit", "kit")
BOXED_IDS = {k: tuple(b["id"] for b in BOXED if b["kind"] == k) for k in BOXED_KINDS}

BY_ID = {b["id"]: b for b in BRANDS + BOXED}
IDS = tuple(b["id"] for b in BRANDS)
'''

DENY_OLD = '''              "KETTLE", "ZAPPS", "TGI", "WAWA", "EAGLES", "FLYERS", "PHILLIES", "SIXERS")'''
DENY_NEW = '''              "KETTLE", "ZAPPS", "TGI", "WAWA", "EAGLES", "FLYERS", "PHILLIES", "SIXERS",
              # 1.40.0, the boxed stock: the snack-cake makers (Philadelphia's
              # own first), the lunch kit's, the fruit snacks'
              "KRIMPET", "KRIMPETS", "KANDY", "KAKE", "KAKES", "JUNIORS", "TWINKIE", "TWINKIES",
              "DEBBIE", "DRAKE", "DRAKES", "YODELS", "ZINGERS", "SNOBALLS", "HOHOS",
              "LUNCHABLES", "OSCAR", "MAYER", "GUSHERS", "WELCH", "WELCHS", "WELCH'S",
              "SUNKIST", "BETTY", "CROCKER", "FARLEY", "FARLEYS")'''

PARTS_OLD = '''              "UTZ ", "HERR'")'''
PARTS_NEW = '''              "UTZ ", "HERR'",
              "KANDY KAKE", "LITTLE DEBBIE", "DING DONG", "HO HO", "SNO BALL", "DEVIL DOG",
              "RING DING", "SWISS ROLL", "FRUIT BY THE", "ROLL-UP", "ROLLUP", "ROLL UP",
              "SHARK BITE", "HANDI-SNACK", "HANDI SNACK")'''

# --------------------------------------------------------------------------- #
# core/snack_gondola_forms.py
# --------------------------------------------------------------------------- #

DOC_OLD = '''TWO SUBMISSIONS WHATEVER THE LENGTH: the steel'''
DOC_NEW = '''MORE THAN CHIPS (1.40.0). The walker's 90s snack references: "fruit snacks,
lunch kits, snack cakes on shelves, candy". The -Y face stays the chip aisle;
the +Y face is SECTIONS, a bay each: YUMMYJAWNS snack cakes (flat cartons, one
flavour a shelf -- stripes of colour), fruit snacks, lunch kits (upright
boxes) and bagged candy. A carton is a 12-triangle box with its front on its
tile; every product is on the bags' one image. A lunch kit belongs in a
cooler and stands here anyway: the cooler's doors are a different species
and the walker asked to see them on the shelves.

TWO SUBMISSIONS WHATEVER THE LENGTH: the steel'''

IMPORT_OLD = '''from . import pixel_type as pt
from . import prims as P
from . import snack_brands as SB
'''
IMPORT_NEW = '''from . import candy_brands as CB
from . import pixel_type as pt
from . import prims as P
from . import snack_brands as SB
'''

CONST_OLD = '''BAG_CROWN = 0.03          # the puff of a bag's front
'''
CONST_NEW = '''BAG_CROWN = 0.03          # the puff of a bag's front

#: WHAT A BAY OF THE SECTIONED FACE SELLS (1.40.0), cycled along the run.
SECTIONS = ("cake", "fruit", "kit", "candy")
#: kind: (width, height, depth, gap, facings a product, form). Zero facings
#: is one product the whole shelf: a YUMMYJAWNS flavour is a stripe.
STOCK = {
    "chips": (BAG_W, 0.30, BAG_D, BAG_GAP, 2, "bag"),
    "cake": (0.20, 0.16, 0.06, 0.012, 0, "box"),
    "fruit": (0.135, 0.18, 0.05, 0.012, 3, "box"),
    "kit": (0.135, 0.18, 0.04, 0.012, 3, "box"),
    "candy": (0.125, 0.17, 0.05, 0.016, 2, "bag"),
}
CANDY_CROWN = 0.02
'''

BAG_START = '''def bag(x, y_front, z0, bw, bh, brand):'''
BAG_END = '''def layout(w, d, h, key="snack_gondola", variant=0):'''
BAG_NEW = '''def bag(x, y_front, z0, bw, bh, brand, depth=BAG_D, crown=BAG_CROWN):
    """One bag, its puffed front toward -Y at ``y_front``, standing on
    ``z0`` (buried `BURY`), centred on ``x``. A `prims.pillow` built on its
    back and turned up: its crowned top becomes the front. ``uvs`` put the
    four front quads on the brand's tile and every other face on the
    brand's colour block; ``front`` names those four faces."""
    # the pillow in a local frame: x across, y is the bag's height, z its depth
    p = P.pillow("Snack_Bag", "bag", (-bw / 2.0, 0.0, 0.0), (bw / 2.0, bh, depth), crown)
    # turn +Z (the crown) to -Y and +Y (the bag's height) to +Z
    p = P.rotate_x(p, math.pi / 2.0, about=(0.0, 0.0))
    p = P.translate(p, (x, y_front + depth + crown, z0 - BURY))
    # faces 1-4 are the crowned top -- the front now
    xs = [v[0] for v in p["verts"]]
    zs = [v[2] for v in p["verts"]]
    x0, x1, zb, zt = min(xs), max(xs), min(zs), max(zs)
    uvs = []
    for k, f in enumerate(p["faces"]):
        if 1 <= k <= 4:
            uvs.append(tuple(("tile_" + brand, (p["verts"][i][0] - x0) / (x1 - x0),
                              (p["verts"][i][2] - zb) / (zt - zb)) for i in f))
        else:
            uvs.append(tuple(("solid_" + brand,) for _ in f))
    p["uvs"] = uvs
    p["front"] = (1, 2, 3, 4)
    return p


def carton(x, y_front, z0, bw, bh, bd, brand):
    """One carton (1.40.0): a box standing on ``z0`` (buried `BURY`), its
    front toward -Y at ``y_front``, centred on ``x``. `prims.box`'s face 2
    is its -Y face, corners (0, 1, 5, 4): the tile's bottom-left, bottom-
    right, top-right, top-left. Every other face is the brand's colour."""
    p = P.box("Snack_Bag", "bag", (x - bw / 2.0, y_front, z0 - BURY),
              (x + bw / 2.0, y_front + bd, z0 - BURY + bh))
    t = "tile_" + brand
    uvs = []
    for k, f in enumerate(p["faces"]):
        if k == 2:
            uvs.append(((t, 0.0, 0.0), (t, 1.0, 0.0), (t, 1.0, 1.0), (t, 0.0, 1.0)))
        else:
            uvs.append(tuple(("solid_" + brand,) for _ in f))
    p["uvs"] = uvs
    p["front"] = (2,)
    return p


def section(key, variant, face, bi):
    """What bay ``bi`` of ``face`` sells: face "a" is the chip aisle, face
    "b" cycles `SECTIONS` from a start the gondola's own name picks."""
    if face == "a":
        return "chips"
    return SECTIONS[(_h(key, variant, "section") + bi) % len(SECTIONS)]


def product(kind, key, variant, face, bi, k, i):
    """The product at facing ``i`` of shelf ``k``. Chips keep 1.13.0's
    formula exactly, so the chip aisle is the one that shipped."""
    if kind == "chips":
        return SB.IDS[(_h(key, variant, face, bi, k) + i // 2) % len(SB.IDS)]
    if kind == "candy":
        return CB.IDS[(_h(key, variant, face, bi, k) + i // 2) % len(CB.IDS)]
    ids = SB.BOXED_IDS[kind]
    facings = STOCK[kind][4]
    return ids[(_h(key, variant, face, bi) + k + (i // facings if facings else 0)) % len(ids)]


def _side(xs0, xs1, bays_, h, d, key, variant, face):
    """One shelved face of the run (the -Y one), over x ``xs0..xs1``."""
    out, n_bags, stock = [], 0, {}
    levels, pitch = shelf_levels(h)
    y_front = -d / 2.0 + 0.02                         # the shelves' front edge
    y_back = -SPINE_T / 2.0 + BURY                    # buried into the spine
    for bi, (bx, bw) in enumerate(bays_):
        sx0, sx1 = bx - bw / 2.0 + UPRIGHT_W / 2.0 + 0.004, bx + bw / 2.0 - UPRIGHT_W / 2.0 - 0.004
        kind = section(key, variant, face, bi)
        iw, ih, idp, gap, _facings, form = STOCK[kind]
        bh = min(ih, pitch - SHELF_T - 0.06)
        for k, z in enumerate(levels):
            if k:        # the deck is the kick's top
                out.append(P.box("Snack_Shelf", "steel", (sx0, y_front, z - SHELF_T), (sx1, y_back, z)))
            out.append(P.box("Snack_Strip", "strip", (sx0 + 0.003, y_front - STRIP_T, z - STRIP_H + 0.004),
                             (sx1 - 0.003, y_front + BURY, z + 0.006)))
            n = max(1, int((sx1 - sx0 - 0.02) // (iw + gap)))
            span = n * iw + (n - 1) * gap
            bx0 = (sx0 + sx1) / 2.0 - span / 2.0 + iw / 2.0
            for i in range(n):
                brand = product(kind, key, variant, face, bi, k, i)
                x = bx0 + i * (iw + gap)
                if form == "box":
                    out.append(carton(x, y_front + 0.014, z, iw, bh, idp, brand))
                elif kind == "candy":
                    out.append(bag(x, y_front + 0.014, z, iw, bh, brand, idp, CANDY_CROWN))
                else:
                    # a pair of facings a brand, as a real shelf is stocked
                    out.append(bag(x, y_front + 0.014, z, iw, bh, brand))
                n_bags += 1
                stock[kind] = stock.get(kind, 0) + 1
    return out, n_bags, stock


'''

SIDES_OLD = '''    side, n_bags = _side(xa, xb, bays_, h, d, key, variant, "a")
    other, n_b = _side(xa, xb, bays_, h, d, key, variant, "b")
    out += side + [P.rotate_z(p, math.pi, about=(0.0, 0.0)) for p in other]
    n_bags += n_b
'''
SIDES_NEW = '''    side, n_bags, stock = _side(xa, xb, bays_, h, d, key, variant, "a")
    other, n_b, stock_b = _side(xa, xb, bays_, h, d, key, variant, "b")
    out += side + [P.rotate_z(p, math.pi, about=(0.0, 0.0)) for p in other]
    n_bags += n_b
    for kind, n in stock_b.items():
        stock[kind] = stock.get(kind, 0) + n
'''

CAPBAG_OLD = '''                    cap.append(P.translate(b, (ex + 0.02 + 0.014, by, 0.0)))
                    n_bags += 1
'''
CAPBAG_NEW = '''                    cap.append(P.translate(b, (ex + 0.02 + 0.014, by, 0.0)))
                    n_bags += 1
                    stock["chips"] = stock.get("chips", 0) + 1
'''

FACTS_OLD = '''             "shelves": len(shelf_levels(h)[0]), "run": L,
'''
FACTS_NEW = '''             "shelves": len(shelf_levels(h)[0]), "run": L, "stock": stock,
'''

ART_START = '''TILE = (40, 60)          # a bag's front, pixels'''
ART_NEW = '''TILE = (40, 60)          # a bag's front, pixels
COLS = 6
CARTON_TILE = (48, 38)   # a YUMMYJAWNS carton's front: 0.20 x 0.16 m
SMALL_TILE = (36, 48)    # a fruit-snack box, a lunch kit, a candy bag
SMALL_COLS = 6
CREAM = (250, 244, 228)
MARK_RED = (200, 30, 40)


def _set(c, text, x0, y, tw, ink, plate=None):
    """``text`` in m5x7, centred on a tile ``tw`` wide whose left edge is
    ``x0``, its top at ``y``. A word wider than the tile is a defect, not a
    crop: it raises."""
    m = pt.trim(pt.render(text, 1, "m5x7"))
    assert len(m[0]) <= tw - 2, (text, len(m[0]), tw)
    mx = x0 + (tw - len(m[0])) // 2
    if plate is not None:
        c.rect(mx - 2, y - 1, mx + len(m[0]) + 2, y + len(m) + 1, plate)
    c.mask(m, mx, y, ink)


def _dark(rgb, by=60):
    return tuple(max(0, v - by) for v in rgb)


def _paint_bag(c, x0, y0, b):
    tw, th = TILE
    body, second, ink = SB.hex_rgb(b["body"]), SB.hex_rgb(b["second"]), SB.hex_rgb(b["ink"])
    c.rect(x0, y0, x0 + tw, y0 + th, body)
    if b["design"] == "band":
        c.rect(x0, y0 + th * 40 // 100, x0 + tw, y0 + th * 62 // 100, second)
    elif b["design"] == "window":
        c.rect(x0 + 8, y0 + th * 55 // 100, x0 + tw - 8, y0 + th * 85 // 100, second)
        # the chips through the window
        for k in range(5):
            c.rect(x0 + 11 + k * 4, y0 + th * 62 // 100 + (k % 2) * 4, x0 + 14 + k * 4,
                   y0 + th * 62 // 100 + (k % 2) * 4 + 3, (230, 190, 90))
    elif b["design"] == "stripe":
        for k in range(3):
            c.rect(x0, y0 + th * (25 + k * 22) // 100, x0 + tw, y0 + th * (25 + k * 22) // 100 + 3, second)
    else:
        c.rect(x0, y0 + th // 2, x0 + tw, y0 + th, second)
    # the crimped seals, top and bottom
    c.rect(x0, y0, x0 + tw, y0 + 3, tuple(min(255, v + 40) for v in body))
    c.rect(x0, y0 + th - 3, x0 + tw, y0 + th, tuple(max(0, v - 40) for v in body))
    _set(c, b["short"], x0, y0 + th * 18 // 100, tw, ink, _dark(body))
    return [b["short"]]


def _paint_cake(c, x0, y0, b):
    """A YUMMYJAWNS carton: the wordmark on a cream band, the flavour's
    colour under it -- the shelf's stripe -- and the flavour's name."""
    tw, th = CARTON_TILE
    body, second, ink = SB.hex_rgb(b["body"]), SB.hex_rgb(b["second"]), SB.hex_rgb(b["ink"])
    c.rect(x0, y0, x0 + tw, y0 + th, body)
    c.rect(x0, y0, x0 + tw, y0 + 13, CREAM)
    _set(c, SB.CAKE_MARK, x0, y0 + 3, tw, MARK_RED)
    c.rect(x0, y0 + 13, x0 + tw, y0 + 15, second)
    _set(c, b["short"], x0, y0 + 20, tw, ink)
    c.rect(x0 + 4, y0 + 31, x0 + tw - 4, y0 + 33, second)
    c.rect(x0, y0 + th - 1, x0 + tw, y0 + th, _dark(body, 40))
    return [SB.CAKE_MARK, b["short"]]


def _paint_fruit(c, x0, y0, b):
    """A fruit-snack box: the name, and the pieces loose down its front."""
    tw, th = SMALL_TILE
    body, second, ink = SB.hex_rgb(b["body"]), SB.hex_rgb(b["second"]), SB.hex_rgb(b["ink"])
    c.rect(x0, y0, x0 + tw, y0 + th, body)
    c.rect(x0, y0, x0 + tw, y0 + 2, second)
    _set(c, b["short"], x0, y0 + 6, tw, ink, _dark(body))
    pieces = (second, (240, 80, 60), (90, 200, 90), (250, 150, 40))
    for k in range(9):
        px, py = x0 + 5 + (k % 3) * 10 + (k // 3 % 2) * 2, y0 + 20 + (k // 3) * 8
        c.rect(px, py, px + 5, py + 4, pieces[k % len(pieces)])
    c.rect(x0, y0 + th - 3, x0 + tw, y0 + th, _dark(body, 40))
    return [b["short"]]


def _paint_kit(c, x0, y0, b):
    """A lunch kit: the name on its band, and the tray through the window --
    crackers, meat, cheese."""
    tw, th = SMALL_TILE
    body, second, ink = SB.hex_rgb(b["body"]), SB.hex_rgb(b["second"]), SB.hex_rgb(b["ink"])
    c.rect(x0, y0, x0 + tw, y0 + th, body)
    c.rect(x0, y0 + 3, x0 + tw, y0 + 15, second)
    _set(c, b["short"], x0, y0 + 6, tw, ink)
    c.rect(x0 + 3, y0 + 19, x0 + tw - 3, y0 + th - 4, (60, 40, 30))
    c.rect(x0 + 5, y0 + 21, x0 + 15, y0 + th - 6, (222, 184, 116))       # crackers
    c.rect(x0 + 17, y0 + 21, x0 + tw - 5, y0 + 29, (212, 112, 112))      # meat
    c.rect(x0 + 17, y0 + 31, x0 + tw - 5, y0 + th - 6, (242, 172, 44))   # cheese
    return [b["short"]]


def _paint_candy(c, x0, y0, b):
    """A bag of the counter rack's candy: the wrapper's own colours and
    design (`candy_brands`), crimped top and bottom."""
    tw, th = SMALL_TILE
    body, second, ink = CB.hex_rgb(b["body"]), CB.hex_rgb(b["second"]), CB.hex_rgb(b["ink"])
    c.rect(x0, y0, x0 + tw, y0 + th, body)
    if b["design"] == "band":
        c.rect(x0, y0 + 24, x0 + tw, y0 + 36, second)
    elif b["design"] == "stripe":
        for k in range(3):
            c.rect(x0, y0 + 22 + k * 8, x0 + tw, y0 + 24 + k * 8, second)
    elif b["design"] == "split":
        c.rect(x0, y0 + th // 2, x0 + tw, y0 + th, second)
    else:                                   # diag: a stepped band, corner to corner
        for k in range(9):
            c.rect(x0 + k * 4, y0 + 40 - k * 2, x0 + k * 4 + 4, y0 + 46 - k * 2, second)
    c.rect(x0, y0, x0 + tw, y0 + 3, tuple(min(255, v + 40) for v in body))
    c.rect(x0, y0 + th - 3, x0 + tw, y0 + th, _dark(body, 40))
    _set(c, b["short"], x0, y0 + 8, tw, ink, _dark(body))
    return [b["short"]]


def bag_art():
    """ONE image for every product on the gondola: a front tile each
    (`tile_<id>`) and a solid block of its body colour (`solid_<id>`) for
    its sides and back. The chip bags' tiles are where 1.13.0 put them; the
    cartons, the small boxes and the candy bags are the rows under them.
    ``{canvas, size, rects, said, name}``; rects are pixel boxes, row 0 at
    the top."""
    tw, th = TILE
    rows = int(math.ceil(len(SB.BRANDS) / float(COLS)))
    cakes = [b for b in SB.BOXED if b["kind"] == "cake"]
    small = [(b, _paint_fruit if b["kind"] == "fruit" else _paint_kit)
             for b in SB.BOXED if b["kind"] != "cake"] + [(b, _paint_candy) for b in CB.BRANDS]
    small_rows = int(math.ceil(len(small) / float(SMALL_COLS)))
    y_cake = rows * th
    y_small = y_cake + CARTON_TILE[1]
    y_solid = y_small + small_rows * SMALL_TILE[1]
    W, H = COLS * tw, y_solid + 8
    assert len(cakes) * CARTON_TILE[0] <= W and SMALL_COLS * SMALL_TILE[0] <= W
    c = Canvas(W, H, (20, 20, 20))
    rects, said, solids = {}, [], []

    def put(b, x0, y0, size, said_):
        assert "tile_" + b["id"] not in rects, b["id"]
        rects["tile_" + b["id"]] = (x0, y0, x0 + size[0], y0 + size[1])
        said.extend(said_)
        solids.append(b)

    for i, b in enumerate(SB.BRANDS):
        x0, y0 = (i % COLS) * tw, (i // COLS) * th
        put(b, x0, y0, TILE, _paint_bag(c, x0, y0, b))
    for i, b in enumerate(cakes):
        x0 = i * CARTON_TILE[0]
        put(b, x0, y_cake, CARTON_TILE, _paint_cake(c, x0, y_cake, b))
    for i, (b, paint) in enumerate(small):
        x0, y0 = (i % SMALL_COLS) * SMALL_TILE[0], y_small + (i // SMALL_COLS) * SMALL_TILE[1]
        put(b, x0, y0, SMALL_TILE, paint(c, x0, y0, b))
    assert len(solids) * 5 <= W, len(solids)
    for i, b in enumerate(solids):
        sx = i * 5
        c.rect(sx, y_solid + 2, sx + 4, y_solid + 6, SB.hex_rgb(b["body"]))
        rects["solid_" + b["id"]] = (sx, y_solid + 2, sx + 4, y_solid + 6)
    digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
    return {"canvas": c, "size": (W, H), "rects": rects, "said": said,
            "name": f"snackbags_{W}x{H}_{digest:08x}"}
'''

# --------------------------------------------------------------------------- #
# tests/test_snack_gondola.py
# --------------------------------------------------------------------------- #

T_IMPORT_OLD = '''from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import prims as P
'''
T_IMPORT_NEW = '''from zoo_keeper.core import candy_brands as CB
from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import prims as P
'''

T_FACE_OLD = '''        a, b, c = (p["verts"][i] for i in p["faces"][1][:3])'''
T_FACE_NEW = '''        a, b, c = (p["verts"][i] for i in p["faces"][p["front"][0]][:3])'''

T_MAP_OLD = '''        fronts = [c for f in p["uvs"][1:5] for c in f]
        assert all(c[0].startswith("tile_") and c[0] in art["rects"] for c in fronts)
        others = [c for k, f in enumerate(p["uvs"]) if not 1 <= k <= 4 for c in f]
        assert all(c[0].startswith("solid_") and c[0] in art["rects"] for c in others)
'''
T_MAP_NEW = '''        # 1.40.0: a stock item names its own front faces -- a bag's four
        # crowned quads, a carton's one
        fronts = [c for k in p["front"] for c in p["uvs"][k]]
        assert all(c[0].startswith("tile_") and c[0] in art["rects"] for c in fronts)
        assert all(0.0 <= c[1] <= 1.0 and 0.0 <= c[2] <= 1.0 for c in fronts)
        others = [c for k, f in enumerate(p["uvs"]) if k not in p["front"] for c in f]
        assert all(c[0].startswith("solid_") and c[0] in art["rects"] for c in others)
'''

T_SAID_OLD = '''    assert a["said"] == [br["short"] for br in SB.BRANDS]
'''
T_SAID_NEW = '''    # 1.40.0: the chips first and as they were, then every boxed product
    # and every candy bag; a carton says the YUMMYJAWNS mark too
    assert a["said"][:len(SB.BRANDS)] == [br["short"] for br in SB.BRANDS]
    for br in SB.BOXED + CB.BRANDS:
        assert br["short"] in a["said"], br["id"]
    assert a["said"].count(SB.CAKE_MARK) == len(SB.BOXED_IDS["cake"])


def test_no_two_tiles_overlap_and_every_tile_is_inside_the_art():
    a = S.bag_art()
    W, H = a["size"]
    tiles = [(n, r) for n, r in a["rects"].items()]
    for n, (x0, y0, x1, y1) in tiles:
        assert 0 <= x0 < x1 <= W and 0 <= y0 < y1 <= H, n
    for (n, r), (m, q) in itertools.combinations(tiles, 2):
        assert r[2] <= q[0] or q[2] <= r[0] or r[3] <= q[1] or q[3] <= r[1], (n, m)


def test_one_face_is_the_chip_aisle_and_the_other_is_sections():
    """1.40.0. The walker's 90s snack references: "fruit snacks, lunch kits,
    snack cakes on shelves, candy". The -Y face is chips; the +Y face
    cycles the four sections a bay each; the end caps are chips."""
    w, d, h = S.DC_SIZES[0]
    g = S.plan(w, d, h)
    f = g["facts"]
    assert sum(f["stock"].values()) == f["bags"]
    assert set(f["stock"]) == {"chips"} | set(S.SECTIONS), f["stock"]
    kind_of = {i: "chips" for i in SB.IDS}
    kind_of.update({i: "candy" for i in CB.IDS})
    kind_of.update({b["id"]: b["kind"] for b in SB.BOXED})
    for p in (q for q in g["prims"] if q["mat"] == "bag"):
        brand = p["uvs"][p["front"][0]][0][0][len("tile_"):]
        cy = sum(v[1] for v in p["verts"]) / len(p["verts"])
        cx = sum(v[0] for v in p["verts"]) / len(p["verts"])
        if abs(cx) > f["run"] / 2.0 or cy < 0:           # an end cap, or the chip aisle
            assert kind_of[brand] == "chips", (brand, cx, cy)
        else:
            assert kind_of[brand] in S.SECTIONS, (brand, cx, cy)
    # the shortest run is one bay: still one section, whatever it is
    f1 = S.plan(S.RANGES["width"][0], 1.0, 1.6)["facts"]
    assert len(set(f1["stock"]) - {"chips"}) == 1, f1["stock"]


def test_a_shelf_of_snack_cakes_is_one_flavour_and_the_next_is_another():
    """ "four to six of each flavour side by side ... from two metres it
    reads as stripes of colour" (docs/proposals/GAS_STATION_SHOP.md)."""
    w, d, h = S.DC_SIZES[0]
    cakes = set(SB.BOXED_IDS["cake"])
    by_shelf = {}
    for p in (q for q in S.plan(w, d, h)["prims"] if q["mat"] == "bag"):
        brand = p["uvs"][p["front"][0]][0][0][len("tile_"):]
        if brand in cakes:
            cx = sum(v[0] for v in p["verts"]) / len(p["verts"])
            z = round(min(v[2] for v in p["verts"]), 3)
            by_shelf.setdefault((round(cx / S.BAY_MAX), z), []).append((cx, brand))
    assert by_shelf
    for (_bay, _z), row in by_shelf.items():
        assert 4 <= len(row) <= 6, len(row)
    # one bay's shelves, bottom to top: neighbours differ
    bay = sorted({b for b, _z in by_shelf})[0]
    stack = [sorted(by_shelf[k])[0][1] for k in sorted(by_shelf) if k[0] == bay]
    assert all(a != b for a, b in zip(stack, stack[1:])), stack


def test_every_boxed_product_is_invented_and_legible():
    ids = {b["id"] for b in SB.BRANDS} | set(CB.IDS)
    for br in SB.BOXED:
        assert br["id"] not in ids
        ids.add(br["id"])
        assert br["kind"] in SB.BOXED_KINDS and len(br["short"]) <= 6
        up = SB.words(br).upper()
        toks = set(re.findall(r"[A-Z0-9&'!]+", up))
        for w_ in SB.DENY_WORDS + CB.DENY_WORDS:
            assert w_ not in toks, (br["id"], w_)
        for part in SB.DENY_PARTS + CB.DENY_PARTS:
            assert part not in up, (br["id"], part)
    assert SB.CAKE_MARK not in SB.DENY_WORDS
'''


def main():
    rel = "zoo_keeper/core/snack_brands.py"
    p, s, crlf = _load(rel)
    assert "BOXED" not in s, "already applied"
    s = _once(rel, s, BRANDS_OLD, BRANDS_NEW)
    s = _once(rel, s, DENY_OLD, DENY_NEW)
    s = _once(rel, s, PARTS_OLD, PARTS_NEW)
    _save(p, s, crlf)

    rel = "zoo_keeper/core/snack_gondola_forms.py"
    p, s, crlf = _load(rel)
    s = _once(rel, s, DOC_OLD, DOC_NEW)
    s = _once(rel, s, IMPORT_OLD, IMPORT_NEW)
    s = _once(rel, s, CONST_OLD, CONST_NEW)
    s = _between(rel, s, BAG_START, BAG_END, BAG_NEW)
    s = _once(rel, s, SIDES_OLD, SIDES_NEW)
    s = _once(rel, s, CAPBAG_OLD, CAPBAG_NEW)
    s = _once(rel, s, FACTS_OLD, FACTS_NEW)
    assert s.count(ART_START) == 1, "art anchor"
    s = s[:s.index(ART_START)] + ART_NEW
    _save(p, s, crlf)

    rel = "tests/test_snack_gondola.py"
    p, s, crlf = _load(rel)
    s = _once(rel, s, T_IMPORT_OLD, T_IMPORT_NEW)
    s = _once(rel, s, T_FACE_OLD, T_FACE_NEW)
    s = _once(rel, s, T_MAP_OLD, T_MAP_NEW)
    s = _once(rel, s, T_SAID_OLD, T_SAID_NEW)
    _save(p, s, crlf)


if __name__ == "__main__":
    main()
