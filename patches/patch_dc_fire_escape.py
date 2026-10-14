"""Deli Counter 0.220.0: a walk-up stands a fire escape on its front, a storey a slot -- Zoo's `fire_escape`
(factory roadmaps 156 and 241; the factory's `docs/proposals/FIRE_ESCAPE.md`, step 2).

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  fire_escape_stack.py       NEW (`dc_fire_escape/fire_escape_stack.py.txt`): where each storey stands, pure
  spec_types.py              `LevelSpec.fire_escape_stack`, a side or None
  schema/level.schema.json   the level may carry `fire_escape_stack`, "front" or null (0.218.0's lesson)
  deli_counter.py            imports `fire_escape_stack`; a facade calls `_fire_escape_stack` after `_awning`; it
                             writes a `prop` slot a storey and its visual greybox box, no collider
  presets.py                 `empty_midrise(..., fire_escape=None)`: by the walk-up rule unless told; a block that
                             stands one declares `metal_painted`
  build_freshness.py         `fire_escape_stack.py` among the sources baked into a shell
  specs/gs_midrise_{a,b,g,h,i}.json   regenerated from the patched presets; every other mid-rise and corner block
                             asserted unchanged; `specs/CATALOG.md` regenerated (`catalog.py`)
  test_walkup_fire_escape.py NEW (`dc_fire_escape/test_walkup_fire_escape.py.txt`)
CHANGELOG and VERSION from `dc_fire_escape/CHANGELOG_0.220.0.md`; `--results-pending` leaves RESULT_ keys to `--fill`.
The shells are built after (`build.py --all`, since `presets.py` moves).

Read before it was written, in this session: `shop_awning.py` (the pattern: a pure plan in the building's frame),
`_awning` and its call in the facade build, the stoop railing's `metal_painted` slot and its palette entry,
`presets.empty_midrise` whole (3.1 m storeys, bays about 3.2 m, the door bay nearest `lobby`, windows 1.1 m on a
0.85 m sill), `EMPTY_MIDRISES`, `EMPTY_MIDRISE_NARROW` and `EMPTY_CORNERS`, `_opening_to_hole` (storey s's walking
surface at s * story_height + floor_thick / 2), `Opening.pos` and `.tag`, `LevelSpec.n_stories`, the schema's
`awning` entry, `build_freshness.GEOMETRY_SOURCES`, `material_kind` (`metal_painted` a kind already),
`test_corner_awning.py` (the tests this follows), and Zoo 1.110.0's `fire_escape_forms` (its numbers). Every file LF.

    python patches/patch_dc_fire_escape.py --results-pending
    (python -m pytest -q in deli_counter; then python build.py --all --blender C:/blender/blender.exe)
    python patches/patch_dc_fire_escape.py --fill
"""
import hashlib
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_fire_escape"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_FAILING": "result_failing.txt", "RESULT_SUITE": "result_suite.txt",
           "RESULT_BUILD": "result_build.txt"}
VERSION_WAS, VERSION = b"Deli Counter 0.219.0", b"Deli Counter 0.220.0"
CHANGELOG_HEAD = "## [0.219.0] - the corner blocks hang an awning over the shop\n"
SHA = {"spec_types.py": "c6279d399b9bf230", "deli_counter.py": "60c898a35d8267d3",
       "presets.py": "a2d89b20f1f23d79", "build_freshness.py": "405e1db633c7991b",
       "schema/level.schema.json": "6da812ac198fce67"}
NEW = {"fire_escape_stack.py": "fire_escape_stack.py.txt",
       "test_walkup_fire_escape.py": "test_walkup_fire_escape.py.txt"}

