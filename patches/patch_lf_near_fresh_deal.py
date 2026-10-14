"""Level Factory 0.203.0: a spent bag is not a full street -- the near side deals afresh where a design fits and the
bag's remainder does not (factory roadmap 241).

`empties.infill` left a room open whenever what was left in the bag was too wide for it: cold run 9289's seed_9104
kept a 6.70 m room its 6.6 m block fits, that block dealt already. On the test street (rooms 42, 22, 32 m; designs
15, 24, 6.6 m; forty seeds) 0.202.0 left 58 of 120 rooms with a design's width or more empty.

Anchored edits to `packages/pipeline/empties.py`, each asserted exactly once and the file's sha16 pinned, nothing
written until all matched: `_fitting` (the shells no wider than a room, from the bag's end back) before `infill`;
`infill`'s fits read through it, and where none fits and a design does, a fresh deal behind the remainder;
its docstring says so. `tests/unit/test_near_side_fresh_deal.py` NEW (`lf_near_fresh_deal/...py.txt`).
CHANGELOG and VERSION from `lf_near_fresh_deal/CHANGELOG_0.203.0.md`; `--results-pending` leaves RESULT_ keys to
`--fill`.

Read before it was written, in this session: `empties.py` (`_deal`, which deals from the END of its list and
swaps an immediate repeat; `infill` whole: the stops, the room, `if not bag`, the fits, the repeat sort, the lane
check, the pop); `tests/unit/test_urban_near_side.py`'s street. Every file LF.

    python patches/patch_lf_near_fresh_deal.py --results-pending
    (python -m pytest -q in level_factory)
    python patches/patch_lf_near_fresh_deal.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_near_fresh_deal"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_COLD": "result_cold.txt", "RESULT_FAILING": "result_failing.txt",
           "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.202.0", b"0.203.0"
CHANGELOG_HEAD = ("## [0.202.0] - What a pick counts: the grade breaks a tie, and two kinds of major are shown and "
                  "not counted")
SHA = {"packages/pipeline/empties.py": "d158286ec058b46d"}
NEW = {"tests/unit/test_near_side_fresh_deal.py": "test_near_side_fresh_deal.py.txt"}

DOC_OLD = ("    deals them (`_deal`), and where the next one is wider than the room left before an obstacle, the next\n"
           "    narrower one on the bag is tried; a room no shell fits stays open, a gap the street keeps.\n")
DOC_NEW = ("    deals them (`_deal`), and where the next one is wider than the room left before an obstacle, the next\n"
           "    narrower one on the bag is tried. Where nothing left on the bag fits and some design does, a fresh\n"
           "    deal goes behind what was left (0.203.0). A room no design fits stays open, a gap the street keeps.\n")

HELPER_OLD = "def infill(rows, extents, stream, roads, span_x, buildings):\n"
HELPER_NEW = ("def _fitting(bag, extents, room):\n"
              "    \"\"\"Indices into ``bag`` of the shells no wider than ``room``, from its end -- the next dealt --\n"
              "    back.\"\"\"\n"
              "    return [i for i in range(len(bag) - 1, -1, -1)\n"
              "            if _turned(extents[bag[i][\"id\"]], 0)[1] - _turned(extents[bag[i][\"id\"]], 0)[0] <= room + 1e-9]\n"
              "\n"
              "\n"
              "def infill(rows, extents, stream, roads, span_x, buildings):\n")

FITS_OLD = ("        if not bag:\n"
            "            bag = _deal(usable, stream, prev)\n"
            "        fits = [i for i in range(len(bag) - 1, -1, -1)\n"
            "                if _turned(extents[bag[i][\"id\"]], 0)[1] - _turned(extents[bag[i][\"id\"]], 0)[0] <= room + 1e-9]\n")
FITS_NEW = ("        if not bag:\n"
            "            bag = _deal(usable, stream, prev)\n"
            "        fits = _fitting(bag, extents, room)\n"
            "        # A SPENT BAG IS NOT A FULL STREET (0.203.0, roadmap 241). The deal shows every design once\n"
            "        # before a new bag, and a room the bag's remainder was too wide for stayed open though the\n"
            "        # next bag held a design that fits: cold run 9289's seed_9104 kept a 6.70 m room its 6.6 m\n"
            "        # block fits. So where nothing left fits and some design does, a fresh deal goes behind the\n"
            "        # remainder, which still shows first where it fits; a room no design fits asks nothing of\n"
            "        # the stream, and the bag never grows by a deal that could not help.\n"
            "        if not fits and _fitting(usable, extents, room):\n"
            "            bag = _deal(usable, stream, prev) + bag\n"
            "            fits = _fitting(bag, extents, room)\n")

EDITS = {"packages/pipeline/empties.py": [(DOC_OLD, DOC_NEW), (HELPER_OLD, HELPER_NEW), (FITS_OLD, FITS_NEW)]}


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.203.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.203.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.203.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.203.0] - "), entry[:40]
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
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:70])
            text = text.replace(old, new)
        compile(text, rel, "exec")
        writes[rel] = (text, eol)
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
    print("Level Factory 0.202.0 -> 0.203.0")


if __name__ == "__main__":
    main()
