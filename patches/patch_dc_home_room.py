"""Deli Counter 0.206.1: a home's room in any building takes the home rule (roadmap 229).

Cold run 9229's deli hung three rows of four over its `apartment_hideout` because 0.206.0's home
rule keyed on the building. Anchored edits in `lights.py` and `test_fixture_rows.py`, each pinned
by hash and asserted once, nothing written on a miss; CHANGELOG and VERSION from
`dc_home_room/CHANGELOG_0.206.1.md`. Then, chained:

    python patches/patch_dc_home_room.py --suite-pending && cd deli_counter && python -m pytest -q

and `python build.py --all` for the library; `--draft` applies to a `DC_ROOT` copy.
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_home_room"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv
SHA = {"lights.py": "e1edcc40014b91c1", "test_fixture_rows.py": "36a195c7cdae9579"}

FLOOR_OLD = "_WORK_PLANE_FLOOR = 0.0\n"
FLOOR_NEW = (
    "_WORK_PLANE_FLOOR = 0.0\n"
    "#: A residence-like ROOM inside any building takes the home rule (0.206.1):\n"
    "#: cold run 9229's deli hung three rows of four over its `apartment_hideout`,\n"
    "#: an office ceiling on a bedsit, because the rule keyed on the building.\n"
    "_HOME_WORDS = (\"apartment\", \"hideout\", \"bedroom\", \"living\", \"flat\", \"bedsit\")\n")
PITCH_FN = "def _ceiling_pitch(work_plane):\n"
HOME_FN = (
    "def _home_room(r, residence):\n"
    "    \"\"\"A home's room: by the building (`residence`) or by the room's own\n"
    "    words (0.206.1, `_HOME_WORDS`).\"\"\"\n"
    "    if residence:\n"
    "        return True\n"
    "    key = ((r.get(\"role\") or \"\") + \" \" + (r.get(\"id\") or \"\")).lower()\n"
    "    return any(w in key for w in _HOME_WORDS)\n"
    "\n"
    "\n")
CALL_OLD = (
    "            rows = _rows_for_room(bounds, ceiling_z, c[2],\n"
    "                                  _work_plane(r, residence), residence)\n")
CALL_NEW = (
    "            home = _home_room(r, residence)\n"
    "            rows = _rows_for_room(bounds, ceiling_z, c[2],\n"
    "                                  _work_plane(r, home), home)\n")
TEST_ANCHOR = "    assert rows[1][\"pos\"][1] != 4.2                    # moved to the larger side's centre\n"
TEST_NEW = TEST_ANCHOR + (
    "\n"
    "\n"
    "def test_a_home_room_in_a_shop_takes_the_home_rule():\n"
    "    # cold run 9229: the deli's apartment hideout, 21 x 16 m, took three rows of four\n"
    "    r = {\"id\": \"apartment_hideout\", \"story\": 1, \"bounds\": [-2.0, -14.0, 19.0, 2.0],\n"
    "         \"role\": \"fortifiable\", \"center\": [8.5, -6.0, 3.3]}\n"
    "    rows = _rows(_derive([r]), \"apartment_hideout\")\n"
    "    assert len(rows) == 1 and rows[0][\"row\"] == {\"count\": 1, \"spacing\": 0.0}\n"
    "    assert rows[0][\"pos\"][:2] == [8.5, -6.0]\n"
    "    # the same bounds under a name that says nothing of a home is still an office ceiling\n"
    "    office = dict(r, id=\"upper_office\")\n"
    "    assert len(_rows(_derive([office]), \"upper_office\")) == 3\n")
TEST2_OLD = (
    "    # the same room in a store is two rows: 7 / 4.65 = 1.5 spacings, past the slack\n"
    "    assert len(_rows(_derive([r]), \"living_room\")) == 2\n")
TEST2_NEW = (
    "    # the same bounds under a name with no home in it, in a store, is two rows: 7 / 4.65 =\n"
    "    # 1.5 spacings, past the slack (0.206.1: a living room is a home's in any building)\n"
    "    assert len(_rows(_derive([dict(r, id=\"back_floor\")]), \"back_floor\")) == 2\n")
CHANGELOG_HEAD = "## [0.206.0] - ceiling rows laid to the work, on the ceiling's grid\n"


def _read(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _stage():
    staged = {}
    edits = {"lights.py": [(FLOOR_OLD, FLOOR_NEW, 1), (PITCH_FN, HOME_FN + PITCH_FN, 1), (CALL_OLD, CALL_NEW, 1)],
             "test_fixture_rows.py": [(TEST_ANCHOR, TEST_NEW, 1), (TEST2_OLD, TEST2_NEW, 1)]}
    for rel, pairs in edits.items():
        p = DC / rel
        d = p.read_bytes()
        got = hashlib.sha256(d).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        assert b"\r" not in d, (rel, "has CR; this patch writes LF")
        t = d.decode("utf-8")
        assert "_HOME_WORDS" not in t and "home rule" not in t.split("def _work_plane")[0][-200:], (rel, "already applied")
        for old, new, times in pairs:
            n = t.count(old)
            assert n == times, (rel, n, times, old[:70])
            t = t.replace(old, new)
        staged[p] = t.encode("utf-8")
    return staged


def main():
    if DRAFT and not os.environ.get("DC_ROOT"):
        sys.exit("refusing: --draft is for a DC_ROOT copy, never the repo")
    v = (DC / "VERSION").read_bytes()
    assert v == b"Deli Counter 0.206.0", repr(v)
    staged = _stage()
    entry = _read("CHANGELOG_0.206.1.md")
    assert entry.startswith("## [0.206.1] - "), entry[:40]
    if not DRAFT:
        left = entry.replace("RESULT_SUITE", "").replace("RESULT_CENSUS", "") if SUITE_PENDING else entry
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    cl = DC / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r" not in data, "CHANGELOG.md is not LF"
    text = data.decode("utf-8")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:90]
    # Every anchor and hash matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + text).encode("utf-8"))
    (DC / "VERSION").write_bytes(b"Deli Counter 0.206.1")
    print("Deli Counter 0.206.0 -> 0.206.1" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