SPEC = [('''    # A CORNER SHOP'S AWNING (0.219.0, factory roadmap 241): Zoo's `shop_awning`
    # form (`shop_awning.FORMS`, the shop's canvas colour), hung over the
    # storefront where `shop_awning.plan` says; None, no awning.
    awning: Optional[str] = None
''', '''    # A CORNER SHOP'S AWNING (0.219.0, factory roadmap 241): Zoo's `shop_awning`
    # form (`shop_awning.FORMS`, the shop's canvas colour), hung over the
    # storefront where `shop_awning.plan` says; None, no awning.
    awning: Optional[str] = None
    # A WALK-UP'S FIRE ESCAPE (0.220.0, factory roadmaps 156 and 241): Zoo's
    # `fire_escape`, a storey a slot, on that wall ("front") where
    # `fire_escape_stack.plan` says; None, none.
    fire_escape_stack: Optional[str] = None
''')]

SCHEMA = [('''    "awning": {
      "type": ["string", "null"],
      "description": "a corner block's awning: Zoo's shop_awning form, hung over the storefront (shop_awning.plan, 0.219.0)"
    },
''', '''    "awning": {
      "type": ["string", "null"],
      "description": "a corner block's awning: Zoo's shop_awning form, hung over the storefront (shop_awning.plan, 0.219.0)"
    },
    "fire_escape_stack": {
      "type": ["string", "null"],
      "enum": ["front", null],
      "description": "a walk-up's fire escape: Zoo's fire_escape a storey a slot, on that wall (fire_escape_stack.plan, 0.220.0)"
    },
''')]

DELI = [
    ("import shop_awning\nimport stoop\n", "import shop_awning\nimport fire_escape_stack\nimport stoop\n"),
    ('''            # A CORNER SHOP'S AWNING (0.219.0): over its storefront, a
            # `prop` slot Zoo dresses; nothing on any other Empty.
            self._awning()
''', '''            # A CORNER SHOP'S AWNING (0.219.0): over its storefront, a
            # `prop` slot Zoo dresses; nothing on any other Empty.
            self._awning()
            # A WALK-UP'S FIRE ESCAPE (0.220.0): on its front, a `prop` slot
            # a storey Zoo dresses; nothing on any other Empty.
            self._fire_escape_stack()
'''),
    ('''            "fit": {"dims": [round(v, 4) for v in size],
                    "pivot": "center", "openings": [], "collision": "none"},
        })

    # ----------------------------------------------------------------------
    # KITBASHING  --  import external models and place instances
''', '''            "fit": {"dims": [round(v, 4) for v in size],
                    "pivot": "center", "openings": [], "collision": "none"},
        })

    def _fire_escape_stack(self):
        """A WALK-UP'S FIRE ESCAPE (0.220.0, factory roadmaps 156 and 241;
        `fire_escape_stack.py`): Zoo's `fire_escape` (>= 1.110.0) on the
        front, a `prop` slot a storey and one for the drop ladder, in painted
        steel, each greyboxed as a visual box. No collision: the lowest landing
        stands a storey up, and Level Factory reads an Empty's street edge off
        its colliders. Nothing when the spec asks for none."""
        parts = fire_escape_stack.plan(self.s)
        if not parts:
            return
        mat = "metal_painted"
        style = skin_style.style_for(mat, self._mat_style,
                                     self.s.default_material)
        for p in parts:
            c, size = p["centre"], p["size"]
            self._box(p["slot_id"], c, size, self.VISUAL, role="prop")
            self.slots.append({
                "slot_id": p["slot_id"], "role": "prop", "size_mod": "full",
                "style": style, "material": mat, "species": "fire_escape",
                "stock": None, "variant": 0, "form": p["form"],
                "current_ref": "prop_greybox_01", "kit_axis": "material",
                "wall": None, "story": None, "facing": None,
                "transform": {"translation": [round(c[0], 4), round(c[1], 4),
                                              round(c[2], 4)],
                              "rot_y": 0.0, "scale": [1.0, 1.0, 1.0]},
                "fit": {"dims": [round(v, 4) for v in size],
                        "pivot": "center", "openings": [],
                        "collision": "none"},
            })

    # ----------------------------------------------------------------------
    # KITBASHING  --  import external models and place instances
'''),
]

