"""Edit a Zoo clone for 1.133.0: `snack_gondola`'s `grocery` form -- a supermarket's gondola whose two faces sell the
two categories the aisle markers name on either side of it, on an image of its own. Run from the clone's root. Asserts
every anchor once; refuses on a miss. The snack form's every byte is unchanged."""
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


F = "zoo_keeper/core/snack_gondola_forms.py"
edit(F, [
('''The +Y side is the -Y side turned half round about the centre, and the +X
end cap the -X one, so both faces read the right way round.
"""''',
'''The +Y side is the -Y side turned half round about the centre, and the +X
end cap the -X one, so both faces read the right way round.

THE GROCERY FORM (1.133.0, `params.form == "grocery"`). The walker's grocery
comps (the factory's docs/reference/GROCERY_STORE_COMPS.md): "shiny floor,
bright lights, isles, glowing freezer section, stacked high" -- and a
supermarket whose gondolas sold the convenience store's chips read as a big
convenience store. The same frame, shelves and strips; each FACE sells one
category of `grocery_brands.CATEGORIES`, the names the aisle markers print
(`card_brands.GROCERY_AISLE_SAYS`, two a lane):

  * THE VARIANT IS THE GONDOLA'S LINE. Line n of a store's gondolas stands
    between lane n - 1 and lane n; the lane's marker names its two
    categories, and in the markers' flat order the face toward lane n - 1
    sells category 2n - 1 and the face toward lane n category 2n
    (`grocery_faces`). Face "a" (-Y) is the first, face "b" (+Y) the
    second, so a shelf sells what the sign over its lane says when the
    store stands its gondolas in order, -Y toward the lane before.
  * A CATEGORY IS A PACK (`GROCERY_PACKS`): cartons (cereal, pasta, mixes,
    paper goods), hexagonal cans STACKED as high as the shelf's clearance
    takes them (the comps' "stacked high"), jars, bottles and jugs with a
    shoulder and a neck, bags (bread, chips, candy, sacks of pet food and
    charcoal). CHIPS are `snack_brands`', CANDY `candy_brands`', SODA the
    vending machine's (`brands`) in two-litre bottles.
  * The end caps are cereal.

ITS OWN IMAGE (`grocery_art`), so every snack gondola that shipped keeps its
image's bytes and its name.
"""'''),
('''from . import candy_brands as CB
from . import pixel_type as pt''',
'''from . import brands as DB
from . import candy_brands as CB
from . import card_brands as KB
from . import grocery_brands as GB
from . import pixel_type as pt'''),
('''CANDY_CROWN = 0.02
''',
'''CANDY_CROWN = 0.02

#: THE GROCERY FORM'S PACKS (1.133.0): pack -> (width, height, depth, gap,
#: facings a product, shape). A can's, a jar's and a bottle's width is its
#: extent along the shelf, across its corners; a bag's depth is its thickness.
GROCERY_PACKS = {
    "cereal": (0.19, 0.28, 0.07, 0.012, 2, "box"),
    "box": (0.13, 0.22, 0.05, 0.010, 3, "box"),
    "small": (0.07, 0.12, 0.04, 0.008, 4, "box"),
    "pack": (0.30, 0.28, 0.22, 0.012, 1, "box"),
    "can": (0.085, 0.115, 0.085, 0.008, 3, "can"),
    "canister": (0.12, 0.16, 0.12, 0.010, 2, "can"),
    "jar": (0.09, 0.13, 0.09, 0.010, 3, "jar"),
    "bottle": (0.105, 0.30, 0.105, 0.012, 2, "bottle"),
    "jug": (0.14, 0.28, 0.14, 0.014, 2, "bottle"),
    "bag": (BAG_W, 0.30, BAG_D, BAG_GAP, 2, "bag"),
    "candy": (0.125, 0.17, 0.05, 0.016, 2, "bag"),
    "loaf": (0.13, 0.14, 0.22, 0.020, 2, "bag"),
    "sack": (0.30, 0.40, 0.12, 0.020, 1, "bag"),
}
#: a bag pack's crown, the puff of its front
GROCERY_CROWN = {"bag": BAG_CROWN, "candy": CANDY_CROWN, "loaf": 0.02, "sack": 0.03}
#: THE TRIANGLE CEILINGS (1.133.0), regression detectors and not frame costs:
#: every gondola is two submissions whatever it stocks. The genome's
#: `tris_lod0` is the grocery form's, 46,116 at the range's largest corner
#: (14 x 1.5 x 2.2, line 2) rounded up; the snack form keeps the 22,000 it
#: shipped under (21,660 at that corner), held by its own test.
SNACK_TRIS_BUDGET = 22000
#: a stacked can's foot over the one under it: clear of the coplanar census
CAN_STACK_GAP = 0.003
#: (fraction of height, fraction of the body's radius) up a bottle and a jar
BOTTLE_RINGS = ((0.0, 1.0), (0.64, 1.0), (0.84, 0.34), (1.0, 0.34))
JAR_RINGS = ((0.0, 1.0), (0.80, 1.0), (0.84, 0.86), (1.0, 0.86))
#: the sodas a bottle's label can set: the vending machine's, six letters or
#: fewer
SODA_IDS = tuple(b["id"] for b in DB.BRANDS if len(b["short"]) <= 6)
#: every category, in the aisle markers' flat order
GROCERY_CATEGORIES = tuple(c for lane in KB.GROCERY_AISLE_SAYS for c in lane)
'''),
('''def shelf_levels(h):''',
'''def form_of(plan_):
    """``"grocery"`` when the slot asks for it (1.133.0), else ``"snack"``."""
    module = plan_.get("module") or {}
    params = plan_.get("params") or {}
    return "grocery" if "grocery" in (module.get("form"), params.get("form")) else "snack"


def shelf_levels(h):'''),
('''def section(key, variant, face, bi):''',
'''def _prism(x, y_front, z0, rings, h, brand, label_to):
    """A hexagonal solid, a flat toward -Y at ``y_front``, centred on ``x``,
    standing on ``z0`` (buried `BURY`); ``rings`` are (fraction of ``h``,
    half its width along x -- across its corners, so neighbours ``2r`` apart
    clear each other) up it. The faces of the bands under ring
    ``label_to`` that look toward -Y carry the tile ``tile_<brand>`` by x
    and z; every other face is the brand's colour block. Wound outward: the
    rings run counter-clockwise seen from +Z."""
    c30 = math.cos(math.radians(30.0))
    yc = y_front + rings[0][1] * c30
    zb = z0 - BURY
    angles = [math.radians(-120.0 + 60.0 * k) for k in range(6)]
    verts = []
    for f, r in rings:
        verts += [(x + r * math.cos(a), yc + r * math.sin(a), zb + h * f) for a in angles]
    n = len(rings)
    faces = [tuple(range(5, -1, -1))]                                 # the foot
    for j in range(n - 1):
        for k in range(6):
            a, b = 6 * j + k, 6 * j + (k + 1) % 6
            faces.append((a, b, b + 6, a + 6))
    faces.append(tuple(range(6 * (n - 1), 6 * n)))                     # the top
    p = P.mesh("Snack_Bag", "bag", verts, faces)
    x0, x1 = x - rings[0][1], x + rings[0][1]
    z_lo, z_hi = zb + h * rings[0][0], zb + h * rings[label_to][0]
    front, uvs = [], []
    for fi, f in enumerate(p["faces"]):
        band = (fi - 1) // 6 if 1 <= fi <= 6 * (n - 1) else -1
        y_mid = sum(p["verts"][i][1] for i in f) / float(len(f))
        if 0 <= band < label_to and y_mid < yc - 1e-9:
            front.append(fi)
            uvs.append(tuple(("tile_" + brand,
                              min(1.0, max(0.0, (p["verts"][i][0] - x0) / (x1 - x0))),
                              min(1.0, max(0.0, (p["verts"][i][2] - z_lo) / (z_hi - z_lo))))
                             for i in f))
        else:
            uvs.append(tuple(("solid_" + brand,) for _ in f))
    p["uvs"] = uvs
    p["front"] = tuple(front)
    return p


def can(x, y_front, z0, w, h, brand):
    """One can (1.133.0): a hexagonal prism ``w`` across its corners, its label
    the whole height. 20 triangles."""
    return _prism(x, y_front, z0, ((0.0, w / 2.0), (1.0, w / 2.0)), h, brand, 1)


def jar(x, y_front, z0, w, h, brand):
    """One jar (1.133.0): a hexagonal body, a lid a little narrower
    (`JAR_RINGS`), the label round the body. 44 triangles."""
    return _prism(x, y_front, z0, tuple((f, w / 2.0 * k) for f, k in JAR_RINGS), h, brand, 1)


def bottle(x, y_front, z0, w, h, brand):
    """One bottle or jug (1.133.0): a hexagonal body ``w`` across its corners,
    a shoulder drawing in to a neck (`BOTTLE_RINGS`), the label round the
    body. 44 triangles."""
    return _prism(x, y_front, z0, tuple((f, w / 2.0 * k) for f, k in BOTTLE_RINGS), h, brand, 1)


def grocery_faces(variant):
    """``(face a's category, face b's)`` for the gondola on line ``variant``
    of its store (see the module's docstring): categories 2v - 1 and 2v of
    the aisle markers' flat order, round the list."""
    n = len(GROCERY_CATEGORIES)
    v = int(variant)
    return GROCERY_CATEGORIES[(2 * v - 1) % n], GROCERY_CATEGORIES[(2 * v) % n]


def grocery_ids(category):
    """The products of ``category``, as tile ids."""
    if category == "CHIPS":
        return SB.IDS
    if category == "CANDY":
        return CB.IDS
    if category == "SODA":
        return SODA_IDS
    return tuple(p["id"] for p in GB.CATEGORIES[category][1])


def section(key, variant, face, bi):'''),
('''def _side(xs0, xs1, bays_, h, d, key, variant, face):
    """One shelved face of the run (the -Y one), over x ``xs0..xs1``."""
    out, n_bags, stock = [], 0, {}
    levels, pitch = shelf_levels(h)
    y_front = -d / 2.0 + 0.02                         # the shelves' front edge
    y_back = -SPINE_T / 2.0 + BURY                    # buried into the spine
    for bi, (bx, bw) in enumerate(bays_):
        sx0, sx1 = bx - bw / 2.0 + UPRIGHT_W / 2.0 + 0.004, bx + bw / 2.0 - UPRIGHT_W / 2.0 - 0.004
        kind = section(key, variant, face, bi)
        iw, ih, idp, gap, _facings, form = STOCK[kind]''',
'''def _side(xs0, xs1, bays_, h, d, key, variant, face, grocery=False):
    """One shelved face of the run (the -Y one), over x ``xs0..xs1``."""
    out, n_bags, stock = [], 0, {}
    levels, pitch = shelf_levels(h)
    y_front = -d / 2.0 + 0.02                         # the shelves' front edge
    y_back = -SPINE_T / 2.0 + BURY                    # buried into the spine
    if grocery:
        category = grocery_faces(variant)[0 if face == "a" else 1]
        pack = GB.CATEGORIES[category][0]
        ids = grocery_ids(category)
    for bi, (bx, bw) in enumerate(bays_):
        sx0, sx1 = bx - bw / 2.0 + UPRIGHT_W / 2.0 + 0.004, bx + bw / 2.0 - UPRIGHT_W / 2.0 - 0.004
        if grocery:
            kind = category
            iw, ih, idp, gap, facings, form = GROCERY_PACKS[pack]
        else:
            kind = section(key, variant, face, bi)
            iw, ih, idp, gap, _facings, form = STOCK[kind]'''),
('''            for i in range(n):
                brand = product(kind, key, variant, face, bi, k, i)
                x = bx0 + i * (iw + gap)
                if form == "box":''',
'''            for i in range(n):
                x = bx0 + i * (iw + gap)
                if grocery:
                    brand = ids[(_h(key, variant, face, bi, k) + i // facings) % len(ids)]
                    if form == "can":
                        # STACKED as high as the shelf's clearance takes them
                        tiers = max(1, int((pitch - SHELF_T - 0.04 + CAN_STACK_GAP) // (ih + CAN_STACK_GAP)))
                        got = [can(x, y_front + 0.014, z + t * (ih + CAN_STACK_GAP) + (BURY if t else 0.0),
                                   iw, ih, brand) for t in range(tiers)]
                    elif form == "jar":
                        got = [jar(x, y_front + 0.014, z, iw, min(ih, bh), brand)]
                    elif form == "bottle":
                        got = [bottle(x, y_front + 0.014, z, iw, bh, brand)]
                    elif form == "bag":
                        got = [bag(x, y_front + 0.014, z, iw, bh, brand, idp, GROCERY_CROWN[pack])]
                    else:
                        got = [carton(x, y_front + 0.014, z, iw, bh, idp, brand)]
                    out += got
                    n_bags += len(got)
                    stock[kind] = stock.get(kind, 0) + len(got)
                    continue
                brand = product(kind, key, variant, face, bi, k, i)
                if form == "box":'''),
('''def layout(w, d, h, key="snack_gondola", variant=0):
    """Every part at slot (w, d, h): ``(prims, facts)``."""''',
'''def layout(w, d, h, key="snack_gondola", variant=0, form="snack"):
    """Every part at slot (w, d, h): ``(prims, facts)``. ``form`` is
    ``"snack"`` or ``"grocery"`` (1.133.0)."""
    grocery = form == "grocery"'''),
('''    side, n_bags, stock = _side(xa, xb, bays_, h, d, key, variant, "a")
    other, n_b, stock_b = _side(xa, xb, bays_, h, d, key, variant, "b")''',
'''    side, n_bags, stock = _side(xa, xb, bays_, h, d, key, variant, "a", grocery)
    other, n_b, stock_b = _side(xa, xb, bays_, h, d, key, variant, "b", grocery)'''),
('''                for i in range(n):
                    brand = SB.IDS[(_h(key, variant, "cap", s, k) + i // 2) % len(SB.IDS)]
                    # built facing -Y at the origin, then turned to face -X
                    b = bag(0.0, 0.0, z, BAG_W, bh, brand)
                    b = P.rotate_z(b, -math.pi / 2.0, about=(0.0, 0.0))
                    by = ys0 + (ys1 - ys0 - span) / 2.0 + BAG_W / 2.0 + i * (BAG_W + BAG_GAP)
                    cap.append(P.translate(b, (ex + 0.02 + 0.014, by, 0.0)))
                    n_bags += 1
                    stock["chips"] = stock.get("chips", 0) + 1''',
'''                for i in range(n):
                    # built facing -Y at the origin, then turned to face -X
                    if grocery:
                        # a grocery end cap is cereal, two facings a brand
                        ids = grocery_ids("CEREAL")
                        brand = ids[(_h(key, variant, "cap", s, k) + i // 2) % len(ids)]
                        b = carton(0.0, 0.0, z, BAG_W, bh, GROCERY_PACKS["cereal"][2], brand)
                        got = "CEREAL"
                    else:
                        brand = SB.IDS[(_h(key, variant, "cap", s, k) + i // 2) % len(SB.IDS)]
                        b = bag(0.0, 0.0, z, BAG_W, bh, brand)
                        got = "chips"
                    b = P.rotate_z(b, -math.pi / 2.0, about=(0.0, 0.0))
                    by = ys0 + (ys1 - ys0 - span) / 2.0 + BAG_W / 2.0 + i * (BAG_W + BAG_GAP)
                    cap.append(P.translate(b, (ex + 0.02 + 0.014, by, 0.0)))
                    n_bags += 1
                    stock[got] = stock.get(got, 0) + 1'''),
('''    facts = {"bays": len(bays_), "bay_width": bays_[0][1], "end_caps": caps, "bags": n_bags,''',
'''    facts = {"bays": len(bays_), "bay_width": bays_[0][1], "end_caps": caps, "bags": n_bags, "form": form,
             "faces": grocery_faces(variant) if grocery else None,'''),
('''def plan(w, d, h, key="snack_gondola", variant=0):
    prims, facts = layout(w, d, h, key, variant)''',
'''def plan(w, d, h, key="snack_gondola", variant=0, form="snack"):
    prims, facts = layout(w, d, h, key, variant, form)'''),
])

