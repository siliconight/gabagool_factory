"""Lux 0.74.0: one bad tube a room, not a row (roadmap 229, beside Deli Counter 0.206.0).

`LuxFixtureSpawner.choose_failing` picked one failing lamp an anchor; Deli Counter 0.206.0 lays a
wide room's ceiling in two or three row anchors, so a sales floor would stutter three tubes. Now
`room_of(anchor)` groups the markers by the anchor's room, everything up to and including its
`_ceiling` or `_bulbs`, and one lamp a room fails.

Anchored edits, each asserted once, nothing written on a miss, the file's own line endings kept:
- `addons/lux/runtime/lux_fixture_spawner.gd`: `room_of` before `choose_failing`, whose doc and
  grouping key change;
- `tools/failing_fixtures_selftest.gd`: the rows' case after the spawner's.
CHANGELOG and VERSION from `lux_failing_room/CHANGELOG_0.74.0.md`; `--results-pending` leaves
RESULT_SELFTEST to `--fill` from `result_selftest.txt`.

    LUX_ROOT=<copy> python patches/patch_lux_failing_room.py --draft
    python patches/patch_lux_failing_room.py --results-pending
    python patches/patch_lux_failing_room.py --fill
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LUX = pathlib.Path(os.environ.get("LUX_ROOT") or HERE.parent / "lux")
SRC = HERE / "lux_failing_room"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SELFTEST": "result_selftest.txt"}
VERSION_WAS, VERSION = b"Lux 0.73.0", b"Lux 0.74.0"
CHANGELOG_HEAD = "## [0.73.0] - the glow at the horizon: a town's light over dark land\n"

SPAWNER = "addons/lux/runtime/lux_fixture_spawner.gd"
S_DOC_OLD = (
    "## Which markers fail, and how: ``{marker: [kind, seed]}``. One a\n"
    "## `lux_anchor_id` among the fluorescent and pendant markers, chosen by the\n"
    "## anchor id's hash -- deterministic, and an authored rename is the only\n"
    "## thing that moves it. Markers with no anchor id are grouped by their type.\n"
    "static func choose_failing(markers: Array) -> Dictionary:\n")
S_DOC_NEW = (
    "## ONE BAD TUBE A ROOM, NOT A ROW (0.74.0, roadmap 229). Deli Counter 0.206.0\n"
    "## lays a wide room's ceiling in two or three row anchors, `<room>_ceiling`,\n"
    "## `<room>_ceiling_r1`, `_r2`, each split run `_<i>`; one failing lamp an\n"
    "## anchor would stutter three tubes in one sales floor, a fault rather than\n"
    "## the tell one bad tube is. An anchor's room is everything up to and\n"
    "## including its `_ceiling` or `_bulbs`; an anchor named otherwise is its\n"
    "## own group, as before.\n"
    "static func room_of(anchor: String) -> String:\n"
    "\tfor stem: String in [\"_ceiling\", \"_bulbs\"]:\n"
    "\t\tvar k: int = anchor.rfind(stem)\n"
    "\t\tif k >= 0:\n"
    "\t\t\treturn anchor.substr(0, k + stem.length())\n"
    "\treturn anchor\n"
    "\n"
    "\n"
    "## Which markers fail, and how: ``{marker: [kind, seed]}``. One a ROOM\n"
    "## (`room_of`, 0.74.0) among the fluorescent and pendant markers, chosen by\n"
    "## the room's hash among every lamp of every row -- deterministic, and an\n"
    "## authored rename is the only thing that moves it. Markers with no anchor\n"
    "## id are grouped by their type.\n"
    "static func choose_failing(markers: Array) -> Dictionary:\n")
S_KEY_OLD = "\t\tvar anchor := String(marker_payload(mk, \"lux_anchor_id\", t))\n"
S_KEY_NEW = "\t\tvar anchor := room_of(String(marker_payload(mk, \"lux_anchor_id\", t)))\n"

SELFTEST = "tools/failing_fixtures_selftest.gd"
T_ANCHOR = (
    "\t_check(\"the same anchors choose the same lamps\", again.keys() == chosen.keys(), true)\n"
    "\tfor mk in markers:\n"
    "\t\tmk.free()\n")
T_CASE = (
    "\t# --- one a room across its rows (0.74.0) ----------------------------------\n"
    "\tvar rows: Array = [\n"
    "\t\t_marker(\"LuxEmit_fluorescent_21\", \"sales_floor_ceiling\"),\n"
    "\t\t_marker(\"LuxEmit_fluorescent_22\", \"sales_floor_ceiling\"),\n"
    "\t\t_marker(\"LuxEmit_fluorescent_23\", \"sales_floor_ceiling_r1\"),\n"
    "\t\t_marker(\"LuxEmit_fluorescent_24\", \"sales_floor_ceiling_r1\"),\n"
    "\t\t_marker(\"LuxEmit_fluorescent_25\", \"sales_floor_ceiling_r2\"),\n"
    "\t\t_marker(\"LuxEmit_fluorescent_26\", \"sales_floor_ceiling_r2_0\"),\n"
    "\t\t_marker(\"LuxEmit_fluorescent_27\", \"sales_floor_ceiling_r2_1\"),\n"
    "\t\t_marker(\"LuxEmit_fluorescent_28\", \"stockroom_ceiling\"),\n"
    "\t\t_marker(\"LuxEmit_pendant_21\", \"vault_bulbs\"),\n"
    "\t\t_marker(\"LuxEmit_pendant_22\", \"vault_bulbs_1\"),\n"
    "\t]\n"
    "\tvar by_room: Dictionary = spawner.choose_failing(rows)\n"
    "\t_check(\"a room is its anchor up to _ceiling\", spawner.room_of(\"sales_floor_ceiling_r2_1\"), \"sales_floor_ceiling\")\n"
    "\t_check(\"a bulb run's room is its anchor up to _bulbs\", spawner.room_of(\"vault_bulbs_1\"), \"vault_bulbs\")\n"
    "\t_check(\"an anchor named otherwise is its own room\", spawner.room_of(\"room_a\"), \"room_a\")\n"
    "\t_check(\"three rooms, three failing lamps across their rows\", by_room.size(), 3)\n"
    "\tvar rooms: Dictionary = {}\n"
    "\tfor mk in by_room:\n"
    "\t\trooms[spawner.room_of(String(mk.get_meta(\"lux_anchor_id\")))] = true\n"
    "\t_check(\"one each in the sales floor, the stockroom and the vault\", rooms.size(), 3)\n"
    "\tfor mk in rows:\n"
    "\t\tmk.free()\n")


def _eol(raw, rel):
    """The file's own line ending. A file with both refuses: there is no one ending to restore."""
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _text(rel):
    raw = (LUX / rel).read_bytes()
    return raw.decode("utf-8").replace("\r\n", "\n"), _eol(raw, rel)


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _write(rel, text, eol):
    (LUX / rel).write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))


