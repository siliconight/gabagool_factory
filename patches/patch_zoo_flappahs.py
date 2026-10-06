"""Zoo 1.75.0: the brand is FLAPPAHS, and a convenience store's door says so.

The walker, 2026-10-06: "Flappahs store always Flappahs" -- and wrote it
"flappahs". Pixelcoat's sign profile and mark already spell it FLAPPAHS
(`profiles/signs/delco.json`, `marks/flappahs_red.svg`); Zoo spelled it
FLAPPHAS, in the one constant every Flappahs surface reads
(`price_pylon_forms.STORE`: pylon, pumps, coffee island, slush machine, the
door sign), so a station could wear FLAPPAHS on its fascia under a FLAPPHAS
pylon. Every Zoo occurrence outside the changelog is respelled; both are eight
letters, so nothing sized from the string moves.

And the door. `storefront_names` reads a building's kind from whole words of
its business string, and the gas kind's words are gas / fuel / gs / stop. The
Flappahs store became `convenience_store_a01` (Deli Counter 0.188.0), and a
generated one reads `<level> convenience_store`: neither carries any of them,
so its door would have shown a street number. `convenience` joins the kind.

    python patch_zoo_flappahs.py
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
ZOO = ROOT / "zoo"

KIND_OLD = '''    ("gas", ("gas", "fuel", "gs", "stop"), (PY.STORE,)),
'''
KIND_NEW = '''    # `convenience` (1.75.0): the Flappahs store, `convenience_store_a01` or a
    # generated `<level> convenience_store`, carries none of the other words.
    ("gas", ("gas", "fuel", "gs", "stop", "convenience"), (PY.STORE,)),
'''

TEST_ANCHOR = '''def test_a_gas_station_says_flappahs_in_the_pylon_s_colours():
    s = SN.sign_for("gas_station_a02")
    assert s["text"] == PY.STORE and s["colours"] == PY.COLOURWAYS[0]
'''
TEST_NEW = TEST_ANCHOR + '''

def test_the_brand_is_spelled_the_walkers_way():
    """1.75.0: FLAPPAHS, as the walker writes it and Pixelcoat's sign spells
    it. Zoo had FLAPPHAS."""
    assert PY.STORE == "FLAPPAHS"


def test_a_convenience_store_is_a_flappahs():
    """1.75.0: the Flappahs store is always Flappahs (the walker,
    2026-10-06). The library's is `convenience_store_a01`; a generated one
    reads `<level> convenience_store` -- neither carries gas, fuel, gs or
    stop, so before `convenience` joined the kind its door showed a street
    number."""
    for b in ("convenience_store_a01", "lf_flappahs_001_1 convenience_store"):
        s = SN.sign_for(b)
        assert s["kind"] == "gas" and s["text"] == PY.STORE, (b, s)
'''


def main():
    staged = {}
    # the spelling, everywhere outside the changelog
    for path in sorted(ZOO.rglob("*.py")):
        if ".git" in path.parts:
            continue
        data = path.read_bytes()
        text = data.decode("utf-8")
        if "FLAPPHAS" not in text and "flapphas" not in text:
            continue
        crlf = data.count(b"\r\n")
        assert crlf in (0, data.count(b"\n")), f"{path}: mixed line endings"
        staged[path] = text.replace("FLAPPHAS", "FLAPPAHS").replace("flapphas", "flappahs")
    assert not [p for p, t in staged.items() if re.search("flapphas", t, re.I)]
    sn = ZOO / "zoo_keeper/core/storefront_names.py"
    t = staged.get(sn) or sn.read_bytes().decode("utf-8")
    assert t.count(KIND_OLD) == 1, "the gas kind"
    staged[sn] = t.replace(KIND_OLD, KIND_NEW)
    tp = ZOO / "tests/test_storefront_names.py"
    t = staged.get(tp) or tp.read_bytes().decode("utf-8")
    assert t.count(TEST_ANCHOR) == 1, "the flappahs test, respelled"
    staged[tp] = t.replace(TEST_ANCHOR, TEST_NEW)
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
