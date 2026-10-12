"""Lot 0.119.2: the wires' pixel floor is written as a float, so a scene reads it (factory roadmap 240,
found in cold run 9264's package: `shader_parameter/min_px = null` in Lux's re-save).

Anchored edits, each asserted once, nothing written until all of them matched:
  site_poles.py              `wire_meshes` writes `min_px` as a float literal, with why
  tests/test_site_wires.py   the shader test asks for the float literal; one test appended
CHANGELOG and VERSION from `lot_wires_float/CHANGELOG_0.119.2.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`.

Read before it was written: `wire_meshes`' material lines, and `docs/findings/pole_line/min_px_resave.gd`
(Godot 4.7, headless): a scene written `min_px = 1` or `= 2` loads and re-saves it as null, one written
`1.0` or `2.0` keeps it. No other tool writes a `shader_parameter/` line (searched: lot, level_factory's
packages, deli_counter, zoo_keeper, lux/tools, pixelcoat, patina, dispatch).

    python patches/patch_lot_wires_float.py --results-pending && cd lot && python -m pytest -q
    python patches/patch_lot_wires_float.py --fill
    LOT_ROOT=<copy> python patches/patch_lot_wires_float.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_wires_float"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_MEASURED": "result_measured.txt", "RESULT_TESTS": "result_tests.txt",
           "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Lot 0.119.1", b"Lot 0.119.2"
CHANGELOG_HEAD = ("## 0.119.1 - a far wire is a faint line, not a dotted one: drawn a pixel wide at least "
                  "and faded by what it covers\n")
POLES = "site_poles.py"
TEST = "tests/test_site_wires.py"
SHA = {POLES: "809e3e618602072e", TEST: "2697fce7943a55a1"}

MAT_OLD = ('                f"shader_parameter/colour = Color({cr:g}, {cg:g}, {cb:g}, 1)",\n'
           '                f"shader_parameter/min_px = {WIRE_MIN_PX:g}", ""]\n')
MAT_NEW = ('                f"shader_parameter/colour = Color({cr:g}, {cg:g}, {cb:g}, 1)",\n'
           "                # A FLOAT LITERAL (0.119.2): Godot reads `min_px = 1` for a float uniform\n"
           "                # as no value -- it loads null and a re-save writes `null` -- and the shader\n"
           "                # falls back to its own default, so any other WIRE_MIN_PX would be lost\n"
           "                # (the factory's docs/findings/pole_line/min_px_resave.gd)\n"
           '                f"shader_parameter/min_px = {float(WIRE_MIN_PX)!r}", ""]\n')

TEST_OLD = '    assert "shader_parameter/min_px = %g" % site_poles.WIRE_MIN_PX in sub\n'
TEST_NEW = '    assert "shader_parameter/min_px = %r" % float(site_poles.WIRE_MIN_PX) in sub\n'
TEST_APPEND = '''

def test_a_float_uniform_is_written_as_a_float():
    """0.119.2: Godot 4.7 reads an integer literal given to a float uniform as no value -- a scene
    written `shader_parameter/min_px = 1` loads it null, and a re-save writes `null` (cold run 9264's
    package; the factory's docs/findings/pole_line/min_px_resave.gd). Every shader parameter Lot
    writes for a float uniform carries a decimal point, whatever WIRE_MIN_PX is."""
    _roads, cover = _cover()
    keep = site_poles.WIRE_MIN_PX
    try:
        for value in (1, 2, 1.5):
            site_poles.WIRE_MIN_PX = value
            _body, sub, _files = site_poles.wire_meshes(cover, lot.SIDEWALK_H)
            line = [l for l in sub if l.startswith("shader_parameter/min_px = ")]
            assert len(line) == 1, sub
            literal = line[0].split(" = ", 1)[1]
            assert "." in literal and float(literal) == float(value), line[0]
    finally:
        site_poles.WIRE_MIN_PX = keep
'''


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _read(rel):
    p = LOT / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def fill():
    assert (LOT / "VERSION").read_bytes().strip() == VERSION, (LOT / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LOT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.119.2.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Lot 0.119.2: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.119.2.md")
    assert entry.startswith("## 0.119.2 - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    pp, p_eol, poles = _read(POLES)
    assert "float(WIRE_MIN_PX)" not in poles, "already applied"
    poles = _once(poles, MAT_OLD, MAT_NEW, "wire_meshes' material")
    tp, t_eol, test = _read(TEST)
    test = _once(test, TEST_OLD, TEST_NEW, "the shader test's min_px line")
    test = test.rstrip("\n") + "\n" + TEST_APPEND
    cl = LOT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    pp.write_bytes(poles.replace("\n", p_eol.decode()).encode("utf-8"))
    tp.write_bytes(test.replace("\n", t_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.119.1 -> 0.119.2" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
