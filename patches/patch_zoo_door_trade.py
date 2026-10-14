"""Zoo 1.112.0: a door under its building's band says the trade (the walker's walk of cold runs 9305-9307,
2026-10-14, finding 4: the factory's `docs/findings/walk_2026-10-14/`).

The pharmacy's street band and its door box both read DOC'S DISCOUNT DRUGS: 1.79.0 dressed the door in the pack
Level Factory dealt the building's band (the walker's option A of 2026-10-06). The walker, seeing the two stack on a
one-storey front -- "double sign here looks...redundant" -- chose the trade for the door.

  zoo_keeper/core/storefront_names.py   `TRADE`, `trade_for`; `all_strings` carries the trade words
  zoo_keeper/recipes/sign_box.py        a pack handed in means a band names the shop: the door paints its trade
  tests/test_door_wears_the_band.py     rewritten whole from `zoo_door_trade/test_door_wears_the_band.py.txt`: its
                                        third check read 1.79.0's worn pack
  tests/test_storefront_names.py        `test_a_door_under_a_band_says_its_trade`, appended

Every file's sha16 pinned and every anchor asserted once, nothing written until all matched. CHANGELOG and VERSION
from `zoo_door_trade/CHANGELOG_1.112.0.md`; `--results-pending` leaves the RESULT_ keys to `--fill`.

Read before it was written, in this session: `sign_box.py` whole (the pack paths, the painted face, `build_art`);
`storefront_names.py` (the module docstring, `KINDS`, `CIVIC`, `sign_for`, `all_strings`, `voice_for`);
`tests/test_door_wears_the_band.py` whole; `tests/test_storefront_names.py` (its imports,
`test_every_name_sets_on_every_sign_the_library_derives`, its last test); `tests/test_door_box_fits_its_art.py`'s
Blender check with a pack, run inside Blender after. Every file LF.

    python patches/patch_zoo_door_trade.py --results-pending
    (python -m pytest -q tests in zoo; the Blender checks)
    python patches/patch_zoo_door_trade.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_door_trade"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt", "RESULT_BLENDER": "result_blender.txt"}
VERSION_WAS, VERSION = b"1.111.0", b"1.112.0"
CHANGELOG_HEAD = "## [1.111.0] - a desk's stock faces its sitter, and a shop's room glows under its goods"
SHA = {"zoo_keeper/core/storefront_names.py": "43b30cecc14c6cd0",
       "zoo_keeper/recipes/sign_box.py": "d90968b8081bd936",
       "tests/test_door_wears_the_band.py": "e7873aef8dd3de0f",
       "tests/test_storefront_names.py": "ec2054f225ca63dc"}
WHOLE = {"tests/test_door_wears_the_band.py": "test_door_wears_the_band.py.txt"}

TRADE = '''#: WHAT A DOOR SAYS UNDER ITS BAND (1.112.0). Where Level Factory hangs a street band naming the shop, the door box
#: said the same name again -- 1.79.0's one name on both signs, the walker's option A of 2026-10-06 -- and on a
#: one-storey front the two stack. The walker, at cold run 9305's pharmacy: "double sign here looks...redundant",
#: and chose the trade for the door. A civic building's words are its trade already; a kind with no word here, and a
#: building of no kind, says OPEN.
TRADE = {"club": "OPEN", "gas": "OPEN 24 HOURS", "pizza": "PIZZA", "deli": "DELI", "pawn": "PAWN", "bank": "BANK",
         "pharmacy": "PHARMACY", "clinic": "CLINIC", "market": "GROCERY", "card": "CARDS", "video": "VIDEO",
         "brewery": "BREWERY", "casino": "CASINO", "funeral": "FUNERAL HOME", "country": "CLUBHOUSE"}


def trade_for(business):
    """``{kind, text, colours}`` for the sign over a door whose building's band names it (1.112.0): the trade, in
    the colours `sign_for` gives the name."""
    said = sign_for(business)
    if said["kind"] in CIVIC:
        return said
    return {"kind": said["kind"], "text": TRADE.get(said["kind"], "OPEN"), "colours": said["colours"]}


def all_strings():
    out = []
    for _kind, _m, names in KINDS:
        out += list(names or ())
    return out + sorted(set(TRADE.values()) | {"OPEN"})
'''

EDITS = {
    "zoo_keeper/core/storefront_names.py": [
        ("def all_strings():\n"
         "    out = []\n"
         "    for _kind, _m, names in KINDS:\n"
         "        out += list(names or ())\n"
         "    return out\n",
         TRADE),
    ],
    "zoo_keeper/recipes/sign_box.py": [
        ("    face_t = 0.02\n"
         "    pack = None\n"
         "    if plan.get(\"sign_pack\"):\n"
         "        # 1.79.0: the business Level Factory dealt this building -- the pack\n"
         "        # its street band wears -- so the door and the band are one name\n"
         "        from ..core import skins as skinlib\n"
         "        pack = skinlib.load_pack(str(plan[\"sign_pack\"]))\n"
         "    skins_dir, skin_theme = materials.get_skin_library()\n"
         "    if pack is None and skins_dir:\n",
         "    face_t = 0.02\n"
         "    pack = None\n"
         "    # A BAND THAT NAMES THE SHOP LEAVES THE DOOR ITS TRADE (1.112.0). 1.79.0\n"
         "    # dressed the door in the pack Level Factory dealt the building's street\n"
         "    # band, so the two said one name, the walker's option A of 2026-10-06;\n"
         "    # on a one-storey front they stacked, and the walker chose the trade for\n"
         "    # the door: \"double sign here looks...redundant\". A pack handed in is\n"
         "    # the sign that a band names the shop; the door paints its trade below.\n"
         "    banded = bool(plan.get(\"sign_pack\"))\n"
         "    skins_dir, skin_theme = materials.get_skin_library()\n"
         "    if not banded and skins_dir:\n"),
        ("        said = SN.sign_for(plan.get(\"business\") or plan.get(\"anchor_id\", \"\"))\n",
         "        # under a band, its trade (1.112.0): `trade_for` keeps the name's colours\n"
         "        said = (SN.trade_for if banded else SN.sign_for)(plan.get(\"business\") or plan.get(\"anchor_id\", \"\"))\n"),
    ],
    "tests/test_storefront_names.py": [
        ("        assert doc[\"samplers\"][doc[\"textures\"][ti][\"sampler\"]][\"magFilter\"] == 9729, face[\"name\"]\n",
         "        assert doc[\"samplers\"][doc[\"textures\"][ti][\"sampler\"]][\"magFilter\"] == 9729, face[\"name\"]\n"
         + (SRC / "test_trade.txt").read_text(encoding="utf-8").rstrip("\n") + "\n"),
    ],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION, (ZOO / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(ZOO / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_1.112.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Zoo 1.112.0: results filled")


def main():
    if FILL:
        return fill()
    vraw = (ZOO / "VERSION").read_bytes()
    assert vraw.strip() == VERSION_WAS, vraw
    entry = (SRC / "CHANGELOG_1.112.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [1.112.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel in SHA:
        p = ZOO / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        if rel in WHOLE:
            text = (SRC / WHOLE[rel]).read_text(encoding="utf-8").replace("\r\n", "\n")
        else:
            text = raw.decode("utf-8").replace("\r\n", "\n")
            for old, new in EDITS[rel]:
                assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
                text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    cl = ZOO / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (ZOO / "VERSION").write_bytes(vraw.replace(VERSION_WAS, VERSION))
    print("Zoo 1.111.0 -> 1.112.0")


if __name__ == "__main__":
    main()
