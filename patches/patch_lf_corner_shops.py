"""Level Factory 0.206.0: corner shops -- an urban wall's runs open and close on a corner block (factory roadmap
241, the corner shop's step 3).

Step 3 of the factory root's `docs/proposals/CORNER_SHOP.md`. Deli Counter 0.218.0 builds four corner blocks,
`gs_cornershop_a` to `_d`, mid-rises whose ground-floor front is a shop; Zoo 1.107.0 paints the shop. This stands
them where a block face ends.

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  packages/pipeline/building_library.py   `CORNER_PREFIX`; `empty_rows(..., family="empty")`; an urban brief's
                                          Empties are the mid-rises and the corner blocks, as their own family
  packages/pipeline/empties.py            `_width`, `_runs`, `_corner_at`, `_cornered`; `terrace` sets a corner
                                          row aside and, on a continuous wall with one, hands the wall to
                                          `_cornered`; `infill` stands none
  apps/cli/commands/__init__.py           the compose stage says which shop closes each run, or that the
                                          library holds none
  tests/unit/test_urban_corner_shops.py   NEW (`lf_corner_shops/test_urban_corner_shops.py.txt`)
CHANGELOG and VERSION from `lf_corner_shops/CHANGELOG_0.206.0.md`; `--results-pending` leaves RESULT_ keys to
`--fill`.

Read before it was written, in this session: `empties.py` whole -- `_turned`, `_far_side`, `_blocked`, `_deal`,
`_target`, `_by_height`, `terrace` (the continuous loop, its strict fit `x + width > x_end`, the remainder left at a
run's end), `_fitting` and `infill` (its fresh deal behind the remainder); `building_library.empty_rows` and
`empties_for_brief`, and every reader of a row's `family` (the enterable library's, not an Empty's); the compose
stage's Empties block (`_empty_rows`, `_ext`, `_row`, `_heights`, the `terrace` and `infill` calls); the planner's
and the lock's use of `empties_for_brief`; `tests/unit/test_urban_heights_by_cause.py` and
`test_streetscape_urban.py` (the fixtures reused). The control digest was read off 0.205.0 before this was written.
Every file LF.

    python patches/patch_lf_corner_shops.py --results-pending
    (python -m pytest -q in level_factory)
    python patches/patch_lf_corner_shops.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_corner_shops"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_FAILING": "result_failing.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.205.0", b"0.206.0"
CHANGELOG_HEAD = ("## [0.205.0] - The site says what its street is: an urban brief's spec carries "
                  "`streetscape: \"urban\"`\n")
SHA = {"packages/pipeline/building_library.py": "f9c29d612b102e0e", "packages/pipeline/empties.py": "ec6e4401a485fcac",
       "apps/cli/commands/__init__.py": "86263e960a2fd8fc"}
NEW = {"tests/unit/test_urban_corner_shops.py": "test_urban_corner_shops.py.txt"}

LIBRARY = [
    ("MIDRISE_PREFIX = \"gs_midrise_\"\n",
     "MIDRISE_PREFIX = \"gs_midrise_\"\n"
     "#: THE CORNER BLOCKS (0.206.0, factory roadmap 241): Deli Counter 0.218.0's\n"
     "#: mid-rises whose ground-floor front is a shop. An urban brief draws them\n"
     "#: as their own family, and the wall stands one only where a run of it opens\n"
     "#: or closes (`empties.terrace`). Not `gs_corner_`: that is\n"
     "#: `gs_corner_station`'s, an enterable gas station.\n"
     "CORNER_PREFIX = \"gs_cornershop_\"\n"),
    ("def empty_rows(build_dir, prefix=EMPTY_PREFIX) -> list[dict]:\n"
     "    \"\"\"Every Empty in a Deli Counter build dir that can be themed, sorted by\n"
     "    id: ``{\"id\", \"family\", \"glb\", \"gameplay\", \"slots\"}``. An Empty is one\n",
     "def empty_rows(build_dir, prefix=EMPTY_PREFIX, family=\"empty\") -> list[dict]:\n"
     "    \"\"\"Every Empty in a Deli Counter build dir that can be themed, sorted by\n"
     "    id: ``{\"id\", \"family\", \"glb\", \"gameplay\", \"slots\"}``, ``family`` as\n"
     "    given -- ``empty``, or ``corner`` for the corner blocks (0.206.0). An Empty is one\n"),
    ("        row = {\"id\": aid, \"family\": \"empty\", \"glb\": str(glb),\n",
     "        row = {\"id\": aid, \"family\": family, \"glb\": str(glb),\n"),
    ("    if streetscape_effective(getattr(model, \"streetscape\", \"\"), empties):\n"
     "        return empty_rows(library, MIDRISE_PREFIX)\n"
     "    return empty_rows(library)\n",
     "    if streetscape_effective(getattr(model, \"streetscape\", \"\"), empties):\n"
     "        # and the corner blocks (0.206.0, roadmap 241), as their own family:\n"
     "        # the wall stands them only where a run of it opens or closes\n"
     "        return (empty_rows(library, MIDRISE_PREFIX)\n"
     "                + empty_rows(library, CORNER_PREFIX, family=\"corner\"))\n"
     "    return empty_rows(library)\n"),
]

CORNERED = '''def _width(extents, rid):
    """A shell's width along the street once turned to face it (rot 180), metres."""
    tx0, tx1, _ty0, _ty1 = _turned(extents[rid], 180)
    return tx1 - tx0


