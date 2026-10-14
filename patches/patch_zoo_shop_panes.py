"""Zoo 1.107.0: a corner shop's window, painted -- its own atlas of storefront states (factory roadmap 241).

Step 1 of the factory root's `docs/proposals/CORNER_SHOP.md`: a second painted atlas beside `window_panes`,
landscape cells on a material of their own, worn by a facade window whose `pane` is a shop state.

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  zoo_keeper/recipes/_arch.py   imports `shop_panes`; `PANE_ATLASES` (a state -> its atlas, material and image
                                name); the facade window's painted branch reads them from it, so a window state's
                                material and images keep their names
  zoo_keeper/core/kit.py        a facade window's `pane` is honoured when it is a window state or a shop state
  zoo_keeper/core/shop_panes.py   NEW (`zoo_shop_panes/shop_panes.py.txt`)
  tests/test_shop_panes.py        NEW (`zoo_shop_panes/test_shop_panes.py.txt`)
CHANGELOG and VERSION from `zoo_shop_panes/CHANGELOG_1.107.0.md`; `--results-pending` leaves RESULT_ keys to
`--fill`.

Read before it was written, in this session: `window_panes`' constants, `cell_rect`, `uv_rect`, `frame_uv` and
`face_uv` (the module the new one mirrors); `tests/test_window_panes.py` whole (the test the new one mirrors);
`_arch.build_slab`'s painted-pane branch (1.64.0, 1.66.0) and the module's imports and constants; `kit.py`'s pane
acceptance (1.64.0), `module_stem`'s `_p<state>` and the bucket key carrying `pane`; `dna.resolve_module_plan`
passing `pane` through unfiltered; `materials.image_from_png` (cached by name) and `make_pane_material`; Deli
Counter's `themed_tscn` stem test against its own `empty_panes.STATES`; Lux's emissive binder's `SUFFIXES`; Level
Factory's `test_worldskin_lit_faces.py`. Every file LF.

    python patches/patch_zoo_shop_panes.py --results-pending
    (python -m pytest -q in zoo)
    python patches/patch_zoo_shop_panes.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_shop_panes"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_TESTS": "result_tests.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"1.106.0", b"1.107.0"
CHANGELOG_HEAD = "## [1.106.0] - floaters: one rule for a detail laid on a surface\n"
SHA = {"zoo_keeper/recipes/_arch.py": "314ed389c7108933", "zoo_keeper/core/kit.py": "63b4c67bf6d5596a"}
NEW = {"zoo_keeper/core/shop_panes.py": "shop_panes.py.txt", "tests/test_shop_panes.py": "test_shop_panes.py.txt"}

IMPORT_OLD = "from ..core import arch, doors, partnames, window_panes\n"
IMPORT_NEW = "from ..core import arch, doors, partnames, shop_panes, window_panes\n"

TABLE_OLD = ("FACADE_DOOR_SETBACK = 0.08\n"
             "FACADE_DOOR_THICK = 0.045\n"
             "FACADE_DOOR_COLOR = (0.16, 0.20, 0.28)\n")
TABLE_NEW = (TABLE_OLD +
             "\n"
             "#: A PAINTED PANE'S ATLAS BY ITS STATE (1.107.0): the atlas, its material and\n"
             "#: its images' name. A home's window is `window_panes` (1.64.0); a corner\n"
             "#: shop's front is `shop_panes`, landscape cells on a material of its own.\n"
             "#: The two state sets never meet (`tests/test_shop_panes.py`).\n"
             "PANE_ATLASES = {\n"
             "    **{s: (window_panes, \"M_Window_pane_Face\", \"window_pane\") for s in window_panes.STATES},\n"
             "    **{s: (shop_panes, \"M_Shop_pane_Face\", \"shop_pane\") for s in shop_panes.STATES},\n"
             "}\n")

BRANCH_OLD = ("        state = plan.get(\"pane\")\n"
              "        if glazing_kind == \"glass_facade\" and state in window_panes.STATES:\n")
BRANCH_NEW = ("        state = plan.get(\"pane\")\n"
              "        painted = PANE_ATLASES.get(state)\n"
              "        if glazing_kind == \"glass_facade\" and painted is not None:\n"
              "            panes, material_name, image = painted\n")

UV_OLD = ("                    loop[uv].uv = window_panes.face_uv(\n"
          "                        state, face.normal.y, co.x, co.z, cx, cz, hx, hz)\n")
UV_NEW = ("                    loop[uv].uv = panes.face_uv(\n"
          "                        state, face.normal.y, co.x, co.z, cx, cz, hx, hz)\n")

MAT_OLD = ("            albedo, emission = window_panes.atlas()\n"
           "            pane.data.materials.append(materials.make_pane_material(\n"
           "                \"M_Window_pane_Face\",\n"
           "                materials.image_from_png(\"window_pane_albedo\", albedo.png()),\n"
           "                materials.image_from_png(\"window_pane_emission\", emission.png()),\n"
           "                window_panes.EMISSION, window_panes.ALBEDO))\n")
MAT_NEW = ("            albedo, emission = panes.atlas()\n"
           "            pane.data.materials.append(materials.make_pane_material(\n"
           "                material_name,\n"
           "                materials.image_from_png(f\"{image}_albedo\", albedo.png()),\n"
           "                materials.image_from_png(f\"{image}_emission\", emission.png()),\n"
           "                panes.EMISSION, panes.ALBEDO))\n")

KIT_OLD = ("        # A FACADE WINDOW'S PAINTED STATE (1.64.0, Deli Counter >= 0.179.0)\n"
           "        from zoo_keeper.core import window_panes as _panes\n"
           "        pane = (str(s[\"pane\"]) if typ == \"window\" and s.get(\"glazing\") == \"facade\"\n"
           "                and s.get(\"pane\") in _panes.STATES else None)\n")
KIT_NEW = ("        # A FACADE WINDOW'S PAINTED STATE (1.64.0, Deli Counter >= 0.179.0):\n"
           "        # a home's sash, or a corner shop's front (1.107.0, `shop_panes`)\n"
           "        from zoo_keeper.core import shop_panes as _shop, window_panes as _panes\n"
           "        pane = (str(s[\"pane\"]) if typ == \"window\" and s.get(\"glazing\") == \"facade\"\n"
           "                and (s.get(\"pane\") in _panes.STATES\n"
           "                     or s.get(\"pane\") in _shop.STATES) else None)\n")

EDITS = {
    "zoo_keeper/recipes/_arch.py": [(IMPORT_OLD, IMPORT_NEW), (TABLE_OLD, TABLE_NEW), (BRANCH_OLD, BRANCH_NEW),
                                    (UV_OLD, UV_NEW), (MAT_OLD, MAT_NEW)],
    "zoo_keeper/core/kit.py": [(KIT_OLD, KIT_NEW)],
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
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(ZOO / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_1.107.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Zoo 1.107.0: results filled")


def main():
    if FILL:
        return fill()
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION_WAS, (ZOO / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_1.107.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [1.107.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (ZOO / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, edits in EDITS.items():
        raw = (ZOO / rel).read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:60])
            text = text.replace(old, new)
        compile(text, rel, "exec")
        writes[rel] = (text, eol)
    news = {r: (SRC / s).read_bytes().replace(b"\r\n", b"\n") for r, s in NEW.items()}
    for r, data in news.items():
        compile(data.decode("utf-8"), r, "exec")
    cl = ZOO / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for rel, (body, e) in writes.items():
        (ZOO / rel).write_bytes(body.encode("utf-8").replace(b"\n", e))
    for r, data in news.items():
        (ZOO / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (ZOO / "VERSION").write_bytes(VERSION)
    print("Zoo 1.106.0 -> 1.107.0")


if __name__ == "__main__":
    main()
