"""Level Factory 0.175.1: the backdrop's by-side count counts every piece, not the rowhomes.

Cold run 9226's yards exported `(N 0, S 0, E 0, W 0; 1 tower)` beside 121 instances:
`ship_backdrop` tallied `backdrop_rowhome` orders a side. `pieces_by_side(orders)` counts every
order but the tower. Anchored edits pinned by hash, each asserted once, nothing written on a
miss; CHANGELOG and VERSION from `lf_backdrop_tally/CHANGELOG_0.175.1.md`; `--suite-pending`
leaves RESULT_SUITE to `--fill` from `result_suite.txt`.

    python patches/patch_lf_backdrop_tally.py --suite-pending     # LF_ROOT=<copy> ... --draft
    python patches/patch_lf_backdrop_tally.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_backdrop_tally"
DRAFT = "--draft" in sys.argv
PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"0.175.0", b"0.175.1"
CHANGELOG_HEAD = "## [0.175.0] - The brief names what stands beyond the edge, or the archetype decides\n"
SHA = {"packages/exporting/backdrop_layer.py": "c587073442ad1495",
       "tests/unit/test_backdrop_layer.py": "356d07904ec8bc50"}

LAYER = "packages/exporting/backdrop_layer.py"
FN_ANCHOR = "def ship_backdrop(export_dir: Path, drawn_path, godot_executable, *,\n"
FN_NEW = (
    "def pieces_by_side(orders) -> dict:\n"
    "    \"\"\"How many pieces stand on each side, the tower aside (0.175.1): cold run 9226's yards\n"
    "    exported `(N 0, S 0, E 0, W 0; 1 tower)` beside 121 instances because the count was of\n"
    "    `backdrop_rowhome` orders alone.\"\"\"\n"
    "    return {s: sum(1 for o in orders if o[\"side\"] == s and o[\"species\"] != \"water_tower\")\n"
    "            for s in SIDES}\n"
    "\n"
    "\n")
SIDE_OLD = (
    "    houses = [o for o in manifest[\"orders\"] if o[\"species\"] == \"backdrop_rowhome\"]\n"
    "    report.update({\n"
    "        \"shipped\": True, \"scene\": scene_name, \"modules\": modules, \"mesh_paths\": mesh_paths,\n"
    "        \"by_side\": {s: sum(1 for o in houses if o[\"side\"] == s) for s in SIDES},\n")
SIDE_NEW = (
    "    report.update({\n"
    "        \"shipped\": True, \"scene\": scene_name, \"modules\": modules, \"mesh_paths\": mesh_paths,\n"
    "        \"by_side\": pieces_by_side(manifest[\"orders\"]),\n")

TEST = "tests/unit/test_backdrop_layer.py"
TEST_ANCHOR = (
    "    assert \"res://site_backdrop.tscn\" in (tmp_path / \"mission.tscn\").read_text(encoding=\"utf-8\")\n")
TEST_NEW = TEST_ANCHOR + (
    "\n"
    "\n"
    "def test_the_by_side_count_is_of_every_piece_but_the_tower():\n"
    "    # cold run 9226's yards: containers and warehouses, no rowhome, one tower\n"
    "    orders = ([{\"species\": \"cargo_container\", \"side\": \"N\"}] * 3\n"
    "              + [{\"species\": \"backdrop_warehouse\", \"side\": \"E\"}] * 2\n"
    "              + [{\"species\": \"water_tower\", \"side\": \"N\"}])\n"
    "    assert backdrop_layer.pieces_by_side(orders) == {\"N\": 3, \"S\": 0, \"E\": 2, \"W\": 0}\n"
    "    assert backdrop_layer.pieces_by_side([]) == {\"N\": 0, \"S\": 0, \"E\": 0, \"W\": 0}\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _load(rel):
    raw = (LF / rel).read_bytes()
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return raw.decode("utf-8").replace("\r\n", "\n"), _eol(raw, rel)


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _write(rel, text, eol):
    (LF / rel).write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))


def _fill():
    cl = LF / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    value = (SRC / "result_suite.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").strip()
    assert value and not value.endswith("."), "result_suite.txt must be one sentence without its final stop"
    text = _once(text, "RESULT_SUITE", value, "RESULT_SUITE")
    _write("CHANGELOG.md", text, eol)
    print("Level Factory 0.175.1's changelog filled")


def main():
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.175.1.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.175.1] - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    layer, l_eol = _load(LAYER)
    assert "pieces_by_side" not in layer, "already applied"
    layer = _once(layer, FN_ANCHOR, FN_NEW + FN_ANCHOR, "ship_backdrop")
    layer = _once(layer, SIDE_OLD, SIDE_NEW, "by_side")
    test, t_eol = _load(TEST)
    test = _once(test, TEST_ANCHOR, TEST_NEW, "the test's tail")
    cl_raw = (LF / "CHANGELOG.md").read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl.startswith(CHANGELOG_HEAD) and cl.count(CHANGELOG_HEAD) == 1, cl[:90]
    # Every pin and anchor matched: now write.
    _write(LAYER, layer, l_eol)
    _write(TEST, test, t_eol)
    _write("CHANGELOG.md", entry.rstrip("\n") + "\n\n" + cl, cl_eol)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.175.0 -> 0.175.1" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
