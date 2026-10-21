"""Level Factory 0.226.2: `contracts.GROUNDED`'s deli_counter row re-grounded to 0.241.0 for factory 1.41.0 -- one
row, ahead of the install test that certifies the set. 0.226.1 (`patch_lf_reground_1_41_0.py`) moved six rows for
that set; install test 10 then found the parking garage's ramp cut that Deli Counter 0.241.0 fixes, so the set the
factory certifies carries 0.241.0 and the table owes it its row.

  packages/tools/contracts.py   the deli_counter row 0.240.0 -> 0.241.0; a RE-GROUNDED note ahead of 0.226.1's
  tests/fixtures/repos/deli_counter/VERSION and the stub's contract command follow the pin

Every file's sha16 pinned and every anchor asserted once, nothing written until all matched. CHANGELOG and VERSION
from `lf_reground_0_226_2/CHANGELOG_0.226.2.md`; `--results-pending` leaves the RESULT_ keys to `--fill`.

Read before it was written, in this session: `contracts.py` line 64 (0.226.1's note) and 192 (the row), the stand-in's
VERSION and its stub's version line, each file's byte count and hash.

    python patches/patch_lf_reground_0_226_2.py --results-pending
    (LF_TOOLS_DIR=<factory> pytest tests/real_tools; the suite in level_factory)
    python patches/patch_lf_reground_0_226_2.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_reground_0_226_2"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SMOKE": "result_smoke.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.226.1", b"0.226.2"
CHANGELOG_HEAD = "## [0.226.1] - the certified table re-grounded for factory 1.41.0"
SHA = {"packages/tools/contracts.py": "32ead643d506d107",
       "tests/fixtures/repos/deli_counter/VERSION": "01a974cf113ffd26",
       "tests/fixtures/repos/deli_counter/deli_counter/__main__.py": "24098068a015b770"}

NOTE_ANCHOR = "# RE-GROUNDED 2026-10-20 (0.226.1), SIX ROWS, for factory 1.41.0: deli_counter\n"
NOTE = (
    "# RE-GROUNDED 2026-10-20 (0.226.2), ONE ROW, for factory 1.41.0: deli_counter\n"
    "# 0.240.0 -> 0.241.0 (a ramp's slab cut stops at its head, railed), which\n"
    "# install test 10 found the set needed after 0.226.1 was grounded to it.\n"
    "# Licensed by the real-tool smoke, which read exactly this row DRIFT before\n"
    "# and all green after.\n"
    "#\n")

EDITS = {"packages/tools/contracts.py": [
    (NOTE_ANCHOR, NOTE + NOTE_ANCHOR),
    ('    "deli_counter": {"version": "0.240.0", "source": "VERSION"},\n',
     '    "deli_counter": {"version": "0.241.0", "source": "VERSION"},\n'),
],
    "tests/fixtures/repos/deli_counter/VERSION": [("Deli Counter 0.240.0\n", "Deli Counter 0.241.0\n")],
    "tests/fixtures/repos/deli_counter/deli_counter/__main__.py": [
        ('    print(json.dumps({"tool_version": "0.240.0", "gameplay_schema": "1.21.0",\n',
         '    print(json.dumps({"tool_version": "0.241.0", "gameplay_schema": "1.21.0",\n')],
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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.226.2.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.226.2: results filled")


def main():
    if FILL:
        return fill()
    vraw = (LF / "VERSION").read_bytes()
    assert vraw.strip() == VERSION_WAS, vraw
    entry = (SRC / "CHANGELOG_0.226.2.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.226.2] - "), entry[:40]
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
    print("Level Factory 0.226.1 -> 0.226.2")


if __name__ == "__main__":
    main()