def _runs(x0, x1, blocked):
    """The stretches of ``[x0, x1]`` that the ``blocked`` intervals leave, west to east: the faces of the blocks
    an urban wall stands along."""
    runs, a = [], x0
    for b0, b1 in blocked:
        if b1 <= a or b0 >= x1:
            continue
        if b0 > a:
            runs.append((a, b0))
        a = max(a, b1)
    if x1 > a:
        runs.append((a, x1))
    return runs


def _corner_at(bag, extents, room, widest=False, not_id=None):
    """The index on ``bag`` of a corner block no wider than ``room``: the next dealt that fits, or with
    ``widest`` the widest, passing over ``not_id`` while another fits. None when none fits."""
    fits = [i for i in range(len(bag) - 1, -1, -1) if _width(extents, bag[i]["id"]) <= room]
    fits = [i for i in fits if bag[i]["id"] != not_id] or fits
    if not fits:
        return None
    if widest:
        return max(fits, key=lambda i: (_width(extents, bag[i]["id"]), i))
    return fits[0]


def _cornered(usable, corners, extents, stream, roads, span_x, action=None, heights=None):
    """`terrace` for an urban wall with corner blocks to stand (0.206.0, factory roadmap 241).

    The comps: "Corners carry the life. The corner building has the shop at grade (lit, awning), homes above.
    The middle of the block is residential." Each run of the wall -- between two roads crossing the far side,
    or a road and the plate's end, so one block face -- OPENS on the next corner block dealt that fits it and
    CLOSES on the widest one left on the corner bag that fits, not the one it opened on while another fits.
    Between them the wall is dealt as `terrace` deals it, heights by cause where given, and keeps clear before
    the run's end the narrowest closing block's width, so the run can close. The wall's remainder stays where
    it always stood, at the run's end. A run no corner block fits is dealt plainly."""
    edge, line = _far_side(roads[0])
    x0 = -float(span_x) / 2.0 + CLEARANCE
    x1 = float(span_x) / 2.0 - CLEARANCE
    by_cause = bool(action is not None and heights
                    and all(heights.get(r["id"]) is not None for r in usable))
    if by_cause:
        lo = min(heights[r["id"]] for r in usable)
        hi = max(heights[r["id"]] for r in usable)
        reach = max(float(action) - x0, x1 - float(action))
    out, need, prev, bag, cbag = [], 0.0, None, [], []

    def place(pick, x):
        nonlocal need
        tx0, tx1, ty0, ty1 = _turned(extents[pick["id"]], 180)
        at_y = line - ty1                              # the street edge on the line
        out.append({"id": f"e{len(out)}", "archetype": pick["id"],
                    "at": [round(x - tx0, 3), round(at_y, 3)], "rot": 180,
                    "size_x": round(tx1 - tx0, 3), "size_y": round(ty1 - ty0, 3),
                    "front": round(at_y + ty1, 3)})
        need = max(need, -(at_y + ty0))
        return tx1 - tx0

    for a, b in _runs(x0, x1, _blocked(roads, edge)):
        x, end, opened = a, b, None
        if not cbag:
            cbag = _deal(corners, stream)
        at = _corner_at(cbag, extents, b - a)
        if at is not None:
            pick = cbag.pop(at)
            opened = pick["id"]
            x += place(pick, x)
            others = [_width(extents, r["id"]) for r in corners if r["id"] != opened]
            end = b - min(others or [_width(extents, opened)])
        while True:
            if not bag:
                bag = _deal(usable, stream, prev)
            if by_cause:
                i = _by_height(bag, extents, heights, x, end, float(action), reach, lo, hi, prev)
            else:
                i = len(bag) - 1 if x + _width(extents, bag[-1]["id"]) <= end else None
            if i is None:
                break                                  # nothing on the bag fits before the closing corner
            pick = bag.pop(i)
            prev = pick["id"]
            x += place(pick, x)
        if opened is None:
            continue
        at = _corner_at(cbag, extents, b - x, widest=True, not_id=opened)
        if at is None or cbag[at]["id"] == opened:
            # a spent corner bag is not a closed run: a fresh deal behind what is left
            cbag = _deal(corners, stream, opened) + cbag
            at = _corner_at(cbag, extents, b - x, widest=True, not_id=opened)
        if at is not None:
            place(cbag.pop(at), x)
    return out, need


