"""Zoo 1.137.0, part two: teller_line's `bank` form -- the nameboard. Run in a Zoo clone's root, after
edit_zoo_bank_posters.py; the new module and its test sit beside this script."""
import json
import pathlib
import shutil

S = pathlib.Path(__file__).parent
R = pathlib.Path.cwd()


def edit(rel, pairs):
    p = R / rel
    t = p.read_bytes().decode("utf-8")
    crlf = "\r\n" in t
    t = t.replace("\r\n", "\n")
    for a, b in pairs:
        assert t.count(a) == 1, (rel, a[:70])
        t = t.replace(a, b)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print(p, "edited")


for src, rel in (("teller_line_forms.py", "zoo_keeper/core/teller_line_forms.py"),
                 ("test_teller_line_bank.py", "tests/test_teller_line_bank.py")):
    dst = R / rel
    assert not dst.exists(), dst
    shutil.copyfile(S / src, dst)
    print(dst, "written")

edit("zoo_keeper/core/card_art.py", [
('''    if kind == "storefront_sign":
        from . import storefront_names as SN
        return SN.paint(spec)
''',
 '''    if kind == "storefront_sign":
        from . import storefront_names as SN
        return SN.paint(spec)
    # A BANK'S TELLER LINE (1.137.0): its nameboard, `teller_line_forms`'
    if kind == "teller_board":
        from . import teller_line_forms as TF
        return TF.paint(spec)
'''),
])

edit("zoo_keeper/recipes/teller_line.py", [
('''This builds only the intact state.''',
 '''THE BANK FORM (1.137.0, the walker's bank comps: a name over the line, a
number on every window). The header rises to `teller_line_forms.BANK_HEADER`
and steps back by a nameboard's thickness, and the board fills the step: the
bank's name across it, each window's number over its bay, painted in one
atlas (`teller_line_forms.bank_board`). The middle posts stop just inside the
raised header, where they would cut through the board. The default form is
the line it always was.

This builds only the intact state.'''),
('''from ..core import arch
from ._bays import bay_max_of, bays''',
 '''from ..core import arch
from ..core import teller_line_forms as TF
from ._bays import bay_max_of, bays'''),
('''    header = min(float(p.get("header", 0.20)), (h - counter_h) * 0.5)
''',
 '''    header = min(float(p.get("header", 0.20)), (h - counter_h) * 0.5)
    bank = str(p.get("form") or "auto") == "bank"
    if bank:
        header = TF.header_of(header, h, counter_h)
    # the bank's header steps back by its nameboard, which fills the step
    step = TF.BOARD_T if bank else 0.0
''' ),
('''        box(f"{root}_Header", (0.0, 0.0, (header_bot + hh) / 2.0),
            (w - 2.0 * post, d, header))''',
 '''        box(f"{root}_Header", (0.0, step / 2.0, (header_bot + hh) / 2.0),
            (w - 2.0 * post, d - step, header))'''),
('''            tag = "L" if i == 0 else ("R" if i == len(edges) - 1 else "M%d" % i)
            box(f"{root}_Post_{tag}", (x, 0.0, (counter_top + hh) / 2.0),
                (post, d, hh - counter_top))''',
 '''            tag = "L" if i == 0 else ("R" if i == len(edges) - 1 else "M%d" % i)
            top = hh
            if bank and tag.startswith("M"):
                top = header_bot + TF.POST_INTO_HEADER
            box(f"{root}_Post_{tag}", (x, 0.0, (counter_top + top) / 2.0),
                (post, d, top - counter_top))'''),
('''    materials.assign(structure, body)
''',
 '''    materials.assign(structure, body)
    art = []
    if bank:
        from ._card_atlas import build_art
        prims, tiles = TF.bank_board(w, d, h, post, header, runs, p.get("variant", 0))
        art, _atlas = build_art(prims, collection, dict(plan, _tiles=tiles), streams,
                                "TellerLine_Board", smooth=True)
'''),
('''    return {"objects": structure + glassboxes, "collision_boxes": cboxes,''',
 '''    return {"objects": structure + glassboxes + art, "collision_boxes": cboxes,'''),
])

g = R / "zoo_keeper/genome/species/teller_line.json"
d = json.loads(g.read_text(encoding="utf-8"))
assert "form" not in d["params"] and "module_variants" not in d
d["params"]["form"] = ["auto", "bank"]
d["module_variants"] = 16
d["parts"].append("TellerLine_Board")
d["license"]["notes"] += (" 1.137.0: form 'bank' -- a nameboard on the header's public face, the bank's name "
                          "(storefront_names' bank names) over each window's number; sixteen variants, four names in four colourways, the door sign's by `teller_line_forms.variant_for`.")
g.write_bytes((json.dumps(d, indent=2) + "\n").encode("utf-8"))
print(g, "edited")
