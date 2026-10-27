"""Edit a Zoo clone for 1.131.0: the aisle sign's `grocery` form, a supermarket's numbered aisle marker. Run from the
clone's root. Asserts every anchor once; refuses on a miss."""
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


edit("zoo_keeper/core/card_brands.py", [
('''    "DICE AND DOODADS",
    "BACK ISSUES HON",
)
''', '''    "DICE AND DOODADS",
    "BACK ISSUES HON",
)

#: THE SUPERMARKET'S AISLE MARKERS (1.131.0): what the `grocery` form of
#: `aisle_sign` prints under an aisle's number, two lines a sign, in the order
#: a 1990s store walks them. The walker's comps, 2026-10-26 (the factory's
#: docs/reference/GROCERY_STORE_COMPS.md): a numbered sign over every aisle
#: naming what is down it. Categories only -- never a product or a brand.
GROCERY_AISLE_SAYS = (
    ("BREAD", "PEANUT BUTTER"),
    ("CEREAL", "COFFEE & TEA"),
    ("CANNED VEG", "SOUP"),
    ("PASTA & RICE", "SAUCES"),
    ("BAKING", "SPICES"),
    ("CHIPS", "SODA"),
    ("COOKIES", "CANDY"),
    ("JUICE", "DRINK MIX"),
    ("PAPER GOODS", "CLEANING"),
    ("PET FOOD", "CHARCOAL"),
    ("HEALTH", "BEAUTY"),
    ("BABY", "CARDS"),
)
'''),
])

edit("zoo_keeper/core/card_art.py", [
('''def painted_strings(games=None, makers=None, teams=None, says=None,
                    aisle=None):''', '''def painted_strings(games=None, makers=None, teams=None, says=None,
                    aisle=None, grocery=None):'''),
('''    out += list(aisle if aisle is not None else CB.AISLE_SAYS)
    return tuple(out)''', '''    out += list(aisle if aisle is not None else CB.AISLE_SAYS)
    # 1.131.0: the grocery aisle markers' lines, `flat_art.grocery_marker`
    for pair in (grocery if grocery is not None else CB.GROCERY_AISLE_SAYS):
        out += list(pair)
    return tuple(out)'''),
])

edit("zoo_keeper/core/flat_art.py", [
('''def playmat_face(game, w_px, h_px, key):''', '''#: The grocery marker's colours: a 1990s chain's printed aisle sign, white on
#: a blue ground under a white rule.
GROCERY_GROUND = (28, 66, 140)
GROCERY_INK = (244, 244, 238)


def grocery_marker(number, says, w_px, h_px, key):
    """A supermarket's aisle marker (1.131.0): the aisle's NUMBER large in a
    white-ruled box at the hoist end, and the two lines of what is down it
    beside it. Printed, not hand-lettered -- this is the chain's sign, not the
    card shop's marker board. The number is the one thing that has to read
    from the head of the aisle, so it takes the box's whole height."""
    c = Canvas(w_px, h_px, GROCERY_GROUND)
    rule = max(1, h_px // 18)
    _frame(c, 0, 0, w_px, h_px, rule, GROCERY_INK)
    pad = max(2, h_px // 9)
    box = min(int(w_px * 0.34), h_px - 2 * pad)
    _frame(c, pad, pad, pad + box, pad + box, rule, GROCERY_INK)
    _stamp(c, str(int(number)), pad + rule + 1, pad + rule + 1, pad + box - rule - 1,
           pad + box - rule - 1, GROCERY_INK, cap=12)
    x0 = pad + box + pad
    half = (h_px - 2 * pad) // 2
    for i, line in enumerate(says[:2]):
        _stamp(c, line, x0, pad + i * half, w_px - pad, pad + (i + 1) * half,
               GROCERY_INK, cap=6)
    return c


def playmat_face(game, w_px, h_px, key):'''),
('''    if kind == "aisle":
        return aisle_letters(spec.get("says", ""), w, h, key)''',
'''    if kind == "aisle":
        if spec.get("number"):
            return grocery_marker(spec["number"], tuple(spec.get("lines") or ()), w, h, key)
        return aisle_letters(spec.get("says", ""), w, h, key)'''),
])

edit("zoo_keeper/core/flat_forms.py", [
('''    params = params or {}
    says = params.get("says")
    if not says:
        says = CB.AISLE_SAYS[variant % len(CB.AISLE_SAYS)]
    spread = 0.30 + 0.04 * (variant % 4)
    prims, tiles = [], {}
    xs = (-w * spread, w * spread)
    board_h = _hung_board(prims, tiles, w, d, h, SIGN_DROP_K, xs,
                          {"kind": "aisle", "says": says}, "AisleSign", key)''',
'''    params = params or {}
    # THE GROCERY FORM (1.131.0): a supermarket's numbered aisle marker, the
    # number the variant's (aisle 1 is variant 0) and its two lines
    # `card_brands.GROCERY_AISLE_SAYS`'s, printed on `flat_art.grocery_marker`
    if params.get("form") == "grocery":
        lines = CB.GROCERY_AISLE_SAYS[variant % len(CB.GROCERY_AISLE_SAYS)]
        prims, tiles = [], {}
        # a variant is a different module in GEOMETRY too, not only in its tile
        # (`test_flat_art`'s rule): the drops step in by 5 mm an aisle
        spread = 0.40 - 0.005 * variant
        xs = (-w * spread, w * spread)
        board_h = _hung_board(prims, tiles, w, d, h, SIGN_DROP_K, xs,
                              {"kind": "aisle", "number": variant + 1, "lines": list(lines)},
                              "AisleSign", key)
        prims, _ = P.fit_exact(prims, (-w / 2.0, -d / 2.0, 0.0),
                               (w / 2.0, d / 2.0, h))
        return {"prims": prims, "tiles": tiles, "collision": [],
                "facts": {"variant": variant, "says": " / ".join(lines), "form": "grocery",
                          "number": variant + 1, "tiles": len(tiles),
                          "tris": P.tri_count(prims), "drop_m": round(h - board_h, 3),
                          "board_m": round(board_h, 3)}}
    says = params.get("says")
    if not says:
        says = CB.AISLE_SAYS[variant % len(CB.AISLE_SAYS)]
    # variants 0-3 as they shipped; past them (1.131.0, the grocery form's
    # twelve) the drops step out 5 mm a round, so each variant stays its own
    # module in geometry
    spread = 0.30 + 0.04 * (variant % 4) + 0.005 * (variant // 4)
    prims, tiles = [], {}
    xs = (-w * spread, w * spread)
    board_h = _hung_board(prims, tiles, w, d, h, SIGN_DROP_K, xs,
                          {"kind": "aisle", "says": says}, "AisleSign", key)'''),
])

g = Path("zoo_keeper/genome/species/aisle_sign.json")
raw = g.read_bytes()
assert b"\r\n" not in raw
d = json.loads(raw)
assert d["params"] == {"says": ""} and d["module_variants"] == 4
old_p = '''  "params": {\n    "says": ""\n  },'''
t = raw.decode("utf-8")
assert t.count(old_p) == 1
t = t.replace(old_p, '''  "params": {\n    "says": "",\n    "form": [\n      "auto",\n      "grocery"\n    ]\n  },''')
assert t.count('"module_variants": 4,') == 1
t = t.replace('"module_variants": 4,', '"module_variants": 12,')
d2 = json.loads(t)
assert d2["params"]["form"] == ["auto", "grocery"] and d2["module_variants"] == 12
g.write_bytes(t.encode("utf-8"))
print(g, "form grocery, module_variants 12")
