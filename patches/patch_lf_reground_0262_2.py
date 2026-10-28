"""Level Factory 0.262.2: `contracts.GROUNDED`'s deli_counter row re-grounded, 0.286.1 -> 0.286.2, for factory
1.42.1 -- one row, as 0.226.2 re-grounded one for 1.41.0. Deli Counter 0.286.2 releases the migrations index line
committed after 0.286.1 was tagged, which `verify-manifest --strict` read STALE. Copied from
`patch_lf_reground_1_42_1.py`; its rows, stand-ins and versions changed.

  packages/tools/contracts.py   the deli_counter row; a RE-GROUNDED note ahead of 0.262.1's
  tests/fixtures/repos/deli_counter  the stand-in's VERSION and its contract command follow the pin

    python patches/patch_lf_reground_0262_2.py --results-pending
    (LF_TOOLS_DIR=<factory> pytest tests/real_tools; the suite in level_factory)
    python patches/patch_lf_reground_0262_2.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_reground_0262_2"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SMOKE": "result_smoke.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.262.1", b"0.262.2"
CHANGELOG_HEAD = "## [0.262.1] - `contracts.GROUNDED` re-grounded for factory 1.42.1: eight rows"
SHA = {"packages/tools/contracts.py": "8fa2cb19ff3b8961",
       "tests/fixtures/repos/deli_counter/VERSION": "5c9e6116ac3c7f4b",
       "tests/fixtures/repos/deli_counter/deli_counter/__main__.py": "64ff010ac87ad2a8"}

NOTE_ANCHOR = "# RE-GROUNDED 2026-10-28 (0.262.1), EIGHT ROWS, for factory 1.42.1: deli_counter\n"
NOTE = (
    "# RE-GROUNDED 2026-10-28 (0.262.2), ONE ROW, for factory 1.42.1: deli_counter\n"
    "# 0.286.1 -> 0.286.2 (the migrations index line committed after 0.286.1 was\n"
    "# tagged, which verify-manifest --strict read STALE). Licensed by the\n"
    "# real-tool smoke, which read exactly this row DRIFT before and all green after.\n"
    "#\n")

EDITS = {"packages/tools/contracts.py": [
    (NOTE_ANCHOR, NOTE + NOTE_ANCHOR),
    ('    "deli_counter": {"version": "0.286.1", "source": "VERSION"},\n',
     '    "deli_counter": {"version": "0.286.2", "source": "VERSION"},\n'),
],
    "tests/fixtures/repos/deli_counter/VERSION": [("Deli Counter 0.286.1", "Deli Counter 0.286.2")],
    "tests/fixtures/repos/deli_counter/deli_counter/__main__.py": [
        ('    print(json.dumps({"tool_version": "0.286.1", "gameplay_schema": "1.21.0",\n',
         '    print(json.dumps({"tool_version": "0.286.2", "gameplay_schema": "1.21.0",\n')],
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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.262.2.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.262.2: results filled")


def main():
    if FILL:
        return fill()
    vraw = (LF / "VERSION").read_bytes()
    assert vraw.strip() == VERSION_WAS, vraw
    entry = (SRC / "CHANGELOG_0.262.2.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.262.2] - "), entry[:40]
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
    print("Level Factory 0.262.1 -> 0.262.2")


if __name__ == "__main__":
    main()
