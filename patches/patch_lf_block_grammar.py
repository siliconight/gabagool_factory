"""Level Factory 0.177.0: the `block` road grammar -- a second side street and a service lane behind
the row, one loop (roadmap 199 and 230 step 3).

Anchored edits in `packages/pipeline/road_grammar.py` (the vocabulary, the lane's constants, the
new functions from `lf_block_grammar/road_grammar_block.py.txt`, the block branch in `roads_for`)
and five tests appended to `tests/unit/test_road_grammar.py`; each file pinned by hash and each
anchor asserted once, nothing written on a miss; the file's own line endings kept. CHANGELOG and
VERSION from `lf_block_grammar/CHANGELOG_0.177.0.md`; `--suite-pending` leaves RESULT_SUITE to
`--fill`. Lot 0.113.0 lands first (one test here reads Lot's junction control).

    python patches/patch_lf_block_grammar.py --suite-pending && cd level_factory && python -m pytest -q > out.txt 2>&1; echo exit=$?
    python patches/patch_lf_block_grammar.py --fill
    LF_ROOT=<copy> python patches/patch_lf_block_grammar.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_block_grammar"
DRAFT = "--draft" in sys.argv
PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"0.176.1", b"0.177.0"
CHANGELOG_HEAD = "## [0.176.1] - The site spec's draw takes the cluster template too\n"
SHA = {"packages/pipeline/road_grammar.py": "831cea799eefee6a",
       "tests/unit/test_road_grammar.py": "1d0f4443c37f2fc5"}

G_OLD = 'GRAMMARS = ("T", "cross")\n'
G_NEW = 'GRAMMARS = ("T", "cross", "block")\n'
A_OLD = ('    "x": "cross", "intersection": "cross", "four_corners": "cross",\n'
         '}\n')
A_NEW = ('    "x": "cross", "intersection": "cross", "four_corners": "cross",\n'
         '    "block": "block", "loop": "block", "service_lane": "block",\n'
         '    "rear_lane": "block", "alley": "block", "back_lane": "block",\n'
         '}\n')
C_OLD = 'FRONTAGE = ROAD_MARGIN\n'
C_NEW = (
    'FRONTAGE = ROAD_MARGIN\n'
    '\n'
    '#: THE SERVICE LANE (0.177.0, roadmap 199 and 230): the adjacency guide\'s\n'
    '#: "small service lane for van-scale work", 3.5 to 5 m (7.4). Five, so a\n'
    '#: hauler reaches the dumpsters that stand on the rear walls.\n'
    'LANE_WIDTH = 5.0\n'
    '#: What stands on a rear wall before the lane: Lot\'s dumpster pad and its\n'
    '#: apron (`site_yards.PAD_OUT + APRON`, 3 + 3), mirrored here because this\n'
    '#: module cannot import Lot and the pad is laid after the roads are. A\n'
    '#: change there is a change here.\n'
    'REAR_YARD = 6.0\n'
    '#: The lane\'s near edge from the deepest rear face: the yard, then the\n'
    '#: margin this module keeps between a road\'s band and anything else.\n'
    'LANE_SETBACK = REAR_YARD + ROAD_MARGIN\n')
F_OLD = 'def roads_for(grammar, buildings, footprints, span_x, span_y):\n'
R_OLD = (
    '    # THE CROSS STREET GETS ITS ADDRESSES. Without these it is a road through\n'
    '    # empty ground: `street_members` read `{0: [b0, b1, b2], 1: []}` on every\n'
    '    # site ever generated, so the junction added approaches nobody could use.\n'
    '    doors = _spurs(faces, y_road) + _lateral_spurs(\n'
    '        spans, [b.get("id") for b in buildings], x_cross, y_road,\n'
    '        span_y, flank)\n'
    '    return [road, cross], doors, span_x, span_y\n')
R_NEW = (
    '    # THE BLOCK\'S ADDITIONS (0.177.0): a second side street past the row\'s far\n'
    '    # end and a service lane behind the row between the two, one loop; the\n'
    '    # plate may widen and deepen for them, and the T\'s roads follow it. A T\n'
    '    # and a crossroads add nothing and are byte for byte what they were.\n'
    '    ids = [b.get("id") for b in buildings]\n'
    '    extra, extra_doors = [], []\n'
    '    if shape == "block":\n'
    '        extra, extra_doors, span_x, span_y = _block(\n'
    '            spans, edges, ids, x_cross, y_road, span_x, span_y)\n'
    '        road["a"][0], road["b"][0] = -span_x / 2.0, span_x / 2.0\n'
    '        cross["b"][1] = span_y / 2.0 - ROAD_MARGIN\n'
    '    # THE CROSS STREET GETS ITS ADDRESSES. Without these it is a road through\n'
    '    # empty ground: `street_members` read `{0: [b0, b1, b2], 1: []}` on every\n'
    '    # site ever generated, so the junction added approaches nobody could use.\n'
    '    doors = _spurs(faces, y_road) + _lateral_spurs(\n'
    '        spans, ids, x_cross, y_road, span_y, flank) + extra_doors\n'
    '    return [road, cross] + extra, doors, span_x, span_y\n')


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
    p = LF / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _fill():
    cl = LF / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    value = (SRC / "result_suite.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").strip()
    assert value and not value.endswith("."), "result_suite.txt must be one sentence without its final stop"
    text = _once(text, "RESULT_SUITE", value, "RESULT_SUITE")
    cl.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    print("Level Factory 0.177.0's changelog filled")


def main():
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.177.0.md")
    assert entry.startswith("## [0.177.0] - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    block = _src("road_grammar_block.py.txt")
    assert block.startswith("def _far_line(") and "def _block(" in block and block.endswith("\n\n\n")

    gp, g_eol, gram = _read("packages/pipeline/road_grammar.py")
    assert "_block(" not in gram and "LANE_WIDTH" not in gram, "already applied"
    gram = _once(gram, G_OLD, G_NEW, "the vocabulary")
    gram = _once(gram, A_OLD, A_NEW, "the spellings")
    gram = _once(gram, C_OLD, C_NEW, "the constants")
    gram = _once(gram, F_OLD, block + F_OLD, "the new functions")
    gram = _once(gram, R_OLD, R_NEW, "roads_for's tail")

    tp, t_eol, tests = _read("tests/unit/test_road_grammar.py")
    assert tests.endswith("\n")
    tests = tests.rstrip("\n") + "\n" + _src("test_road_grammar_block.py.txt")

    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    # Every pin and anchor matched: now write.
    gp.write_bytes(gram.replace("\n", g_eol.decode()).encode("utf-8"))
    tp.write_bytes(tests.replace("\n", t_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.176.1 -> 0.177.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