# the grocery image, appended after the snack image's code
p = Path(F)
t = p.read_bytes().decode("utf-8")
assert t.endswith('''            "name": f"snackbags_{W}x{H}_{digest:08x}"}
''') and t.count("def grocery_art(") == 0
t += '''

# --- the grocery form's image (1.133.0) ---------------------------------------------------

#: pack -> a front tile, pixels: six letters across 40. The chips' and
#: candy's are the snack image's own sizes.
GROCERY_TILES = {"cereal": (40, 58), "box": (40, 50), "small": (40, 40), "pack": (40, 50),
                 "can": (40, 28), "canister": (40, 28), "jar": (40, 28), "bottle": (40, 26),
                 "jug": (40, 26), "bag": TILE, "candy": SMALL_TILE, "loaf": (40, 44), "sack": (40, 60)}
GROCERY_W = 240


def _cols(b):
    return GB.hex_rgb(b["body"]), GB.hex_rgb(b["second"]), GB.hex_rgb(b["ink"])


def _paint_cereal(c, x0, y0, b, size):
    """A cereal box: the name on a plate across its top, a bowl of it under."""
    tw, th = size
    body, second, ink = _cols(b)
    c.rect(x0, y0, x0 + tw, y0 + th, body)
    _set(c, b["short"], x0, y0 + 6, tw, ink, _dark(body))
    c.rect(x0 + 6, y0 + 36, x0 + tw - 6, y0 + 48, CREAM)              # the bowl
    c.rect(x0 + 9, y0 + 48, x0 + tw - 9, y0 + 51, _dark(CREAM, 40))
    for k in range(7):                                                # what is in it
        px = x0 + 8 + k * 4
        c.rect(px, y0 + 32 + (k % 2) * 2, px + 3, y0 + 37 + (k % 2) * 2, second)
    c.rect(x0, y0 + th - 3, x0 + tw, y0 + th, _dark(body, 40))
    return [b["short"]]


def _paint_box(c, x0, y0, b, size):
    """A carton: a band of the second colour across its top, the name under
    it, a window of the second colour -- and on the pasta, the NONNA mark in
    the band and the pasta through the window."""
    tw, th = size
    body, second, ink = _cols(b)
    pasta = b["category"] == "PASTA & RICE"
    c.rect(x0, y0, x0 + tw, y0 + th, body)
    c.rect(x0, y0, x0 + tw, y0 + 11, second)
    said = []
    if pasta:
        _set(c, GB.PASTA_MARK, x0, y0 + 2, tw, body)
        said.append(GB.PASTA_MARK)
    _set(c, b["short"], x0, y0 + 14, tw, ink, _dark(body) if not pasta else None)
    said.append(b["short"])
    if th - 6 > 26:
        c.rect(x0 + 5, y0 + 25, x0 + tw - 5, y0 + th - 6, (60, 40, 30) if pasta else second)
        if pasta:
            for k in range(8):
                px, py = x0 + 7 + (k % 4) * 5, y0 + 27 + (k // 4) * 7
                c.rect(px, py, px + 4, py + 5, (236, 206, 130))
    c.rect(x0, y0 + th - 2, x0 + tw, y0 + th, _dark(body, 40))
    return said


def _paint_label(c, x0, y0, b, size):
    """A label round a can, a jar or a bottle: bands of the second colour
    top and bottom, the name across."""
    tw, th = size
    body, second, ink = _cols(b)
    c.rect(x0, y0, x0 + tw, y0 + th, body)
    c.rect(x0, y0 + 2, x0 + tw, y0 + 4, second)
    c.rect(x0, y0 + th - 4, x0 + tw, y0 + th - 2, second)
    _set(c, b["short"], x0, y0 + (th - 7) // 2, tw, ink)
    return [b["short"]]


def _paint_sack(c, x0, y0, b, size):
    """A bag of bread, kibble or coals: the name on a plate, a band of the
    second colour, the seals top and bottom."""
    tw, th = size
    body, second, ink = _cols(b)
    c.rect(x0, y0, x0 + tw, y0 + th, body)
    c.rect(x0, y0 + th * 55 // 100, x0 + tw, y0 + th * 75 // 100, second)
    c.rect(x0, y0, x0 + tw, y0 + 3, tuple(min(255, v + 40) for v in body))
    c.rect(x0, y0 + th - 3, x0 + tw, y0 + th, _dark(body, 40))
    _set(c, b["short"], x0, y0 + th * 20 // 100, tw, ink, _dark(body))
    return [b["short"]]


def _paint_soda(c, x0, y0, b, size):
    """A two-litre's label: the vending machine's panel colours, its button
    label across them."""
    tw, th = size
    top, bot = DB.hex_rgb(b["bg"][0]), DB.hex_rgb(b["bg"][1])
    c.rect(x0, y0, x0 + tw, y0 + th // 2, top)
    c.rect(x0, y0 + th // 2, x0 + tw, y0 + th, bot)
    _set(c, b["short"], x0, y0 + (th - 7) // 2, tw, DB.hex_rgb(b["ink"]), DB.hex_rgb(b["edge"]))
    return [b["short"]]


_PAINT = {"cereal": _paint_cereal, "box": _paint_box, "small": _paint_box, "pack": _paint_box,
          "can": _paint_label, "canister": _paint_label, "jar": _paint_label, "bottle": _paint_label,
          "jug": _paint_label, "loaf": _paint_sack, "sack": _paint_sack}


def grocery_items():
    """``[(product, size, painter, solid rgb)]`` for every product the grocery
    form can stock, in the aisle markers' order: a tile each."""
    out = []
    for cat in GROCERY_CATEGORIES:
        pack = GB.CATEGORIES[cat][0]
        size = GROCERY_TILES[pack]
        if cat == "CHIPS":
            out += [(b, size, lambda c, x, y, b, s: _paint_bag(c, x, y, b), SB.hex_rgb(b["body"]))
                    for b in SB.BRANDS]
        elif cat == "CANDY":
            out += [(b, size, lambda c, x, y, b, s: _paint_candy(c, x, y, b), CB.hex_rgb(b["body"]))
                    for b in CB.BRANDS]
        elif cat == "SODA":
            out += [(DB.BY_ID[i], size, _paint_soda, DB.hex_rgb(DB.BY_ID[i]["bg"][1])) for i in SODA_IDS]
        else:
            out += [(b, size, _PAINT[pack], GB.hex_rgb(b["body"])) for b in GB.CATEGORIES[cat][1]]
    return out


def grocery_art():
    """ONE image for every product of the grocery form: a front tile each
    (`tile_<id>`), shelved left to right in rows the height of their tallest
    tile, and a solid block (`solid_<id>`) for its sides, back and top -- a
    soda's the colour of what is in the bottle. ``{canvas, size, rects,
    said, name}``; rects are pixel boxes, row 0 at the top."""
    items = grocery_items()
    W = GROCERY_W
    x = y = row_h = 0
    placed = []
    for b, (tw, th), paint, solid in items:
        if x + tw > W:
            x, y, row_h = 0, y + row_h, 0
        placed.append((b, paint, x, y, (tw, th), solid))
        x += tw
        row_h = max(row_h, th)
    y_solid = y + row_h
    per_row = W // 5
    H = y_solid + 5 * int(math.ceil(len(placed) / float(per_row))) + 3
    c = Canvas(W, H, (20, 20, 20))
    rects, said = {}, []
    for i, (b, paint, x0, y0, size, solid) in enumerate(placed):
        assert "tile_" + b["id"] not in rects, b["id"]
        rects["tile_" + b["id"]] = (x0, y0, x0 + size[0], y0 + size[1])
        said.extend(paint(c, x0, y0, b, size))
        sx, sy = (i % per_row) * 5, y_solid + 2 + (i // per_row) * 5
        c.rect(sx, sy, sx + 4, sy + 4, solid)
        rects["solid_" + b["id"]] = (sx, sy, sx + 4, sy + 4)
    digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
    return {"canvas": c, "size": (W, H), "rects": rects, "said": said,
            "name": f"grocery_{W}x{H}_{digest:08x}"}
'''
p.write_bytes(t.encode("utf-8"))
print(F, "grocery_art appended")

