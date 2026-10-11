"""Deli Counter 0.207.1: a home's room takes a fixture a bay, not one whatever its size (roadmap 229).

Cold run 9232's deli hung one troffer over a 21 x 16 m hideout. Anchored edits in `lights.py`
(the constant, the home branch of `_rows_for_room`, its docstring) and one test appended to
`test_fixture_rows.py`, each pinned by hash and asserted once, nothing written on a miss; the
file's own line endings kept. CHANGELOG and VERSION from `dc_home_bays/CHANGELOG_0.207.1.md`.
Then, chained:

    python patches/patch_dc_home_bays.py --suite-pending && cd deli_counter && python -m pytest -q

and `python build.py --all` for the library; `--draft` applies to a `DC_ROOT` copy.
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_home_bays"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv
SHA = {"lights.py": "0cf6c5b7e3dbee7a", "test_fixture_rows.py": "1f203a41e41bc2bd"}
VERSION_WAS, VERSION = b"Deli Counter 0.207.0", b"Deli Counter 0.207.1"
CHANGELOG_HEAD = "## [0.207.0] - ceiling rows over the aisles, between the shelf runs\n"

CONST_OLD = "_HOME_WORDS = (\"apartment\", \"hideout\", \"bedroom\", \"living\", \"flat\", \"bedsit\")\n"
CONST_NEW = CONST_OLD + (
    "#: A HOME IS LIT A ROOM AT A TIME (0.207.1): one ceiling fixture a bay the\n"
    "#: size of an ordinary room (the guide's \"by room\": a pendant or flush mount\n"
    "#: over the sink, one pendant in a bedroom; docs/reference/\n"
    "#: INDOOR_FIXTURE_PLACEMENT_GUIDE.md in the factory). A home's room within\n"
    "#: one bay keeps its one fixture at its centre; a bigger one -- cold run\n"
    "#: 9232's 21 x 16 m hideout, dark at both ends under one troffer -- takes\n"
    "#: a grid of bays at this spacing, the fixtures at the bays' centres.\n"
    "_HOME_SPACING = 7.0\n")
DOC_OLD = (
    "    pitch inside its band. A home's room is one fixture at its centre\n"
    "    whatever its size: a line of one is not a line.\n")
DOC_NEW = (
    "    pitch inside its band. A home's room is one fixture at its centre while\n"
    "    it is one bay (`_HOME_SPACING`), and a fixture a bay beyond that, at the\n"
    "    bays' centres (0.207.1): a line of one is not a line, and a hall is not\n"
    "    a bedsit.\n")
HOME_OLD = (
    "    if residence:\n"
    "        return [(rot, round(cx, 3), round(cy, 3), 1, 0.0)]\n"
    "    length = dx if along_x else dy\n")
HOME_NEW = (
    "    length, width = (dx, dy) if along_x else (dy, dx)\n"
    "    if residence:\n"
    "        # a fixture a bay (0.207.1): WOOD's row rule at the bay's spacing, the\n"
    "        # lines at the bays' centres, never snapped -- a home hangs its fixture\n"
    "        # from the middle of the room; one bay is the one fixture it always was\n"
    "        b = _HOME_SPACING\n"
    "        n_rows = max(1, min(_MAX_ROWS, int(-(-(width / b - _ROW_SLACK) // 1))))\n"
    "        count = max(1, min(_MAX_FIXTURES, int(round(length / b))))\n"
    "        while n_rows * count > _MAX_LAMPS_ROOM and count > 1:\n"
    "            count -= 1\n"
    "        spacing = round(length / count, 3) if count > 1 else 0.0\n"
    "        rows = []\n"
    "        for k in range(n_rows):\n"
    "            line = (cy if along_x else cx) + (k + 0.5) * width / n_rows - width / 2.0\n"
    "            if along_x:\n"
    "                rows.append((rot, round(cx, 3), round(line, 3), count, spacing))\n"
    "            else:\n"
    "                rows.append((rot, round(line, 3), round(cy, 3), count, spacing))\n"
    "        return rows\n")
# 0.206.1's test pinned the hideout at ONE fixture; the bay rule is the point of this release
TEST_OLD = (
    "    rows = _rows(_derive([r]), \"apartment_hideout\")\n"
    "    assert len(rows) == 1 and rows[0][\"row\"] == {\"count\": 1, \"spacing\": 0.0}\n"
    "    assert rows[0][\"pos\"][:2] == [8.5, -6.0]\n")
TEST_NEW = (
    "    rows = _rows(_derive([r]), \"apartment_hideout\")\n"
    "    # the home rule, not the office ceiling: a fixture a bay (0.207.1), two rows of three at\n"
    "    # the bays' centres rather than three rows of four on the tile grid\n"
    "    assert len(rows) == 2 and all(a[\"row\"] == {\"count\": 3, \"spacing\": 7.0} for a in rows)\n"
    "    assert [a[\"pos\"][1] for a in rows] == [-10.0, -2.0]\n")
TEST_ADDED = (
    "\n\ndef test_a_big_home_room_takes_a_fixture_a_bay():\n"
    "    # cold run 9232: the deli's 21 x 16 m hideout read dark at both ends under one troffer;\n"
    "    # at a 7 m bay it is two rows of three at the bays' centres, 7 m apart along, no snap\n"
    "    r = {\"id\": \"apartment_hideout\", \"story\": 1, \"bounds\": [-2.0, -14.0, 19.0, 2.0],\n"
    "         \"role\": \"fortifiable\", \"center\": [8.5, -6.0, 3.3]}\n"
    "    rows = _rows(_derive([r]), \"apartment_hideout\")\n"
    "    assert [a[\"id\"] for a in rows] == [\"apartment_hideout_ceiling\", \"apartment_hideout_ceiling_r1\"]\n"
    "    assert [a[\"pos\"][1] for a in rows] == [-10.0, -2.0]\n"
    "    assert all(a[\"row\"] == {\"count\": 3, \"spacing\": 7.0} and a[\"pos\"][0] == 8.5 for a in rows)\n"
    "    # a bedroom is one bay and keeps its one fixture at its centre\n"
    "    bed = {\"id\": \"bedroom\", \"story\": 1, \"bounds\": [0.0, 0.0, 4.0, 5.0], \"role\": \"connector\",\n"
    "           \"center\": [2.0, 2.5, 3.3]}\n"
    "    one = _rows(_derive([bed]), \"bedroom\")\n"
    "    assert len(one) == 1 and one[0][\"pos\"][:2] == [2.0, 2.5] and one[0][\"row\"] == {\"count\": 1, \"spacing\": 0.0}\n")


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


def main():
    if DRAFT and not os.environ.get("DC_ROOT"):
        sys.exit("refusing: --draft is for a DC_ROOT copy, never the repo")
    assert (DC / "VERSION").read_bytes().strip() == VERSION_WAS, (DC / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.207.1.md")
    assert entry.startswith("## [0.207.1] - "), entry[:40]
    if not DRAFT and not SUITE_PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"

    lp, l_eol, lights = _read("lights.py")
    assert "_HOME_SPACING" not in lights, "already applied"
    lights = _once(lights, CONST_OLD, CONST_NEW, "the constant")
    lights = _once(lights, DOC_OLD, DOC_NEW, "the docstring")
    lights = _once(lights, HOME_OLD, HOME_NEW, "the home branch")

    tp, t_eol, tests = _read("test_fixture_rows.py")
    assert tests.endswith("\n")
    tests = _once(tests, TEST_OLD, TEST_NEW, "the hideout's old pin")
    tests = tests.rstrip("\n") + "\n" + TEST_ADDED

    cl = DC / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:90]
    # Every pin and anchor matched: now write.
    lp.write_bytes(lights.replace("\n", l_eol.decode()).encode("utf-8"))
    tp.write_bytes(tests.replace("\n", t_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (DC / "VERSION").write_bytes(VERSION)
    print("Deli Counter 0.207.0 -> 0.207.1" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
