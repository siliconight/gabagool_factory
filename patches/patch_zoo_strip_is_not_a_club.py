"""Zoo 1.76.0: a retail strip is not a strip club.

`docs/findings/two_names_one_building/` (2026-10-06): `strip_retail_a01` and
`a02` -- a retail strip -- said THE WOODER HOLE over the door. The club kind
matched the WORD `strip`; Deli Counter decides a strip club by
`level_design._strip_club_building`, `"strip_club" in` the id, and furnishes
it (and gives it a neon) by that rule only. The door now follows the same
rule, so the neon and the door still agree on every club and a retail strip
shows its street number under its retail band.

    python patch_zoo_strip_is_not_a_club.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ZOO = ROOT / "zoo"

EDITS = {
    ZOO / "zoo_keeper/core/storefront_names.py": [
        ('''        if kind == "club":
            return {"kind": kind, "text": CN.name_for(k % len(CN.NAMES)),
''',
         '''        if kind == "club":
            # A strip club by Deli Counter's own rule (`level_design.
            # _strip_club_building`: "strip_club" in the id), not the word
            # `strip` alone. Until 1.76.0 `strip_retail_a01`, a retail strip,
            # said THE WOODER HOLE over its door.
            if "strip_club" not in str(business or "").lower():
                continue
            return {"kind": kind, "text": CN.name_for(k % len(CN.NAMES)),
'''),
    ],
    ZOO / "tests/test_storefront_names.py": [
        ('''    for b in ("convenience_store_a01", "lf_flappahs_001_1 convenience_store"):
        s = SN.sign_for(b)
        assert s["kind"] == "gas" and s["text"] == PY.STORE, (b, s)
''',
         '''    for b in ("convenience_store_a01", "lf_flappahs_001_1 convenience_store"):
        s = SN.sign_for(b)
        assert s["kind"] == "gas" and s["text"] == PY.STORE, (b, s)


def test_a_retail_strip_is_not_a_strip_club():
    """1.76.0: the word `strip` alone made `strip_retail_a01`'s door say a
    club's name, THE WOODER HOLE. Deli Counter's rule is `strip_club` in
    the id, and the door follows it."""
    for b in ("strip_retail_a01", "strip_retail_a02"):
        assert SN.sign_for(b)["kind"] != "club", b
    for b in ("strip_club_a01", "lf_club_block_014_7 strip_club"):
        assert SN.sign_for(b)["kind"] == "club", b
'''),
    ],
}


def main():
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        crlf = data.count(b"\r\n")
        assert crlf in (0, data.count(b"\n")), f"{path}: mixed line endings"
        eol = "\r\n" if crlf else "\n"
        text = data.decode("utf-8")
        for old, new in pairs:
            old, new = old.replace("\n", eol), new.replace("\n", eol)
            n = text.count(old)
            assert n == 1, f"{path}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        staged[path] = text
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
