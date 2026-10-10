"""Lot 0.110.0: the tree belt in clusters, in three forms (roadmap 228 step F, beside Zoo 1.97.0).

The walker, on cold run 9227's parkland: "those trees in the distance are a little lazy imo
(giant lolipops vs. trees)". Zoo 1.97.0's tree takes its form from the slot's proportions; this
mixes six dims (two oaks, two maples, two elms), lays the near belt in clusters with daylight
between them, and stands the belt 6 m off the fence. Anchored edits in `site_backdrop.py` and
`tests/test_site_backdrop_2.py`, each pinned by hash and asserted once, nothing written on a
miss; the file's own line endings kept. Applies on Lot 0.109.1 (the tally fix edits `lot.py`
only, so `site_backdrop.py` is 0.109.0's). CHANGELOG and VERSION from
`lot_tree_belt/CHANGELOG_0.110.0.md`; `--suite-pending` leaves RESULT_SUITE to `--fill`.

    python patches/patch_lot_tree_belt.py --suite-pending && cd lot && python -m pytest -q
    python patches/patch_lot_tree_belt.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_tree_belt"
DRAFT = "--draft" in sys.argv
PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"Lot 0.109.1", b"Lot 0.110.0"
CHANGELOG_HEAD = "## 0.109.1 - the backdrop's summary line counts pieces, not rowhomes\n"
SHA = {"site_backdrop.py": "91c43a4f1966c99e", "tests/test_site_backdrop_2.py": "8f048a796fe6aba7"}

CONST_OLD = (
    "#: the parkland: a belt of trees, three sizes, and a sparser far belt\n"
    "TREES = ((5.0, 5.0, 7.0), (7.0, 7.0, 10.0), (9.0, 9.0, 13.0))\n"
    "TREE_BELT = (2.5, 38.0)\n"
    "TREE_STEP = (1.2, 3.2)\n"
    "FAR_TREE_BELT = (60.0, 90.0)\n"
    "FAR_TREE_STEP = (4.0, 9.0)\n"
    "#: the roadside: a thin belt of trees and a few far warehouses\n"
    "ROADSIDE_BELT = (2.5, 20.0)\n"
    "ROADSIDE_STEP = (2.0, 5.0)\n")
CONST_NEW = (
    "#: the parkland: a belt of trees in CLUSTERS, and a sparser far belt (0.110.0,\n"
    "#: roadmap 228 step F). The walker, on cold run 9227: \"those trees in the\n"
    "#: distance are a little lazy imo (giant lolipops vs. trees)\". Zoo 1.97.0's\n"
    "#: tree takes its form from the slot's proportions -- a squat slot is a broad\n"
    "#: oak, a tall one a vase-shaped elm, between them a round maple -- so the\n"
    "#: dims here are the forms the belt mixes, two of each. And a wood's edge is\n"
    "#: not a rank at one step: trees stand in groups with daylight between them,\n"
    "#: so the near belt is laid as clusters of TREE_CLUSTER trees at TREE_STEP\n"
    "#: apart with TREE_CLUSTER_GAP between the groups. The near edge stands 6 m\n"
    "#: off the fence (2.5 before): on 9227's 87 m plate a crown filled an\n"
    "#: elevated view's foreground larger than the building.\n"
    "TREES = ((8.0, 8.0, 8.0), (11.0, 11.0, 12.0),      # oaks\n"
    "         (5.0, 5.0, 7.0), (7.0, 7.0, 10.0),        # maples\n"
    "         (4.0, 4.0, 9.0), (6.0, 6.0, 13.0))        # elms\n"
    "TREE_BELT = (6.0, 38.0)\n"
    "TREE_STEP = (1.5, 3.0)\n"
    "TREE_CLUSTER = (4, 9)\n"
    "TREE_CLUSTER_GAP = (5.0, 18.0)\n"
    "FAR_TREE_BELT = (60.0, 90.0)\n"
    "FAR_TREE_STEP = (4.0, 9.0)\n"
    "#: the roadside: a thin belt of trees, in the same clusters, and a few far warehouses\n"
    "ROADSIDE_BELT = (4.0, 20.0)\n"
    "ROADSIDE_STEP = (2.0, 5.0)\n")
TREES_OLD = (
    "def _trees(ground, rng, side, belt, step, band, start=0) -> list:\n"
    "    out = []\n"
    "    s0, s1 = _span(side, ground)\n"
    "    t = s0\n"
    "    k = start\n"
    "    while t < s1:\n"
    "        w, d, h = TREES[rng.randrange(len(TREES))]\n"
    "        # a crown never overhangs the plate: its foot stands at least its\n"
    "        # radius beyond the edge, and the fence, whatever the belt's near edge\n"
    "        near = max(belt[0], w / 2.0 + 0.25)\n"
    "        at = _place(side, t, rng.uniform(near, max(near, belt[1])), ground)\n"
    "        out.append(_piece(f\"Backdrop_{side}_{band}_{k}\", TREE_SPECIES, side, band, at,\n"
    "                          rng.choice((0.0, 90.0, 180.0, 270.0)), (w, d, h)))\n"
    "        k += 1\n"
    "        t += rng.uniform(*step)\n"
    "    return out\n")
TREES_NEW = (
    "def _trees(ground, rng, side, belt, step, band, start=0, cluster=None) -> list:\n"
    "    \"\"\"A belt of trees along one side: in groups of ``cluster`` (a (lo, hi)\n"
    "    count) at ``step`` apart with TREE_CLUSTER_GAP of daylight between the\n"
    "    groups (0.110.0), or one run at ``step`` when ``cluster`` is None (the\n"
    "    far belt). Each tree draws its dims, and so its form, from TREES.\"\"\"\n"
    "    out = []\n"
    "    s0, s1 = _span(side, ground)\n"
    "    t = s0 + (rng.uniform(0.0, TREE_CLUSTER_GAP[0]) if cluster else 0.0)\n"
    "    k = start\n"
    "    while t < s1:\n"
    "        n = rng.randint(*cluster) if cluster else 1\n"
    "        for _ in range(n):\n"
    "            if t >= s1:\n"
    "                break\n"
    "            w, d, h = TREES[rng.randrange(len(TREES))]\n"
    "            # a crown never overhangs the plate: its foot stands at least its\n"
    "            # radius beyond the edge, and the fence, whatever the belt's near edge\n"
    "            near = max(belt[0], w / 2.0 + 0.25)\n"
    "            at = _place(side, t, rng.uniform(near, max(near, belt[1])), ground)\n"
    "            out.append(_piece(f\"Backdrop_{side}_{band}_{k}\", TREE_SPECIES, side, band, at,\n"
    "                              rng.choice((0.0, 90.0, 180.0, 270.0)), (w, d, h)))\n"
    "            k += 1\n"
    "            t += rng.uniform(*step)\n"
    "        if cluster:\n"
    "            t += rng.uniform(*TREE_CLUSTER_GAP)\n"
    "    return out\n")
PARK_OLD = "        out += _trees(ground, rng, side, TREE_BELT, TREE_STEP, 0)\n"
PARK_NEW = "        out += _trees(ground, rng, side, TREE_BELT, TREE_STEP, 0, cluster=TREE_CLUSTER)\n"
ROAD_OLD = "        out += _trees(ground, rng, side, ROADSIDE_BELT, ROADSIDE_STEP, 0)\n"
ROAD_NEW = "        out += _trees(ground, rng, side, ROADSIDE_BELT, ROADSIDE_STEP, 0, cluster=TREE_CLUSTER)\n"
TEST_OLD = "    assert 300 <= s[\"by_species\"][SB.TREE_SPECIES] <= 1200\n"
TEST_NEW = ("    # clusters with daylight between them since 0.110.0: a belt of a few hundred, not a rank\n"
            "    assert 150 <= s[\"by_species\"][SB.TREE_SPECIES] <= 1200\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _load(rel):
    raw = (LOT / rel).read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return raw.decode("utf-8").replace("\r\n", "\n"), _eol(raw, rel)


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _write(rel, text, eol):
    (LOT / rel).write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))


def _fill():
    cl = LOT / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    value = (SRC / "result_suite.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").strip()
    assert value and not value.endswith("."), "result_suite.txt must be one sentence without its final stop"
    text = _once(text, "RESULT_SUITE", value, "RESULT_SUITE")
    _write("CHANGELOG.md", text, eol)
    print("Lot 0.110.0's changelog filled")


def main():
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.110.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## 0.110.0 - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    sb, sb_eol = _load("site_backdrop.py")
    assert "TREE_CLUSTER" not in sb, "already applied"
    sb = _once(sb, CONST_OLD, CONST_NEW, "the tree constants")
    sb = _once(sb, TREES_OLD, TREES_NEW, "_trees")
    sb = _once(sb, PARK_OLD, PARK_NEW, "_parkland's near belt")
    sb = _once(sb, ROAD_OLD, ROAD_NEW, "_roadside's belt")
    test, t_eol = _load("tests/test_site_backdrop_2.py")
    test = _once(test, TEST_OLD, TEST_NEW, "the parkland's floor")
    cl_raw = (LOT / "CHANGELOG.md").read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl.startswith(CHANGELOG_HEAD) and cl.count(CHANGELOG_HEAD) == 1, cl[:90]
    # Every pin and anchor matched: now write.
    _write("site_backdrop.py", sb, sb_eol)
    _write("tests/test_site_backdrop_2.py", test, t_eol)
    _write("CHANGELOG.md", entry.rstrip("\n") + "\n\n" + cl, cl_eol)
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.109.1 -> 0.110.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
