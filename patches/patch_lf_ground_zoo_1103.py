"""Level Factory 0.193.1: re-grounded to Zoo 1.103.0 (factory roadmap 239, ahead of factory 1.39.0).

Anchored edits, each asserted once, nothing written until all of them matched:
  packages/tools/contracts.py        the 0.193.1 note above the newest one; the zoo row 1.102.0 ->
                                     1.103.0
  tests/fixtures/repos/zoo/VERSION   1.102.0 -> 1.103.0
CHANGELOG and VERSION from `lf_ground_zoo_1103/CHANGELOG_0.193.1.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`.

Read before it was written: the real-tool smoke on 0.193.0 (LF_TOOLS_DIR=<factory> pytest
tests/real_tools): exactly the zoo row DRIFT, grounded 1.102.0, installed 1.103.0.

    python patches/patch_lf_ground_zoo_1103.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_ground_zoo_1103.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_ground_zoo_1103"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SMOKE": "result_smoke.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.193.0", b"0.193.1"
CHANGELOG_HEAD = ("## [0.193.0] - The bake's editor stops drawing for the bake; its work copy is copied "
                  "in parallel and removed in the background\n")
CONTRACTS = "packages/tools/contracts.py"
STAND_IN = "tests/fixtures/repos/zoo/VERSION"
SHA = {CONTRACTS: "4280dedd8b277911", STAND_IN: "50d45e654632c03c"}

NOTE_ANCHOR = "# RE-GROUNDED 2026-10-11 (0.180.1), ONE ROW: lot 0.116.0 -> 0.117.0 (the walk\n"
NOTE_NEW = ("# RE-GROUNDED 2026-10-12 (0.193.1), ONE ROW: zoo 1.102.0 -> 1.103.0 (a mesh\n"
            "# leaves with its faces in one order, the same every build), ahead of the\n"
            "# install test that certifies factory 1.39.0. Licensed by the real-tool\n"
            "# smoke, which read exactly this row DRIFT before and all green after.\n"
            "#\n")
ROW_OLD = '    "zoo":          {"version": "1.102.0", "source": "VERSION",\n'
ROW_NEW = '    "zoo":          {"version": "1.103.0", "source": "VERSION",\n'


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.193.1.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.193.1: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.193.1.md")
    assert entry.startswith("## [0.193.1] - "), entry[:40]
    left = entry
    if PENDING:
        for key in RESULTS:
            left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    cp, c_eol, con = _read(CONTRACTS)
    con = _once(con, NOTE_ANCHOR, NOTE_NEW + NOTE_ANCHOR, "the newest note")
    con = _once(con, ROW_OLD, ROW_NEW, "the zoo row")
    sp, s_eol, stand = _read(STAND_IN)
    assert stand == "1.102.0\n", repr(stand)
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    _write(cp, c_eol, con)
    _write(sp, s_eol, "1.103.0\n")
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.193.0 -> 0.193.1")


if __name__ == "__main__":
    main()
