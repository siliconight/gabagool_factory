"""Zoo 1.111.0: a desk's stock faces its sitter, and a shop's room glows under its goods (the walker's walk of cold
runs 9305-9307, 2026-10-14, findings 3 and 1: the factory's `docs/findings/walk_2026-10-14/`).

- `core/cubicle_forms.py`: each bay's region carried `pi if out > 0 else 0` as its stock's facing, which
  `_surface_stock.plan_surface` reads as "the person stands at -Y" at 0 -- turning every item to the spine, since the
  surface (and its drawer fronts) stand on the spine's `-out` side. Now `0 if out > 0 else pi`.
- `core/shop_panes.py`: `_room` painted the room into the emission map at its full colour while the goods glowed at
  47 %, so at night the wall outshone the goods. `ROOM_GLOW` (90 of 255) scales the room's emission; `EMISSION`
  stays 2.2.
- Two tests: `test_cubicle_bank.py` (each bay's facing against its own drawer fronts), `test_shop_panes.py` (each
  lit cell's emission under half its paint). Both fail on 1.110.0.

Anchored edits, each asserted exactly once and every file's sha16 pinned, nothing written until all matched.
CHANGELOG and VERSION from `zoo_desk_facing_shop_glow/CHANGELOG_1.111.0.md`; `--results-pending` leaves the RESULT_
keys to `--fill`.

Read before it was written, in this session: `cubicle_forms.py` (the bay loop, 136-182), `recipes/cubicle_bank.py`
(its docstring's "facing that band's sitter", `build_stock`), `recipes/_surface_stock.py` (the module docstring and
`plan_surface`'s, `_place_group`), `bpylayer/prim_mesh.build_stock`; `shop_panes.py` (the colours, `_scale`, `_room`,
`_shelves`, the grocery painter); `tests/test_cubicle_bank.py` (`_library_plan`, `ALL`), `tests/test_shop_panes.py`
(`_cell_sum`, the bytes test, `test_a_shop_glows_brighter_than_a_home`). Every file LF.

    python patches/patch_zoo_desk_facing_shop_glow.py --results-pending
    (python -m pytest -q tests in zoo; the Blender checks)
    python patches/patch_zoo_desk_facing_shop_glow.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_desk_facing_shop_glow"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt", "RESULT_BLENDER": "result_blender.txt"}
VERSION_WAS, VERSION = b"1.110.0", b"1.111.0"
CHANGELOG_HEAD = "## [1.110.0] - a steel fire escape, a storey a slot: `fire_escape`"
SHA = {"zoo_keeper/core/cubicle_forms.py": "9b0a11a79010d1ca",
       "zoo_keeper/core/shop_panes.py": "09a94f92f89bdbfb",
       "tests/test_cubicle_bank.py": "f2c2598c7386301e",
       "tests/test_shop_panes.py": "84d02a447d810731"}

EDITS = {
    "zoo_keeper/core/cubicle_forms.py": [
        ("            regions.append((bx - inner / 2.0, bx + inner / 2.0,\n"
         "                            surf_y - sd / 2.0, surf_y + sd / 2.0, surf_h,\n"
         "                            3.141592653589793 if out > 0 else 0.0, 0.5, ()))\n",
         "            # The stock faces the sitter, who stands where the drawer fronts\n"
         "            # face: the `-out` side. `plan_surface` reads facing 0 as \"they\n"
         "            # stand at -Y\" (1.111.0; this was `pi if out > 0`, every\n"
         "            # computer turned to the spine).\n"
         "            regions.append((bx - inner / 2.0, bx + inner / 2.0,\n"
         "                            surf_y - sd / 2.0, surf_y + sd / 2.0, surf_h,\n"
         "                            0.0 if out > 0 else 3.141592653589793, 0.5, ()))\n"),
    ],
    "zoo_keeper/core/shop_panes.py": [
        ("EMISSION = 2.2\n",
         "EMISSION = 2.2\n"
         "#: How bright the room behind the goods glows, of its paint (1.111.0). At its full colour the wall outshone\n"
         "#: the goods (`_shelves` glows them at 120) and a cool room clipped to white at night: the walker, at the\n"
         "#: corner grocery's glass, \"not sure what I'm looking at\".\n"
         "ROOM_GLOW = 90\n"),
        ("        c.rect(x0, y, x1, y + 1, rgb)\n"
         "        e.rect(x0, y, x1, y + 1, rgb)\n",
         "        c.rect(x0, y, x1, y + 1, rgb)\n"
         "        e.rect(x0, y, x1, y + 1, _scale(rgb, ROOM_GLOW))\n"),
    ],
    "tests/test_cubicle_bank.py": [
        ("\n\nALL = [v for k, v in sorted(globals().items()) if k.startswith(\"test_\")]\n",
         "\n\n" + (SRC / "test_cubicle_facing.txt").read_text(encoding="utf-8").rstrip("\n") + "\n\n\n"
         "ALL = [v for k, v in sorted(globals().items()) if k.startswith(\"test_\")]\n"),
    ],
    "tests/test_shop_panes.py": [
        ("    assert glass and glass[0].data.materials[0].name == \"M_Shop_pane_Face\"\n",
         "    assert glass and glass[0].data.materials[0].name == \"M_Shop_pane_Face\"\n"
         + (SRC / "test_shop_glow.txt").read_text(encoding="utf-8").rstrip("\n") + "\n"),
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
    for path, rel in [(ZOO / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_1.111.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Zoo 1.111.0: results filled")


def main():
    if FILL:
        return fill()
    vraw = (ZOO / "VERSION").read_bytes()
    assert vraw.strip() == VERSION_WAS, vraw
    entry = (SRC / "CHANGELOG_1.111.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [1.111.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel, pairs in EDITS.items():
        p = ZOO / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
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
    print("Zoo 1.110.0 -> 1.111.0")


if __name__ == "__main__":
    main()
