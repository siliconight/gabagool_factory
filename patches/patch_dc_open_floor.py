"""Deli Counter 0.223.0: an open floor nobody named -- layout_lint L26 (the factory's roadmap 255, found tracing
the walker's walk of 2026-10-14, finding 5).

  tactical.py               `OPEN_FLOOR_M`, spelled once where it was spelled four times; `open_edge` returns
                            where; `shared_open_edge` asks it
  layout_lint.py            `_story_parts`, one reading of a storey's partitions; `open_floors`,
                            `open_floor_findings` (L26); registered after L24
  schema/level.schema.json  a room's `open_to`
  test_open_floor.py        new, from `dc_open_floor/test_open_floor.py.txt`
  open_floor_baseline.py    new, from `dc_open_floor/open_floor_baseline.py.txt`; run it once after this
                            applies, so `open_floor_baseline.json` exists before the suite

Every file's sha16 pinned and every anchor asserted once, nothing written until all matched. CHANGELOG and
VERSION from `dc_open_floor/CHANGELOG_0.223.0.md`; `--results-pending` leaves RESULT_CENSUS and RESULT_SUITE to
`--fill`. `DC_ROOT` points it at a copy.

Read before it was written, in this session: tactical.py 1-66 (the head, `MIN_OPENING_WIDTH`), 68-113
(`shared_open_edge` whole) and 176-200 (`build_graph`'s use); layout_lint.py 48-125 (the room helpers and the
graph's partition loop), 964-1062 (`_reach_from_ext`, its partition tuples), 1082-1108 (L24), 1330-1354
(`lint_spec`'s registrations), 1500-1506 (the exit code counts FAILs alone); check.py 66-82 (the lint's return
code is or-ed in); schema/level.schema.json 918-990 (the rooms block, `additionalProperties: false`);
test_walk_reach.py whole (the fixture and the baseline pattern); walk_reach_baseline.json's shape; the census
`partition_gaps.py --min 1.2` (32 stretches in 20 of 446 specs). Every file LF.

    python patches/patch_dc_open_floor.py --results-pending
    (in deli_counter: python open_floor_baseline.py; python -m pytest -q)
    python patches/patch_dc_open_floor.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_open_floor"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_CENSUS": "result_census.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.222.0", b"0.223.0"
CHANGELOG_HEAD = "## [0.222.0] - the delis' basement divider runs wall to wall, and the utility room gets a door"
SHA = {"tactical.py": "936f3c87274568a9",
       "layout_lint.py": "541cb527a4c356f6",
       "schema/level.schema.json": "b0e7210b49c50b83"}
NEW = {"test_open_floor.py": "test_open_floor.py.txt",
       "open_floor_baseline.py": "open_floor_baseline.py.txt"}

TAC_CONST_OLD = "MIN_OPENING_WIDTH = 0.8   # m; below this a passage is too tight\n"
TAC_CONST_NEW = TAC_CONST_OLD + (
    "#: Two same-storey rooms whose shared edge no partition covers for this much are one\n"
    "#: continuous floor (`open_edge`, `shared_open_edge`). 0.223.0 lifted it out of four\n"
    "#: literals so layout_lint L26 names exactly the floors the engine walks.\n"
    "OPEN_FLOOR_M = 1.2\n")

TAC_DOC1_OLD = "    for at least 1.2 m? Then they are one continuous floor.\n"
TAC_DOC1_NEW = "    for at least `OPEN_FLOOR_M`, 1.2 m? Then they are one continuous floor.\n"
TAC_DOC2_OLD = "    every same-axis partition lying on that line, must leave 1.2 m.\n"
TAC_DOC2_NEW = "    every same-axis partition lying on that line, must leave `OPEN_FLOOR_M`.\n"

TAC_BODY_OLD = (
    "    ax0, ay0, ax1, ay1 = a\n"
    "    bx0, by0, bx1, by1 = b\n"
    "    # vertical shared edge (a's right == b's left or vice versa)\n"
    "    for x_edge, lo, hi in ((ax1, max(ay0, by0), min(ay1, by1))\n"
    "                           if abs(ax1 - bx0) < 0.05 else (None, 0, 0),\n"
    "                           (bx1, max(ay0, by0), min(ay1, by1))\n"
    "                           if abs(bx1 - ax0) < 0.05 else (None, 0, 0)):\n"
    "        if x_edge is not None and hi - lo >= 1.2:\n"
    "            covered = 0.0\n"
    "            for axis, pos, start, end in parts:\n"
    "                if axis != \"Y\":\n"
    "                    continue\n"
    "                if abs(pos - x_edge) < 0.05:\n"
    "                    covered += max(0.0, min(end, hi) - max(start, lo))\n"
    "            if (hi - lo) - covered >= 1.2:\n"
    "                return True\n"
    "    # horizontal shared edge\n"
    "    for y_edge, lo, hi in ((ay1, max(ax0, bx0), min(ax1, bx1))\n"
    "                           if abs(ay1 - by0) < 0.05 else (None, 0, 0),\n"
    "                           (by1, max(ax0, bx0), min(ax1, bx1))\n"
    "                           if abs(by1 - ay0) < 0.05 else (None, 0, 0)):\n"
    "        if y_edge is not None and hi - lo >= 1.2:\n"
    "            covered = 0.0\n"
    "            for axis, pos, start, end in parts:\n"
    "                if axis != \"X\":\n"
    "                    continue\n"
    "                if abs(pos - y_edge) < 0.05:\n"
    "                    covered += max(0.0, min(end, hi) - max(start, lo))\n"
    "            if (hi - lo) - covered >= 1.2:\n"
    "                return True\n"
    "    return False\n")
TAC_BODY_NEW = (
    "    return open_edge(a, b, parts) is not None\n"
    "\n"
    "\n"
    "def open_edge(a, b, parts):\n"
    "    \"\"\"The edge two same-storey room rects meet along, where the partitions on\n"
    "    that line leave at least `OPEN_FLOOR_M` of it uncovered: ``(axis, pos, lo,\n"
    "    hi, uncovered)`` -- the line's axis (\"Y\" for a vertical edge at x = pos, \"X\"\n"
    "    for a horizontal one at y = pos), the shared span along it and the length no\n"
    "    partition covers -- or None. `shared_open_edge`'s body since 0.197.0,\n"
    "    returned so layout_lint L26 can say where (0.223.0). The vertical edges are\n"
    "    asked first, as they were.\"\"\"\n"
    "    ax0, ay0, ax1, ay1 = a\n"
    "    bx0, by0, bx1, by1 = b\n"
    "    edges = []\n"
    "    if abs(ax1 - bx0) < 0.05:\n"
    "        edges.append((\"Y\", ax1, max(ay0, by0), min(ay1, by1)))\n"
    "    if abs(bx1 - ax0) < 0.05:\n"
    "        edges.append((\"Y\", bx1, max(ay0, by0), min(ay1, by1)))\n"
    "    if abs(ay1 - by0) < 0.05:\n"
    "        edges.append((\"X\", ay1, max(ax0, bx0), min(ax1, bx1)))\n"
    "    if abs(by1 - ay0) < 0.05:\n"
    "        edges.append((\"X\", by1, max(ax0, bx0), min(ax1, bx1)))\n"
    "    for axis, line, lo, hi in edges:\n"
    "        if hi - lo < OPEN_FLOOR_M:\n"
    "            continue\n"
    "        covered = 0.0\n"
    "        for p_axis, pos, start, end in parts:\n"
    "            if p_axis == axis and abs(pos - line) < 0.05:\n"
    "                covered += max(0.0, min(end, hi) - max(start, lo))\n"
    "        uncovered = (hi - lo) - covered\n"
    "        if uncovered >= OPEN_FLOOR_M:\n"
    "            return axis, line, lo, hi, uncovered\n"
    "    return None\n")

LINT_DEF_OLD = "def _reach_from_ext(spec, walk_only=False):\n"
LINT_DEF_NEW = (
    "def _story_parts(spec, st):\n"
    "    \"\"\"A storey's partitions as `tactical.open_edge` reads them, ``(axis, pos,\n"
    "    start, end)``; a partition with no start or end runs the footprint, as\n"
    "    `_opening_xy` reads it. The open-floor search's own reading (0.197.0), one\n"
    "    helper since 0.223.0 because L26 asks it too.\"\"\"\n"
    "    hx, hy = spec[\"footprint_x\"] / 2, spec[\"footprint_y\"] / 2\n"
    "    parts = []\n"
    "    for p in spec.get(\"partitions\", []):\n"
    "        if p.get(\"story\", 0) != st:\n"
    "            continue\n"
    "        lo, hi = (-hy, hy) if p[\"axis\"] == \"Y\" else (-hx, hx)\n"
    "        parts.append((p[\"axis\"], p[\"pos\"],\n"
    "                      lo if p.get(\"start\") is None else p[\"start\"],\n"
    "                      hi if p.get(\"end\") is None else p[\"end\"]))\n"
    "    return parts\n"
    "\n"
    "\n" + LINT_DEF_OLD)

LINT_LOOP_OLD = (
    "    for st, rs in by.items():\n"
    "        parts = []\n"
    "        for p in spec.get(\"partitions\", []):\n"
    "            if p.get(\"story\", 0) != st:\n"
    "                continue\n"
    "            lo, hi = (-hy, hy) if p[\"axis\"] == \"Y\" else (-hx, hx)\n"
    "            parts.append((p[\"axis\"], p[\"pos\"],\n"
    "                          lo if p.get(\"start\") is None else p[\"start\"],\n"
    "                          hi if p.get(\"end\") is None else p[\"end\"]))\n"
    "        for i, ra in enumerate(rs):\n")
LINT_LOOP_NEW = (
    "    for st, rs in by.items():\n"
    "        parts = _story_parts(spec, st)\n"
    "        for i, ra in enumerate(rs):\n")

LINT_L24_END_OLD = "            for r in walk_unreachable(spec)]\n"
LINT_L24_END_NEW = LINT_L24_END_OLD + '''

def open_floors(spec):
    """Two rooms on one storey that tactical's rule joins as one floor -- their
    shared edge uncovered by any partition for `tactical.OPEN_FLOOR_M` -- and
    that neither room's `open_to` names (L26). Dicts in spec order:
    ``{story, a, b, axis, pos, lo, hi, uncovered}``; the spec is not changed."""
    import tactical
    out = []
    by = _rooms_by_story(spec)
    for st in sorted(by):
        rs = by[st]
        parts = _story_parts(spec, st)
        for i, ra in enumerate(rs):
            for rb in rs[i + 1:]:
                if ra["id"] == rb["id"]:
                    continue
                edge = tactical.open_edge(ra["bounds"], rb["bounds"], parts)
                if edge is None:
                    continue
                if rb["id"] in (ra.get("open_to") or ()) or ra["id"] in (rb.get("open_to") or ()):
                    continue
                axis, pos, lo, hi, uncovered = edge
                out.append({"story": st, "a": ra["id"], "b": rb["id"], "axis": axis, "pos": pos,
                            "lo": lo, "hi": hi, "uncovered": uncovered})
    return out


def open_floor_findings(spec):
    """L26 (advisory WARN, 0.223.0): an open floor nobody named. The walker's
    walk of 2026-10-14, finding 5: the delis' basement divider stopped 7 m
    short of each wall and the vault stood open to the utility room, and no
    spec said so -- 59 such stretches in 31 of 446 specs then (the factory's
    roadmap 255). Where two rooms meet along a wall line no partition covers
    for `tactical.OPEN_FLOOR_M`, tactical joins them as one floor and the
    engine walks it; this names each such pair unless a room's `open_to` says
    it is meant. `open_floor_baseline.json` freezes today's for the walker to
    sort, and test_open_floor fails on a new one. Some are lobbies flowing into
    bullpens; this does not say which."""
    return ["L26 open floor nobody named: '%s' and '%s' (story %s) meet along %s = %g from %g to %g "
            "with %.2f m of it uncovered by any partition; the engine walks it as one floor -- say so "
            "(`open_to` on either room) or build the wall"
            % (f["a"], f["b"], f["story"], "y" if f["axis"] == "X" else "x", f["pos"], f["lo"], f["hi"],
               f["uncovered"])
            for f in open_floors(spec)]
'''

LINT_REG_OLD = "    warns += walk_reach_findings(spec)      # L24 a room only a breach, window or drop reaches\n"
LINT_REG_NEW = LINT_REG_OLD + "    warns += open_floor_findings(spec)      # L26 an open floor nobody named\n"

SCHEMA_OLD = ('          "ceiling_material": {\n'
              '            "type": [\n'
              '              "string",\n'
              '              "null"\n'
              '            ]\n'
              '          }\n'
              '        }\n')
SCHEMA_NEW = ('          "ceiling_material": {\n'
              '            "type": [\n'
              '              "string",\n'
              '              "null"\n'
              '            ]\n'
              '          },\n'
              '          "open_to": {\n'
              '            "type": "array",\n'
              '            "items": {\n'
              '              "type": "string"\n'
              '            }\n'
              '          }\n'
              '        }\n')

EDITS = {"tactical.py": [(TAC_CONST_OLD, TAC_CONST_NEW), (TAC_DOC1_OLD, TAC_DOC1_NEW), (TAC_DOC2_OLD, TAC_DOC2_NEW),
                         (TAC_BODY_OLD, TAC_BODY_NEW)],
         "layout_lint.py": [(LINT_DEF_OLD, LINT_DEF_NEW), (LINT_LOOP_OLD, LINT_LOOP_NEW),
                            (LINT_L24_END_OLD, LINT_L24_END_NEW), (LINT_REG_OLD, LINT_REG_NEW)],
         "schema/level.schema.json": [(SCHEMA_OLD, SCHEMA_NEW)]}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert VERSION in (DC / "VERSION").read_bytes(), (DC / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(DC / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.223.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Deli Counter 0.223.0: results filled")


def main():
    if FILL:
        return fill()
    vraw = (DC / "VERSION").read_bytes()
    assert VERSION_WAS in vraw and VERSION not in vraw, vraw
    entry = (SRC / "CHANGELOG_0.223.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.223.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel in SHA:
        p = DC / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in EDITS[rel]:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    for rel, name in NEW.items():
        p = DC / rel
        assert not p.exists(), (rel, "already exists")
        writes[p] = (SRC / name).read_bytes().replace(b"\r\n", b"\n")
    cl = DC / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (DC / "VERSION").write_bytes(vraw.replace(VERSION_WAS, VERSION))
    print("Deli Counter 0.222.0 -> 0.223.0")


if __name__ == "__main__":
    main()
