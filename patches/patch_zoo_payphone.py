"""Zoo 1.88.0: the 1990s coin payphone, redrawn -- three enclosures, one
atlas, one draw (roadmap 210, and the modern low-poly standard's payphone).

1.87.0's payphone was a half-booth of boxes in three materials: no keypad, no
coin slot, no cord, nothing printed (the walker, 2026-10-09: it "doesn't have a
phone or appropriate decals"). `core.payphone_forms` plans it in pure Python --
a booth on a post (the default), a pedestal shroud or a wall unit; a stainless
instrument with twelve keys, a coin slot, a real coin-return recess, the vault
door, the instruction card and the cradle; the handset on an armoured cord --
and the recipe builds it with `_card_atlas.build_art`.

Anchored edits (an anchor matches once; refuses on a miss; nothing is written
until every anchor and every replaced file's hash matched):
- `zoo_keeper/core/card_art.py`: `paint` dispatches `payphone_` tiles.
- `tests/test_coincident_faces.py`: the payphone leaves `RESIDUE` (its 2 pairs
  are 0), and the xfail's species count is read off the table.
Replaced, refused unless the file is the one read (sha256):
- `zoo_keeper/recipes/payphone.py`, `zoo_keeper/genome/species/payphone.json`.
New, refused if present: `zoo_keeper/core/payphone_forms.py`,
`tests/test_payphone.py`.
CHANGELOG and VERSION from `zoo_payphone/CHANGELOG_1.88.0.md`.

    python patch_zoo_payphone.py
    ZOO_ROOT=<copy> python patch_zoo_payphone.py
"""
import hashlib
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_payphone"

CHANGELOG_HEAD = "## [1.87.0] - weighted normals: a bevelled part's faces read flat, and its edges catch the light\n"

EDITS = {
    "zoo_keeper/core/card_art.py": [
        ("""    if kind.startswith("dumpster_"):
        from . import dumpster_forms as DF
        return DF.paint(spec)
""",
         """    if kind.startswith("dumpster_"):
        from . import dumpster_forms as DF
        return DF.paint(spec)
    # THE PAYPHONE (1.88.0): its shroud, header, printed face, stickers and
    # cord are `payphone_forms`' tiles
    if kind.startswith("payphone_"):
        from . import payphone_forms as PPF
        return PPF.paint(spec)
"""),
    ],
    "tests/test_coincident_faces.py": [
        ("""    "payphone": (2, 2, 0, 2, None, 2.4),
""", ""),
        ("""@pytest.mark.xfail(strict=True, reason="59 species still ship coincident "
                                       "faces -- the RESIDUE table above")
""",
         """@pytest.mark.xfail(strict=True, reason="%d species still ship coincident "
                                       "faces -- the RESIDUE table above" % len(RESIDUE))
"""),
        ("""    sign over a door, and `sign_box`'s 6 went with its blank face: 2997.\"\"\"
    total = sum(v[0] for v in RESIDUE.values()) + sum(GATED.values())
    assert total == 2997, total
    exposed = sum(v[3] for v in RESIDUE.values())
    assert exposed == 973, exposed
    assert total + 18 + 6 + 6 == 3027      # 0.96.0's, the ATM's, sign_box's
""",
         """    sign over a door, and `sign_box`'s 6 went with its blank face: 2997.
    1.88.0 redrew the payphone, and its 2 (both exposed) went: 2995.\"\"\"
    total = sum(v[0] for v in RESIDUE.values()) + sum(GATED.values())
    assert total == 2995, total
    exposed = sum(v[3] for v in RESIDUE.values())
    assert exposed == 971, exposed
    assert total + 18 + 6 + 6 + 2 == 3027      # 0.96.0's, the ATM's, sign_box's, the payphone's
"""),
    ],
}

REPLACE = {
    "zoo_keeper/recipes/payphone.py": ("payphone.py",
                                       "3d26d7e3e5da3320e29a2552e00f0af7e435e008778aa4b8ca0ba40381371662"),
    "zoo_keeper/genome/species/payphone.json": ("payphone.json",
                                                "bd5889a731f02aa710711d98293447847d999ce375d5569b100fc5863b340c88"),
}

NEW = {
    "zoo_keeper/core/payphone_forms.py": "payphone_forms.py",
    "tests/test_payphone.py": "test_payphone.py",
}


def _stage(root, edits):
    """{path: bytes}: every file's new content, every anchor matched once,
    endings kept; raises before anything is written."""
    staged = {}
    for rel, pairs in edits.items():
        p = root / rel
        d = p.read_bytes()
        crlf, lf = d.count(b"\r\n"), d.count(b"\n")
        assert crlf in (0, lf), (rel, "mixed endings")
        t = d.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            n = t.count(old)
            assert n == 1, (rel, n, old[:70])
            t = t.replace(old, new)
        staged[p] = (t.replace("\n", "\r\n") if crlf else t).encode("utf-8")
    return staged


def main():
    v = (ZOO / "VERSION").read_bytes().strip()
    assert v == b"1.87.0", repr(v)
    staged = _stage(ZOO, EDITS)
    for rel, (name, sha) in REPLACE.items():
        p = ZOO / rel
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        assert got == sha, (rel, "is not the file this patch read", got)
        staged[p] = (SRC / name).read_bytes()
    for rel, name in NEW.items():
        p = ZOO / rel
        assert not p.exists(), p
        staged[p] = (SRC / name).read_bytes()
    entry = (SRC / "CHANGELOG_1.88.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    cl = ZOO / "CHANGELOG.md"
    data = cl.read_bytes()
    crlf, lf = data.count(b"\r\n"), data.count(b"\n")
    assert crlf in (0, lf), "CHANGELOG.md has mixed endings"
    text = data.decode("utf-8").replace("\r\n", "\n")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:90]
    # Every anchor and hash matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    out = entry + text
    cl.write_bytes((out.replace("\n", "\r\n") if crlf else out).encode("utf-8"))
    vfile = ZOO / "VERSION"
    vfile.write_bytes(vfile.read_bytes().replace(b"1.87.0", b"1.88.0"))
    print("Zoo 1.87.0 -> 1.88.0")


if __name__ == "__main__":
    main()
