"""Lot 0.121.0: every planner that keeps clear of what already stands keeps clear of the Empties (factory roadmap 241,
the urban street's near side).

Anchored edits to `lot.py`, each asserted exactly once and the file's sha16 pinned, nothing written until all
matched: the blockers' rects read once before the parking fields (`site_spawns.blocker_rects`, margin 0), and
the four `standing` lists -- fields and their cars, pylons and dumpsters, pads and bags, cover -- start with
them. `tests/test_blockers_stand.py` NEW (`lot_blockers_stand/test_blockers_stand.py.txt`). CHANGELOG and
VERSION from `lot_blockers_stand/CHANGELOG_0.121.0.md`; `--results-pending` leaves RESULT_ keys to `--fill`.

Read before it was written, in this session: `assemble` from the parking fields to the cover plan (the four
`standing` lists, each started empty and filled with the cover so far; one function scope, no top-level def
between); `site_fields.plan_fields`, `site_dumpsters.plan_dumpsters` and `site_cover.plan_cover`, whose
`standing` is "the plan rects of what already stands" -- obstacles, never buildings to serve; `site_yards`;
`site_spawns.blocker_rects` and `site_extent.blocker_rect` (world extents, no rotation); the example compound
the test assembles. Every file LF.

    python patches/patch_lot_blockers_stand.py --results-pending
    (docs/findings/urban_street/lot_replay.py replay after + diff before_a after; python -m pytest -q in lot)
    python patches/patch_lot_blockers_stand.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_blockers_stand"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_REPLAY": "result_replay.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Lot 0.120.2", b"Lot 0.121.0"
CHANGELOG_HEAD = "## 0.120.2 - the cover fallback is the contract's cell"
SHA = {"lot.py": "d997b6984a0399f1"}
NEW = {"tests/test_blockers_stand.py": "test_blockers_stand.py.txt"}

EDITS = [
    ("    _rects_f = {}\n",
     "    # THE EMPTIES STAND (0.121.0, factory roadmap 241). Every planner below\n"
     "    # that keeps clear of what already stands -- fields and their cars,\n"
     "    # pylons and dumpsters, pads and bags, cover -- keeps clear of the\n"
     "    # blockers too. They stood only across the road, where none of these\n"
     "    # places anything, until the urban street's near side stood them in the\n"
     "    # gaps beside the mission's buildings. Obstacles, as built; never a\n"
     "    # building a field or a dumpster serves.\n"
     "    import site_spawns as _blk_spawns\n"
     "    _blockers = _blk_spawns.blocker_rects(site_spec, margin=0.0)\n"
     "    _rects_f = {}\n"),
    ("    _standing_f = []\n", "    _standing_f = list(_blockers)\n"),
    ("    _standing0 = []\n", "    _standing0 = list(_blockers)\n"),
    ("    _standing_y = []\n", "    _standing_y = list(_blockers)\n"),
    ("    standing = []\n", "    standing = list(_blockers)\n"),
]


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (LOT / "VERSION").read_bytes().strip() == VERSION, (LOT / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LOT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.121.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Lot 0.121.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.121.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## 0.121.0 - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (LOT / rel).exists(), ("already applied", rel)
    rel = "lot.py"
    raw = (LOT / rel).read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    eol = _eol(raw, rel)
    text = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in EDITS:
        assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:60])
        text = text.replace(old, new)
    compile(text, rel, "exec")
    news = {r: (SRC / s).read_bytes().replace(b"\r\n", b"\n") for r, s in NEW.items()}
    cl = LOT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    (LOT / rel).write_bytes(text.encode("utf-8").replace(b"\n", eol))
    for r, data in news.items():
        (LOT / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.120.2 -> 0.121.0")


if __name__ == "__main__":
    main()
