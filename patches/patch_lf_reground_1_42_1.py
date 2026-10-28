"""Level Factory 0.262.1: `contracts.GROUNDED` re-grounded for factory 1.42.1 -- eight rows, ahead of the install test
that certifies the set (0.172.1's note: any tool's release owes this table its row before the factory certifies a
set carrying it). Factory 1.42.0 was certified without it, and its install test's five drift lines were that.
`patch_lf_reground_1_41_0.py` is this one's pattern, copied; its rows, stand-ins and versions changed.

  packages/tools/contracts.py   eight rows' versions; a RE-GROUNDED note ahead of 0.226.2's
  tests/fixtures/repos/*/VERSION  the eight stand-in tools follow the pins; the stub Deli Counter's contract command
                                reports 0.286.1, the stub Dispatch's contract and build lock 0.5.4

Every file's sha16 pinned and every anchor asserted once, nothing written until all matched. CHANGELOG and VERSION
from `lf_reground_1_42_1/CHANGELOG_0.262.1.md`; `--results-pending` leaves the RESULT_ keys to `--fill`.

Read before it was written, in this session: `contracts.py` 60-76 (the RE-GROUNDED notes) and 197-240 (`GROUNDED`),
the eight stand-ins' VERSION files, both stubs' version lines, `python -m dispatch contract` (version 0.5.4), and the
smoke's failure before (`lf_reground_1_42_1/smoke_before.out.txt`: exactly these eight rows DRIFT, 10 of 12 ran,
dispatch's example skipped as before). Every file LF.

    python patches/patch_lf_reground_1_42_1.py --results-pending
    (LF_TOOLS_DIR=<factory> pytest tests/real_tools; the suite in level_factory)
    python patches/patch_lf_reground_1_42_1.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_reground_1_42_1"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SMOKE": "result_smoke.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.262.0", b"0.262.1"
CHANGELOG_HEAD = "## [0.262.0] - a bank's band is dealt the name its other faces already give it"
SHA = {"packages/tools/contracts.py": "a10769e371766500",
       "tests/fixtures/repos/deli_counter/VERSION": "ca4742fa554fef1b",
       "tests/fixtures/repos/dispatch/VERSION": "27ecff1fcdaf65ab",
       "tests/fixtures/repos/laser_tag/VERSION": "a915bc7aef6ab546",
       "tests/fixtures/repos/lot/VERSION": "876573c8f5520c83",
       "tests/fixtures/repos/lux/VERSION": "114a4c3372a58294",
       "tests/fixtures/repos/patina/VERSION": "cb796060d9f9d1b4",
       "tests/fixtures/repos/pixelcoat/VERSION": "7cd8609f32b95929",
       "tests/fixtures/repos/zoo/VERSION": "ff2e97e12c073a7c",
       "tests/fixtures/repos/deli_counter/deli_counter/__main__.py": "dec6cbb3d9e12307",
       "tests/fixtures/repos/dispatch/dispatch/__main__.py": "ce9515ad1b2f3f96"}

NOTE_ANCHOR = "# RE-GROUNDED 2026-10-20 (0.226.2), ONE ROW, for factory 1.41.0: deli_counter\n"
NOTE = (
    "# RE-GROUNDED 2026-10-28 (0.262.1), EIGHT ROWS, for factory 1.42.1: deli_counter\n"
    "# 0.241.0 -> 0.286.1, dispatch 0.5.3 -> 0.5.4, laser_tag 0.32.0 -> 0.32.1, lot\n"
    "# 0.126.0 -> 0.135.0, lux 0.79.0 -> 0.80.0, patina 0.32.0 -> 0.32.1, pixelcoat\n"
    "# 0.62.0 -> 0.63.0 and zoo 1.117.0 -> 1.142.0 -- every release since factory\n"
    "# 1.41.0. Factory 1.42.0 was certified WITHOUT this, and its install test's\n"
    "# setup read five of these rows as drift: the manifest's promotion does not\n"
    "# move this table. Licensed by the real-tool smoke, which read exactly these\n"
    "# eight rows DRIFT before and all green after.\n"
    "#\n")

EDITS = {"packages/tools/contracts.py": [
    (NOTE_ANCHOR, NOTE + NOTE_ANCHOR),
    ('    "deli_counter": {"version": "0.241.0", "source": "VERSION"},\n',
     '    "deli_counter": {"version": "0.286.1", "source": "VERSION"},\n'),
    ('    "lot":          {"version": "0.126.0", "source": "VERSION"},\n',
     '    "lot":          {"version": "0.135.0", "source": "VERSION"},\n'),
    ('    "laser_tag":    {"version": "0.32.0", "source": "VERSION",\n',
     '    "laser_tag":    {"version": "0.32.1", "source": "VERSION",\n'),
    ('    "pixelcoat":    {"version": "0.62.0", "source": "VERSION",\n',
     '    "pixelcoat":    {"version": "0.63.0", "source": "VERSION",\n'),
    ('    "zoo":          {"version": "1.117.0", "source": "VERSION",\n',
     '    "zoo":          {"version": "1.142.0", "source": "VERSION",\n'),
    ('    "lux":          {"version": "0.79.0", "source": "VERSION"},\n',
     '    "lux":          {"version": "0.80.0", "source": "VERSION"},\n'),
    ('    "patina":       {"version": "0.32.0", "source": "VERSION",\n',
     '    "patina":       {"version": "0.32.1", "source": "VERSION",\n'),
    ('    "dispatch":     {"version": "0.5.3",  "source": "contract probe",\n',
     '    "dispatch":     {"version": "0.5.4",  "source": "contract probe",\n'),
],
    # THE STAND-INS FOLLOW THE PINS (`test_the_stub_repos_declare_the_grounded_versions`), as in 0.226.1
    "tests/fixtures/repos/deli_counter/VERSION": [("Deli Counter 0.241.0", "Deli Counter 0.286.1")],
    "tests/fixtures/repos/dispatch/VERSION": [("0.5.3", "0.5.4")],
    "tests/fixtures/repos/laser_tag/VERSION": [("Laser Tag 0.32.0", "Laser Tag 0.32.1")],
    "tests/fixtures/repos/lot/VERSION": [("Lot 0.126.0", "Lot 0.135.0")],
    "tests/fixtures/repos/lux/VERSION": [("Lux 0.79.0", "Lux 0.80.0")],
    "tests/fixtures/repos/patina/VERSION": [("Patina 0.32.0", "Patina 0.32.1")],
    "tests/fixtures/repos/pixelcoat/VERSION": [("Pixelcoat 0.62.0", "Pixelcoat 0.63.0")],
    "tests/fixtures/repos/zoo/VERSION": [("1.117.0", "1.142.0")],
    "tests/fixtures/repos/deli_counter/deli_counter/__main__.py": [
        ('    print(json.dumps({"tool_version": "0.241.0", "gameplay_schema": "1.21.0",\n',
         '    print(json.dumps({"tool_version": "0.286.1", "gameplay_schema": "1.21.0",\n')],
    "tests/fixtures/repos/dispatch/dispatch/__main__.py": [
        ('The version it reports is the grounded one, 0.5.3 (Level Factory 0.226.1; 0.5.2 from 0.170.0)."""\n',
         'The version it reports is the grounded one, 0.5.4 (Level Factory 0.262.1; 0.5.3 from 0.226.1, 0.5.2 from '
         '0.170.0)."""\n'),
        ('    "tool": "dispatch", "version": "0.5.3", "contract": "dispatch.mission.v0.2",\n',
         '    "tool": "dispatch", "version": "0.5.4", "contract": "dispatch.mission.v0.2",\n'),
        ('        {"tool": "dispatch", "version": "0.5.3"}, sort_keys=True))\n',
         '        {"tool": "dispatch", "version": "0.5.4"}, sort_keys=True))\n')],
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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.262.1.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.262.1: results filled")


def main():
    if FILL:
        return fill()
    vraw = (LF / "VERSION").read_bytes()
    assert vraw.strip() == VERSION_WAS, vraw
    entry = (SRC / "CHANGELOG_0.262.1.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.262.1] - "), entry[:40]
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
    print("Level Factory 0.262.0 -> 0.262.1")


if __name__ == "__main__":
    main()
