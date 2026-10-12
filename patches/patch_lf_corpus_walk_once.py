"""Level Factory 0.193.2: the archetype corpus is walked once a session, and never into a directory it
discards (factory roadmap 239: the suite is half the iteration loop).

Anchored edits, each asserted once, nothing written until all of them matched:
  tests/test_archetype_resolution.py   functools and os imported beside json; `_brief_paths` becomes
                                       `_keep`, `_corpus_walk` and a cached `_brief_paths`
                                       (`walk_helpers.py.txt`); three tests appended at the end
                                       (`walk_tests.py.txt`)
CHANGELOG and VERSION from `lf_corpus_walk_once/CHANGELOG_0.193.2.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`.

Read before it was written: the suite's JUnit from 0.193.1's run (`_scratch/lf_01931_suite.xml`:
443.1 s, this module 118.8 s) and docs/findings/lf_suite_time/brief_walk_probe.py's four alternated
walks (the same 487 briefs; 29.95 s against 18.85 s warm).

    python patches/patch_lf_corpus_walk_once.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_corpus_walk_once.py --fill
    LF_ROOT=<copy> python patches/patch_lf_corpus_walk_once.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_corpus_walk_once"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_TIME": "result_time.txt", "RESULT_TESTS": "result_tests.txt",
           "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.193.1", b"0.193.2"
CHANGELOG_HEAD = ("## [0.193.1] - re-grounded to Zoo 1.103.0, a mesh's faces in one order (factory "
                  "roadmap 239)\n")
TEST = "tests/test_archetype_resolution.py"
SHA = {TEST: "378a280ee9904055"}

IMPORTS_OLD = "import json\n"
IMPORTS_NEW = "import functools\nimport json\nimport os\n"
WALK_OLD = '''def _brief_paths():
    """Every brief in the repo: examples, recorded cold runs, workspaces.

    A PREDICATE RATHER THAN A LIST OF PATTERNS, deliberately. The first
    version of this spelled four globs and missed `level_factory/examples/`
    entirely -- it found 19 of 21 briefs and reported the corpus clean of a
    defect that was sitting in one of the 2. A walk cannot miss a directory
    shape nobody thought of.
    """
    assert _ROOT is not None, (
        "the factory root is not above %s -- set LF_DC_ROOT. A corpus sweep "
        "with no corpus passes and proves nothing."
        % Path(__file__).resolve().parent)
    out = []
    for path in _ROOT.rglob("*.json"):
        if _SKIP_DIRS & set(path.parts):
            continue
        if path.name == "brief.json" or path.parent.name == "briefs":
            out.append(path)
    return sorted(out)
'''
TAIL = ('    assert seen == set(_KNOWN_UNRESOLVABLE), (\n'
        '        "recorded %s, found %s" % (sorted(_KNOWN_UNRESOLVABLE), sorted(seen)))\n')


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = LF / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _write(p, eol, text):
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.193.2.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.193.2: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.193.2.md")
    assert entry.startswith("## [0.193.2] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    tp, t_eol, test = _read(TEST)
    assert "_corpus_walk" not in test, "already applied"
    test = _once(test, IMPORTS_OLD, IMPORTS_NEW, "the json import")
    test = _once(test, WALK_OLD, _src("walk_helpers.py.txt"), "_brief_paths")
    assert test.endswith(TAIL) and test.count(TAIL) == 1, test[-160:]
    test = test + _src("walk_tests.py.txt")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    _write(tp, t_eol, test)
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.193.1 -> 0.193.2" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
