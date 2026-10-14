"""Level Factory 0.204.0: heights by cause -- the urban wall stands its lowest blocks across from the action and rises
with distance from it (factory roadmap 241).

The comps (`docs/reference/URBAN_MIDRISE_COMPS.md`): "the tallest stand furthest away", the skyline stepping up with
distance; roadmap 241 wrote the rule down, heights by cause, never by jitter. 0.203.0 dealt the wall's blocks off a
shuffled bag and their heights fell as the deal put them: cold run 9291's seed_9104 stood 5, 7, 5, 10, 8, 6, 4, 12,
6 and 8 storeys from west to east.

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  packages/pipeline/street_line.py   `shell_top`, the top of a shell's collider hulls (glTF y up)
  packages/pipeline/empties.py       `_target` and `_by_height`; `terrace(..., action=None, heights=None)` picks
                                     by height on a continuous wall given both, the strip and an urban wall
                                     without them exactly as before
  apps/cli/commands/__init__.py      for an urban brief, the action's centre (the middle of the span the spawn,
                                     objective and extraction buildings cover) and the shells' tops, passed in
  tests/unit/test_urban_heights_by_cause.py   NEW (`lf_heights_by_cause/...py.txt`)
CHANGELOG and VERSION from `lf_heights_by_cause/CHANGELOG_0.204.0.md`; `--results-pending` leaves RESULT_ keys to
`--fill`. `--preview DIR` writes the three edited sources under DIR and nothing else, so the code can be measured
before it is applied.

Read before it was written, in this session: `empties.py` (the header, `_far_side`, `_blocked`, `_deal`, `terrace`
whole, `infill`); `street_line.shell_extents` (`glb_collision.collision_solids`, each solid's centre and size,
glTF y up); the compose stage's urban block (`_urban`, `_ext`, the terrace and infill calls, `buildings` with
`id`, `fp_list`, `spec`'s spawn/objective/extraction ids); every built mid-rise's collider top measured off
`deli_counter/build` (13.2 m at four storeys to 38.7 m at twelve); `tests/unit/test_terrace_stoop.py`'s
`glb_fixture.write_glb`. Every file LF.

    python patches/patch_lf_heights_by_cause.py --preview _scratch/heights_preview
    python patches/patch_lf_heights_by_cause.py --results-pending
    (python -m pytest -q in level_factory)
    python patches/patch_lf_heights_by_cause.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_heights_by_cause"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
PREVIEW = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
RESULTS = {"RESULT_RHO": "result_rho.txt", "RESULT_FAILING": "result_failing.txt",
           "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.203.0", b"0.204.0"
CHANGELOG_HEAD = "## [0.203.0] - A spent bag is not a full street: the near side deals afresh where a design fits"
SHA = {"packages/pipeline/street_line.py": "12a8dad81f3bba79",
       "packages/pipeline/empties.py": "90f2b69a278cc6c4",
       "apps/cli/commands/__init__.py": "34bb7cc7dc07542a"}
NEW = {"tests/unit/test_urban_heights_by_cause.py": "test_urban_heights_by_cause.py.txt"}

TOP_OLD = "\n\ndef south_reach(extents, rot):\n"
TOP_NEW = (
    "\n\ndef shell_top(glb_path):\n"
    "    \"\"\"The top of a shell's collider hulls above its own floor, metres (glTF y\n"
    "    is up); None when the geometry cannot be read (0.204.0). The urban wall\n"
    "    draws its heights by it (`empties.terrace`): the factory's mid-rises read\n"
    "    13.2 m at four storeys to 38.7 m at twelve, about 3.3 m a storey.\"\"\"\n"
    "    try:\n"
    "        from packages.validation import glb_collision\n"
    "    except ImportError:                       # pragma: no cover - packaging only\n"
    "        return None\n"
    "    reading = glb_collision.collision_solids(Path(glb_path))\n"
    "    if not reading.read or not reading.solids:\n"
    "        return None\n"
    "    return max(s.centre[1] + s.size[1] / 2.0 for s in reading.solids)\n"
    "\n\ndef south_reach(extents, rot):\n")

HELPERS_OLD = "def terrace(rows, extents, stream, roads, span_x, continuous=False):\n"
HELPERS_NEW = (
    "def _target(x, centre, reach, lo, hi):\n"
    "    \"\"\"The height a block standing at ``x`` is drawn toward (0.204.0): ``lo``\n"
    "    across from the action's centre, rising in proportion to the distance from\n"
    "    it, to ``hi`` at ``reach`` metres and beyond.\"\"\"\n"
    "    if reach <= 0:\n"
    "        return lo\n"
    "    return lo + (hi - lo) * min(1.0, abs(x - centre) / reach)\n"
    "\n"
    "\n"
    "def _by_height(bag, extents, heights, x, x_end, centre, reach, lo, hi, prev):\n"
    "    \"\"\"The index on ``bag`` of the shell whose height is nearest the height a\n"
    "    block standing at its own centre is drawn toward (`_target`), among those\n"
    "    that fit before ``x_end``; not ``prev`` while another fits. Ties go to the\n"
    "    deal's order, the end of the bag first. None when nothing fits.\"\"\"\n"
    "    best = None\n"
    "    for i in range(len(bag) - 1, -1, -1):\n"
    "        tx0, tx1, _ty0, _ty1 = _turned(extents[bag[i][\"id\"]], 180)\n"
    "        width = tx1 - tx0\n"
    "        if x + width > x_end:\n"
    "            continue\n"
    "        miss = abs(heights[bag[i][\"id\"]] - _target(x + width / 2.0, centre, reach, lo, hi))\n"
    "        key = (bag[i][\"id\"] == prev, miss)\n"
    "        if best is None or key < best[0]:\n"
    "            best = (key, i)\n"
    "    return None if best is None else best[1]\n"
    "\n"
    "\n"
    "def terrace(rows, extents, stream, roads, span_x, continuous=False, action=None, heights=None):\n")

DOC_OLD = ("    ``continuous`` (0.200.0, factory roadmap 241): the urban street's wall,\n"
           "    with no alley between runs -- one row broken only where a road crosses\n"
           "    the far side. Off, the terrace draws exactly as it did.\"\"\"\n")
DOC_NEW = ("    ``continuous`` (0.200.0, factory roadmap 241): the urban street's wall,\n"
           "    with no alley between runs -- one row broken only where a road crosses\n"
           "    the far side. Off, the terrace draws exactly as it did.\n"
           "\n"
           "    HEIGHTS BY CAUSE (0.204.0, roadmap 241). ``action`` is the x of the\n"
           "    action's centre along the street, ``heights`` {archetype: top, metres}\n"
           "    (`street_line.shell_top`). Given both on a continuous wall, each block is\n"
           "    the one on the bag whose height is nearest the height a block standing at\n"
           "    its centre is drawn toward (`_target`): the shortest design's across from\n"
           "    the action, rising with the distance from it to the tallest's at the\n"
           "    plate's farther end -- the comps' \"the tallest stand furthest away\" (the\n"
           "    factory root's `docs/reference/URBAN_MIDRISE_COMPS.md`), never jitter.\n"
           "    Before it, cold run 9291's seed_9104 stood 5, 7, 5, 10, 8, 6, 4, 12, 6 and\n"
           "    8 storeys from west to east, as the deal fell. Every design is still dealt\n"
           "    once a bag, and a block that does not fit before the plate's end gives way\n"
           "    to the nearest-height one that does. Without either, or on the strip's\n"
           "    terrace, the deal decides alone, exactly as before.\"\"\"\n")

LOOP_OLD = ("    need = 0.0\n"
            "    bag: list = []\n"
            "    while True:\n")
LOOP_NEW = ("    need = 0.0\n"
            "    bag: list = []\n"
            "    by_cause = bool(continuous and action is not None and heights\n"
            "                    and all(heights.get(r[\"id\"]) is not None for r in usable))\n"
            "    if by_cause:\n"
            "        lo = min(heights[r[\"id\"]] for r in usable)\n"
            "        hi = max(heights[r[\"id\"]] for r in usable)\n"
            "        reach = max(float(action) - x, x_end - float(action))\n"
            "    while True:\n")

PICK_OLD = ("        if not bag:\n"
            "            bag = _deal(usable, stream, prev)\n"
            "        pick = bag[-1]\n")
PICK_NEW = ("        if not bag:\n"
            "            bag = _deal(usable, stream, prev)\n"
            "        if by_cause:\n"
            "            at = _by_height(bag, extents, heights, x, x_end, float(action), reach, lo, hi, prev)\n"
            "            if at is None:\n"
            "                break                              # nothing on the bag fits before the plate's end\n"
            "        else:\n"
            "            at = len(bag) - 1\n"
            "        pick = bag[at]\n")

POP_OLD = ("        bag.pop()\n"
           "        prev = pick[\"id\"]\n"
           "        x += width\n"
           "        in_run += 1\n")
POP_NEW = ("        bag.pop(at)\n"
           "        prev = pick[\"id\"]\n"
           "        x += width\n"
           "        in_run += 1\n")

CALL_OLD = ("        _row = {r[\"id\"]: r for r in _empty_rows}\n"
            "        placed_e, need_half = _empties.terrace(\n"
            "            _empty_rows, _ext, site_variation.stream(int(seed) ^ 0x5E3A11),\n"
            "            roads, spec[\"ground\"][\"size_x\"], continuous=_urban)\n")
CALL_NEW = ("        _row = {r[\"id\"]: r for r in _empty_rows}\n"
            "        # HEIGHTS BY CAUSE (0.204.0, roadmap 241): an urban wall stands its lowest\n"
            "        # blocks across from the action and rises with distance from it. The\n"
            "        # action's centre is the middle of the span the spawn, objective and\n"
            "        # extraction buildings cover along the street; the heights are read off\n"
            "        # the shells. A strip brief reads neither.\n"
            "        _action, _heights = None, None\n"
            "        if _urban:\n"
            "            _ids = {spec.get(k) for k in (\"spawn\", \"objective\", \"extraction\")} - {None}\n"
            "            _act = [_empties.building_rect(b[\"at\"], b[\"rot\"], fp)\n"
            "                    for b, fp in zip(buildings, fp_list) if fp and b.get(\"id\") in _ids]\n"
            "            if _act:\n"
            "                _action = (min(r[0] for r in _act) + max(r[1] for r in _act)) / 2.0\n"
            "            _heights = {r[\"id\"]: _sl.shell_top(r[\"glb\"]) for r in _empty_rows}\n"
            "            if _action is None or any(v is None for v in _heights.values()):\n"
            "                print(\"  URBAN_HEIGHTS_UNREAD: the action's centre or a mid-rise's height could \"\n"
            "                      \"not be read -- the wall is dealt without heights by cause\", file=sys.stderr)\n"
            "        placed_e, need_half = _empties.terrace(\n"
            "            _empty_rows, _ext, site_variation.stream(int(seed) ^ 0x5E3A11),\n"
            "            roads, spec[\"ground\"][\"size_x\"], continuous=_urban,\n"
            "            action=_action, heights=_heights)\n"
            "        if _urban and _action is not None:\n"
            "            print(f\"[site] the urban wall's heights by cause: lowest across from x {_action:.1f}, \"\n"
            "                  f\"rising to the plate's ends\")\n")

EDITS = {
    "packages/pipeline/street_line.py": [(TOP_OLD, TOP_NEW)],
    "packages/pipeline/empties.py": [(HELPERS_OLD, HELPERS_NEW), (DOC_OLD, DOC_NEW), (LOOP_OLD, LOOP_NEW),
                                     (PICK_OLD, PICK_NEW), (POP_OLD, POP_NEW)],
    "apps/cli/commands/__init__.py": [(CALL_OLD, CALL_NEW)],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _edited():
    writes = {}
    for rel, edits in EDITS.items():
        raw = (LF / rel).read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:70])
            text = text.replace(old, new)
        compile(text, rel, "exec")
        writes[rel] = (text, eol)
    return writes


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.204.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.204.0: results filled")


def preview(out):
    out = pathlib.Path(out)
    for rel, (text, eol) in _edited().items():
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode("utf-8").replace(b"\n", eol))
    print(f"previewed under {out}; Level Factory untouched")


def main():
    if PREVIEW:
        return preview(PREVIEW)
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.204.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.204.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (LF / rel).exists(), ("already applied", rel)
    writes = _edited()
    news = {r: (SRC / s).read_bytes().replace(b"\r\n", b"\n") for r, s in NEW.items()}
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for rel, (body, e) in writes.items():
        (LF / rel).write_bytes(body.encode("utf-8").replace(b"\n", e))
    for r, data in news.items():
        (LF / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.203.0 -> 0.204.0")


if __name__ == "__main__":
    main()
