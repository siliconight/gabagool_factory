"""Level Factory 0.215.0: the backdrop's ground is unshaded (the factory's roadmap 252, priced 2026-10-15).

  packages/exporting/backdrop_layer.py     the ground's material takes `shading_mode = 0`; the record says so
  tests/unit/test_backdrop_ground.py       the first test restated; a new test on the material

Every file's sha16 pinned and every anchor asserted once, nothing written until all matched. CHANGELOG and VERSION
from `lf_ground_unshaded/CHANGELOG_0.215.0.md`; `--results-pending` leaves RESULT_SUITE to `--fill`. The scene
this writes is byte for byte the priced arm's (`docs/findings/walk_2026-10-14/ground_strip.py unshaded` inserts the
same line at the same place), so the price applies to what ships.

Read before it was written, in this session: backdrop_layer.py 52-60 (the ground's constants and their comment),
122-147 (`with_ground` whole); test_backdrop_ground.py 1-41 (the fixture and the first test). Every file LF.

    python patches/patch_lf_ground_unshaded.py --results-pending
    (the suite in level_factory; COMMANDS.md trap 1: tally the progress characters)
    python patches/patch_lf_ground_unshaded.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_ground_unshaded"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.214.0", b"0.215.0"
CHANGELOG_HEAD = "## [0.214.0] - What the three pins bring is held too"
SHA = {"packages/exporting/backdrop_layer.py": "163f1d0f65b8fbcc",
       "tests/unit/test_backdrop_ground.py": "86dda5c4f7ad2a35"}

CONST_OLD = ("#: The ground under the backdrop (0.211.0): a tenth of a metre under the plate, so the plate covers it\n"
             "#: wherever both stand -- cold run 9305's plate reaches x +-99 past fences at +-94.75 -- and this far past\n"
             "#: the pieces.\n")
CONST_NEW = (CONST_OLD +
             "#: UNSHADED (0.215.0, the factory's roadmap 252): shaded, this plane is reached by every lamp on the\n"
             "#: level, and on cold run 9308's package it cost +1 to +7 draws a heading and +7.20 ms on the p95 at the\n"
             "#: heaviest heading; unshaded, +1 draw everywhere and at most +0.52 ms. The lamps' pools past the fence\n"
             "#: are what the shaded one bought (`docs/findings/walk_2026-10-14/ground_frames/`).\n")

MAT_OLD = ("            '[sub_resource type=\"StandardMaterial3D\" id=\"BackdropGround_mat\"]\\n'\n"
           "            'albedo_color = Color(%s, %s, %s, 1)\\nroughness = 1.0\\n\\n') % (w, d, *GROUND_RGB)\n")
MAT_NEW = ("            '[sub_resource type=\"StandardMaterial3D\" id=\"BackdropGround_mat\"]\\n'\n"
           "            'albedo_color = Color(%s, %s, %s, 1)\\nshading_mode = 0\\nroughness = 1.0\\n\\n') % (w, d, *GROUND_RGB)\n")

RECORD_OLD = '    return text.rstrip("\\n") + "\\n" + node, {"size": [w, d], "y": GROUND_Y, "centre": [cx, cy], "draw_calls": 1}\n'
RECORD_NEW = ('    return text.rstrip("\\n") + "\\n" + node, {"size": [w, d], "y": GROUND_Y, "centre": [cx, cy],\n'
              '                                             "draw_calls": 1, "shaded": False}\n')

TEST_RECORD_OLD = ('    assert ground == {"size": [round(want_w, 3), round(want_d, 3)], "y": B.GROUND_Y,\n'
                   '                      "centre": [15.0, 5.0], "draw_calls": 1}\n')
TEST_RECORD_NEW = ('    assert ground == {"size": [round(want_w, 3), round(want_d, 3)], "y": B.GROUND_Y,\n'
                   '                      "centre": [15.0, 5.0], "draw_calls": 1, "shaded": False}\n')

TEST_END_OLD = "def test_no_orders_no_ground():\n"
TEST_END_NEW = ('def test_the_ground_takes_no_light():\n'
                '    """0.215.0 (the factory\'s roadmap 252): shaded, the plane cost up to +7 draws and +7.20 ms a heading on\n'
                '    cold run 9308\'s package; unshaded, +1 draw. The line stands where the priced arm put it, ahead of the\n'
                '    roughness, so the scene is the priced one byte for byte. Fails on 0.214.0."""\n'
                '    text, ground = B.with_ground(SCENE, ORDERS)\n'
                '    mat = re.search(r\'\\[sub_resource type="StandardMaterial3D" id="BackdropGround_mat"\\]\\n(.*?)\\n\\n\',\n'
                '                    text, re.S)\n'
                '    assert mat and mat.group(1).split("\\n") == [\n'
                '        "albedo_color = Color(%s, %s, %s, 1)" % B.GROUND_RGB, "shading_mode = 0", "roughness = 1.0"]\n'
                '    assert ground["shaded"] is False\n'
                '\n'
                '\n' + TEST_END_OLD)

EDITS = {"packages/exporting/backdrop_layer.py": [(CONST_OLD, CONST_NEW), (MAT_OLD, MAT_NEW), (RECORD_OLD, RECORD_NEW)],
         "tests/unit/test_backdrop_ground.py": [(TEST_RECORD_OLD, TEST_RECORD_NEW), (TEST_END_OLD, TEST_END_NEW)]}


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.215.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.215.0: results filled")


def main():
    if FILL:
        return fill()
    vraw = (LF / "VERSION").read_bytes()
    assert vraw.strip() == VERSION_WAS, vraw
    entry = (SRC / "CHANGELOG_0.215.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.215.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel in SHA:
        p = LF / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in EDITS[rel]:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(vraw.replace(VERSION_WAS, VERSION))
    print("Level Factory 0.214.0 -> 0.215.0")


if __name__ == "__main__":
    main()
