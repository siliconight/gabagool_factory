"""Level Factory 0.197.0: a stoop's railings stand in the frontage with it (factory roadmap 240, with Deli
Counter 0.212.0's railings; the walker's calls of 2026-10-13).

Anchored edits, each asserted exactly once and every file's sha16 pinned, nothing written until all of
them matched:
  packages/pipeline/street_line.py   `STOOP_COLLIDERS` names the railings' colliders, `stoop_rail_`
  tests/unit/test_terrace_stoop.py   the docstring; a comment that counted three names; `RAILS`, the
                                     railings' hulls read off a built shell; the railings' test
CHANGELOG and VERSION from `lf_stoop_railings/CHANGELOG_0.197.0.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`.

Read before it was written, in this session: `street_line.py` whole (`STOOP_COLLIDERS`, `shell_extents`'
prefix test), `empties.py`'s docstring and `stoop_reach`, `test_terrace_stoop.py` whole (`WALLS`, `STOOP`
and `TWIN_STOOP`, glTF metres, the door at x -1.5), `glb_collision.collision_solids` (`_node_matrix`
reads a node's rotation, so a turned slab's hull is its true box), the 0.195.0 patch this follows, and,
in Deli Counter 0.212.0, the twelve built `gs_empty_rowhome_*.glb` through `lf_stoop_railings/
rail_hulls.py` (`rail_hulls_0196.log`): every railing collider named `stoop_rail_<w|e>_<level|flight>_col`,
and `RAILS` below copied from `gs_empty_rowhome_a`'s. Every file LF.

    python patches/patch_lf_stoop_railings.py --results-pending
    (python -m pytest -q in level_factory; exit 0 and the tally, docs/COMMANDS.md trap 1)
    python patches/patch_lf_stoop_railings.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_stoop_railings"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.196.0", b"0.197.0"
CHANGELOG_HEAD = "## [0.196.0] - A rowhome's stoop merges with its front"
SHA = {"packages/pipeline/street_line.py": "31429138275bfc33",
       "tests/unit/test_terrace_stoop.py": "fc10dd2591551b5d"}

EDITS = {
    "packages/pipeline/street_line.py": [
        ("#: Deli Counter 0.211.0's stoop colliders (`Builder._stoop`): the steps in\n"
         "#: front of a rowhome Empty's raised door. The terrace stands an Empty's FRONT\n"
         "#: FACE on its line and its stoop in the frontage before it -- the 2.0 m strip\n"
         "#: a Philadelphia stoop stands in (`empties.FRONTAGE`, factory roadmap 240) --\n"
         "#: so it leaves them out of the house's extent, and `empties.stoop_reach` holds\n"
         "#: them inside the strip. Named exactly: a twin's `stoop_right` volume is its\n"
         "#: own lot's, read with the building as a porch is.\n"
         "STOOP_COLLIDERS = (\"stoop_landing\", \"stoop_under_\", \"stoop_ramp\")\n",
         "#: Deli Counter 0.211.0's stoop colliders (`Builder._stoop`): the steps in\n"
         "#: front of a rowhome Empty's raised door, and 0.212.0's railings on them. The\n"
         "#: terrace stands an Empty's FRONT FACE on its line and its stoop in the\n"
         "#: frontage before it -- the 2.0 m strip a Philadelphia stoop stands in\n"
         "#: (`empties.FRONTAGE`, factory roadmap 240) -- so it leaves them out of the\n"
         "#: house's extent, and `empties.stoop_reach` holds them inside the strip. Named\n"
         "#: exactly: a twin's `stoop_right` volume is its own lot's, read with the\n"
         "#: building as a porch is. Read with the house, a railing's flight was its\n"
         "#: street edge, 1.41 m in front of its facade (0.197.0).\n"
         "STOOP_COLLIDERS = (\"stoop_landing\", \"stoop_under_\", \"stoop_ramp\",\n"
         "                   \"stoop_rail_\")\n"),
    ],
    "tests/unit/test_terrace_stoop.py": [
        ("out (`STOOP_COLLIDERS`), the front face stands on the line as it did, and `stoop_reach` holds the stoop\n"
         "inside the strip.\n"
         "\"\"\"\n",
         "out (`STOOP_COLLIDERS`), the front face stands on the line as it did, and `stoop_reach` holds the stoop\n"
         "inside the strip.\n"
         "\n"
         "0.197.0: Deli Counter 0.212.0 stands an iron railing on each side of the stoop, its colliders named\n"
         "`stoop_rail_*`. They are the stoop's too: read with the house, a flight's slab was its street edge.\n"
         "\"\"\"\n"),
        ("TWIN_STOOP = [(\"stoop_right_col-convcolonly\", (2.0, 0.1, 7.35), (1.8, 0.2, 1.2))]\n",
         "TWIN_STOOP = [(\"stoop_right_col-convcolonly\", (2.0, 0.1, 7.35), (1.8, 0.2, 1.2))]\n"
         "#: Deli Counter 0.212.0's railings on that stoop, their hulls as the reader gives them off the built\n"
         "#: gs_empty_rowhome_a, whose door is at x -1.5 too (the factory's patches/lf_stoop_railings/\n"
         "#: rail_hulls_0196.log): a box along the landing a side, and the box round the slab under each flight\n"
         "RAILS = [(\"stoop_rail_w_level_col-convcolonly\", (-2.181, 0.9906, 6.6), (0.038, 0.9144, 0.9)),\n"
         "         (\"stoop_rail_w_flight_col-convcolonly\", (-2.181, 0.9628, 7.0897), (0.038, 0.9699, 0.9382)),\n"
         "         (\"stoop_rail_e_level_col-convcolonly\", (-0.819, 0.9906, 6.6), (0.038, 0.9144, 0.9)),\n"
         "         (\"stoop_rail_e_flight_col-convcolonly\", (-0.819, 0.9628, 7.0897), (0.038, 0.9699, 0.9382))]\n"),
        ("    # porch or a canopy off the walk); the skip names Deli Counter 0.211.0's three colliders only\n",
         "    # porch or a canopy off the walk); the skip names Deli Counter's stoop and railing colliders only\n"),
        ("    assert {p[\"front\"] for p in placed_whole} == {-37.65}\n"
         "    assert all(abs((a[\"at\"][1] - b[\"at\"][1]) - 1.738) < 1e-6 for a, b in zip(placed, placed_whole))\n",
         "    assert {p[\"front\"] for p in placed_whole} == {-37.65}\n"
         "    assert all(abs((a[\"at\"][1] - b[\"at\"][1]) - 1.738) < 1e-6 for a, b in zip(placed, placed_whole))\n"
         "\n"
         "\n"
         "def test_a_stoop_s_railings_are_the_stoop_s_not_the_house_s(tmp_path):\n"
         "    plain = street_line.shell_extents(write_glb(tmp_path / \"plain.glb\", WALLS))\n"
         "    railed = write_glb(tmp_path / \"railed.glb\", WALLS + STOOP + RAILS)\n"
         "    house = street_line.shell_extents(railed, skip=street_line.STOOP_COLLIDERS)\n"
         "    assert house == plain\n"
         "    # the stoop's reach is still its ramp's foot: the railings end inside it\n"
         "    assert abs(empties.stoop_reach(street_line.shell_extents(railed), house) - 1.738) < 1e-9\n"
         "    # skipping 0.195.0's three only, a flight is the house's street edge: the row 1.41 m back\n"
         "    three = street_line.shell_extents(railed, skip=(\"stoop_landing\", \"stoop_under_\", \"stoop_ramp\"))\n"
         "    assert abs((plain[2] - three[2]) - 1.4088) < 1e-4\n"),
    ],
}


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
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.197.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.197.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.197.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.197.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel, pairs in EDITS.items():
        p = LF / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.196.0 -> 0.197.0")


if __name__ == "__main__":
    main()