PRESETS = [
    ("import stoop as stoop_geom\n", "import stoop as stoop_geom\nimport fire_escape_stack\n"),
    ("                  awning: str = None) -> dict:\n",
     "                  awning: str = None, fire_escape: bool = None) -> dict:\n"),
    ("    in canvas the palette then declares.\"\"\"\n",
     "    in canvas the palette then declares. A walk-up (0.220.0) stands Zoo's\n"
     "    `fire_escape` on its front, a storey a slot (`fire_escape_stack`):\n"
     "    `fire_escape` None asks the walk-up rule -- `WALKUP_STOREYS` storeys or\n"
     "    fewer and no shop -- and True or False overrides it.\"\"\"\n"),
    ('''    # and its awning (0.219.0), in canvas, which the palette then declares
    if awning:
        s["awning"] = awning
        s["materials"].append({"id": "canvas", "acoustic": "Curtain",
                               "absorption": 0.5, "damping": 0.4})
    return s
''', '''    # and its awning (0.219.0), in canvas, which the palette then declares
    if awning:
        s["awning"] = awning
        s["materials"].append({"id": "canvas", "acoustic": "Curtain",
                               "absorption": 0.5, "damping": 0.4})
    # and a walk-up's fire escape (0.220.0), in painted steel, which the
    # palette then declares
    if fire_escape is None:
        fire_escape = (int(floors) <= fire_escape_stack.WALKUP_STOREYS
                       and not shop)
    if fire_escape:
        s["fire_escape_stack"] = "front"
        if not any(m["id"] == "metal_painted" for m in s["materials"]):
            s["materials"].append({"id": "metal_painted", "acoustic": "Metal",
                                   "absorption": 0.25, "damping": 0.2})
    return s
'''),
]

FRESH = [('''    # where a corner block's awning hangs, a slot of its shell (0.219.0)
    "shop_awning.py",
)
''', '''    # where a corner block's awning hangs, a slot of its shell (0.219.0)
    "shop_awning.py",
    # where a walk-up's fire escape stands, a storey a slot (0.220.0)
    "fire_escape_stack.py",
)
''')]

EDITS = {"spec_types.py": SPEC, "schema/level.schema.json": SCHEMA, "deli_counter.py": DELI,
         "presets.py": PRESETS, "build_freshness.py": FRESH}

REGEN = (
    "import json, sys\n"
    "sys.path.insert(0, '.')\n"
    "import presets, fire_escape_stack\n"
    "rows = {}\n"
    "for t in (presets.EMPTY_MIDRISES, presets.EMPTY_MIDRISE_NARROW, presets.EMPTY_CORNERS):\n"
    "    rows.update(t)\n"
    "wrote = []\n"
    "for n, a in sorted(rows.items()):\n"
    "    p = 'specs/%s.json' % n\n"
    "    data = json.dumps(presets.empty_midrise(name=n, **a), indent=2).encode('utf-8')\n"
    "    if a['floors'] <= fire_escape_stack.WALKUP_STOREYS and not a.get('shop'):\n"
    "        open(p, 'wb').write(data)\n"
    "        wrote.append(n)\n"
    "    else:\n"
    "        assert open(p, 'rb').read() == data, ('a spec moved', p)\n"
    "print('rewrote', wrote, '; the other', len(rows) - len(wrote), 'unchanged')\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (DC / "VERSION").read_bytes().strip() == VERSION, (DC / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(DC / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.220.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Deli Counter 0.220.0: results filled")


def main():
    if FILL:
        return fill()
    assert (DC / "VERSION").read_bytes().strip() == VERSION_WAS, (DC / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.220.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.220.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (DC / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, edits in EDITS.items():
        raw = (DC / rel).read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:60])
            text = text.replace(old, new)
        if rel.endswith(".py"):
            compile(text, rel, "exec")
        writes[rel] = (text, eol)
    import json
    json.loads(writes["schema/level.schema.json"][0])
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
    for r, data in news.items():
        (DC / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (DC / "VERSION").write_bytes(VERSION)
    subprocess.run([sys.executable, "-c", REGEN], cwd=DC, check=True)
    subprocess.run([sys.executable, "catalog.py"], cwd=DC, check=True)
    print("Deli Counter 0.219.0 -> 0.220.0")


if __name__ == "__main__":
    main()
