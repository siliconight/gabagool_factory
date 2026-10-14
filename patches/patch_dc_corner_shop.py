"""Deli Counter 0.218.0: the corner blocks -- a mid-rise Empty whose ground-floor front is a shop (factory roadmap
241, the corner shop's step 2).

Step 2 of the factory root's `docs/proposals/CORNER_SHOP.md`. Zoo 1.107.0 paints a shop's window from its own atlas
(`zoo_keeper.core.shop_panes`); this authors which windows show a shop and which shop.

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  spec_types.py           `Opening.pane`, an authored state, None by default
  deli_counter.py         `_opening_to_hole` carries `pane`; a facade window's slot takes the authored state before
                          `empty_panes.choose` draws one
  empty_panes.py          `SHOP_STATES` (Zoo's shop atlas, in its order); `authored`, refusing an unknown state
  themed_tscn.py          `resolve_themed_stem` names a shop state as Zoo's `plan_kit` does
  presets.py              `SHOP_WINDOW`; `empty_midrise(..., security_door=False, shop=None)`; `EMPTY_CORNERS`
                          (gs_cornershop_a to _d) after `EMPTY_MIDRISE_NARROW`
  schema/level.schema.json  an opening may carry `pane`, a string or null. The four corner specs failed the
                          build's own schema gate without it ("'pane' was unexpected"), found by reading their
                          validation manifests after the first build, before anything was committed
  navgate_baseline.json   four UNJUDGED entries after `gs_midrise_i`; `counts.unjudged` 30 -> 34
  specs/gs_cornershop_a/b/c/d.json   NEW, written from the patched presets (indent=2, no closing newline,
                          as the nine are); `specs/CATALOG.md` regenerated (`catalog.py`)
  test_empty_corner.py    NEW (`dc_corner_shop/test_empty_corner.py.txt`)
CHANGELOG and VERSION from `dc_corner_shop/CHANGELOG_0.218.0.md`; `--results-pending` leaves RESULT_ keys to
`--fill`. The shells are built after (`build.py --all`, since `presets.py` moves).

Read before it was written, in this session: `presets.empty_midrise` whole, `MIDRISE_BAY`, `EMPTY_MIDRISES`,
`EMPTY_MIDRISE_NARROW`, `_facade`, `empty_rowhome`'s `door_finish` and `security_door`; `spec_types.Opening` (a
dataclass, `spec_loader` builds it with `Opening(**o)`, so an undeclared key does not load); `deli_counter.
_opening_to_hole`, its two callers and `_record_opening_slot`'s facade branch; `empty_panes` whole;
`themed_tscn.resolve_themed_stem`'s pane test; `navgate_baseline.json`'s last Empty entry and its counts; a
mid-rise spec's form on disk; `test_empty_panes.py` and `test_empty_midrise_narrow.py` (the new test's patterns);
`patch_dc_midrise_narrow.py` (this patch's machinery). Every file LF.

    python patches/patch_dc_corner_shop.py --results-pending
    (build.py --all; python -m pytest -q in deli_counter)
    python patches/patch_dc_corner_shop.py --fill
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_corner_shop"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_BUILT": "result_built.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Deli Counter 0.217.0", b"Deli Counter 0.218.0"
CHANGELOG_HEAD = "## [0.217.0] - three narrow mid-rises: the blocks that fit between the mission's buildings\n"
SHA = {"spec_types.py": "d5b005560e42c9a4", "deli_counter.py": "c212920122928d2d", "empty_panes.py": "66bb971320100d46",
       "themed_tscn.py": "fff4ec53c3486695", "presets.py": "700e08ac7c8ca77a",
       "navgate_baseline.json": "c025034d24cfcd5a", "schema/level.schema.json": "9b8ed3efbec8dbcf"}
NEW = {"test_empty_corner.py": "test_empty_corner.py.txt"}
NAMES = ["gs_cornershop_a", "gs_cornershop_b", "gs_cornershop_c", "gs_cornershop_d"]

SPEC = [
    ("    face: Optional[Literal[\"N\", \"S\", \"E\", \"W\"]] = None\n"
     "\n"
     "    def resolved(self):\n",
     "    face: Optional[Literal[\"N\", \"S\", \"E\", \"W\"]] = None\n"
     "    # AN EMPTY WINDOW'S AUTHORED STATE (0.218.0, factory roadmap 241): a corner\n"
     "    # shop's window shows its shop (`empty_panes.SHOP_STATES`, which Zoo >=\n"
     "    # 1.107.0 paints), not a drawn room. None: drawn (`empty_panes.choose`).\n"
     "    pane: Optional[str] = None\n"
     "\n"
     "    def resolved(self):\n"),
]

DELI = [
    ("                    # which opening this is (0.182.0): an Empty's front door\n"
     "                    # is the one its preset tagged `front_door`\n"
     "                    tag=getattr(op, \"tag\", None))\n",
     "                    # which opening this is (0.182.0): an Empty's front door\n"
     "                    # is the one its preset tagged `front_door`\n"
     "                    tag=getattr(op, \"tag\", None),\n"
     "                    # and what an Empty's window shows where its preset says\n"
     "                    # (0.218.0): a corner shop's front\n"
     "                    pane=getattr(op, \"pane\", None))\n"),
    ("            if role == \"window\":\n"
     "                slot[\"pane\"] = empty_panes.choose(\n"
     "                    self.s.name, self.s.seed, vb, story,\n"
     "                    vacant=getattr(self.s, \"vacant\", False))\n",
     "            if role == \"window\":\n"
     "                # AUTHORED BEFORE DRAWN (0.218.0): a corner shop's window\n"
     "                # shows the shop its preset names on the opening\n"
     "                slot[\"pane\"] = empty_panes.authored(h.get(\"pane\")) or empty_panes.choose(\n"
     "                    self.s.name, self.s.seed, vb, story,\n"
     "                    vacant=getattr(self.s, \"vacant\", False))\n"),
]

PANES = [
    ("          \"dark_curtain\", \"dark_bars\", \"dark_fan\", \"boarded\")\n",
     "          \"dark_curtain\", \"dark_bars\", \"dark_fan\", \"boarded\")\n"
     "#: A CORNER SHOP'S STATES (0.218.0, factory roadmap 241), in Zoo's shop atlas\n"
     "#: order (`zoo_keeper.core.shop_panes.STATES`, pinned by `test_empty_corner.py`).\n"
     "#: AUTHORED on the opening, never drawn: a shop is one room, and which shop\n"
     "#: stands on a corner is a fact about the building (`presets.EMPTY_CORNERS`).\n"
     "SHOP_STATES = (\"shop_deli\", \"shop_grocery\", \"shop_bar\", \"shop_laundry\",\n"
     "               \"shop_gate\", \"shop_dark\")\n"),
    ("    if vacant:\n"
     "        return \"boarded\"\n"
     "    return _pick(GROUND if int(story or 0) <= 0 else UPPER,\n"
     "                 \"%s:%s:%s\" % (building, seed, slot_id))\n",
     "    if vacant:\n"
     "        return \"boarded\"\n"
     "    return _pick(GROUND if int(story or 0) <= 0 else UPPER,\n"
     "                 \"%s:%s:%s\" % (building, seed, slot_id))\n"
     "\n"
     "\n"
     "def authored(pane):\n"
     "    \"\"\"An opening's authored state (0.218.0), or None where its preset\n"
     "    authored none and `choose` draws one. A corner shop's front names its\n"
     "    shop (`SHOP_STATES`); a window state is honoured as authored too. Anything\n"
     "    else is refused rather than dropped, as a door finish is.\"\"\"\n"
     "    if pane is None:\n"
     "        return None\n"
     "    if pane not in STATES and pane not in SHOP_STATES:\n"
     "        raise ValueError(\"pane %r is not one of %s or %s\" % (pane, STATES, SHOP_STATES))\n"
     "    return pane\n"),
]

STEM = [
    ("    # the same test Zoo's `plan_kit` makes (1.64.0), so the names agree\n"
     "    import empty_panes\n"
     "    pane = (slot.get(\"pane\") if typ == \"window\" and slot.get(\"glazing\") == \"facade\"\n"
     "            and slot.get(\"pane\") in empty_panes.STATES else None)\n",
     "    # the same test Zoo's `plan_kit` makes (1.64.0), so the names agree --\n"
     "    # a corner shop's state too (0.218.0, Zoo >= 1.107.0)\n"
     "    import empty_panes\n"
     "    pane = (slot.get(\"pane\") if typ == \"window\" and slot.get(\"glazing\") == \"facade\"\n"
     "            and (slot.get(\"pane\") in empty_panes.STATES\n"
     "                 or slot.get(\"pane\") in empty_panes.SHOP_STATES) else None)\n"),
]

PRESETS = [
    ("MIDRISE_BAY = 3.2\n"
     "\n"
     "\n"
     "def empty_midrise(",
     "MIDRISE_BAY = 3.2\n"
     "#: A CORNER SHOP'S WINDOW (0.218.0, roadmap 241): a bay less a pier either\n"
     "#: side, from a low bulkhead to the front door's head, so the storefront reads\n"
     "#: as one run of glass with the shop's door in it. CHOSEN, not read: 2.4 m of\n"
     "#: glass in a bay of about 3 m, 0.3 m up, its head at the door's 2.4 m.\n"
     "SHOP_WINDOW = {\"kind\": \"window\", \"width\": 2.4, \"height\": 2.1, \"sill\": 0.3,\n"
     "               \"material\": \"glass\"}\n"
     "\n"
     "\n"
     "def empty_midrise("),
    ("                  scale_ref: bool = False, door_finish: str = None) -> dict:\n"
     "    \"\"\"A mid-rise apartment block Empty. `floors` storeys of windows in\n",
     "                  scale_ref: bool = False, door_finish: str = None,\n"
     "                  security_door: bool = False, shop: str = None) -> dict:\n"
     "    \"\"\"A mid-rise apartment block Empty. `floors` storeys of windows in\n"),
    ("    3.1 m a storey, the rowhome Empty's storey. Non-enterable, as every\n"
     "    Empty is.\"\"\"\n"
     "    sh = 3.1\n",
     "    3.1 m a storey, the rowhome Empty's storey. Non-enterable, as every\n"
     "    Empty is.\n"
     "\n"
     "    A CORNER BLOCK (0.218.0, factory roadmap 241): with `shop`, one of\n"
     "    `empty_panes.SHOP_STATES`, the ground floor's front is that shop. Every\n"
     "    front bay but the door's is a `SHOP_WINDOW` authored in the shop's\n"
     "    state, the front door is the shop's, and the homes above keep the\n"
     "    service door behind. `security_door` hangs an iron door on the front,\n"
     "    as the rowhome Empty's does.\"\"\"\n"
     "    sh = 3.1\n"),
    ("            else:\n"
     "                front.append(dict(win, pos=p))\n"
     "                back.append(dict(win, pos=p))\n"
     "        ext.append({\"wall\": \"S\", \"story\": st, \"material\": wall, \"openings\": front})\n",
     "            elif st == 0 and shop:\n"
     "                front.append(dict(SHOP_WINDOW, pos=p, pane=shop))\n"
     "                back.append(dict(win, pos=p))\n"
     "            else:\n"
     "                front.append(dict(win, pos=p))\n"
     "                back.append(dict(win, pos=p))\n"
     "        ext.append({\"wall\": \"S\", \"story\": st, \"material\": wall, \"openings\": front})\n"),
    ("    if door_finish:\n"
     "        s[\"door_finish\"] = door_finish\n"
     "    return s\n"
     "\n"
     "\n"
     "#: The mid-rise Empties built into the library, one row a block: width (m),\n",
     "    if door_finish:\n"
     "        s[\"door_finish\"] = door_finish\n"
     "    if security_door:\n"
     "        s[\"security_door\"] = True\n"
     "    return s\n"
     "\n"
     "\n"
     "#: The mid-rise Empties built into the library, one row a block: width (m),\n"),
    ("    \"gs_midrise_i\": dict(width=6.3, floors=4, wall=\"brick_brown\", lobby=0.0, cornice=0.8,\n"
     "                         seed=1939, door_finish=\"green\"),\n"
     "}\n",
     "    \"gs_midrise_i\": dict(width=6.3, floors=4, wall=\"brick_brown\", lobby=0.0, cornice=0.8,\n"
     "                         seed=1939, door_finish=\"green\"),\n"
     "}\n"
     "\n"
     "#: THE CORNER BLOCKS (0.218.0, factory roadmap 241). The comps: \"Corners carry\n"
     "#: the life. The corner building has the shop at grade (lit, awning), homes\n"
     "#: above\" (the factory root's `docs/reference/URBAN_MIDRISE_COMPS.md`). Four\n"
     "#: mid-rises whose ground-floor front is a shop (`empty_midrise`'s `shop`),\n"
     "#: one shop each and no two alike: which shop stands on a corner is a fact\n"
     "#: about the building, so it is authored, as `vacant` is. Their own prefix,\n"
     "#: `gs_cornershop_`: Level Factory deals `gs_midrise_` along an urban street's\n"
     "#: wall, and a corner block dealt mid-block would put the life in the middle.\n"
     "#: The door's bay is the centre's, so the shop's door stands mid-front at\n"
     "#: whichever end of a wall the block closes.\n"
     "EMPTY_CORNERS = {\n"
     "    \"gs_cornershop_a\": dict(width=15.0, floors=6, wall=\"brick\", lobby=0.0, cornice=1.0,\n"
     "                            seed=1941, door_finish=\"black\", security_door=True, shop=\"shop_deli\"),\n"
     "    \"gs_cornershop_b\": dict(width=18.0, floors=8, wall=\"brick_orange\", lobby=0.0, cornice=1.2,\n"
     "                            seed=1942, door_finish=\"oxblood\", shop=\"shop_bar\"),\n"
     "    \"gs_cornershop_c\": dict(width=12.0, floors=5, wall=\"brick_brown\", lobby=0.0, cornice=1.0,\n"
     "                            seed=1943, door_finish=\"white\", shop=\"shop_laundry\"),\n"
     "    \"gs_cornershop_d\": dict(width=16.5, floors=7, wall=\"stone_ext\", lobby=0.0, cornice=1.4,\n"
     "                            seed=1944, door_finish=\"green\", security_door=True, shop=\"shop_grocery\"),\n"
     "}\n"),
]

REASON = ("a corner mid-rise Empty (Deli Counter 0.218.0, roadmap 241): facade-only, sealed, its shop painted on its "
          "windows, no interior for a spawn marker to stand in, so zero markers checked is the correct outcome -- the "
          "same call as every Empty")
BASELINE_OLD = ("      \"reason\": \"a narrow mid-rise Empty (Deli Counter 0.217.0, roadmap 241): facade-only, sealed, no "
                "interior for a spawn marker to stand in, so zero markers checked is the correct outcome -- the same "
                "call as every Empty\"\n"
                "    }\n"
                "  ],\n"
                "  \"stair_failures\": [\n")
BASELINE_NEW = BASELINE_OLD[:-len("    }\n  ],\n  \"stair_failures\": [\n")] + "".join(
    "    },\n"
    "    {\n"
    "      \"shell\": \"%s\",\n"
    "      \"checked\": 0,\n"
    "      \"navigable\": null,\n"
    "      \"stairs_ok\": true,\n"
    "      \"reason\": \"%s\"\n" % (n, REASON) for n in NAMES) + "    }\n  ],\n  \"stair_failures\": [\n"
COUNT_OLD, COUNT_NEW = "    \"unjudged\": 30,\n", "    \"unjudged\": 34,\n"

#: The schema's last property is the opening's `face`; `pane` follows it.
SCHEMA_FACE = ("        \"face\": {\n"
               "          \"enum\": [\n"
               "            \"N\",\n"
               "            \"S\",\n"
               "            \"E\",\n"
               "            \"W\",\n"
               "            null\n"
               "          ]\n")
SCHEMA_CLOSE = ("      }\n"
                "    }\n"
                "  }\n"
                "}\n")
SCHEMA_OLD = SCHEMA_FACE + "        }\n" + SCHEMA_CLOSE
SCHEMA_NEW = (SCHEMA_FACE + "        },\n"
              "        \"pane\": {\n"
              "          \"type\": [\n"
              "            \"string\",\n"
              "            \"null\"\n"
              "          ],\n"
              "          \"description\": \"an Empty window's authored state: a corner shop's front "
              "(empty_panes.SHOP_STATES, 0.218.0); absent, the state is drawn\"\n"
              "        }\n" + SCHEMA_CLOSE)

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
    "print('wrote', len(presets.EMPTY_CORNERS), 'specs; the nine mid-rises unchanged')\n")

EDITS = {"spec_types.py": SPEC, "deli_counter.py": DELI, "empty_panes.py": PANES, "themed_tscn.py": STEM,
         "presets.py": PRESETS}


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
    for path, rel in [(DC / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.218.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Deli Counter 0.218.0: results filled")


def main():
    if FILL:
        return fill()
    assert (DC / "VERSION").read_bytes().strip() == VERSION_WAS, (DC / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.218.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.218.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in list(NEW) + ["specs/%s.json" % n for n in NAMES]:
        assert not (DC / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, edits in EDITS.items():
        eol, text = _read(rel)
        for old, new in edits:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:60])
            text = text.replace(old, new)
        compile(text, rel, "exec")
        writes[rel] = (text, eol)
    eol_b, base = _read("navgate_baseline.json")
    for old, new in ((BASELINE_OLD, BASELINE_NEW), (COUNT_OLD, COUNT_NEW)):
        assert base.count(old) == 1, ("navgate_baseline.json", "anchor", base.count(old), old[:60])
        base = base.replace(old, new)
    json.loads(base)
    eol_s, schema = _read("schema/level.schema.json")
    assert schema.count(SCHEMA_OLD) == 1 and schema.endswith(SCHEMA_OLD), ("schema", schema.count(SCHEMA_OLD))
    schema = schema.replace(SCHEMA_OLD, SCHEMA_NEW)
    assert "pane" in json.loads(schema)["$defs"]["opening"]["properties"]
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
    (DC / "navgate_baseline.json").write_bytes(base.encode("utf-8").replace(b"\n", eol_b))
    (DC / "schema/level.schema.json").write_bytes(schema.encode("utf-8").replace(b"\n", eol_s))
    for r, data in news.items():
        (DC / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (DC / "VERSION").write_bytes(VERSION)
    subprocess.run([sys.executable, "-c", REGEN], cwd=DC, check=True)
    subprocess.run([sys.executable, "catalog.py"], cwd=DC, check=True)
    print("Deli Counter 0.217.0 -> 0.218.0")


if __name__ == "__main__":
    main()