def _entry():
    entry = (SRC / "CHANGELOG_0.74.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.74.0] - "), entry[:40]
    return entry


def _fill():
    """Replace the entry's placeholders in the repo's CHANGELOG from the result files."""
    cl = LUX / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    for key, name in RESULTS.items():
        value = (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n").strip()
        assert value and not value.endswith("."), (name, "must be one sentence without its final stop")
        text = _once(text, key, value, key)
    assert "RESULT_" not in text.split("## [0.73.0]")[0], "a placeholder is left in the entry"
    _write("CHANGELOG.md", text, eol)
    print("Lux 0.74.0's changelog filled")


def main():
    if DRAFT and not os.environ.get("LUX_ROOT"):
        sys.exit("refusing: --draft is for a LUX_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    v = (LUX / "VERSION").read_bytes()
    assert v == VERSION_WAS, repr(v)
    entry = _entry()
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    spawner, s_eol = _text(SPAWNER)
    assert "room_of" not in spawner, "already applied"
    spawner = _once(spawner, S_DOC_OLD, S_DOC_NEW, "choose_failing doc")
    spawner = _once(spawner, S_KEY_OLD, S_KEY_NEW, "grouping key")
    selftest, t_eol = _text(SELFTEST)
    assert "room_of" not in selftest, "selftest already carries the case"
    selftest = _once(selftest, T_ANCHOR, T_ANCHOR + "\n" + T_CASE, "selftest case")
    cl_raw = (LUX / "CHANGELOG.md").read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl.count(CHANGELOG_HEAD) == 1, cl[:200]
    cl = cl.replace(CHANGELOG_HEAD, entry.rstrip("\n") + "\n\n" + CHANGELOG_HEAD)
    # Every anchor matched: now write.
    _write(SPAWNER, spawner, s_eol)
    _write(SELFTEST, selftest, t_eol)
    _write("CHANGELOG.md", cl, cl_eol)
    (LUX / "VERSION").write_bytes(VERSION)
    print("Lux 0.73.0 -> 0.74.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
