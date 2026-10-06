"""Pixelcoat 0.60.0: FLAPPAHS is cream on green, and the chain-link fabric
blends its texture.

1. THE BRAND'S COLOURS. The walker, 2026-10-06, asked whether the brand is
   the band's cream on red or the pylon's cream on green: "We can do the
   green and cream". Zoo draws the pylon, the pumps and the door box in
   `price_pylon_forms.COLOURWAYS[0]`: field (24, 78, 52), rule (226, 206,
   150), ink (246, 238, 214). The band now draws in the same three colours:
   panel `#184e34`, border `#e2ce96`, text `#f6eed6`. A mirror test reads
   Zoo's tuple, so the two cannot drift.
   - `marks/flappahs_green.svg` is the goose mark with its red fills in the
     brand green.
   - `flappahs_red.svg` stays: it is the art the brand was named with
     (2026-09-26). Nothing renders either one; the mark is reference art.
2. THE FABRIC BLENDS ITS TEXTURE. `chain_link_galvanized`'s transparency
   was `alpha_mode: scissor`. At distance its mips (about 25 % wire) fall
   under the 0.5 test and the fabric vanishes (cold run 9183, roadmap 188).
   - Rendered on cold run 9184's walk copy, blending the same texture keeps
     a faint screen at 20 m and along a 16.8 m run.
   - A second, distant card cannot fix that second case: visibility ranges
     switch a whole node.
   - The hint is now `blend_texture`, which Zoo 1.78.0 honours. The cutout
     alpha itself is unchanged.

    python patch_pixelcoat_brand_and_fabric.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PX = ROOT / "pixelcoat"
SIGNS = PX / "profiles" / "signs"
GREEN = {"panel": "#184e34", "border": "#e2ce96", "text_color": "#f6eed6"}
RED_FILL = "#EE241C"


def _rt(path):
    raw = path.read_bytes()
    assert b"\r\n" not in raw, path
    text = raw.decode("utf-8")
    data = json.loads(text)
    for indent in (1, 2):
        if json.dumps(data, indent=indent, ensure_ascii=False) + "\n" == text:
            return data, indent
    raise SystemExit(f"{path}: does not round-trip; edit by hand")


def _write(path, data, indent):
    path.write_bytes((json.dumps(data, indent=indent, ensure_ascii=False) + "\n").encode("utf-8"))


def main():
    staged = []
    for name in ("delco.json", "delco_1997.json"):
        data, indent = _rt(SIGNS / name)
        flap = [s for s in data["signs"] if s.get("slug") == "flappahs"]
        assert len(flap) == 1, name
        s = flap[0]
        assert s["panel"].lower() == "#ee241c" and s["mark"] == "marks/flappahs_red.svg", (name, s)
        s.update(GREEN)
        s["mark"] = "marks/flappahs_green.svg"
        staged.append((SIGNS / name, data, indent))

    red = (SIGNS / "marks" / "flappahs_red.svg").read_bytes().decode("utf-8")
    # five fills and the stroke of the swoosh under the wordmark
    assert red.count(RED_FILL) == 6, red.count(RED_FILL)
    assert red.count("A red, cream, and charcoal goose mascot") == 1
    green_svg = (red.replace(RED_FILL, "#184E34")
                 .replace("A red, cream, and charcoal goose mascot",
                          "A green, cream, and charcoal goose mascot"))
    green_path = SIGNS / "marks" / "flappahs_green.svg"
    assert not green_path.exists()

    chain = PX / "profiles" / "materials" / "chain_link_galvanized.json"
    cdata, cindent = _rt(chain)
    assert cdata["transparency"] == {"opacity": 1.0, "alpha_mode": "scissor"}, cdata["transparency"]
    cdata["transparency"]["alpha_mode"] = "blend_texture"

    test = PX / "tests" / "test_chain_link.py"
    t = test.read_bytes().decode("utf-8")
    old = ('''def test_the_fabric_is_a_scissor_cutout_mostly_open():
    g = mg.MaterialGrammar.load(_PROFILE)
    assert g.kind == "chain_link" and g.transparency["alpha_mode"] == "scissor"
''')
    new = ('''def test_the_fabric_is_a_cutout_that_blends_mostly_open():
    """0.60.0: the cutout alpha is unchanged, and the consumer BLENDS it
    rather than testing it. Tested at 0.5 the far fabric vanished, its mips
    being about a quarter wire (cold run 9183); blended, it keeps a faint
    screen at 20 m and along a 16.8 m run (rendered on 9184's walk copy)."""
    g = mg.MaterialGrammar.load(_PROFILE)
    assert g.kind == "chain_link" and g.transparency["alpha_mode"] == "blend_texture"
''')
    assert b"\r\n" not in test.read_bytes() and t.count(old) == 1
    t = t.replace(old, new)

    ftest = PX / "tests" / "test_flappahs_signs.py"
    ft = ftest.read_bytes().decode("utf-8")
    assert b"\r\n" not in ftest.read_bytes()
    ft = ft.rstrip("\n") + '''


def _zoo_colourway_0():
    """Zoo's `price_pylon_forms.COLOURWAYS[0]` -- (field, rule, ink) -- read
    as source from a Zoo checkout above this repo, or None."""
    import ast
    for parent in Path(__file__).resolve().parents:
        src = parent / "zoo" / "zoo_keeper" / "core" / "price_pylon_forms.py"
        if src.is_file():
            tree = ast.parse(src.read_text(encoding="utf-8"))
            for n in tree.body:
                if isinstance(n, ast.Assign) and any(getattr(t, "id", None) == "COLOURWAYS"
                                                     for t in n.targets):
                    return ast.literal_eval(n.value)[0]
    return None


@pytest.mark.parametrize("profile", PROFILES, ids=lambda p: p.stem)
def test_the_brand_is_cream_on_green_as_zoo_draws_it(profile):
    """0.60.0. The walker, 2026-10-06: "We can do the green and cream".
    The band draws in the colours Zoo gives the pylon, the pumps and the door
    box, read from Zoo rather than copied, so the two cannot drift."""
    cw = _zoo_colourway_0()
    if cw is None:
        pytest.skip("no Zoo checkout above this repo")
    hexed = ["#%02x%02x%02x" % tuple(c) for c in cw]
    data = json.loads(profile.read_text(encoding="utf-8"))
    flap = [s for s in data["signs"] if s.get("slug") == "flappahs"]
    if not flap:
        pytest.skip(f"{profile.stem} names no FLAPPAHS")
    s = flap[0]
    assert [s["panel"].lower(), s["border"].lower(), s["text_color"].lower()] == hexed, s
    assert (SIGNS / s["mark"]).is_file()
'''
    for path, data, indent in staged:
        _write(path, data, indent)
        print("patched", path.relative_to(ROOT))
    green_path.write_bytes(green_svg.encode("utf-8"))
    print("wrote", green_path.relative_to(ROOT))
    _write(chain, cdata, cindent)
    print("patched", chain.relative_to(ROOT))
    test.write_bytes(t.encode("utf-8"))
    print("patched", test.relative_to(ROOT))
    ftest.write_bytes(ft.encode("utf-8"))
    print("patched", ftest.relative_to(ROOT))


if __name__ == "__main__":
    main()
