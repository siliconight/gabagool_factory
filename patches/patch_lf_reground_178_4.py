"""Level Factory 0.178.4: re-grounded to the set factory 1.38.0 certifies (roadmap 202). See
`lf_reground_178_4/CHANGELOG_0.178.4.md`.

Anchored edits, each asserted to match exactly once, nothing written until all of them did:
  packages/tools/contracts.py   four `GROUNDED` rows (deli_counter 0.207.1 -> 0.208.0, lot 0.115.0
                                -> 0.116.0, zoo 1.97.0 -> 1.100.0, lux 0.74.0 -> 0.75.0), and the
                                re-grounding's note above 0.178.2's
  tests/fixtures/repos/{deli_counter,lot,lux,zoo}/VERSION   the stand-ins declare the grounded
                                versions (`test_the_stub_repos_declare_the_grounded_versions`)
  tests/fixtures/repos/deli_counter/deli_counter/__main__.py  the stub's `contract` reports it
CHANGELOG and VERSION from `CHANGELOG_0.178.4.md`.

    python patches/patch_lf_reground_178_4.py --results-pending   apply, the smoke's and suite's results unfilled
    python patches/patch_lf_reground_178_4.py --fill               fill both from result_smoke.txt, result_suite.txt
    LF_ROOT=<copy> python patches/patch_lf_reground_178_4.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_reground_178_4"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SMOKE": "result_smoke.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.178.3", b"0.178.4"
CHANGELOG_HEAD = "## [0.178.3] - "

CONTRACTS = "packages/tools/contracts.py"
SHA = {CONTRACTS: "db3bf7a6e286c792",
       "tests/fixtures/repos/deli_counter/deli_counter/__main__.py": "c298c484eaba717d"}
ROWS = [
    ('    "deli_counter": {"version": "0.207.1", "source": "VERSION"},\n',
     '    "deli_counter": {"version": "0.208.0", "source": "VERSION"},\n'),
    ('    "lot":          {"version": "0.115.0", "source": "VERSION"},\n',
     '    "lot":          {"version": "0.116.0", "source": "VERSION"},\n'),
    ('    "zoo":          {"version": "1.97.0", "source": "VERSION",\n',
     '    "zoo":          {"version": "1.100.0", "source": "VERSION",\n'),
    ('    "lux":          {"version": "0.74.0", "source": "VERSION"},\n',
     '    "lux":          {"version": "0.75.0", "source": "VERSION"},\n'),
]
NOTE_ANCHOR = "# RE-GROUNDED 2026-10-11 (0.178.2), FOUR ROWS, for factory 1.37.0: deli_counter\n"
NOTE = (
    "# RE-GROUNDED 2026-10-11 (0.178.4), FOUR ROWS, for factory 1.38.0: deli_counter\n"
    "# 0.207.1 -> 0.208.0 (a home's room hangs a dome), lot 0.115.0 -> 0.116.0 (a\n"
    "# lane lights its own length), zoo 1.97.0 -> 1.100.0 (the dome fixture and its\n"
    "# fix, the container roof, the hemisphere's upper half, a fixture's parts\n"
    "# merged inside it) and lux 0.74.0 -> 0.75.0 (the dome's rig). Done before the\n"
    "# install test that certifies the set, as 0.172.1's note says it must be.\n"
    "# Licensed by the real-tool smoke (`test_grounded_table`), before and after.\n"
    "#\n"
)
STUBS = [
    ("tests/fixtures/repos/deli_counter/VERSION", b"Deli Counter 0.207.1\n", b"Deli Counter 0.208.0\n"),
    ("tests/fixtures/repos/lot/VERSION", b"Lot 0.115.0\n", b"Lot 0.116.0\n"),
    ("tests/fixtures/repos/lux/VERSION", b"Lux 0.74.0\n", b"Lux 0.75.0\n"),
    ("tests/fixtures/repos/zoo/VERSION", b"1.97.0\n", b"1.100.0\n"),
]
DC_STUB = "tests/fixtures/repos/deli_counter/deli_counter/__main__.py"
DC_EDITS = [
    ("version it reports is the grounded one, 0.207.1 (Level Factory 0.178.2).\"\"\"\n",
     "version it reports is the grounded one, 0.208.0 (Level Factory 0.178.4).\"\"\"\n"),
    ('    print(json.dumps({"tool_version": "0.207.1", "gameplay_schema": "1.21.0",\n',
     '    print(json.dumps({"tool_version": "0.208.0", "gameplay_schema": "1.21.0",\n'),
]


def _eol(raw, rel):
    """The file's own line ending. A file with both refuses: there is no one ending to restore."""
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _text(rel, pin=True):
    raw = (LF / rel).read_bytes()
    if pin and rel in SHA:
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return raw.decode("utf-8").replace("\r\n", "\n"), _eol(raw, rel)


def fill():
    """Put the smoke's and the suite's results where the entry left them, in LF's CHANGELOG and
    in this patch's own copy of the entry, so the record and the release say the same thing."""
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    targets = [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.178.4.md", "the entry")]
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
    print("Level Factory 0.178.4: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.178.4.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.178.4] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    text, eol = _text(CONTRACTS)
    for old, new in ROWS:
        assert text.count(old) == 1, ("row", old.strip()[:30], text.count(old))
        text = text.replace(old, new)
    assert text.count(NOTE_ANCHOR) == 1, ("0.178.2's note", text.count(NOTE_ANCHOR))
    text = text.replace(NOTE_ANCHOR, NOTE + NOTE_ANCHOR)
    contracts = text.encode("utf-8").replace(b"\n", eol)
    for rel, old, _new in STUBS:
        got = (LF / rel).read_bytes()
        assert got == old, (rel, got)
    dc, dc_eol = _text(DC_STUB)
    for old, new in DC_EDITS:
        assert dc.count(old) == 1, ("dc stub", old.strip()[:40], dc.count(old))
        dc = dc.replace(old, new)
    cl_text, cl_eol = _text("CHANGELOG.md", pin=False)
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count("## [0.178.4]") == 0, cl_text[:90]
    # every anchor matched: now write
    (LF / CONTRACTS).write_bytes(contracts)
    for rel, _old, new in STUBS:
        (LF / rel).write_bytes(new)
    (LF / DC_STUB).write_bytes(dc.encode("utf-8").replace(b"\n", dc_eol))
    (LF / "CHANGELOG.md").write_bytes(
        (entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.178.3 -> 0.178.4" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