edit("zoo_keeper/recipes/snack_gondola.py", [
('''    key, variant = SG.resolve(plan)
    got = SG.plan(w, d, h, key, variant)''',
'''    key, variant = SG.resolve(plan)
    form = SG.form_of(plan)
    got = SG.plan(w, d, h, key, variant, form)'''),
('''    A = SG.bag_art()''',
'''    # the grocery form (1.133.0) paints its own image; the snack form's is
    # the one that shipped
    A = SG.grocery_art() if form == "grocery" else SG.bag_art()'''),
('''    print(f"[snack_gondola] bays={f['bays']} shelves={f['shelves']} end_caps={f['end_caps']} "''',
'''    print(f"[snack_gondola] form={form} bays={f['bays']} shelves={f['shelves']} end_caps={f['end_caps']} "'''),
])

# the genome: the form, twelve lines of a store, the note
G = Path("zoo_keeper/genome/species/snack_gondola.json")
raw = G.read_bytes()
g = json.loads(raw.decode("utf-8"))
assert g["params"] == {"form": ["auto"]} and g["module_variants"] == 4, (g["params"], g["module_variants"])
g["params"]["form"] = ["auto", "grocery"]
g["module_variants"] = 12
g["license"]["notes"] += (" 1.133.0: form 'grocery' -- a supermarket's gondola. Each face sells one category of "
                          "core/grocery_brands.py, the names the grocery aisle markers print; the variant is the "
                          "gondola's line in its store, so the faces toward the lanes either side sell what their "
                          "markers say (snack_gondola_forms.grocery_faces). Cartons, stacked hexagonal cans, jars, "
                          "bottles and jugs, bags; its own painted image. module_variants 4 -> 12, a line a pair of "
                          "the markers' 24 categories. budgets.tris_lod0 22000 -> 48000, the grocery form's "
                          "ceiling (46,116 at 14 x 1.5 x 2.2); the snack form keeps 22,000 in its test "
                          "(SNACK_TRIS_BUDGET).")
g["keywords"] += ["grocery gondola", "grocery aisle"]
assert g["budgets"] == {"tris_lod0": 22000}, g["budgets"]
g["budgets"]["tris_lod0"] = 48000
G.write_bytes((json.dumps(g, indent=1) + "\n").encode("utf-8"))
print(G, "edited")

edit("tests/test_snack_gondola.py", [
('''    assert P.tri_count(pr) <= genome_mod.load_species("snack_gondola")["budgets"]["tris_lod0"]
''',
'''    # the snack form's own ceiling (1.133.0 raised the genome's for the
    # grocery form's)
    assert P.tri_count(pr) <= S.SNACK_TRIS_BUDGET
'''),
])
