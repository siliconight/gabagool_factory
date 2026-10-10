"""Level Factory 0.172.1: re-grounded to Lot 0.106.0 (roadmap 202). See
`lf_reground_172_1/CHANGELOG_0.172.1.md`.

Anchored edits, each asserted to match exactly once, nothing written until all of them did:
  packages/tools/contracts.py      `GROUNDED["lot"]` 0.105.0 -> 0.106.0, and the re-grounding's
                                   note above 0.170.0's
  tests/fixtures/repos/lot/VERSION the stand-in Lot declares the grounded version
                                   (`test_the_stub_repos_declare_the_grounded_versions`)
CHANGELOG and VERSION from `CHANGELOG_0.172.1.md`.

    python patch_lf_reground_172_1.py --results-pending   apply, the smoke's and suite's results unfilled
    python patch_lf_reground_172_1.py --fill               fill both from result_smoke.txt, result_suite.txt
    LF_ROOT=<copy> python patch_lf_reground_172_1.py --draft
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_reground_172_1"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SMOKE": "result_smoke.txt", "RESULT_SUITE": "result_suite.txt"}

CONTRACTS = "packages/tools/contracts.py"
ROW_OLD = '    "lot":          {"version": "0.105.0", "source": "VERSION"},\n'
ROW_NEW = '    "lot":          {"version": "0.106.0", "source": "VERSION"},\n'
NOTE_ANCHOR = "# RE-GROUNDED 2026-10-10 (0.170.0), ALL EIGHT BEHIND AGAIN, three weeks after\n"
NOTE = (
    "# RE-GROUNDED 2026-10-10 (0.172.1), ONE ROW, lot 0.105.0 -> 0.106.0: the\n"
    "# release that keeps a lamp or a tree out of a shop band's span (roadmap\n"
    "# 226). Cold run 9223's doctor WARNed `drift vs certified 0.105.0\n"
    "# (grounded); re-certify` and its notes named only the long-paths reminder\n"
    "# beside it, so the package a stranger would have received carried the\n"
    "# advice 0.170.0 took away. The smoke's `test_grounded_table` failed on\n"
    "# this row alone before (10 of 12 ran, test_real_lot passing against\n"
    "# 0.106.0), and that is what licenses the number. Any tool's release owes\n"
    "# this table its row before the factory certifies a set carrying it.\n"
    "#\n"
)
STUB = "tests/fixtures/repos/lot/VERSION"
STUB_OLD = b"Lot 0.105.0\n"
STUB_NEW = b"Lot 0.106.0\n"
CHANGELOG_HEAD = "## [0.172.0] - The walk's visual check fails a fight, not a sparkle\n"


def _eol(raw, rel):
    """The file's own line ending. A file with both refuses: there is no one ending to restore."""
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _text(rel):
    raw = (LF / rel).read_bytes()
    return raw.decode("utf-8").replace("\r\n", "\n"), _eol(raw, rel)


def fill():
    """Put the smoke's and the suite's results where the entry left them, in LF's CHANGELOG and
    in this patch's own copy of the entry, so the record and the release say the same thing."""
    assert (LF / "VERSION").read_bytes().strip() == b"0.172.1", (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value)
        results[key] = value
    targets = [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.172.1.md", "the entry")]
    writes = {}
    for path, rel in targets:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.172.1: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == b"0.172.0", (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.172.1.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.172.1] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    text, eol = _text(CONTRACTS)
    assert text.count(ROW_OLD) == 1, ("the lot row", text.count(ROW_OLD))
    assert text.count(NOTE_ANCHOR) == 1, ("0.170.0's note", text.count(NOTE_ANCHOR))
    text = text.replace(ROW_OLD, ROW_NEW).replace(NOTE_ANCHOR, NOTE + NOTE_ANCHOR)
    contracts = text.encode("utf-8").replace(b"\n", eol)
    stub = (LF / STUB).read_bytes()
    assert stub == STUB_OLD, (STUB, stub)
    cl_text, cl_eol = _text("CHANGELOG.md")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:90]
    # every anchor matched: now write
    (LF / CONTRACTS).write_bytes(contracts)
    (LF / STUB).write_bytes(STUB_NEW)
    (LF / "CHANGELOG.md").write_bytes(
        (entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(b"0.172.1")
    print("Level Factory 0.172.0 -> 0.172.1" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
