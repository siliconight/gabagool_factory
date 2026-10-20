"""Level Factory 0.226.1: `contracts.GROUNDED` re-grounded for factory 1.41.0 -- six rows, ahead of the install test
that certifies the set (0.172.1's note: any tool's release owes this table its row before the factory certifies a
set carrying it). 0.211.1's patch (`patch_lf_reground_1_40_0.py`) is this one's pattern.

  packages/tools/contracts.py   six rows' versions; a RE-GROUNDED note ahead of 0.211.1's
  tests/fixtures/repos/*/VERSION  the six stand-in tools follow the pins; the stub Deli Counter's contract command
                                reports 0.240.0, the stub Dispatch's contract and build lock 0.5.3

Every file's sha16 pinned and every anchor asserted once, nothing written until all matched. CHANGELOG and VERSION
from `lf_reground_1_41_0/CHANGELOG_0.226.1.md`; `--results-pending` leaves the RESULT_ keys to `--fill`.

Read before it was written, in this session: `contracts.py` 60-72 (the RE-GROUNDED notes) and 184-238 (`GROUNDED`
whole), the six stand-ins' VERSION files, both stubs' version lines, and the smoke's failure before
(`lf_reground_1_41_0/smoke_before.out.txt`: exactly these six rows DRIFT, 10 of 12 ran, dispatch's example skipped as
before). Every file LF.

    python patches/patch_lf_reground_1_41_0.py --results-pending
    (LF_TOOLS_DIR=<factory> pytest tests/real_tools; the suite in level_factory)
    python patches/patch_lf_reground_1_41_0.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_reground_1_41_0"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SMOKE": "result_smoke.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.226.0", b"0.226.1"
CHANGELOG_HEAD = "## [0.226.0] - the perf panel calls the primitives monitor what it is"
SHA = {"packages/tools/contracts.py": "866ca15436677994",
       "tests/fixtures/repos/deli_counter/VERSION": "edb738567ab13fcc",
       "tests/fixtures/repos/dispatch/VERSION": "26e0ab83aa1ff6bd",
       "tests/fixtures/repos/lot/VERSION": "9179755006213bc6",
       "tests/fixtures/repos/lux/VERSION": "0f9269cda9907ead",
       "tests/fixtures/repos/patina/VERSION": "542c78ea150e4865",
       "tests/fixtures/repos/zoo/VERSION": "1f7f9e0a4d449de5",
       "tests/fixtures/repos/deli_counter/deli_counter/__main__.py": "d5a8bdffb6d32129",
       "tests/fixtures/repos/dispatch/dispatch/__main__.py": "0f6ae829b4ab7d60"}

NOTE_ANCHOR = "# RE-GROUNDED 2026-10-14 (0.211.1), SIX ROWS, for factory 1.40.0: deli_counter\n"
NOTE = (
    "# RE-GROUNDED 2026-10-20 (0.226.1), SIX ROWS, for factory 1.41.0: deli_counter\n"
    "# 0.222.0 -> 0.240.0, dispatch 0.5.2 -> 0.5.3, lot 0.123.0 -> 0.126.0, lux\n"
    "# 0.77.0 -> 0.79.0, patina 0.31.0 -> 0.32.0 and zoo 1.112.0 -> 1.117.0 -- every\n"
    "# release since factory 1.40.0, ahead of the install test that certifies the\n"
    "# set. Licensed by the real-tool smoke, which read exactly these six rows DRIFT\n"
    "# before and all green after.\n"
    "#\n")

EDITS = {"packages/tools/contracts.py": [
    (NOTE_ANCHOR, NOTE + NOTE_ANCHOR),
    ('    "deli_counter": {"version": "0.222.0", "source": "VERSION"},\n',
     '    "deli_counter": {"version": "0.240.0", "source": "VERSION"},\n'),
    ('    "lot":          {"version": "0.123.0", "source": "VERSION"},\n',
     '    "lot":          {"version": "0.126.0", "source": "VERSION"},\n'),
    ('    "zoo":          {"version": "1.112.0", "source": "VERSION",\n',
     '    "zoo":          {"version": "1.117.0", "source": "VERSION",\n'),
    ('    "lux":          {"version": "0.77.0", "source": "VERSION"},\n',
     '    "lux":          {"version": "0.79.0", "source": "VERSION"},\n'),
    ('    "patina":       {"version": "0.31.0", "source": "VERSION",\n',
     '    "patina":       {"version": "0.32.0", "source": "VERSION",\n'),
    ('    "dispatch":     {"version": "0.5.2",  "source": "contract probe",\n',
     '    "dispatch":     {"version": "0.5.3",  "source": "contract probe",\n'),
],
    # THE STAND-INS FOLLOW THE PINS (`test_the_stub_repos_declare_the_grounded_versions`), as in 0.211.1
    "tests/fixtures/repos/deli_counter/VERSION": [("Deli Counter 0.222.0\n", "Deli Counter 0.240.0\n")],
    "tests/fixtures/repos/dispatch/VERSION": [("0.5.2\n", "0.5.3\n")],
    "tests/fixtures/repos/lot/VERSION": [("Lot 0.123.0\n", "Lot 0.126.0\n")],
    "tests/fixtures/repos/lux/VERSION": [("Lux 0.77.0\n", "Lux 0.79.0\n")],
    "tests/fixtures/repos/patina/VERSION": [("Patina 0.31.0\n", "Patina 0.32.0\n")],
    "tests/fixtures/repos/zoo/VERSION": [("1.112.0\n", "1.117.0\n")],
    "tests/fixtures/repos/deli_counter/deli_counter/__main__.py": [
        ('    print(json.dumps({"tool_version": "0.222.0", "gameplay_schema": "1.21.0",\n',
         '    print(json.dumps({"tool_version": "0.240.0", "gameplay_schema": "1.21.0",\n')],
    "tests/fixtures/repos/dispatch/dispatch/__main__.py": [
        ('The version it reports is the grounded one, 0.5.2 (Level Factory 0.170.0)."""\n',
         'The version it reports is the grounded one, 0.5.3 (Level Factory 0.226.1; 0.5.2 from 0.170.0)."""\n'),
        ('    "tool": "dispatch", "version": "0.5.2", "contract": "dispatch.mission.v0.2",\n',
         '    "tool": "dispatch", "version": "0.5.3", "contract": "dispatch.mission.v0.2",\n'),
        ('        {"tool": "dispatch", "version": "0.5.2"}, sort_keys=True))\n',
         '        {"tool": "dispatch", "version": "0.5.3"}, sort_keys=True))\n')],
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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.226.1.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.226.1: results filled")


def main():
    if FILL:
        return fill()
    vraw = (LF / "VERSION").read_bytes()
    assert vraw.strip() == VERSION_WAS, vraw
    entry = (SRC / "CHANGELOG_0.226.1.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.226.1] - "), entry[:40]
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
    print("Level Factory 0.226.0 -> 0.226.1")


if __name__ == "__main__":
    main()