def terrace(rows, extents, stream, roads, span_x, continuous=False, action=None, heights=None):
'''

EMPTIES = [
    ("def terrace(rows, extents, stream, roads, span_x, continuous=False, action=None, heights=None):\n",
     CORNERED),
    ("    terrace, the deal decides alone, exactly as before.\"\"\"\n"
     "    usable = [r for r in rows if extents.get(r[\"id\"]) is not None]\n"
     "    if not usable or not roads:\n"
     "        return [], 0.0\n"
     "    edge, line = _far_side(roads[0])\n",
     "    terrace, the deal decides alone, exactly as before.\n"
     "\n"
     "    CORNER SHOPS (0.206.0, roadmap 241). A row of the ``corner`` family (Deli\n"
     "    Counter's `gs_cornershop_*`, `building_library.CORNER_PREFIX`) is never\n"
     "    dealt along the wall. On a continuous wall with one, each run between the\n"
     "    roads crossing the far side and the plate's ends opens and closes on a\n"
     "    corner block (`_cornered`). Without one, or on the strip's terrace, every\n"
     "    wall is the one 0.205.0 stood.\"\"\"\n"
     "    usable = [r for r in rows if extents.get(r[\"id\"]) is not None]\n"
     "    corners = [r for r in usable if r.get(\"family\") == \"corner\"]\n"
     "    usable = [r for r in usable if r.get(\"family\") != \"corner\"]\n"
     "    if not usable or not roads:\n"
     "        return [], 0.0\n"
     "    if continuous and corners:\n"
     "        return _cornered(usable, corners, extents, stream, roads, span_x, action, heights)\n"
     "    edge, line = _far_side(roads[0])\n"),
    ("    usable = [r for r in rows if extents.get(r[\"id\"]) is not None]\n"
     "    if not usable or not roads:\n"
     "        return [], 0.0\n"
     "    _edge, line = _near_side(roads[0])\n",
     "    # no corner block (0.206.0): the near side's corners are the mission's own buildings\n"
     "    usable = [r for r in rows if extents.get(r[\"id\"]) is not None and r.get(\"family\") != \"corner\"]\n"
     "    if not usable or not roads:\n"
     "        return [], 0.0\n"
     "    _edge, line = _near_side(roads[0])\n"),
]

COMPOSE = [
    ("        if _urban and _action is not None:\n"
     "            print(f\"[site] the urban wall's heights by cause: lowest across from x {_action:.1f}, \"\n"
     "                  f\"rising to the plate's ends\")\n",
     "        if _urban and _action is not None:\n"
     "            print(f\"[site] the urban wall's heights by cause: lowest across from x {_action:.1f}, \"\n"
     "                  f\"rising to the plate's ends\")\n"
     "        # CORNER SHOPS (0.206.0, roadmap 241): which shop opens and closes each run\n"
     "        _corners = [p[\"archetype\"] for p in placed_e if _row[p[\"archetype\"]].get(\"family\") == \"corner\"]\n"
     "        if _corners:\n"
     "            print(f\"[site] the urban wall's runs open and close on corner shops: {', '.join(_corners)}\")\n"
     "        elif _urban and not any(r.get(\"family\") == \"corner\" for r in _empty_rows):\n"
     "            print(\"  URBAN_WITHOUT_CORNERS: the lot library holds no gs_cornershop_* Empty -- the \"\n"
     "                  \"wall's runs open and close on mid-rises\", file=sys.stderr)\n"),
]

EDITS = {"packages/pipeline/building_library.py": LIBRARY, "packages/pipeline/empties.py": EMPTIES,
         "apps/cli/commands/__init__.py": COMPOSE}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.206.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.206.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.206.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.206.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (LF / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, edits in EDITS.items():
        raw = (LF / rel).read_bytes()
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
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for rel, (text, eol) in writes.items():
        (LF / rel).write_bytes(text.encode("utf-8").replace(b"\n", eol))
    for r, data in news.items():
        (LF / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.205.0 -> 0.206.0")


if __name__ == "__main__":
    main()
