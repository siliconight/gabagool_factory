"""Deli Counter 0.219.0: the corner blocks hang an awning over the shop -- Zoo's `shop_awning` (factory roadmap 241,
the corner shop).

The comps: "Corners carry the life. The corner building has the shop at grade (lit, awning), homes above." 0.218.0
built the shop; Zoo 1.108.0 draws the awning; this hangs one over each corner block's storefront in its shop's
colour.

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  shop_awning.py          NEW (`dc_shop_awning/shop_awning.py.txt`): where the awning hangs, pure
  spec_types.py           `LevelSpec.awning`, a form or None
  schema/level.schema.json  the level may carry `awning`, a string or null (0.218.0's lesson: a spec field the
                          schema does not carry fails the build's own gate)
  deli_counter.py         imports `shop_awning`; a facade calls `_awning` after `_stoop`; `_awning` writes the
                          `prop` slot and its visual greybox box, no collider
  presets.py              `empty_midrise(..., awning=None)`, declaring canvas when it hangs one; each
                          `EMPTY_CORNERS` row its shop's colour
  build_freshness.py      `shop_awning.py` among the sources baked into a shell
  material_kind.py        canvas, a skin kind already: the suite's `test_every_spec_material_has_a_kind` found the
                          row missing after the first build (a spec material with no kind), and it was added to
                          the applied tree by this same anchored edit; the patch from 0.218.0 was then rerun on a
                          clean export and every file it writes compared byte for byte
  specs/gs_cornershop_a..d.json   regenerated from the patched presets; the nine mid-rises asserted unchanged;
                          `specs/CATALOG.md` regenerated (`catalog.py`)
  test_corner_awning.py   NEW (`dc_shop_awning/test_corner_awning.py.txt`)
CHANGELOG and VERSION from `dc_shop_awning/CHANGELOG_0.219.0.md`; `--results-pending` leaves RESULT_ keys to
`--fill`. The shells are built after (`build.py --all`, since `presets.py` moves).

Read before it was written, in this session: `stoop.py` (the pattern: a pure plan, the building's frame, the
terrace's 2.0 m frontage), `_stoop` and its call in the facade build, `_box`'s use for a visual prop, the stoop
railing's slot (`role: prop`, `species`, `form`, `kit_axis: material`); `LevelSpec.stoop` and the schema's
`stoop` (the top level forbids additional properties); `_opening_to_hole`'s z (the floor's walking surface
`floor_thick / 2` over z = 0); `empty_midrise` as 0.218.0 left it and `EMPTY_CORNERS`; the schema's acoustic
names (`Curtain`); `skin_style.style_for`; `build_freshness.GEOMETRY_SOURCES`. Every file LF.

    python patches/patch_dc_shop_awning.py --results-pending
    (build.py --all; python -m pytest -q in deli_counter)
    python patches/patch_dc_shop_awning.py --fill
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_shop_awning"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_BUILT": "result_built.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Deli Counter 0.218.0", b"Deli Counter 0.219.0"
CHANGELOG_HEAD = "## [0.218.0] - the corner blocks: a mid-rise Empty whose ground-floor front is a shop\n"
SHA = {"spec_types.py": "4524b8843293b446", "deli_counter.py": "0c4f3fc552692cf7", "presets.py": "406d1f7fa9b2234a",
       "build_freshness.py": "cddca308d9703c55", "schema/level.schema.json": "3813451ed6015f15",
       "material_kind.py": "d45d268c2e3b301a"}
NEW = {"shop_awning.py": "shop_awning.py.txt", "test_corner_awning.py": "test_corner_awning.py.txt"}

SPEC = [
    ("    # window with it (factory roadmap 240).\n"
     "    stoop: Optional[dict] = None\n",
     "    # window with it (factory roadmap 240).\n"
     "    stoop: Optional[dict] = None\n"
     "    # A CORNER SHOP'S AWNING (0.219.0, factory roadmap 241): Zoo's `shop_awning`\n"
     "    # form (`shop_awning.FORMS`, the shop's canvas colour), hung over the\n"
     "    # storefront where `shop_awning.plan` says; None, no awning.\n"
     "    awning: Optional[str] = None\n"),
]

SCHEMA = [
    ("      \"required\": [\"risers\", \"tread\", \"landing\", \"width\"],\n"
     "      \"additionalProperties\": false\n"
     "    },\n"
     "    \"audit_accept\": {\n",
     "      \"required\": [\"risers\", \"tread\", \"landing\", \"width\"],\n"
     "      \"additionalProperties\": false\n"
     "    },\n"
     "    \"awning\": {\n"
     "      \"type\": [\"string\", \"null\"],\n"
     "      \"description\": \"a corner block's awning: Zoo's shop_awning form, hung over the storefront "
     "(shop_awning.plan, 0.219.0)\"\n"
     "    },\n"
     "    \"audit_accept\": {\n"),
]

AWNING = '''
    def _awning(self):
        """A CORNER SHOP'S AWNING (0.219.0, factory roadmap 241; `shop_awning.py`):
        Zoo's `shop_awning` (>= 1.108.0) over the storefront, recorded as a
        `prop` slot in canvas whose form is the shop's colour, its greybox a
        visual box. No collision: it hangs over a frontage nobody walks at its
        height, and Level Factory reads an Empty's street edge off its
        colliders. Nothing when the spec asks for none."""
        p = shop_awning.plan(self.s)
        if p is None:
            return
        mat = "canvas"
        style = skin_style.style_for(mat, self._mat_style,
                                     self.s.default_material)
        c, size = p["centre"], p["size"]
        self._box("shop_awning", c, size, self.VISUAL, role="prop")
        self.slots.append({
            "slot_id": "shop_awning", "role": "prop", "size_mod": "full",
            "style": style, "material": mat, "species": "shop_awning",
            "stock": None, "variant": 0, "form": p["form"],
            "current_ref": "prop_greybox_01", "kit_axis": "material",
            "wall": None, "story": None, "facing": None,
            "transform": {"translation": [round(c[0], 4), round(c[1], 4),
                                          round(c[2], 4)],
                          "rot_y": 0.0, "scale": [1.0, 1.0, 1.0]},
            "fit": {"dims": [round(v, 4) for v in size],
                    "pivot": "center", "openings": [], "collision": "none"},
        })
'''

DELI = [
    ("import empty_panes\nimport stoop\n",
     "import empty_panes\nimport shop_awning\nimport stoop\n"),
    ("            self._stoop()\n"
     "            # The roof slot, as a building records it, so Zoo dresses the\n",
     "            self._stoop()\n"
     "            # A CORNER SHOP'S AWNING (0.219.0): over its storefront, a\n"
     "            # `prop` slot Zoo dresses; nothing on any other Empty.\n"
     "            self._awning()\n"
     "            # The roof slot, as a building records it, so Zoo dresses the\n"),
    ("            self._record_surface(r[\"name\"] + \"_col\", iron)\n"
     "\n"
     "    # ----------------------------------------------------------------------\n"
     "    # KITBASHING  --  import external models and place instances\n",
     "            self._record_surface(r[\"name\"] + \"_col\", iron)\n"
     + AWNING +
     "\n"
     "    # ----------------------------------------------------------------------\n"
     "    # KITBASHING  --  import external models and place instances\n"),
]

PRESETS = [
    ("                  security_door: bool = False, shop: str = None) -> dict:\n",
     "                  security_door: bool = False, shop: str = None,\n"
     "                  awning: str = None) -> dict:\n"),
    ("    as the rowhome Empty's does.\"\"\"\n",
     "    as the rowhome Empty's does. `awning` (0.219.0) hangs Zoo's\n"
     "    `shop_awning` in that form over the storefront (`shop_awning.plan`),\n"
     "    in canvas the palette then declares.\"\"\"\n"),
    ("    if security_door:\n"
     "        s[\"security_door\"] = True\n"
     "    return s\n",
     "    if security_door:\n"
     "        s[\"security_door\"] = True\n"
     "    # and its awning (0.219.0), in canvas, which the palette then declares\n"
     "    if awning:\n"
     "        s[\"awning\"] = awning\n"
     "        s[\"materials\"].append({\"id\": \"canvas\", \"acoustic\": \"Curtain\",\n"
     "                               \"absorption\": 0.5, \"damping\": 0.4})\n"
     "    return s\n"),
    ("EMPTY_CORNERS = {\n"
     "    \"gs_cornershop_a\": dict(width=15.0, floors=6, wall=\"brick\", lobby=0.0, cornice=1.0,\n"
     "                            seed=1941, door_finish=\"black\", security_door=True, shop=\"shop_deli\"),\n"
     "    \"gs_cornershop_b\": dict(width=18.0, floors=8, wall=\"brick_orange\", lobby=0.0, cornice=1.2,\n"
     "                            seed=1942, door_finish=\"oxblood\", shop=\"shop_bar\"),\n"
     "    \"gs_cornershop_c\": dict(width=12.0, floors=5, wall=\"brick_brown\", lobby=0.0, cornice=1.0,\n"
     "                            seed=1943, door_finish=\"white\", shop=\"shop_laundry\"),\n"
     "    \"gs_cornershop_d\": dict(width=16.5, floors=7, wall=\"stone_ext\", lobby=0.0, cornice=1.4,\n"
     "                            seed=1944, door_finish=\"green\", security_door=True, shop=\"shop_grocery\"),\n"
     "}\n",
     "#: AND THEIR AWNINGS (0.219.0): each in its shop's canvas, a deli's red, a\n"
     "#: bar's black, a laundromat's navy and a grocery's green.\n"
     "EMPTY_CORNERS = {\n"
     "    \"gs_cornershop_a\": dict(width=15.0, floors=6, wall=\"brick\", lobby=0.0, cornice=1.0,\n"
     "                            seed=1941, door_finish=\"black\", security_door=True, shop=\"shop_deli\",\n"
     "                            awning=\"shed_red\"),\n"
     "    \"gs_cornershop_b\": dict(width=18.0, floors=8, wall=\"brick_orange\", lobby=0.0, cornice=1.2,\n"
     "                            seed=1942, door_finish=\"oxblood\", shop=\"shop_bar\", awning=\"shed_black\"),\n"
     "    \"gs_cornershop_c\": dict(width=12.0, floors=5, wall=\"brick_brown\", lobby=0.0, cornice=1.0,\n"
     "                            seed=1943, door_finish=\"white\", shop=\"shop_laundry\", awning=\"shed_navy\"),\n"
     "    \"gs_cornershop_d\": dict(width=16.5, floors=7, wall=\"stone_ext\", lobby=0.0, cornice=1.4,\n"
     "                            seed=1944, door_finish=\"green\", security_door=True, shop=\"shop_grocery\",\n"
     "                            awning=\"shed_green\"),\n"
     "}\n"),
]

FRESH = [
    ("    \"empty_panes.py\",\n)\n",
     "    \"empty_panes.py\",\n"
     "    # where a corner block's awning hangs, a slot of its shell (0.219.0)\n"
     "    \"shop_awning.py\",\n)\n"),
]

KINDS = [
    ("    \"brick_orange\": \"brick_orange\",\n"
     "    \"carpet\": \"carpet\",\n",
     "    \"brick_orange\": \"brick_orange\",\n"
     "    \"canvas\": \"canvas\",\n"
     "    \"carpet\": \"carpet\",\n"),
]

EDITS = {"spec_types.py": SPEC, "deli_counter.py": DELI, "presets.py": PRESETS, "build_freshness.py": FRESH,
         "material_kind.py": KINDS}

REGEN = (
    "import json, sys\n"
    "sys.path.insert(0, '.')\n"
    "import presets\n"
    "for n, a in sorted(presets.EMPTY_CORNERS.items()):\n"
    "    p = 'specs/%s.json' % n\n"
    "    open(p, 'wb').write(json.dumps(presets.empty_midrise(name=n, **a), indent=2).encode('utf-8'))\n"
    "for t in (presets.EMPTY_MIDRISES, presets.EMPTY_MIDRISE_NARROW):\n"
    "    for n, a in sorted(t.items()):\n"
    "        p = 'specs/%s.json' % n\n"
    "        data = json.dumps(presets.empty_midrise(name=n, **a), indent=2).encode('utf-8')\n"
    "        assert open(p, 'rb').read() == data, ('a mid-rise moved', p)\n"
    "print('rewrote', len(presets.EMPTY_CORNERS), 'corner specs; the nine mid-rises unchanged')\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _read(rel):
    raw = (DC / rel).read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def fill():
    assert (DC / "VERSION").read_bytes().strip() == VERSION, (DC / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(DC / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.219.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Deli Counter 0.219.0: results filled")


def main():
    if FILL:
        return fill()
    assert (DC / "VERSION").read_bytes().strip() == VERSION_WAS, (DC / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.219.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.219.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (DC / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, edits in EDITS.items():
        eol, text = _read(rel)
        for old, new in edits:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:60])
            text = text.replace(old, new)
        compile(text, rel, "exec")
        writes[rel] = (text, eol)
    eol_s, schema = _read("schema/level.schema.json")
    for old, new in SCHEMA:
        assert schema.count(old) == 1, ("schema", "anchor", schema.count(old), old[:60])
        schema = schema.replace(old, new)
    assert json.loads(schema)["properties"]["awning"]["type"] == ["string", "null"]
    news = {r: (SRC / s).read_bytes().replace(b"\r\n", b"\n") for r, s in NEW.items()}
    for r, data in news.items():
        compile(data.decode("utf-8"), r, "exec")
    cl = DC / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for rel, (text, eol) in writes.items():
        (DC / rel).write_bytes(text.encode("utf-8").replace(b"\n", eol))
    (DC / "schema/level.schema.json").write_bytes(schema.encode("utf-8").replace(b"\n", eol_s))
    for r, data in news.items():
        (DC / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (DC / "VERSION").write_bytes(VERSION)
    subprocess.run([sys.executable, "-c", REGEN], cwd=DC, check=True)
    subprocess.run([sys.executable, "catalog.py"], cwd=DC, check=True)
    print("Deli Counter 0.218.0 -> 0.219.0")


if __name__ == "__main__":
    main()
