"""Level Factory 0.180.1: re-grounded to Lot 0.117.0 (the walk test's navigation on its own thread,
its clock unsynchronised -- factory roadmap 239). One row of `contracts.GROUNDED`, a note above
0.180.0's, and the stand-in's VERSION; CHANGELOG and VERSION from
`lf_reground_180_1/CHANGELOG_0.180.1.md`. Each anchor asserted once, nothing written on a miss;
`--results-pending` leaves the RESULT_ keys to `--fill`.

    python patches/patch_lf_reground_180_1.py --results-pending
    cd level_factory && LF_TOOLS_DIR=<factory> python -m pytest -q tests/real_tools
    python patches/patch_lf_reground_180_1.py --fill
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_reground_180_1"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SMOKE": "result_smoke.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.180.0", b"0.180.1"
CHANGELOG_HEAD = ("## [0.180.0] - Laser Tag's evaluation runs on a clock that does not wait on real "
                  "seconds; the grounded table follows Laser Tag 0.27.0 and Zoo 1.102.0\n")
CONTRACTS = "packages/tools/contracts.py"
ROWS = [
    ('    "lot":          {"version": "0.116.0", "source": "VERSION"},\n',
     '    "lot":          {"version": "0.117.0", "source": "VERSION"},\n'),
]
NOTE_ANCHOR = "# RE-GROUNDED 2026-10-11 (0.180.0), TWO ROWS: laser_tag 0.26.0 -> 0.27.0 (the\n"
NOTE = (
    "# RE-GROUNDED 2026-10-11 (0.180.1), ONE ROW: lot 0.116.0 -> 0.117.0 (the walk\n"
    "# test's navigation updates on its own thread and walktest.py runs it under\n"
    "# `--fixed-fps 60`). Licensed by the real-tool smoke, which read exactly this\n"
    "# row DRIFT before and all green after.\n"
    "#\n"
)
STUBS = [("tests/fixtures/repos/lot/VERSION", b"Lot 0.116.0\n", b"Lot 0.117.0\n")]


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.180.1.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.180.1: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.180.1.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.180.1] - "), entry[:40]
    left = entry
    if PENDING:
        for key in RESULTS:
            left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    p = LF / CONTRACTS
    raw = p.read_bytes()
    eol = _eol(raw, CONTRACTS)
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert "(0.180.1), ONE ROW" not in text, "already applied"
    for old, new in ROWS:
        assert text.count(old) == 1, (old.strip(), text.count(old))
        text = text.replace(old, new)
    assert text.count(NOTE_ANCHOR) == 1, "0.180.0's note not found once"
    text = text.replace(NOTE_ANCHOR, NOTE + NOTE_ANCHOR)
    stubs = []
    for rel, old, new in STUBS:
        sp = LF / rel
        got = sp.read_bytes()
        assert got.replace(b"\r\n", b"\n") == old, (rel, got)
        stubs.append((sp, new))
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    p.write_bytes(text.encode("utf-8").replace(b"\n", eol))
    for sp, new in stubs:
        sp.write_bytes(new)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.180.0 -> 0.180.1: lot re-grounded (0.117.0), its stub moved")


if __name__ == "__main__":
    sys.exit(main())
