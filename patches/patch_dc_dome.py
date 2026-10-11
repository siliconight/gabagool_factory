"""Deli Counter 0.208.0: a home's room hangs a dome (roadmap 229's species step, beside Zoo 1.98.0
and Lux 0.75.0).

Anchored edits in `lights.py` (a home's room -- `_home_room`, by the building or by the room's own
words -- writes `dome` anchors where it wrote `fluorescent`; the bulb branch says it is no home)
and `test_fixture_rows.py` (the row helper reads a dome as a row; one test pins which rooms take
which); each file pinned by hash and each anchor asserted once, nothing written on a miss; the
files' own line endings kept. Applies on 0.207.1. CHANGELOG and VERSION from
`dc_dome/CHANGELOG_0.208.0.md`; `--results-pending` leaves RESULT_SUITE and RESULT_LIBRARY to
`--fill`. The library must be rebuilt after it lands (`python build.py --all`): each shell's
`lights.json` is where the type ships.

    python patches/patch_dc_dome.py --results-pending && cd deli_counter && python -m pytest -q
    python patches/patch_dc_dome.py --fill
    DC_ROOT=<copy> python patches/patch_dc_dome.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_dome"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt", "RESULT_LIBRARY": "result_library.txt"}
VERSION_WAS, VERSION = b"Deli Counter 0.207.1", b"Deli Counter 0.208.0"
CHANGELOG_HEAD = "## [0.207.1] - a home's room takes a fixture a bay, not one whatever its size\n"
SHA = {"lights.py": "3e8dbca06a2cab0c", "test_fixture_rows.py": "f1bdc66c2b4d2185"}

MOODY_OLD = ("        if moody:\n"
             "            rot, count, spacing = _row_for_bounds(bounds)\n")
MOODY_NEW = ("        if moody:\n"
             "            home = False          # a bare bulb below grade or over the take\n"
             "            rot, count, spacing = _row_for_bounds(bounds)\n")
TYPE_OLD = '                "type": "pendant" if moody else "fluorescent",\n'
TYPE_NEW = ('                # A HOME\'S DOME (0.208.0, roadmap 229\'s species step): a home\'s\n'
            '                # room hangs a flush-mount dome a bay (Zoo 1.98.0\'s hardware,\n'
            '                # Lux 0.75.0\'s warm lamp under its bowl), not a 2 x 4 office\n'
            '                # troffer; the rows are the home rule\'s, unchanged.\n'
            '                "type": "pendant" if moody else ("dome" if home else "fluorescent"),\n')

ROWS_OLD = ('def _rows(anchors, room):\n'
            '    return [a for a in anchors if a["type"] == "fluorescent" and a["room"] == room]\n')
ROWS_NEW = ('def _rows(anchors, room):\n'
            '    # a home\'s room lays the same rows as domes (0.208.0)\n'
            '    return [a for a in anchors if a["type"] in ("fluorescent", "dome") and a["room"] == room]\n')
DOME_TEST = '''

def test_a_homes_room_hangs_domes_and_a_shops_keeps_its_troffers():
    """0.208.0, roadmap 229's species step: the home rule's rows are domes -- in a
    residence, and in a residence-like room inside a shop (the deli's hideout) --
    and a shop's own room keeps its fluorescent rows."""
    home = {"id": "living_room", "story": 0, "bounds": [0.0, 0.0, 9.0, 7.0], "role": "connector",
            "center": [4.5, 3.5, 0.0]}
    hideout = {"id": "apartment_hideout", "story": 1, "bounds": [-2.0, -14.0, 19.0, 2.0],
               "role": "fortifiable", "center": [8.5, -6.0, 3.3]}
    office = {"id": "back_office", "story": 0, "bounds": [30.0, 0.0, 39.0, 7.0], "role": "connector",
              "center": [34.5, 3.5, 0.0]}
    house = _derive([home], residence=True)
    shop = _derive([hideout, office])
    assert _rows(house, "living_room") and _rows(shop, "apartment_hideout")
    assert not [a for a in house if a["room"] == "living_room" and a["type"] == "fluorescent"]
    assert all(a["type"] == "dome" for a in _rows(house, "living_room"))
    assert all(a["type"] == "dome" for a in _rows(shop, "apartment_hideout"))
    assert _rows(shop, "back_office") and all(
        a["type"] == "fluorescent" for a in _rows(shop, "back_office"))
'''


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = DC / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def fill():
    assert (DC / "VERSION").read_bytes().strip() == VERSION, (DC / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    targets = [(DC / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.208.0.md", "the entry")]
    writes = {}
    for path, rel in targets:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Deli Counter 0.208.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("DC_ROOT"):
        sys.exit("refusing: --draft is for a DC_ROOT copy, never the repo")
    assert (DC / "VERSION").read_bytes().strip() == VERSION_WAS, (DC / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.208.0.md")
    assert entry.startswith("## [0.208.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"

    lp, l_eol, lights = _read("lights.py")
    assert '"dome"' not in lights, "already applied"
    lights = _once(lights, MOODY_OLD, MOODY_NEW, "the bulb branch")
    lights = _once(lights, TYPE_OLD, TYPE_NEW, "the anchor's type")
    tp, t_eol, tests = _read("test_fixture_rows.py")
    tests = _once(tests, ROWS_OLD, ROWS_NEW, "the row helper")
    assert tests.endswith("\n")
    tests = tests.rstrip("\n") + "\n" + DOME_TEST

    cl = DC / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    # every anchor matched: now write
    lp.write_bytes(lights.replace("\n", l_eol.decode()).encode("utf-8"))
    tp.write_bytes(tests.replace("\n", t_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (DC / "VERSION").write_bytes(VERSION)
    print("Deli Counter 0.207.1 -> 0.208.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
