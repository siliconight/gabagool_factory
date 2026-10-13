"""Deli Counter 0.211.0: a rowhome Empty stands three steps up, on a stoop (factory roadmap 240's rowhouse
front; the design is `docs/proposals/ROWHOUSE_STOOP.md`).

Anchored edits, each asserted exactly once and every file's sha16 pinned, nothing written until all of
them matched:
  presets.py                 `import stoop as stoop_geom`; `empty_rowhome(stoop=0)` raises the ground
                             storey's front door and window by `lift` and names the stoop and its
                             concrete; every `EMPTY_ROWHOMES` row takes `stoop.RISERS`
  spec_types.py              `LevelSpec.stoop`
  schema/level.schema.json   the `stoop` property
  deli_counter.py            `import stoop`; the facade build calls `_stoop` after `_exterior`; `_stoop`
  stoop.py, test_stoop.py    NEW (`dc_rowhome_stoop/*.txt`)
  specs/gs_empty_rowhome_*.json   regenerated from the patched presets, `json.dumps(indent=2)` and no
                             trailing newline as they are written; the patch first asserts each file is
                             the CURRENT presets' output, byte for byte, so the regeneration can move
                             nothing but what the presets moved
CHANGELOG and VERSION from `dc_rowhome_stoop/CHANGELOG_0.211.0.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`. The twelve Empties are rebuilt after (`build.py`, Blender).

Read before it was written, in this session: `empty_rowhome` and `EMPTY_ROWHOMES` (presets.py), `_facade`
(floor_thick 0.3, grid 0.5), the facade build path (`build`: no `_volumes`, no `_stairs`), `_exterior`
(the S wall's centre line at -footprint_y / 2, `wall_thick` across it), `_opening_to_hole` (an opening's
centre `snap(pos * run)`, its bottom `floor_thick / 2 + sill`), `_opening_piece`, `_volumes` (the slot a
visual box records), `_box`, `_col_box`, `col_suffix`, `_stairs`' ramp riding the nosings and
`stairwell.ramp_foot_extension` / `ramp_head_trim`, `_record_surface`, `spec_loader.spec_from_dict`
(top-level keys pass into `LevelSpec`), the schema's `additionalProperties: false`, the twelve specs (all
`json.dumps(indent=2)`, no trailing newline), and `agent_contract.json` (`unassisted_step_max_m` 0.1025).
Every file LF.

    python patches/patch_dc_rowhome_stoop.py --results-pending
    (rebuild the twelve; python -m pytest -q in deli_counter)
    python patches/patch_dc_rowhome_stoop.py --fill
    DC_ROOT=<copy> python patches/patch_dc_rowhome_stoop.py --draft
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_rowhome_stoop"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_BUILD": "result_build.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Deli Counter 0.210.0", b"Deli Counter 0.211.0"
CHANGELOG_HEAD = "## [0.210.0] - a rowhome Empty's roof is tar"
SHA = {"presets.py": "b792128d12c335b3", "spec_types.py": "e2e9e7ce5b0614a8",
       "deli_counter.py": "2a59a13624226a09", "schema/level.schema.json": "69c10778d7cf2643"}
NEW = {"stoop.py": "stoop.py.txt", "test_stoop.py": "test_stoop.py.txt"}

EDITS = {
    "presets.py": [
        ("import migrate_window_sign\n\n\n",
         "import migrate_window_sign\n"
         "import stoop as stoop_geom\n\n\n"),
        ("                  antenna: bool = False, dish: bool = False) -> dict:\n",
         "                  antenna: bool = False, dish: bool = False,\n"
         "                  stoop: int = 0) -> dict:\n"),
        ("    ext = []\n"
         "    for st in range(int(floors)):\n"
         "        if st == 0:\n"
         "            front = [{\"kind\": \"door\", \"pos\": door, \"width\": 1.0, \"height\": 2.3,\n"
         "                      \"tag\": \"front_door\", \"material\": \"wood\"},\n"
         "                     dict(win, pos=-door)]\n",
         "    # A STOOP (0.211.0, factory roadmap 240): `stoop` steps up to the front\n"
         "    # door -- the comps' \"three or four steps up to each door ... the first\n"
         "    # floor stands above the sidewalk\" -- which `stoop.plan` builds. The\n"
         "    # ground storey's front door and window rise together by `lift`, so the\n"
         "    # floor behind them is the landing's: the door's threshold, the slab's top\n"
         "    # (floor_thick / 2) plus its sill, is `stoop` risers of `stoop.RISER`\n"
         "    # above grade. 0 keeps the door at grade and the spec as it was.\n"
         "    lift = (round(int(stoop) * stoop_geom.RISER - s[\"floor_thick\"] / 2.0, 4)\n"
         "            if stoop else 0.0)\n"
         "    ext = []\n"
         "    for st in range(int(floors)):\n"
         "        if st == 0:\n"
         "            front = [{\"kind\": \"door\", \"pos\": door, \"width\": 1.0, \"height\": 2.3,\n"
         "                      \"tag\": \"front_door\", \"material\": \"wood\"},\n"
         "                     dict(win, pos=-door)]\n"
         "            if lift:\n"
         "                front[0][\"sill\"] = lift\n"
         "                front[1][\"sill\"] = round(win[\"sill\"] + lift, 4)\n"),
        ("    if dish:\n"
         "        s[\"roof_dish\"] = True\n"
         "    return s\n",
         "    if dish:\n"
         "        s[\"roof_dish\"] = True\n"
         "    # and its stoop (0.211.0): what `stoop.plan` builds in front of the raised\n"
         "    # door, in concrete, which the palette then declares\n"
         "    if stoop:\n"
         "        s[\"stoop\"] = {\"risers\": int(stoop), \"tread\": stoop_geom.TREAD,\n"
         "                      \"landing\": stoop_geom.LANDING, \"width\": stoop_geom.WIDTH}\n"
         "        if not any(m[\"id\"] == \"concrete\" for m in s[\"materials\"]):\n"
         "            s[\"materials\"].append({\"id\": \"concrete\", \"acoustic\": \"Concrete\",\n"
         "                                   \"absorption\": 0.7, \"damping\": 0.6})\n"
         "    return s\n"),
        ("    \"gs_empty_rowhome_l\": dict(width=6.4, floors=2, wall=\"stone_ext\", door_side=\"E\", cornice=0.8, seed=1922,\n"
         "                               door_finish=\"stained\", security_door=True),\n"
         "}\n",
         "    \"gs_empty_rowhome_l\": dict(width=6.4, floors=2, wall=\"stone_ext\", door_side=\"E\", cornice=0.8, seed=1922,\n"
         "                               door_finish=\"stained\", security_door=True),\n"
         "}\n"
         "\n"
         "# A STOOP AT EVERY DOOR (0.211.0): the comps' \"three or four steps up to\n"
         "# each door\", three being what the terrace's 2.0 m frontage holds\n"
         "# (`stoop.depth`) -- written once here rather than on every row.\n"
         "for _args in EMPTY_ROWHOMES.values():\n"
         "    _args.setdefault(\"stoop\", stoop_geom.RISERS)\n"),
    ],
    "spec_types.py": [
        ("    roof_antenna: bool = False\n"
         "    roof_dish: bool = False\n",
         "    roof_antenna: bool = False\n"
         "    roof_dish: bool = False\n"
         "    # AN EMPTY'S STOOP (0.211.0): the steps up to its raised front door,\n"
         "    # `{\"risers\", \"tread\", \"landing\", \"width\"}` for `stoop.plan`; None, a\n"
         "    # door at grade. The preset raises the door and the ground storey's front\n"
         "    # window with it (factory roadmap 240).\n"
         "    stoop: Optional[dict] = None\n"),
    ],
    "schema/level.schema.json": [
        ("    \"roof_dish\": {\n"
         "      \"type\": \"boolean\",\n"
         "      \"description\": \"a satellite dish on an Empty's roof (roofs.roof_fixtures, 0.185.0)\"\n"
         "    },\n",
         "    \"roof_dish\": {\n"
         "      \"type\": \"boolean\",\n"
         "      \"description\": \"a satellite dish on an Empty's roof (roofs.roof_fixtures, 0.185.0)\"\n"
         "    },\n"
         "    \"stoop\": {\n"
         "      \"type\": \"object\",\n"
         "      \"description\": \"an Empty's stoop: the steps up to its raised front door (stoop.plan, 0.211.0)\",\n"
         "      \"properties\": {\n"
         "        \"risers\": {\"type\": \"integer\", \"minimum\": 1},\n"
         "        \"tread\": {\"type\": \"number\", \"exclusiveMinimum\": 0},\n"
         "        \"landing\": {\"type\": \"number\", \"exclusiveMinimum\": 0},\n"
         "        \"width\": {\"type\": \"number\", \"exclusiveMinimum\": 0}\n"
         "      },\n"
         "      \"required\": [\"risers\", \"tread\", \"landing\", \"width\"],\n"
         "      \"additionalProperties\": false\n"
         "    },\n"),
    ],
    "deli_counter.py": [
        ("import empty_panes\n"
         "import vault_room\n",
         "import empty_panes\n"
         "import stoop\n"
         "import vault_room\n"),
        ("            self._slabs()\n"
         "            self._exterior()\n"
         "            # The roof slot, as a building records it, so Zoo dresses the\n",
         "            self._slabs()\n"
         "            self._exterior()\n"
         "            # AN EMPTY'S STOOP (0.211.0): the steps up to its raised door,\n"
         "            # built here because a facade runs no `_volumes` or `_stairs`.\n"
         "            self._stoop()\n"
         "            # The roof slot, as a building records it, so Zoo dresses the\n"),
        ("    # ----------------------------------------------------------------------\n"
         "    # KITBASHING  --  import external models and place instances\n",
         "    def _stoop(self):\n"
         "        \"\"\"AN EMPTY'S STOOP (0.211.0, factory roadmap 240; `stoop.py`): the\n"
         "        steps up to its raised front door. The landing and the treads are\n"
         "        visuals recorded as `prop` slots in concrete, so the art pass dresses\n"
         "        them as it does a volume; the collision is what the contract body\n"
         "        walks -- ONE ramp whose top face rides the nosings, the landing, and\n"
         "        a block under each tread but the lowest, one riser short of it -- as\n"
         "        the stairs' is (`_stairs`). Nothing when the spec asks for none.\"\"\"\n"
         "        p = stoop.plan(self.s)\n"
         "        if p is None:\n"
         "            return\n"
         "        mat = \"concrete\"\n"
         "        style = skin_style.style_for(mat, self._mat_style,\n"
         "                                     self.s.default_material)\n"
         "        pieces = [(\"stoop_landing\", p[\"landing\"])] + [\n"
         "            (\"stoop_tread_%d\" % k, piece)\n"
         "            for k, piece in enumerate(p[\"treads\"], 1)]\n"
         "        for name, (c, size) in pieces:\n"
         "            self._box(name, c, size, self.VISUAL, role=\"prop\")\n"
         "            self.slots.append({\n"
         "                \"slot_id\": name, \"role\": \"prop\", \"size_mod\": \"full\",\n"
         "                \"style\": style, \"material\": mat, \"species\": None,\n"
         "                \"stock\": None, \"variant\": 0, \"form\": None,\n"
         "                \"current_ref\": \"prop_greybox_01\", \"kit_axis\": \"material\",\n"
         "                \"wall\": None, \"story\": None, \"facing\": None,\n"
         "                \"transform\": {\"translation\": [round(c[0], 4),\n"
         "                                              round(c[1], 4),\n"
         "                                              round(c[2], 4)],\n"
         "                              \"rot_y\": 0.0, \"scale\": [1.0, 1.0, 1.0]},\n"
         "                # the stoop's collision is its own, below, never a module's\n"
         "                \"fit\": {\"dims\": [round(size[0], 4), round(size[1], 4),\n"
         "                                 round(size[2], 4)],\n"
         "                        \"pivot\": \"center\", \"openings\": [],\n"
         "                        \"collision\": \"none\"},\n"
         "            })\n"
         "        self._col_box(\"stoop_landing_col\", p[\"landing\"][0], p[\"landing\"][1],\n"
         "                      mode=\"convex\")\n"
         "        self._record_surface(\"stoop_landing_col\", mat)\n"
         "        for k, (c, size) in enumerate(p[\"unders\"], 1):\n"
         "            self._col_box(\"stoop_under_%d_col\" % k, c, size, mode=\"convex\")\n"
         "            self._record_surface(\"stoop_under_%d_col\" % k, mat)\n"
         "        c, size, pitch = p[\"ramp\"]\n"
         "        ramp = self._box(\"stoop_ramp\" + self.col_suffix[\"convex\"], c, size,\n"
         "                         self.COLLISION)\n"
         "        # its high end toward the house: local +Y up the flight\n"
         "        ramp.rotation_euler = (pitch, 0.0, 0.0)\n"
         "        self._record_surface(\"stoop_ramp\", mat)\n"
         "\n"
         "    # ----------------------------------------------------------------------\n"
         "    # KITBASHING  --  import external models and place instances\n"),
    ],
}

REGEN = (
    "import json, sys\n"
    "sys.path.insert(0, '.')\n"
    "import presets\n"
    "for n, a in sorted(presets.EMPTY_ROWHOMES.items()):\n"
    "    p = 'specs/%s.json' % n\n"
    "    data = json.dumps(presets.empty_rowhome(name=n, **a), indent=2).encode('utf-8')\n"
    "    if sys.argv[1] == 'check':\n"
    "        assert open(p, 'rb').read() == data, ('not the presets output', p)\n"
    "    else:\n"
    "        open(p, 'wb').write(data)\n"
    "print(sys.argv[1], len(presets.EMPTY_ROWHOMES), 'specs')\n")


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
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(DC / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.211.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Deli Counter 0.211.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("DC_ROOT"):
        sys.exit("refusing: --draft is for a DC_ROOT copy, never the repo")
    assert (DC / "VERSION").read_bytes().strip() == VERSION_WAS, (DC / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.211.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.211.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        for key in RESULTS if PENDING else ():
            left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (DC / rel).exists(), ("already applied", rel)
    # the twelve specs are the CURRENT presets' output, byte for byte
    subprocess.run([sys.executable, "-c", REGEN, "check"], cwd=DC, check=True)
    writes = {}
    for rel, pairs in EDITS.items():
        p = DC / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    news = {rel: (SRC / src).read_bytes().replace(b"\r\n", b"\n") for rel, src in NEW.items()}
    cl = DC / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    for rel, data in news.items():
        (DC / rel).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (DC / "VERSION").write_bytes(VERSION)
    subprocess.run([sys.executable, "-c", REGEN, "write"], cwd=DC, check=True)
    print("Deli Counter 0.210.0 -> 0.211.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
