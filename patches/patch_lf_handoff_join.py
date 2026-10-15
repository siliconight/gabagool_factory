"""Level Factory 0.215.1: HANDOFF.md's layers paragraph stands on its own (found reading cold run 9314's package).

  packages/exporting/export.py     `handoff_text(layers, mode)`; the write site calls it
  tests/unit/test_layers_shown.py  the call-site assertion restated; one new test on the composed text

Every file's sha16 pinned and every anchor asserted once, nothing written until all matched. CHANGELOG and VERSION
from `lf_handoff_join/CHANGELOG_0.215.1.md`; `--results-pending` leaves RESULT_SUITE to `--fill`.

Read before it was written, in this session: export.py 160-163 (`HANDOFF_LANGUAGE`'s last line, one newline) and
2258-2260 (the write); test_layers_shown.py 45 (the call-site assertion); cold run 9314's HANDOFF.md, where
"online correctness.\\nWHAT THIS PACKAGE IS MADE OF" is one paragraph. Every file LF.

    python patches/patch_lf_handoff_join.py --results-pending
    (the suite in level_factory; COMMANDS.md trap 1: tally the progress characters)
    python patches/patch_lf_handoff_join.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_handoff_join"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.215.0", b"0.215.1"
CHANGELOG_HEAD = "## [0.215.0] - The backdrop's ground is unshaded"
SHA = {"packages/exporting/export.py": "8e0445bbaac31ed4",
       "tests/unit/test_layers_shown.py": "a3dd6653d6ca3591"}

WRITE_OLD = ('    (export_dir / "HANDOFF.md").write_text(\n'
             '        HANDOFF_LANGUAGE + handoff_layers_text(layers, profile.mode), encoding="utf-8")\n')
WRITE_NEW = '    (export_dir / "HANDOFF.md").write_text(handoff_text(layers, profile.mode), encoding="utf-8")\n'

HELPER_ANCHOR = '    return text + " `output_layers.json` and `LF_MANIFEST.json` name the layers.\\n"\n'
HELPER_NEW = HELPER_ANCHOR + '''

def handoff_text(layers, mode: str) -> str:
    """HANDOFF.md whole (0.215.1): `HANDOFF_LANGUAGE`, a blank line, the layers
    paragraph. 0.213.0 appended the paragraph straight after the language,
    whose last line ends with one newline, so it landed inside the paragraph
    before it (cold run 9314's package)."""
    return HANDOFF_LANGUAGE.rstrip("\\n") + "\\n\\n" + handoff_layers_text(layers, mode)
'''

TEST_CALL_OLD = '    assert "HANDOFF_LANGUAGE + handoff_layers_text(layers, profile.mode)" in src\n'
TEST_CALL_NEW = ('    assert \'write_text(handoff_text(layers, profile.mode), encoding="utf-8")\' in src\n'
                 '    assert "HANDOFF_LANGUAGE + handoff_layers_text" not in src\n')

TEST_END_OLD = 'def test_the_readme_and_the_design_doc_show_the_light_layer():\n'
TEST_END_NEW = ('def test_the_layers_paragraph_stands_on_its_own():\n'
                '    """0.215.1: cold run 9314\'s HANDOFF.md carried the paragraph as the last line of the one before it.\n'
                '    Fails on 0.215.0, which has no handoff_text."""\n'
                '    text = EX.handoff_text({LAYER_ART, LAYER_GAMEPLAY, LAYER_LIGHT}, EX.MODE_PORTABLE)\n'
                '    assert text.startswith(EX.HANDOFF_LANGUAGE.rstrip("\\n") + "\\n\\n")\n'
                '    assert "\\n\\nWHAT THIS PACKAGE IS MADE OF" in text and "\\n\\n\\n" not in text\n'
                '    assert text.endswith("name the layers.\\n") and not text.endswith("\\n\\n")\n'
                '\n'
                '\n' + TEST_END_OLD)

EDITS = {"packages/exporting/export.py": [(HELPER_ANCHOR, HELPER_NEW), (WRITE_OLD, WRITE_NEW)],
         "tests/unit/test_layers_shown.py": [(TEST_CALL_OLD, TEST_CALL_NEW), (TEST_END_OLD, TEST_END_NEW)]}


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.215.1.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.215.1: results filled")


def main():
    if FILL:
        return fill()
    vraw = (LF / "VERSION").read_bytes()
    assert vraw.strip() == VERSION_WAS, vraw
    entry = (SRC / "CHANGELOG_0.215.1.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.215.1] - "), entry[:40]
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
    print("Level Factory 0.215.0 -> 0.215.1")


if __name__ == "__main__":
    main()
